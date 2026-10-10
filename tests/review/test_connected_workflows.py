"""Connected review diagram contracts; no browser or third-party dependency."""
from collections import Counter,defaultdict
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import math
import re
import sys
import unittest
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/review'))
from payroll_flow_diagrams import layout,box,overlap,segment_hits,navigation_kind
OUT=ROOT/'docs/review/pay-html-001'
NS={'s':'http://www.w3.org/2000/svg'}

class ConnectedWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=json.loads((OUT/'data/model.json').read_text())
        cls.graphs={f['id']:layout(f) for f in cls.model['workflows']}
    def walk(self,edges,seeds):
        seen=set(seeds);todo=list(seeds)
        while todo:
            for n in edges.get(todo.pop(),[]):
                if n not in seen:seen.add(n);todo.append(n)
        return seen
    def svg(self,fid):
        text=(OUT/'workflows'/f'{fid.lower()}.html').read_text()
        source=re.search(r'<svg class="workflow-diagram".*?</svg>',text,re.S).group(0)
        return ET.fromstring(source)
    def test_all_fifteen_are_connected_and_reach_a_review_end(self):
        self.assertEqual(len(self.graphs),15)
        for fid,g in self.graphs.items():
            with self.subTest(flow=fid):
                nodes={n['id'] for n in g['nodes']};forward=defaultdict(list);backward=defaultdict(list)
                self.assertTrue(g['starts']);self.assertTrue(g['ends'])
                for e in g['edges']:
                    self.assertIn(e['from_node'],nodes);self.assertIn(e['to_node'],nodes)
                    forward[e['from_node']].append(e['to_node']);backward[e['to_node']].append(e['from_node'])
                self.assertEqual(self.walk(forward,g['starts']),nodes)
                self.assertEqual(self.walk(backward,g['ends']),nodes)
    def test_every_business_step_is_drawn_once(self):
        for f in self.model['workflows']:
            svg=self.svg(f['id'])
            ids=[n.get('data-step-id') for n in svg.findall('.//*[@data-step-id]')]
            self.assertEqual(Counter(ids),Counter(s['id'] for s in f['steps']),f['id'])
    def test_business_edge_model_svg_and_table_are_identical(self):
        for f in self.model['workflows']:
            svg=self.svg(f['id']);drawn=svg.findall('.//*[@data-source-step]')
            self.assertEqual(len(drawn),len(f['edges']))
            document=(OUT/'workflows'/f'{f["id"].lower()}.html').read_text()
            for i,e in enumerate(f['edges']):
                eid=f'{f["id"]}-edge-{i+1:02}'
                n=next(n for n in drawn if n.get('data-edge-id')==eid)
                self.assertEqual((n.get('data-source-step'),n.get('data-target-step')),(e['from'],e['to']))
                self.assertEqual(n.find('s:title',NS).text,e['label'])
                self.assertEqual(document.count(f'data-edge-reference="{eid}"'),1)
    def test_branch_conditions_are_nonempty_and_distinct(self):
        for f in self.model['workflows']:
            outgoing=defaultdict(list)
            for e in f['edges']:outgoing[e['from']].append(e['label'])
            for source,labels in outgoing.items():
                self.assertTrue(all(label.strip() for label in labels),(f['id'],source))
                self.assertEqual(len(labels),len(set(labels)),(f['id'],source))
    def test_svg_nodes_do_not_overlap_or_clip(self):
        for fid,g in self.graphs.items():
            for annotation in g['annotations']:
                for n in g['nodes']:self.assertFalse(overlap(box(annotation),box(n)),(fid,annotation['id'],n['id']))
            for i,n in enumerate(g['nodes']):
                b=box(n)
                self.assertTrue(0<=b[0]<b[2]<=g['width'] and 65<=b[1]<b[3]<=g['height'],(fid,n['id'],b))
                for other in g['nodes'][i+1:]:self.assertFalse(overlap(b,box(other)),(fid,n['id'],other['id']))
    def test_edges_are_orthogonal_attached_and_avoid_unrelated_nodes(self):
        for fid,g in self.graphs.items():
            byid={n['id']:n for n in g['nodes']}
            for e in g['edges']:
                for p,nid in [(e['points'][0],e['from_node']),(e['points'][-1],e['to_node'])]:
                    b=box(byid[nid]);self.assertTrue(p[0] in (b[0],b[2]) or p[1] in (b[1],b[3]),(fid,e['id'],nid))
                for a,b in zip(e['points'],e['points'][1:]):
                    self.assertTrue(a[0]==b[0] or a[1]==b[1])
                    for n in g['nodes']+g['annotations']:
                        if n['id'] not in (e['from_node'],e['to_node']):self.assertFalse(segment_hits(a,b,box(n)),(fid,e['id'],n['id']))
    def test_labels_do_not_hide_nodes_edges_or_other_labels(self):
        for fid,g in self.graphs.items():
            seen=[]
            for e in g['edges']:
                if 'label_box' not in e:continue
                r=e['label_box']
                distances=[]
                for a,b in zip(e['points'],e['points'][1:]):
                    x1,x2=sorted((a[0],b[0]));y1,y2=sorted((a[1],b[1]))
                    distances.append(math.hypot(max(x1-r[2],r[0]-x2,0),max(y1-r[3],r[1]-y2,0)))
                self.assertLessEqual(min(distances),30,(fid,e['id'],'label too far from its connector'))
                for n in g['nodes']+g['annotations']:self.assertFalse(overlap(r,box(n)),(fid,e['id'],n['id']))
                for prior in seen:self.assertFalse(overlap(r,prior),(fid,e['id']))
                for path in g['edges']:
                    for a,b in zip(path['points'],path['points'][1:]):self.assertFalse(segment_hits(a,b,r),(fid,e['id'],path['id']))
                seen.append(r)
    def test_confirmed_core_unchanged_except_documented_wf15_completion(self):
        fields=['id','name','actor','start','end','status','screen_ids','requirements','source_ids','steps','edges']
        core=[{k:deepcopy(f[k]) for k in fields} for f in self.model['workflows']]
        f=next(f for f in core if f['id']=='WF-15')
        new=[s for s in f['steps'] if s['id']=='h'];self.assertEqual(len(new),1)
        self.assertFalse(new[0]['operation_id']);self.assertIn('PAY-02',new[0]['detail'])
        f['steps']=[s for s in f['steps'] if s['id']!='h'];f['edges']=[e for e in f['edges'] if e['to']!='h']
        data=json.dumps(core,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        self.assertEqual(hashlib.sha256(data).hexdigest(),'d65daa79bd1a3db865db70c443800d3c97df62b2103c0586f6c51fd3a94e39f5')
    def test_parallel_and_rowwise_branches_are_not_exclusive(self):
        flows={f['id']:f for f in self.model['workflows']}
        self.assertEqual(flows['WF-02']['diagram']['gateway_types']['c'],'parallel')
        self.assertEqual(flows['WF-02']['diagram']['gateway_types']['d'],'parallel')
        self.assertEqual(flows['WF-04']['diagram']['gateway_types']['c'],'inclusive')
        self.assertEqual(flows['WF-15']['diagram']['gateway_types']['e'],'inclusive')
    def test_navigation_has_one_source_and_one_node_per_destination_group(self):
        text=(OUT/'navigation.html').read_text();groups=defaultdict(set)
        for o in self.model['operations']:
            if o['screen_id']!=o['destination_screen_id']:groups[o['screen_id']].add(o['destination_screen_id'])
        svgs=re.findall(r'<svg class="navigation-fanout".*?</svg>',text,re.S)
        self.assertEqual(len(svgs),len(groups));seen=[]
        for source in svgs:
            svg=ET.fromstring(source);sid=svg.get('data-navigation-source');seen.append(sid)
            self.assertEqual(len(svg.findall('.//*[@data-source-screen]')),1)
            dests=[n.get('data-destination-screen') for n in svg.findall('.//*[@data-destination-screen]')]
            self.assertEqual(set(dests),groups[sid]);self.assertEqual(len(dests),len(set(dests)))
        self.assertEqual(set(seen),set(groups));self.assertEqual(len(seen),len(set(seen)))
        self.assertNotIn('class="lane-diagram"',text)
    def test_external_routes_are_not_automatic_screen_navigation(self):
        operations={o['id']:o for o in self.model['operations']}
        expected={'OP-F-HTML':'new-tab','OP-F-RETURN-HTML':'tab-return','OP-JLINK-EXPORT':'file-handoff','OP-JINKYU-PROCESS':'file-handoff','OP-AD-CANDIDATE':'information','OP-RETRO-EXPORT':'information'}
        for oid,kind in expected.items():self.assertEqual(navigation_kind(operations[oid])[0],kind)
    def test_static_controls_and_operation_links_exist(self):
        for f in self.model['workflows']:
            document=(OUT/'workflows'/f'{f["id"].lower()}.html').read_text()
            for name in ('data-diagram-all','data-diagram-fit','data-diagram-actual','data-diagram-in','data-diagram-out'):self.assertIn(name,document)
            self.assertIn('BPMN 2.0の実行可能な定義ではありません',document)
            self.assertIn('0.2-review',document)
if __name__=='__main__':unittest.main()
