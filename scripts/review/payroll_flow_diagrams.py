#!/usr/bin/env python3
"""PAY-HTML-002: reviewed, connected swimlane views of the unchanged workflow model.

The original steps/edges are the business definition. Layout metadata is deliberately
separate: events and routing gateways do not add application operations or permissions.
This is BPMN-inspired review notation, not executable BPMN 2.0.
"""
import html
import heapq
import math

E=lambda value: html.escape(str(value),quote=True)
# A position is (lane, row). Lanes describe responsibility and/or execution boundary;
# their explicit subtitles avoid inventing a new business actor for app automation.
CONFIG={
'WF-01':dict(lanes=[('利用者','職員検索・詳細','app'),('利用者','未保存の移動・画面往復','app')], pos={'a':(0,0),'b':(0,1),'c':(0,2),'d':(0,3),'e':(0,4),'f':(0,5),'g':(1,4),'h':(1,3),'i':(1,5),'j':(1,6)}, finish={'c':'読取りで確認区間終了'}, summary='検索 → 職員選択 → 編集。保存は元の詳細へ、移動取消は入力へ、支給明細からの復路は職員選択へ戻ります。'),
'WF-02':dict(lanes=[('秘書課・前工程担当','A～D／給与アプリ外','external'),('給与アプリ','候補作成・番号反映','app'),('給与班','候補の確認・確定','app')],pos={'a':(0,0),'b':(0,1),'i':(0,2),'c':(0,3),'d':(1,4),'e':(2,5),'f':(0,4),'g':(1,6),'h':(2,7)},gateways={'c':'parallel','d':'parallel'},summary='Cの発令登録完了から、候補作成と職員番号発行へ分かれます。番号発行を待たず給与班の確認・確定へ進めます。', notes=['「＋」は並行する後続関係です。番号と候補の整合確認は、給与班の確認・確定を待たせる条件ではありません。','番号反映の合流は、候補の存在と番号発行済みを合わせる関係です。最終の整合確認は給与計算開始の新しい条件ではありません。','自動通知・番号反映の方式と実現可否は未決です。']) ,
'WF-03':dict(lanes=[('給与班・給与アプリ','変更の比較と再確認','app'),('給与班・給与アプリ','取消と計算除外','app')],pos={'a':(0,0),'b':(0,1),'c':(0,2),'d':(0,3),'e':(0,4),'f':(0,5),'g':(1,2),'h':(1,3)},summary='変更は旧値を保持して給与班が再確認。採用取消は候補を削除せず、履歴を残して給与計算から除外します。'),
'WF-04':dict(lanes=[('給与班・取込処理','検証と正常行','app'),('給与班','問題行の判断','app'),('局担当者／給与班','不足の訂正','app')],pos={'a':(0,0),'b':(0,1),'c':(0,2),'d':(0,3),'e':(1,3),'f':(0,4),'g':(1,4),'h':(2,5)},gateways={'c':'inclusive'},summary='ファイルを検証し、正常行を先行取込。問題行は給与班が1行ずつ取り込むか見送るか判断し、確認待ち候補へつなぎます。',notes=['「○」は行ごとの振分けです。同じファイルに正常行と問題行があれば、両方の経路を扱います。勤怠取込の全件事前検証とは異なります。']),
'WF-05':dict(lanes=[('局担当者／給与班','登録・訂正と提出','app'),('給与班','内容確認と確定','app'),('給与計算','未払いの再計算・照合','app')],pos={'a':(0,0),'b':(0,1),'c':(0,2),'d':(0,3),'e':(0,4),'f':(1,5),'g':(0,5),'h':(1,6),'i':(2,7)},summary='実際の変更と誤登録訂正を分け、同じ確認待ちへ合流。不足は訂正へ戻し、給与班確定後に未払い分へ反映します。',notes=['登録・訂正は原則局担当者、給与班も直接修正可能です。レーンはこの権限範囲を追加・縮小しません。']),
'WF-06':dict(lanes=[('局担当者','入力・提出・再提出','app'),('給与アプリ','入力検証・計算参照','app'),('給与班','審査・差戻し・認定','app')],pos={'a':(0,0),'b':(1,1),'c':(0,2),'d':(2,3),'e':(2,2),'f':(2,4),'g':(1,5)},summary='局担当が入力・提出 → 給与班が審査・認定。不備は元の提出者の入力へ戻り、認定後は給与計算が情報を直接参照します。',notes=['差戻しの状態変更はアプリ内、理由の連絡はアプリ外です。認定時の自動PDF生成は行いません。']),
'WF-07':dict(lanes=[('局担当者','事情変更・届出','app'),('給与班','認定・期間・差額','app')],pos={'a':(0,0),'b':(0,1),'c':(0,2),'d':(1,3),'e':(1,4),'f':(1,2),'g':(0,3),'h':(1,5)},summary='変更の種類で、変更通勤届・一時不支給・受給要件喪失へ分岐。旧認定を残し、新認定や終了日を管理します。'),
'WF-08':dict(lanes=[('給与班／局担当者','元の通勤タブ','app'),('同じ利用者・ブラウザー','別タブHTML・印刷／PDF','external')],pos={'a':(0,0),'b':(0,1),'c':(0,2),'d':(1,3),'e':(0,3),'f':(1,4),'g':(0,5)},summary='認定選択 → 別タブで再取得 → 印刷・PDF。権限拒否・不一致は本文を残さず選択へ戻ります。'),
'WF-09':dict(lanes=[('担当局／給与班','アプリ外：手続き・結果受領','external'),('担当局／給与班','決定結果の登録・訂正','app'),('給与班','確認・確定・利用判断','app')],pos={'a':(0,0),'b':(0,1),'c':(1,2),'d':(2,3),'e':(1,3),'f':(2,4),'g':(2,5),'h':(1,6),'i':(2,6)},summary='外部で決まった結果を担当者が登録し、入力内容を給与班が確認。入力不備は訂正へ戻し、確定後に給与への影響を分けます。'),
'WF-10':dict(lanes=[('局担当者／給与班','入力中の操作','app'),('給与アプリ・取込処理','全件検証・反映・復旧','app'),('給与班','報告後の確認・差戻し','app')],pos={'a':(0,0),'b':(0,1),'c':(0,2),'d':(1,2),'e':(1,3),'f':(1,4),'g':(1,5),'h':(0,5),'i':(0,6),'j':(2,7),'k':(2,6),'l':(2,8)},labels={'j':'報告済み内容に訂正が必要か'},summary='入力とExcel取込を分け、保存後に報告へ合流。取込途中失敗は隔離・復旧へ、給与班差戻しは入力中へ戻って再報告します。',notes=['取込中は同じ報告の編集・提出を停止します。復旧・再実行は方式未決（PD-05）であり、無条件のロールバックを保証しません。']),
'WF-11':dict(lanes=[('給与班（配置案）','期末率・勤勉率の登録','app'),('条件確認・給与計算','未決の保留／根拠保持','app')],pos={'a':(0,0),'b':(0,1),'c':(0,2),'d':(0,3),'e':(1,3),'f':(0,4)},summary='期末率と勤勉率を別々に登録。入力不備は登録へ戻し、式などが未確定なら確認で止め、確定条件だけを計算根拠へ渡します。'),
'WF-12':dict(lanes=[('給与班・給与アプリ','計算・照合・確定と記録','app'),('給与班／原因データ担当','訂正・再確認','app'),('外部処理','人給／支払い実施','external')],pos={'a':(0,0),'b':(0,1),'c':(0,2),'d':(2,3),'e':(0,4),'f':(0,5),'g':(0,6),'h':(1,6),'i':(0,7),'j':(2,8),'k':(0,9),'l':(0,10)},summary='計算 → 人給 → 給与簿取込 → 最新版照合。差分は原因側へ戻し、全体最新ゼロを確認して給与班確定、その後に外部支払いと記録を分けます。'),
'WF-13':dict(lanes=[('給与班・給与アプリ','人給連携：出力／取込・照合','app'),('給与班／原因データ担当','原因訂正と再出力準備','app'),('給与班・人給システム','アプリ外：取込・CSV出力','external')],pos={'a':(0,0),'b':(0,1),'c':(0,2),'d':(0,3),'e':(2,4),'f':(0,5),'g':(0,6),'h':(0,7),'i':(1,7),'j':(1,6),'k':(0,8)},labels={'e':'人給へ取込・給与簿CSV出力'},summary='全職員を起点に出力準備 → 人給 → 最新版照合。差分の原因を訂正し、必要な明細だけ再出力するループを、全体確定への主線から分けて示します。',notes=['出力前確認と給与班確定は別です。確定は全体最新ゼロ・未解決なしを検証するボタン操作で、確認ダイアログはありません。','I8の人給エラー取得方式、給与簿と出力明細の対応、最新結果の識別・同時更新の物理方式は未決です。']),
'WF-14':dict(lanes=[('給与班・給与アプリ','差額計算・確認・確定','app'),('給与班','追給／返納と実績管理','app')],pos={'a':(0,0),'b':(0,1),'c':(0,2),'d':(1,2),'e':(0,3),'f':(0,4),'g':(0,5),'h':(1,5),'i':(1,6),'j':(1,7),'k':(1,8)},ends={'k':'実績・根拠の記録区間終了','g':'人給出力の業務へ引継ぎ'},summary='差額内訳の確認・確定後、追給と返納へ分岐。返納は回収実施後に実績を記録し、残額があれば次の回収へ戻ります。',notes=['ルール改定は業務マスタ管理者、差額の確認・確定や返納判断は給与班です。回収実施はアプリ外。正式な回収完了条件はPD-07未決です。']),
'WF-15':dict(lanes=[('業務マスタ管理者','権限確認・有効期間改定','app'),('給与班／給与アプリ','差額への引継ぎ・履歴保持','app')],pos={'a':(0,0),'b':(0,1),'c':(1,1),'d':(0,2),'e':(0,3),'f':(1,4),'g':(0,5),'h':(0,4)},gateways={'e':'inclusive'},labels={'e':'該当する後続処理へ'},notes=['対象期間への通常適用を含みます。遡及影響・停止終了は該当する場合の経路であり、すべての改定で必須ではありません。'],summary='実効権限を確認して有効期間付き改定へ。旧版を残し、過去への影響は差額処理へ引き継ぎ、停止・終了も履歴で管理します。'),
}


def apply_display_metadata(workflows):
    """Copy reviewed presentation choices into the shared JSON model."""
    for flow in workflows:
        c=CONFIG[flow['id']]
        flow['diagram']={
            'notation':'BPMN-style-review', 'direction':'top-to-bottom',
            'lanes':[dict(id=f'lane-{i+1}',label=l[0],scope=l[1],boundary=l[2]) for i,l in enumerate(c['lanes'])],
            'layout':{k:dict(lane_id=f'lane-{v[0]+1}',row=v[1]) for k,v in c['pos'].items()},
            'summary':c['summary'], 'notes':c.get('notes',[]),
            'gateway_types':c.get('gateways',{}), 'display_labels':c.get('labels',{}),
            'end_labels':c.get('ends',{}), 'review_finish':c.get('finish',{}),
        }
        assert set(c['pos'])=={s['id'] for s in flow['steps']},flow['id']


def wrapped(text,max_units=26):
    # Deterministic wrapping by typographic width (Japanese fullwidth = 2 units).
    lines=[];line='';width=0
    for ch in str(text):
        units=1 if ord(ch)<128 else 2
        if width+units>max_units and line:lines.append(line);line='';width=0
        line+=ch;width+=units
    if line:lines.append(line)
    return lines or ['']


def box(node,pad=0):
    return (node['x']-node['w']/2-pad,node['y']-node['h']/2-pad,node['x']+node['w']/2+pad,node['y']+node['h']/2+pad)


def overlap(a,b):
    return a[0]<b[2] and b[0]<a[2] and a[1]<b[3] and b[1]<a[3]


def segment_hits(a,b,r):
    if a[0]==b[0]:return r[0]<a[0]<r[2] and max(min(a[1],b[1]),r[1])<min(max(a[1],b[1]),r[3])
    return r[1]<a[1]<r[3] and max(min(a[0],b[0]),r[0])<min(max(a[0],b[0]),r[2])


def simplify(points):
    out=[]
    for p in points:
        if out and p==out[-1]:continue
        if len(out)>1 and ((out[-2][0]==out[-1][0]==p[0]) or (out[-2][1]==out[-1][1]==p[1])):out[-1]=p
        else:out.append(p)
    return out


def port(n,side):
    return {'top':(n['x'],n['y']-n['h']/2),'bottom':(n['x'],n['y']+n['h']/2),'left':(n['x']-n['w']/2,n['y']),'right':(n['x']+n['w']/2,n['y'])}[side]


def route(start,end,nodes,width,height,used,ordinal):
    """Orthogonal A* routing on obstacle boundaries, with bend/crossing penalties."""
    dy=end['y']-start['y'];dx=end['x']-start['x']
    if abs(dy)<50:
        sides=('right','left') if dx>0 else ('left','right')
    elif dy>0:sides=('bottom','top')
    elif abs(dx)>100:sides=('right','right') if dx>0 else ('left','left')
    else:sides=('left','left')
    a=port(start,sides[0]);b=port(end,sides[1])
    vectors={'top':(0,-8),'bottom':(0,8),'left':(-8,0),'right':(8,0)}
    va,vb=vectors[sides[0]],vectors[sides[1]]
    aa=(a[0]+va[0],a[1]+va[1]);bb=(b[0]+vb[0],b[1]+vb[1])
    obstacles=[box(n,5) for n in nodes]
    xs={aa[0],bb[0],26,width-26};ys={aa[1],bb[1],80,height-28}
    for r in obstacles:
        xs.update((r[0]-12,r[2]+12));ys.update((r[1]-12,r[3]+12))
    # Fine alternatives in lane margins prevent multiple retry lines becoming one bus.
    for x in range(46,int(width),40):xs.add(x)
    for y in range(100,int(height),40):ys.add(y)
    xs=sorted(x for x in xs if 18<=x<=width-18);ys=sorted(y for y in ys if 80<=y<=height-18)
    xi={x:i for i,x in enumerate(xs)};yi={y:i for i,y in enumerate(ys)}
    begin=(xi[aa[0]],yi[aa[1]],0);goal=(xi[bb[0]],yi[bb[1]])
    queue=[(abs(aa[0]-bb[0])+abs(aa[1]-bb[1]),0,begin)];cost={begin:0};prev={}
    valid_cache={};edge_cache={}
    def valid(ix,iy):
        key=(ix,iy)
        if key not in valid_cache:valid_cache[key]=not any(r[0]<xs[ix]<r[2] and r[1]<ys[iy]<r[3] for r in obstacles)
        return valid_cache[key]
    result=None
    while queue:
        _,g,state=heapq.heappop(queue)
        if g!=cost.get(state):continue
        ix,iy,axis=state
        if (ix,iy)==goal:result=state;break
        p=(xs[ix],ys[iy])
        for jx,jy,na in ((ix-1,iy,1),(ix+1,iy,1),(ix,iy-1,2),(ix,iy+1,2)):
            if not(0<=jx<len(xs) and 0<=jy<len(ys)) or not valid(jx,jy):continue
            q=(xs[jx],ys[jy]);key=tuple(sorted((p,q)))
            if key not in edge_cache:
                blocked=any(segment_hits(p,q,r) for r in obstacles)
                penalty=0
                if not blocked:
                    for u,v in used:
                        if p[0]==q[0]==u[0]==v[0] and max(min(p[1],q[1]),min(u[1],v[1]))<min(max(p[1],q[1]),max(u[1],v[1])):penalty+=80
                        elif p[1]==q[1]==u[1]==v[1] and max(min(p[0],q[0]),min(u[0],v[0]))<min(max(p[0],q[0]),max(u[0],v[0])):penalty+=80
                        elif p[0]==q[0] and u[1]==v[1] and min(p[1],q[1])<u[1]<max(p[1],q[1]) and min(u[0],v[0])<p[0]<max(u[0],v[0]):penalty+=45
                        elif p[1]==q[1] and u[0]==v[0] and min(p[0],q[0])<u[0]<max(p[0],q[0]) and min(u[1],v[1])<p[1]<max(u[1],v[1]):penalty+=45
                edge_cache[key]=(blocked,penalty)
            blocked,penalty=edge_cache[key]
            if blocked:continue
            ng=g+abs(p[0]-q[0])+abs(p[1]-q[1])+(32 if axis and na!=axis else 0)+penalty
            ns=(jx,jy,na)
            if ng<cost.get(ns,math.inf):
                cost[ns]=ng;prev[ns]=state
                heapq.heappush(queue,(ng+abs(q[0]-bb[0])+abs(q[1]-bb[1]),ng,ns))
    if result is None:raise ValueError(f'No obstacle-free route {start["id"]} -> {end["id"]}')
    seq=[]
    while result!=begin:
        seq.append((xs[result[0]],ys[result[1]]));result=prev[result]
    seq.append(aa);seq.reverse()
    points=simplify([a]+seq+[b]);used.extend(zip(points,points[1:]));return points


def layout(flow):
    d=flow['diagram'];lane_width=360;width=lane_width*len(d['lanes'])+80
    maxrow=max(v['row'] for v in d['layout'].values());height=210+maxrow*200+180
    nodes=[];nmap={};incoming={s['id']:[] for s in flow['steps']};outgoing={s['id']:[] for s in flow['steps']}
    for i,e in enumerate(flow['edges']):incoming[e['to']].append(i);outgoing[e['from']].append(i)
    def add(id,kind,x,y,w,h,**kw):
        n=dict(id=id,kind=kind,x=x,y=y,w=w,h=h,**kw);nodes.append(n);nmap[id]=n;return n
    for s in flow['steps']:
        p=d['layout'][s['id']];li=int(p['lane_id'].split('-')[-1])-1
        kind='gateway' if s['kind']=='decision' else 'task'
        add(s['id'],kind,40+lane_width*(li+.5),210+p['row']*200,244 if kind=='task' else 250,96 if kind=='task' else 136,step=s,label=d['display_labels'].get(s['id'],s['label']),lane_id=p['lane_id'],gateway_type=d['gateway_types'].get(s['id'],'exclusive'))
    # Readable routing nodes are part of this view, never extra business operations.
    local=[];starts=[];ends=[]
    for s in flow['steps']:
        sid=s['id'];n=nmap[sid]
        if len(incoming[sid])>1:
            add('join-'+sid,'merge',n['x'],n['y']-(90 if n['kind']=='gateway' else 66),20,20,label='合流',lane_id=n['lane_id'])
            local.append(('join-'+sid,sid,''))
        if len(outgoing[sid])>1 and n['kind']!='gateway':
            add('split-'+sid,'split',n['x'],n['y']+66,20,20,label='結果分岐',lane_id=n['lane_id'],gateway_type=d['gateway_types'].get(sid,'exclusive'))
            local.append((sid,'split-'+sid,''))
        if s['kind']=='start':
            event=add('start-'+sid,'start',n['x'],n['y']-110,32,32,label='開始',lane_id=n['lane_id'])
            target='join-'+sid if 'join-'+sid in nmap else sid
            local.append((event['id'],target,''));starts.append(event['id'])
        if not outgoing[sid]:
            event=add('end-'+sid,'end',n['x'],n['y']+96,34,34,label=d['end_labels'].get(sid,'確認区間の終了'),lane_id=n['lane_id'])
            local.append((sid,event['id'],''));ends.append(event['id'])
    # WF-01 is intentionally cyclic; a dotted view boundary is not a new business exit.
    for sid,label in d['review_finish'].items():
        n=nmap[sid]
        event=add('end-'+sid,'end',width-75,145,34,34,label=label,lane_id=n['lane_id'],review_only=True)
        local.append((sid,event['id'],'確認区間'));ends.append(event['id'])
    annotations=[]
    for n in nodes:
        if n['kind'] not in ('start','end'):continue
        lines=wrapped(n['label'],24)
        tw=max(sum(6 if ord(c)<128 else 12 for c in line) for line in lines)+8
        th=18*len(lines)+4
        if n['kind']=='start':
            tx=n['x']+27+tw/2;ty=n['y']+1
        else:
            tx=n['x'];ty=n['y']+30+9*(len(lines)-1)
        annotations.append(dict(id='label-'+n['id'],kind='annotation',x=tx,y=ty,w=tw,h=th))
    routing_nodes=nodes+annotations
    edges=[];used=[]
    # Local stems are short; include them as obstacles for the routing cost.
    for i,(a,b,label) in enumerate(local):
        if nmap[b].get('review_only'):continue
        p=simplify([port(nmap[a],'bottom'),port(nmap[b],'top')]);used.extend(zip(p,p[1:]))
        edges.append(dict(id=f'{flow["id"]}-view-{i+1:02}',from_node=a,to_node=b,points=p,label=label,view_only=True,kind='view'))
    # Route forward spine first, then cross-lane branches, then return paths.
    ordered=sorted(enumerate(flow['edges']),key=lambda ie:(nmap[ie[1]['to']]['y']<=nmap[ie[1]['from']]['y'],abs(nmap[ie[1]['to']]['x']-nmap[ie[1]['from']]['x']),ie[0]))
    for idx,e in ordered:
        a='split-'+e['from'] if 'split-'+e['from'] in nmap else e['from']
        b='join-'+e['to'] if 'join-'+e['to'] in nmap else e['to']
        is_return=nmap[e['to']]['y']<=nmap[e['from']]['y']
        external=any(d['lanes'][int(nmap[z]['lane_id'].split('-')[-1])-1]['boundary']=='external' for z in (a,b))
        points=route(nmap[a],nmap[b],routing_nodes,width,height,used,idx)
        edges.append(dict(id=f'{flow["id"]}-edge-{idx+1:02}',from_node=a,to_node=b,source=e['from'],target=e['to'],points=points,label=e['label'],original_index=idx,kind='external' if external else 'return' if is_return else 'normal'))
    for i,(a,b,label) in enumerate(local):
        if not nmap[b].get('review_only'):continue
        points=route(nmap[a],nmap[b],routing_nodes,width,height,used,i)
        edges.append(dict(id=f'{flow["id"]}-view-{i+1:02}',from_node=a,to_node=b,points=points,label=label,view_only=True,kind='view-boundary'))
    # Prefer a label immediately next to its own connector. Narrow wrapping is
    # tried before any displacement, so crowded retry paths remain identifiable.
    label_boxes=[];node_boxes=[box(n,2) for n in routing_nodes]
    for edge in sorted(edges,key=lambda e:e.get('original_index',-1)):
        if not edge['label']:continue
        def candidates_for(lines):
            lw=max(sum(7.2 if ord(ch)<128 else 14.4 for ch in line) for line in lines)+14
            lh=len(lines)*19+10;candidates=[]
            for a,b in zip(edge['points'],edge['points'][1:]):
                if abs(a[0]-b[0])+abs(a[1]-b[1])<25:continue
                for fraction in (.5,.4,.6,.25,.75,.1,.9,.3,.7):
                    x=a[0]+(b[0]-a[0])*fraction;y=a[1]+(b[1]-a[1])*fraction
                    if a[0]==b[0]:candidates.extend([(x+7,y-lh/2),(x-lw-7,y-lh/2)])
                    else:candidates.extend([(x-lw/2,y-lh-7),(x-lw/2,y+7)])
            return lw,lh,candidates
        def available(r):
            if r[0]<20 or r[1]<84 or r[2]>width-20 or r[3]>height-20:return False
            if any(overlap(r,b) for b in node_boxes+label_boxes):return False
            return not any(segment_hits(a,b,r) for e in edges for a,b in zip(e['points'],e['points'][1:]))
        chosen=None
        for units in (20,12,8):
            lines=wrapped(edge['label'],units);lw,lh,candidates=candidates_for(lines)
            for x,y in candidates:
                r=(x,y,x+lw,y+lh)
                if available(r):chosen=r;break
            if chosen:break
        if chosen is None:
            # A bounded offset remains only for cramped local branch stems.
            for radius in range(10,61,10):
                for x,y in candidates:
                    for ox,oy in ((0,-radius),(0,radius),(-radius,0),(radius,0)):
                        r=(x+ox,y+oy,x+ox+lw,y+oy+lh)
                        if available(r):chosen=r;break
                    if chosen:break
                if chosen:break
        if chosen is None:raise ValueError(f'No nearby label placement {flow["id"]} {edge["id"]}')
        edge['label_box']=chosen;edge['label_lines']=lines;label_boxes.append(chosen)
    return dict(width=width,height=height,nodes=nodes,edges=edges,starts=starts,ends=ends,annotations=annotations)


def render(flow,current,operation_link):
    g=layout(flow);d=flow['diagram'];fid=flow['id'];width=g['width'];height=g['height']
    parts=[f'<svg class="workflow-diagram" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="{fid}-title {fid}-description" data-workflow-id="{fid}">',f'<title id="{fid}-title">{E(fid+" "+flow["name"])}</title>',f'<desc id="{fid}-description">{E(d["summary"])} 工程は一度だけ配置。矢印をたどり、茶色の折返しは訂正・再試行。全条件は同じデータの経路表で確認できます。</desc>',f'<defs><marker id="{fid}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke"/></marker></defs>']
    for i,lane in enumerate(d['lanes']):
        x=40+i*360
        parts.append(f'<g class="flow-lane {E(lane["boundary"])}" data-lane-id="{lane["id"]}"><rect x="{x}" y="0" width="360" height="{height}"/><rect class="lane-heading-bg" x="{x}" y="0" width="360" height="65"/><text x="{x+180}" y="25" class="flow-lane-title" text-anchor="middle">{E(lane["label"])}</text><text x="{x+180}" y="49" class="flow-lane-scope" text-anchor="middle">{E(lane["scope"])}</text></g>')
    # White under-stroke distinguishes genuine junctions from incidental crossings.
    for e in g['edges']:
        path='M '+' L '.join(f'{x:g} {y:g}' for x,y in e['points'])
        attrs=f'data-edge-id="{e["id"]}" data-from="{e["from_node"]}" data-to="{e["to_node"]}"'
        if not e.get('view_only'):attrs+=f' data-source-step="{e["source"]}" data-target-step="{e["target"]}"'
        parts.append(f'<g class="flow-connector {e["kind"]}" {attrs}><path class="flow-edge-halo" d="{path}"/><path class="flow-edge" d="{path}" marker-end="url(#{fid}-arrow)"/><title>{E(e["label"] or "表示用接続")}</title></g>')
    for e in g['edges']:
        if 'label_box' not in e:continue
        x,y,x2,y2=e['label_box']
        parts.append(f'<g class="flow-edge-label {e["kind"]}" data-label-for="{e["id"]}"><rect x="{x:g}" y="{y:g}" width="{x2-x:g}" height="{y2-y:g}" rx="4"/>')
        for j,line in enumerate(e['label_lines']):parts.append(f'<text x="{x+7:g}" y="{y+19+j*19:g}">{E(line)}</text>')
        parts.append('</g>')
    for n in g['nodes']:
        x=n['x'];y=n['y'];kind=n['kind'];b=box(n)
        step=n.get('step');label=n['label'];op=step.get('operation_id') if step else None
        parts.append(f'<g class="flow-node {kind}" data-node-id="{n["id"]}" data-node-kind="{kind}" data-lane-id="{n["lane_id"]}" data-box="{",".join(str(v) for v in b)}"'+(f' data-step-id="{step["id"]}"' if step else '')+'>')
        if step:parts.append(f'<a href="#{E(step["id"])}" aria-label="{E(step["id"]+" "+label+"：工程定義へ")}">')
        parts.append('<title>'+E(label+(('。'+step['detail']) if step else '。表示用要素'))+'</title>')
        if kind in ('start','end'):
            parts.append(f'<circle cx="{x}" cy="{y}" r="{n["w"]/2}"/>')
            if kind=='end':parts.append(f'<circle class="end-inner" cx="{x}" cy="{y}" r="{n["w"]/2-5}"/>')
            # Below-event text is part of the event bounds audit separately.
            for j,line in enumerate(wrapped(label,24)):
                tx=x+27 if kind=='start' else x
                ty=y+5+j*18 if kind=='start' else y+36+j*18
                anchor='start' if kind=='start' else 'middle'
                parts.append(f'<text class="flow-event-label" x="{tx}" y="{ty}" text-anchor="{anchor}">{E(line)}</text>')
        elif kind in ('gateway','split','merge'):
            points=f'{x},{b[1]} {b[2]},{y} {x},{b[3]} {b[0]},{y}'
            parts.append(f'<polygon points="{points}"/>')
            symbol={'exclusive':'×','parallel':'+','inclusive':'○'}.get(n.get('gateway_type'),'')
            if kind=='gateway':
                parts.append(f'<text class="flow-node-id" x="{x}" y="{y-40}" text-anchor="middle">{E(step["id"])} · {symbol}</text>')
                lines=wrapped(label,18)
                for j,line in enumerate(lines):parts.append(f'<text class="flow-task-label" x="{x}" y="{y-8+j*22}" text-anchor="middle">{E(line)}</text>')
            else:parts.append(f'<text class="flow-gateway-symbol" x="{x}" y="{y+3}" text-anchor="middle">{symbol}</text>')
        else:
            parts.append(f'<rect x="{b[0]}" y="{b[1]}" width="{n["w"]}" height="{n["h"]}" rx="13"/>')
            parts.append(f'<text class="flow-node-id" x="{b[0]+14}" y="{b[1]+20}">{E(step["id"])} · {E(step.get("screen_id") or "アプリ外／業務境界")}</text>')
            for j,line in enumerate(wrapped(label,28)):parts.append(f'<text class="flow-task-label" x="{b[0]+14}" y="{b[1]+45+j*22}">{E(line)}</text>')
        if step:parts.append('</a>')
        # Direct operation links are static SVG anchors as well as table references.
        if op and kind=='task':
            parts.append(f'<a href="{E(operation_link(op))}" aria-label="{E(op)} 操作定義"><text class="flow-op-link" x="{b[2]-12}" y="{b[3]-9}" text-anchor="end">操作定義 ↗</text></a>')
        parts.append('</g>')
    parts.append('</svg>')
    toolbar=f'<div class="diagram-tools" data-diagram-tools hidden><button type="button" data-diagram-fit>幅に合わせる</button><button type="button" data-diagram-all>全体を見る</button><button type="button" data-diagram-actual>100%</button><button type="button" data-diagram-out aria-label="業務図を縮小">−</button><button type="button" data-diagram-in aria-label="業務図を拡大">＋</button><output data-diagram-scale aria-live="polite">100%</output><span>図内だけを横・縦スクロールできます</span></div>'
    return '<section class="connected-workflow" data-connected-workflow>'+toolbar+f'<div class="workflow-scroll" tabindex="0" role="region" aria-label="{E(flow["name"])}。上下に流れを追い、枠内をスクロール">'+''.join(parts)+'</div></section>'


def navigation_kind(operation):
    special={
        'OP-F-HTML':('new-tab','別タブを開く','認定簿表示ボタンでHTMLを別タブに起動'),
        'OP-F-RETURN-HTML':('tab-return','利用者のタブ切替','ブラウザーで元のアプリタブを選ぶ'),
        'OP-JLINK-EXPORT':('file-handoff','利用者のシステム切替＋ファイル受渡し','Excelを保存 → 利用者が人給を開いて取込'),
        'OP-JINKYU-PROCESS':('file-handoff','利用者のシステム切替＋ファイル受渡し','人給でCSV出力 → アプリへ戻ってCSV取込'),
        'OP-AD-CANDIDATE':('information','情報受渡し（方式未決）','前工程の通知・候補自動作成目標。画面遷移なし'),
        'OP-RETRO-EXPORT':('information','データ受渡し／画面配置は提案','追給明細を出力処理へ渡す。具体的な遷移は配置案'),
    }
    return special.get(operation['id'],('internal','アプリ内の画面移動',operation['title']))


def render_navigation_fanout(model,operation_link,screen_link):
    screens={s['id']:s for s in model['screens']};groups={}
    for o in model['operations']:
        if o['screen_id']!=o['destination_screen_id']:
            groups.setdefault(o['screen_id'],{}).setdefault(o['destination_screen_id'],[]).append(o)
    out=[]
    for source,destinations in groups.items():
        sid='NAV-'+source
        row_heights=[max(134,64+len(ops)*80) for ops in destinations.values()]
        height=sum(row_heights)+60;source_y=height/2
        parts=[f'<svg class="navigation-fanout" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 {height}" role="img" aria-label="{E(source)}を起点にした1対多の経路" data-navigation-source="{E(source)}"><title>{E(source)} {E(screens[source]["name"])}からの行先</title>',f'<defs><marker id="{sid}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke"/></marker></defs>']
        parts.append(f'<path class="nav-trunk" d="M 280 {source_y:g} H 340 M 340 {30+row_heights[0]/2:g} V {height-30-row_heights[-1]/2:g}"/>')
        parts.append(f'<a href="{E(screen_link(source))}" class="nav-source" data-source-screen="{E(source)}"><rect x="20" y="{source_y-62:g}" width="260" height="124" rx="12"/><text x="38" y="{source_y-36:g}" class="flow-node-id">起点 · {E(source)}</text>')
        for j,line in enumerate(wrapped(screens[source]['name'],28)):parts.append(f'<text x="38" y="{source_y-8+j*24:g}" class="flow-task-label">{E(line)}</text>')
        parts.append(f'<text x="38" y="{source_y+47:g}" class="flow-node-id">{E(screens[source]["status"])}</text></a>')
        top=30
        for (dest,ops),rh in zip(destinations.items(),row_heights):
            cy=top+rh/2;kinds=[navigation_kind(o)[0] for o in ops]
            branch_kind=kinds[0] if len(set(kinds))==1 else 'mixed'
            color='#246797' if branch_kind=='internal' else '#97731f' if branch_kind in ('new-tab','tab-return','file-handoff') else '#765998'
            dash='' if branch_kind=='internal' else ' stroke-dasharray="8 5"'
            parts.append(f'<g class="nav-destination" data-destination-screen="{E(dest)}" data-route-kind="{branch_kind}"><path d="M 340 {cy:g} H 830" fill="none" stroke="{color}" stroke-width="2.2"{dash} marker-end="url(#{sid}-arrow)"/>')
            # Each destination appears once; multiple operations remain distinct links.
            boxheight=max(104,rh-26)
            parts.append(f'<a href="{E(screen_link(dest))}"><rect x="842" y="{cy-boxheight/2:g}" width="330" height="{boxheight:g}" rx="10" class="nav-target {"external" if dest.startswith("EXT-") else ""}"/><text x="860" y="{cy-boxheight/2+24:g}" class="flow-node-id">{E(dest)}{ " · アプリ外" if dest.startswith("EXT-") else ""}</text>')
            for j,line in enumerate(wrapped(screens[dest]['name'],32)):parts.append(f'<text x="860" y="{cy-boxheight/2+51+j*23:g}" class="flow-task-label">{E(line)}</text>')
            parts.append(f'<text x="860" y="{cy+boxheight/2-13:g}" class="flow-node-id">{E(screens[dest]["status"])}</text></a>')
            for k,o in enumerate(ops):
                kind,title,detail=navigation_kind(o);ly=top+12+k*80
                lines=wrapped(detail,52)
                parts.append(f'<a href="{E(operation_link(o["id"]))}" data-operation-id="{E(o["id"])}" data-navigation-kind="{kind}"><rect class="nav-route-label" x="371" y="{ly:g}" width="430" height="72" rx="6"/><text x="385" y="{ly+19:g}" class="nav-route-kind">{E(title)} · {E(o["status"])}</text>')
                for j,line in enumerate(lines[:2]):parts.append(f'<text x="385" y="{ly+40+j*19:g}" class="nav-route-text">{E(line)}</text>')
                parts.append('</a>')
            parts.append('</g>');top+=rh
        parts.append('</svg>')
        out.append(f'<section class="nav-fanout-section" id="fanout-{E(source)}"><h3>{E(source)} {E(screens[source]["name"])}から</h3><div class="diagram-scroll" tabindex="0" role="region" aria-label="{E(source)}の行先。枠内を横スクロール">'+''.join(parts)+'</div></section>')
    return ''.join(out)
