/* PAY-HTML-001 review enhancement. No network, real file access or business writes. */
'use strict';
(() => {
  document.documentElement.classList.add('js-enabled');
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const filters = $$('[data-filter]');
  function filterOperations() {
    let count = 0;
    $$('[data-operation-row]').forEach(row => {
      const show = filters.every(control => {
        const value = control.value.trim().toLowerCase();
        if (!value) return true;
        const key = control.dataset.filter;
        return (key === 'text' ? row.textContent : row.dataset[key]).toLowerCase().includes(value);
      });
      row.hidden = !show;
      if (show) count++;
    });
    const status = $('[data-result-count]');
    if (status) status.textContent = `${count}件を表示`;
  }
  filters.forEach(control => control.addEventListener('input', filterOperations));
  $('[data-reset-filters]')?.addEventListener('click', () => {
    filters.forEach(control => { control.value = ''; }); filterOperations();
  });
  const app = $('[data-mock-screen]');
  if (!app) return;
  const screen = app.dataset.mockScreen;
  const key = 'pay-html-001-fictional-review-v1';
  const defaults = () => ({staff:'009900009901', name:'架空 花子', month:'2026/09', run:'DEMO-RUN-01',
    returnTo:'', role:'payroll', tabs:{}, pay:{version:1, comparedVersion:0, differences:1, unknown:0, imported:false, finalized:false,
    paid:false, exported:false, exportedVersion:0, am:['A','A','A'], selected:[true,true,true]}});
  let context = defaults();
  try { const saved = JSON.parse(sessionStorage.getItem(key)); if (saved?.pay) context = saved; } catch (_) { /* file:// storage can be restricted */ }
  const params = new URLSearchParams(location.search);
  ['staff','name','month','run','returnTo','role'].forEach(name => { if (params.has(name)) context[name] = params.get(name); });
  let dirty = false, editing = false, busy = false, localState = 'normal', dialogAction = null;
  let lastFocus = null;
  const roleControl = $('[data-review-role]');
  const dialog = $('[data-mock-dialog]');
  if (roleControl) roleControl.value = context.role || 'payroll';
  const role = () => roleControl?.value || 'payroll';
  const originalFields = new Map($$('[data-editable]', app).map(input => [input, input.value]));
  let baseline = new Map(originalFields);
  const restoreInputs = () => baseline.forEach((value, input) => { input.value = value; });
  const persist = () => { try {sessionStorage.setItem(key, JSON.stringify(context));} catch (_) {} };
  const status = (message, error = false) => {
    $$('[data-mock-status]', app).forEach(node => {
      node.textContent = message; node.classList.toggle('mock-error', error);
    });
  };
  function drawContext() {
    $$('[data-context-staff]').forEach(x => { x.textContent = `${context.staff} ${context.name}`; });
    $$('[data-context-month]').forEach(x => { x.textContent = context.month; });
    $$('[data-context-run]').forEach(x => { x.textContent = context.run === 'DEMO-RUN-02' ? '例示2026年10月追給' : '例示2026年10月通常'; });
    $$('[data-mode-label]').forEach(x => { x.textContent = busy ? '処理中' : editing ? '編集中' : '読み取り'; });
    $$('[data-staff]').forEach(row => row.setAttribute('aria-pressed', String(row.dataset.staff === context.staff)));
    if ($('[data-run]')) $('[data-run]').value = context.run;
  }
  function applyStaffFixture() {
    const hasFixture=context.staff==='009900009901';
    if(screen==='SCR-002') {
      originalFields.forEach((value,input)=>{input.value=hasFixture?value:'';});
      const number=$('#field-scr-002-0-0'),name=$('#field-scr-002-0-1'),bureau=$('#field-scr-002-0-3');
      if(number)number.value=context.staff;if(name)name.value=context.name;
      if(bureau)bureau.value=context.staff==='009900009903'?'架空他局':'架空総務局';
      $$('.mock-panel',app).forEach((panel,index)=>{
        if(index===0)return;
        const grid=$('.field-grid',panel),ledger=$('[data-ledger-table]',panel),history=$('[data-history]',panel);
        if(grid)grid.hidden=!hasFixture;if(ledger)ledger.hidden=!hasFixture;
        if(history)history.value=hasFixture?'現行 2026/04/01〜2027/03/31':'登録なし';
        let empty=$('[data-empty-fixture]',panel);
        if(!empty){empty=document.createElement('p');empty.dataset.emptyFixture='';empty.textContent='選択職員の登録履歴はありません。';panel.append(empty);}
        empty.hidden=hasFixture;
      });
      const detail=$('[data-staff-detail]');if(detail)detail.hidden=!context.staff;
    }
    if(screen==='SCR-005'&&!hasFixture){
      const summary=$('.mock-summary'),detail=$('.pay-breakdown');
      if(summary)summary.innerHTML='<span>給与支給総額<br>—</span><span>控除額計<br>—</span><span>現金支給額<br>—</span>';
      if(detail)detail.hidden=true;status('選択職員の勤務・計算根拠が未登録です。旧職員の金額・算定説明は表示しません。',true);
    }
    baseline=new Map($$('[data-editable]',app).map(input=>[input,input.value]));
  }
  const retroConfirmed=()=>context.retro?.confirmed&&context.retro.staff===context.staff&&context.retro.run===context.run;
  function canFinalize() {
    const p = context.pay;
    return role() === 'payroll' && !busy && p.imported && p.comparedVersion === p.version &&
      p.differences === 0 && p.unknown === 0 && !p.finalized && !p.paid;
  }
  function lockControls() {
    const writeAllowed = !(screen==='SCR-003'&&context.attendanceIncomplete) && !busy && !['initial','zero','readonly','paid'].includes(localState) && role() !== 'self';
    $$('select, input:not([data-editable])',app).forEach(input=>{input.disabled=busy;});
    $$('[data-editable]', app).forEach(input => {
      input.readOnly = !(editing && writeAllowed && input.dataset.editable === 'true');
    });
    $$('[data-write-control]', app).forEach(control => { control.disabled = !(editing && writeAllowed); });
    $$('[data-payroll-only]', app).forEach(control => { control.disabled = role() !== 'payroll' || busy; });
    $$('[data-master-only]', app).forEach(control => { control.disabled = role() !== 'master' || busy; });
    $$('[data-entry-roles]',app).forEach(control=>{const allowed=control.dataset.entryRoles.split(' ').includes(role());control.classList.toggle('disabled',!allowed);control.setAttribute('aria-disabled',String(!allowed));control.tabIndex=allowed?0:-1;control.title=allowed?'':'給与班のみ利用できます';});
    const emptyView=['initial','zero','error'].includes(localState);
    if(screen!=='SCR-002')$$('.field-grid, table, .mock-context, .mock-summary, .pay-breakdown',app).forEach(node=>{node.hidden=emptyView;});
    const restricted=['FUT-JLINK','FUT-IMPORT','SCR-007','SCR-004'].includes(screen)&&role()!=='payroll';
    const body=$('[data-business-content]'),warning=$('[data-role-warning]');if(body)body.hidden=restricted;if(warning)warning.hidden=!restricted;
    $$('[data-master-entry]', app).forEach(control => {
      const allowed = ['master','system'].includes(role());
      control.classList.toggle('disabled', !allowed); control.setAttribute('aria-disabled', String(!allowed));
      control.tabIndex = allowed ? 0 : -1;
    });
    $$('[data-action]', app).forEach(control => {
      if (busy) control.disabled = true;
      else if (!control.hasAttribute('data-write-control') && !control.hasAttribute('data-payroll-only') && !control.hasAttribute('data-master-only')) control.disabled = false;
      if (['initial','zero','error','readonly','paid'].includes(localState) && ['edit','save','attendance-import','report','add-row','remove-row'].includes(control.dataset.action)) control.disabled = true;
      if (role() === 'self' && !['sidebar','font','search','clear','ledger-range','print-guide'].includes(control.dataset.action)) control.disabled = true;
      if(screen==='SCR-003'&&context.attendanceIncomplete&&['edit','save','report','add-row','remove-row'].includes(control.dataset.action))control.disabled=true;
      if (screen === 'SCR-006' && ['edit','save','master-new','master-stop'].includes(control.dataset.action)) control.disabled = role() !== 'master' || busy;
    });
    $$('[data-retro-output]').forEach(anchor=>{const allowed=!!retroConfirmed()&&role()==='payroll';anchor.setAttribute('aria-disabled',String(!allowed));anchor.classList.toggle('disabled',!allowed);anchor.tabIndex=allowed?0:-1;});
    $$('[data-action="recovery"],[data-action="repay-method"]').forEach(control=>{control.disabled=!retroConfirmed()||role()!=='payroll'||busy;});
    const finalize = $('[data-action="finalize"]'); if (finalize) finalize.disabled = !canFinalize();
    const reexport=$('[data-action="reexport"]');if(reexport)reexport.disabled=busy||role()!=='payroll'||context.pay.differences<=0||context.pay.unknown>0;
    const paid = $('[data-action="mark-paid"]'); if (paid) paid.disabled = role() !== 'payroll' || !context.pay.finalized || context.pay.paid || busy;
    const term=$('[data-staff-search]')?.value.trim()||'';let visibleStaff=0;$$('[data-bureau]',app).forEach(row=>{row.hidden=(role()==='bureau'&&row.dataset.bureau!=='own')||(!!term&&!row.textContent.includes(term));if(!row.hidden)visibleStaff++;});const count=$('[data-search-count]');if(count)count.textContent=visibleStaff+'件';
    $$('[data-allowed-roles]',app).forEach(control=>{if(control.dataset.allowedRoles&&!control.dataset.allowedRoles.split(' ').includes(role()))control.disabled=true;});
    $$('[data-new-tab]').forEach(anchor=>{const allowed=context.staff==='009900009901'&&!['initial','zero','error'].includes(localState);anchor.setAttribute('aria-disabled',String(!allowed));anchor.tabIndex=allowed?0:-1;});
    $$('[data-return-jlink]').forEach(x=>{x.hidden=!context.returnTo;});
    if(screen==='SCR-005'&&(context.staff!=='009900009901'||context.month!=='2026/09')){const detail=$('.pay-breakdown');if(detail)detail.hidden=true;}
    if (screen==='FUT-JLINK') {const restricted=role()!=='payroll';$$('[data-action]',app).forEach(control=>{if(restricted)control.disabled=true;});$$('[data-tab]',app).forEach(control=>{control.disabled=restricted;});$$('.mock-panel',app).forEach(panel=>{panel.hidden=restricted||emptyView||panel.id!==context.tabs?.[screen];});}
    drawContext();
  }
  function updatePay() {
    const p = context.pay;
    const stale = p.exported && p.exportedVersion !== p.version;
    const notice = $('[data-stale-message]'); if (notice) notice.hidden = !stale;
    const summary = $('[data-reconcile-summary]');
    if (summary) summary.textContent = `全体差分：${p.differences}件。未知職員：${p.unknown}件。${p.comparedVersion !== p.version ? '最新結果との照合が必要です。' : '最新版との照合済み。'}`;
    const payStatus = $('[data-pay-status]');
    if (payStatus) payStatus.textContent = p.paid ? '支払い済み' : p.finalized ? '給与班確定' : p.comparedVersion === p.version && !p.differences && !p.unknown ? '差分ゼロ確認' : '照合中';
    const rows = $$('[data-diff-table] tbody tr');
    if(rows[0]){rows[0].cells[4].textContent=p.differences?'193,000':'193,750';rows[0].cells[5].textContent=p.differences?'750':'0';}
    const unresolved=$('[data-unresolved-row]');if(unresolved)unresolved.hidden=p.unknown===0;
    rows.forEach((row,i) => { row.hidden = !$('[data-all-diffs]')?.checked && (i > 0 || !p.differences); });
    lockControls(); persist();
  }
  function history(text) {
    const list = $('[data-mock-history]'); if (!list) return;
    const li = document.createElement('li'); li.textContent = text; list.append(li);
  }
  function modal(title, text, action, confirmText = '続行') {
    lastFocus = document.activeElement; dialogAction = action;
    $('[data-dialog-title]').textContent = title;
    $('[data-dialog-body]').textContent = text;
    $('[data-dialog-confirm]').textContent = confirmText;
    dialog.showModal(); $('[data-dialog-cancel]').focus();
  }
  function closeModal() { dialog.close(); dialogAction = null; lastFocus?.focus(); }
  $('[data-dialog-cancel]')?.addEventListener('click', () => { closeModal(); status('キャンセルしました。対象と入力内容を保持しています。'); });
  $('[data-dialog-confirm]')?.addEventListener('click', () => {
    const action = dialogAction; closeModal(); action?.();
  });
  dialog?.addEventListener('cancel', () => { dialogAction = null; status('キャンセルしました。対象と入力内容を保持しています。'); });
  function guard(action) {
    if (dirty) modal('変更を破棄して移動しますか', '続行すると未保存の入力を破棄します。キャンセルすると現在の職員と入力内容を保持します。', () => { dirty = false; editing = false; restoreInputs(); action(); }, '破棄して続行');
    else action();
  }
  function go(anchor) {
    if (anchor.getAttribute('aria-disabled') === 'true') return;
    const url = new URL(anchor.href, location.href);
    if (screen === 'FUT-JLINK' && ['scr-002.html','scr-003.html'].some(x => url.pathname.endsWith(x))) context.returnTo = 'fut-jlink.html';
    if (url.pathname.endsWith('fut-jlink.html')) context.returnTo = '';
    ['staff','name','month','run','returnTo','role'].forEach(k => url.searchParams.set(k, context[k]));
    if (anchor.dataset.targetTab) url.searchParams.set('tab',anchor.dataset.targetTab);
    persist();
    if (anchor.target === '_blank') window.open(url.href, '_blank', 'noopener');
    else location.href = url.href;
  }
  $$('[data-mock-nav]').forEach(anchor => anchor.addEventListener('click', event => {
    event.preventDefault(); guard(() => go(anchor));
  }));
  if (false && context.returnTo && ['SCR-002','SCR-003'].includes(screen)) {
    const back = document.createElement('a'); back.href = context.returnTo; back.textContent = '人給連携へ戻る'; back.className = 'button';
    back.addEventListener('click', event => {event.preventDefault(); guard(() => go(back));});
    $('.mock-body').prepend(back);
  }
  function selectTab(id) {
    context.tabs=context.tabs||{};context.tabs[screen]=id;persist();
    $$('[data-tab]', app).forEach(button => {
      const selected = button.dataset.tab === id; button.setAttribute('aria-selected', String(selected));
      button.tabIndex = selected ? 0 : -1;
    });
    $$('.mock-panel', app).forEach(panel => { panel.hidden = panel.id !== id; });
  }
  const tabButtons = $$('[data-tab]', app);
  if (tabButtons.length) {const requested=params.get('tab');const target=tabButtons.find(x=>x.textContent===requested)||tabButtons.find(x=>x.dataset.tab===context.tabs?.[screen])||tabButtons[0];selectTab(target.dataset.tab);}
  tabButtons.forEach(button => {
    button.addEventListener('click', () => selectTab(button.dataset.tab));
    button.addEventListener('keydown', event => {
      if (!['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) return;
      event.preventDefault(); let index = tabButtons.indexOf(button);
      if (event.key === 'Home') index = 0;
      else if (event.key === 'End') index = tabButtons.length-1;
      else index = (index + (event.key === 'ArrowRight' ? 1 : -1) + tabButtons.length) % tabButtons.length;
      selectTab(tabButtons[index].dataset.tab); tabButtons[index].focus();
    });
  });
  app.addEventListener('input', event => {
    if (event.target.matches('[data-editable="true"]') && editing) dirty = true;
  });
  async function simulate(message, action) {
    if (busy) return;
    busy = true; lockControls(); status(message);
    await new Promise(resolve => setTimeout(resolve, 650));
    busy = false; action(); lockControls();
  }
  function captureOutput() {
    $$('[data-row-am]').forEach(control => {context.pay.am[Number(control.dataset.rowAm)] = control.value;});
    $$('[data-output-row]').forEach(control => {context.pay.selected[Number(control.dataset.outputRow)] = control.checked;});
    persist();
  }
  $$('[data-row-am]').forEach(control => { control.value = context.pay.am[Number(control.dataset.rowAm)] || 'A'; control.addEventListener('change',captureOutput); });
  $$('[data-output-row]').forEach(control => { control.checked = context.pay.selected[Number(control.dataset.outputRow)] !== false; control.addEventListener('change',captureOutput); });
  const actions = {
    'new-history'() {editing=true;lockControls();status('新しい有効期間の条件を入力してください。既存の履歴は保持します。');},
    'correct-history'() {editing=true;lockControls();status('誤登録の内容を訂正してください。訂正前後の記録を残します。');},
    pending() {dirty=false;editing=false;lockControls();status('確認待ちにしました。給与班が確認・確定するまで給与に反映しません。');},
    'decision-confirm'() {status('外部機関の決定結果を確認しました。機関の決定内容の採否を判断する操作ではありません。');},
    'commute-change'() {editing=true;lockControls();status('変更届を入力してください。旧認定を保持し、新しい認定として再提出します。');},
    'commute-end'() {modal('認定期間の終了を確認','認定期間の終了日を確認します。一時不支給とは分けて扱います。',()=>status('認定期間の終了日を確認しました。独立した終了状態は作りません。'),'期間を確認');},
    'commute-nopay'() {status('病気・欠勤等による一時不支給の期間を確認します。認定自体の終了とは別です。');},
    'assign-number'() {status('発行された12桁の職員番号を確認してください。既存職員の重複登録を避けます。');},
    'upstream-change'() {modal('前工程からの変更を確認','登録済みの内容と前工程の変更内容を比較します。確認済み情報を一律に上書きしません。',()=>status('変更箇所を確認しました。必要な訂正後は再確認を行います。'),'差異を確認');},
    'recover-import'() {simulate('取込結果と復旧対象を確認しています。',()=>{if($('[data-save-result]').value==='failure'){localState='error';context.attendanceIncomplete=true;status('復旧を完了できませんでした。不完全な結果を引き続き計算・報告から除外します。',true);}else{localState='normal';context.attendanceIncomplete=false;status('架空データの復旧を確認しました。内容を再確認して報告してください。');}persist();});},
    'report-month'() {status('勤務報告の対象月を確認しました。入力済み報告の状態を確認してください。');},
    period() {modal('支給回・対象期間を確認','例示2026年10月通常／対象期間2026年9月1日～30日／支給日2026年10月23日。期間と支給日は別々に管理します。',()=>status('支給回・対象期間・支給日を確認しました。'),'設定を確認');},
    adjust() {modal('例外調整を確認','調整は元データ訂正とは別に、理由と処理者を記録します。この画面例では金額を変更しません。',()=>status('調整理由・処理者の記録を確認しました。'),'調整記録を確認');},
    'retro-calculate'() {context.retro={staff:context.staff,run:context.run,confirmed:false};persist();simulate('過去月との比較結果を確認しています。',()=>status('架空の月別内訳を表示しました。確認待ちです。元の支払い済み結果は保持します。'));},
    'repay-method'() {modal('返納方法を確認','給与相殺・納入告知書を分割で併用できます。案件ごとに回収実績と残額を確認します。',()=>status('返納方法を確認しました。回収の実行とは別に記録します。'),'方法を確認');},
    edit() {editing = true; lockControls(); status('編集モードです。入力はこの画面例の中だけで保持します。');},
    read() {guard(() => {editing=false; lockControls();status('読み取りモードに戻りました。');});},
    save() {
      if(screen==='SCR-003'){const overtime=$('#field-scr-003-0-6').value,absence=$('#field-scr-003-0-7').value;if((overtime&&!/^\d+(\.\d{1,3})?$/.test(overtime))||(absence&&!/^\d+$/.test(absence))){status('超過勤務は小数3桁以内、欠勤は整数時間で入力してください。',true);return;}}
      const dates = $$('input[type=date][data-editable="true"]',app).filter(x => !x.closest('[hidden]'));
      if (dates.length >= 2 && dates[0].value && dates[1].value && dates[0].value > dates[1].value) {status('適用開始日は終了日以前にしてください。入力を保持しています。',true);return;}
      simulate('保存中です。操作完了までお待ちください。', () => {
        if ($('[data-save-result]').value === 'failure') status('保存できませんでした。入力を保持しています。内容を確認して再試行してください。',true);
        else {dirty=false;editing=false;const acquired=$('[data-acquired-time]');if(acquired)acquired.textContent='取得日時：2026/10/09 09:01（表示例）';baseline=new Map($$('[data-editable]',app).map(input=>[input,input.value]));if(screen==='SCR-003'){const row=$('table tbody tr',app);if(row)[4,5,6,7,8].forEach((idx,i)=>{row.cells[i+1].textContent=$('#field-scr-003-0-'+idx).value;});}status('模擬保存が完了しました。再取得した読み取り表示を確認してください。実データは更新していません。');}
      });
    },
    font() {app.style.fontSize = app.style.fontSize ? '' : '16px';},
    sidebar() {const side=$('.search-sidebar'); if (!side)return;side.hidden=!side.hidden;$('.mock-layout').style.gridTemplateColumns=side.hidden?'1fr':'';},
    search() {
      guard(() => {
        const term=$('[data-staff-search]').value.trim(); const rows=$$('[data-staff]'); let count=0;
        rows.forEach(row => {row.hidden=(!!term&&!row.textContent.includes(term))||(role()==='bureau'&&row.dataset.bureau==='other');if(!row.hidden)count++;});
        $('[data-search-count]').textContent=`${count}件`;
        $('[data-staff-detail]').hidden=count===0;
        if (!count) {context.staff='';context.name='';status('該当する職員はいません。検索条件を見直してください。');}
        persist();
      });
    },
    clear() {$('[data-staff-search]').value='';actions.search();},
    staff(control) {guard(() => {
      if(role()==='bureau'&&control.dataset.bureau==='other')return;
      context.staff=control.dataset.staff;context.name=control.dataset.name;editing=false;dirty=false;
      applyStaffFixture();drawContext();lockControls();persist();
      status(context.staff==='009900009901'?'選択職員の架空履歴を表示しました。':'選択職員を切り替えました。この架空職員の履歴は未登録です。以前の詳細は表示しません。');
    });},
    'ledger-range'() {const from=$('[data-ledger-from]').value,to=$('[data-ledger-to]').value;if(from>to){status('表示開始月は終了月以前にしてください。',true);return;}const count=(from<='2026-09'&&to>='2026-08')?3:0;$('[data-ledger-table]').hidden=count===0;status(count?`範囲を適用しました。例示の登録済み給与簿を表示しています。`:'選択期間の給与簿は0件です。未登録月の列は作りません。');},
    'add-row'() {const table=$('table tbody',app);if(table){const row=table.rows[0].cloneNode(true);row.cells[0].textContent='009900009903 架空 次郎';table.append(row);}dirty=true;status('職員行を追加しました。保存するまで未保存です。');},
    'remove-row'() {modal('職員行を削除しますか','末尾の架空の明細行をこの画面例から除きます。実データは削除しません。',()=>{const body=$('table tbody',app);if(body?.rows.length>0)body.lastElementChild.remove();dirty=true;status('行を削除しました。保存するまで未保存です。');},'削除');},
    'attendance-import'() {modal('勤怠Excelの取込','架空ファイルを使います。全件検証後に追加・更新し、未掲載の既存行は保持します。掲載行の手修正は上書き、空欄は既存値をクリアします。',()=>simulate('全件検証・取込中です。編集・提出を停止しています。',()=>{if($('[data-save-result]').value==='failure'){localState='error';context.attendanceIncomplete=true;persist();status('途中失敗しました。不完全結果を給与計算から除外し、復旧・再実行を待ちます。前状態への自動復元は保証しません。',true);}else {context.attendanceIncomplete=false;persist();status('架空ファイルの取込を模擬しました。追加更新後の内容を確認してください。');}}),'取込を開始');},
    report() {if(dirty){status('未保存の入力を保存してから報告してください。',true);return;}modal('勤務時間を報告しますか','報告後は編集・取込をロックします。訂正には給与班の差戻しが必要です。',()=>simulate('報告中です。',()=>{localState='readonly';editing=false;const state=$('#field-scr-003-0-2');if(state)state.value='報告済み';status('報告済みです。編集・取込をロックしました。');}),'報告する');},
    reopen() {if(role()!=='payroll')return;localState='normal';const state=$('#field-scr-003-0-2');if(state)state.value='入力中';status('入力中に戻しました。訂正後は再提出してください。');lockControls();},
    submit() {status('提出を模擬しました。給与班の確認を待ちます。');},
    return() {status('差戻しを模擬しました。通勤の差戻し理由はシステム外で連絡します。');},
    certify() {status('認定を模擬しました。元の認定は保持し、新認定との関連を確認します。');},
    'staff-confirm'() {status('給与情報の確認・確定を模擬しました。必要情報の未確認がある場合は確定できません。');},
    'decision-register'() {status('決定結果を確認待ちとして登録する操作を模擬しました。給与班確認前は給与計算に使用しません。');},
    'adoption-cancel'() {modal('採用取消を記録しますか','確認待ち・確定の候補を採用取消とし、給与計算対象から外す操作例です。支払い済み給与を取り消す操作ではありません。',()=>status('採用取消を模擬しました。候補の履歴を保持し計算対象から除外します。'),'採用取消');},
    trial() {simulate('仮例の再表示中です。実際の給与計算は実行しません。',()=>status('既存試算の架空表示を確認しました。実際の計算は行っていません。'));},
    'master-new'() {editing=true;lockControls();status('改定内容の入力例を確認してください。既存の有効期間履歴は残します。');},
    'master-stop'() {modal('使用を停止しますか','終了を記録して履歴を残します。物理削除は行いません。',()=>status('使用停止を模擬しました。過去の履歴は残ります。'),'使用停止');},
    'candidate-import'() {simulate('架空ファイルの行を検証しています。',()=>status('正常行2件・注意行1件。勤怠取込とは別に、正常行先行・注意行の個別判断を行います。'));},
    'candidate-accept'() {simulate('正常行の候補登録を模擬しています。',()=>status('正常行を確認待ちにしました。注意行は給与班の判断を待ちます。'));},
    'candidate-review'() {modal('注意行の取込可否を確認','勤務条件の内容が既存の取込済み候補と重複する可能性を確認してください。番号発行待ちだけでは不備にしません。',()=>status('注意行の判断を模擬しました。新たな職員基本の重複作成は行いません。'),'判断内容を確認');},
    calculate() {if(context.attendanceIncomplete){status('取込が完了していない勤務報告があります。不完全な結果を計算に使わず、復旧・再実行を確認してください。',true);return;}if(context.pay.paid){status('支払い済み結果は訂正しません。追給・返納を別に扱います。',true);return;}simulate('計算版作成の画面動線を確認しています。実計算は行いません。',()=>{context.pay.version++;context.pay.finalized=false;status('最新結果の更新を模擬しました。旧差分ゼロは失効し、再照合が必要です。');history('最新版更新を模擬');updatePay();});},
    'target-visible'() {$$('[data-output-row]').forEach(x=>{x.checked=!x.closest('tr').hidden;});captureOutput();status('表示中の明細だけを出力対象に選択しました。');},
    'target-all'() {$$('[data-output-row]').forEach(x=>{x.checked=true;});captureOutput();status('全明細を出力対象に選択しました。');},
    'apply-am'() {const value=$('[data-bulk-am]').value;$$('[data-output-row]').forEach(box=>{if(box.checked)$(`[data-row-am="${box.dataset.outputRow}"]`).value=value;});captureOutput();status('選択した明細へ指定したA/Mを適用しました。');},
    'export-review'() {
      captureOutput();const selected=$$('[data-output-row]').filter(x=>x.checked);
      if(!selected.length){status('出力する明細を選択してください。',true);return;}
      const staff=new Set(selected.map(x=>x.dataset.staffNumber));const a=selected.filter(x=>$(`[data-row-am="${x.dataset.outputRow}"]`).value==='A').length;
      modal('Excel出力前確認',`支給回：${context.run==='DEMO-RUN-02'?'例示2026年10月追給':'例示2026年10月通常'}／人数：${staff.size}人／明細数：${selected.length}件／A：${a}件／M：${selected.length-a}件。選択した明細をExcel出力します。（デモのため実ファイルは生成しません）`,()=>simulate('Excel出力の動線を確認しています。',()=>{context.pay.exported=true;context.pay.exportedVersion=context.pay.version;status('Excel出力を模擬しました。人給の取込・計算はアプリ外で行います。');history('Excel出力を模擬');updatePay();}),'Excel出力');
    },
    'ledger-import'() {simulate('架空の給与簿CSVを検証しています。',()=>{if($('[data-save-result]').value==='failure'){status('給与簿の取込に失敗しました。前回成功分は維持します。再試行してください。',true);}else{context.pay.imported=true;context.pay.comparedVersion=0;status('架空給与簿CSVの取込を模擬しました。最新版と照合してください。');history('給与簿CSV取込を模擬');}updatePay();});},
    reconcile() {if(!context.pay.imported){status('給与簿CSVの取込成功分がありません。先に取り込んでください。',true);return;}simulate('最新版の計算結果と給与簿を照合しています。',()=>{context.pay.comparedVersion=context.pay.version;status(context.pay.differences||context.pay.unknown?'差分または未解決行があります。原因を確認して訂正・再照合してください。':'最新の支給回全体で差分ゼロを確認しました。給与班確定が可能です。');history('最新版との照合を模擬');updatePay();});},
    reexport() {context.pay.selected=[true,false,false];$$('[data-output-row]').forEach(x=>{x.checked=context.pay.selected[Number(x.dataset.outputRow)];});captureOutput();selectTab('panel-j1');status('差分に対応する明細だけを初期選択しました。対象は変更できます。A/Mは指定を保持しています。架空の行対応を示しています。');},
    finalize() {if(!canFinalize()){status('確定できません。給与班権限と支給回全体の最新照合・差分ゼロ・未解決行なしを確認してください。',true);return;}context.pay.finalized=true;status('給与班確定を模擬しました。確認ダイアログは表示していません。支払い済み記録は別の操作です。');history('給与班確定を模擬');updatePay();},
    'mark-paid'() {if(!context.pay.finalized||context.pay.paid||role()!=='payroll')return;context.pay.paid=true;localState='paid';status('支払い済みの記録を模擬しました。送金・支払実行はしていません。');history('支払い済み記録を模擬');updatePay();},
    'retro-review'() {status('月別差額と追給集約・返納案件の対応を確認します。架空の月別内訳と出力内容を確認してください。');},
    'retro-confirm'() {context.retro={staff:context.staff,run:context.run,confirmed:true};persist();lockControls();status('差額を確定しました。追給・返納へ進めます。支給・返納の実施記録とは別です。');},
    recovery() {modal('回収実績の確認','給与相殺／納入告知書の回収記録を確認します。実際の回収・請求は行いません。金額・対象案件を確認してください。',()=>status('架空の回収実績を確認しました。複数回の実績と残額を対応させます。'),'記録を確認');},
    'print-guide'() {status('実装ではブラウザーの印刷からA4横2ページを1PDFに保存します。この画面例は正式帳票を出力しません。');}
  };
  app.addEventListener('click', event => {
    const control=event.target.closest('[data-action]');
    if(control&&!control.disabled) actions[control.dataset.action]?.(control);
  });
  $('[data-trial-month]')?.addEventListener('change',event=>{
    context.month=event.target.value.replace('-','/');persist();drawContext();
    const available=context.month==='2026/09'&&context.staff==='009900009901';
    const detail=$('.pay-breakdown'),summary=$('.mock-summary');
    if(detail)detail.hidden=!available;
    if(summary)summary.innerHTML=available?'<span>給与支給総額<br>200,000円</span><span>− 控除額計<br>48,200円</span><span>＝ 現金支給額<br>151,800円</span>':'<span>給与支給総額<br>—</span><span>控除額計<br>—</span><span>現金支給額<br>—</span>';
    status(available?'登録済みの架空表示に切り替えました。':'この対象月の勤務・計算根拠は未登録です。旧金額と算定説明は表示しません。',!available);
  });
  $('[data-all-diffs]')?.addEventListener('change',updatePay);
  $('[data-output-filter]')?.addEventListener('input',event=>{
    $$('[data-output-row]').forEach(control=>{control.closest('tr').hidden=!!event.target.value&&!control.closest('tr').textContent.includes(event.target.value);});
  });
  $('[data-run]')?.addEventListener('change',event=>guard(()=>{context.run=event.target.value;context.pay=defaults().pay;$$('[data-row-am]').forEach(x=>{x.value='A';});$$('[data-output-row]').forEach(x=>{x.checked=true;});updatePay();drawContext();status('支給回を切り替えました。前の回の照合結果は確定に利用しません。');}));
  $$('[data-history]').forEach(control=>control.addEventListener('change',()=>guard(()=>{
    const panel=control.closest('.mock-panel');const grid=$('.field-grid',panel);grid.hidden=control.value==='登録なし';status(grid.hidden?'この履歴は0件です。以前の履歴・認定IDを使用しません。':'選択履歴の表示を模擬しました。');
  })));
  roleControl?.addEventListener('change',()=>{const selected=roleControl.value;roleControl.value=context.role||'payroll';guard(()=>{roleControl.value=selected;context.role=selected;editing=false;if(selected==='bureau'&&context.staff==='009900009903'){context.staff='';context.name='';applyStaffFixture();}lockControls();updatePay();status(role()==='self'?'本人機能は将来追加です。初回運用の更新操作は利用できません。':`確認用の役割を${roleControl.selectedOptions[0].textContent}に切り替えました。実際の認可は変更していません。`);});});
  $('[data-review-state]')?.addEventListener('change',event=>{
    localState=event.target.value;editing=false;dirty=false;busy=localState==='loading';
    const detail=$('[data-staff-detail]');if(detail)detail.hidden=['initial','zero','error'].includes(localState);
    if(localState==='clean'){context.pay.imported=true;context.pay.comparedVersion=context.pay.version;context.pay.differences=0;context.pay.unknown=0;context.pay.finalized=false;context.pay.paid=false;}
    if(localState==='difference'){context.pay.imported=true;context.pay.comparedVersion=context.pay.version;context.pay.differences=1;context.pay.unknown=0;context.pay.finalized=false;}
    if(localState==='unknown'){context.pay.imported=true;context.pay.comparedVersion=context.pay.version;context.pay.differences=0;context.pay.unknown=1;context.pay.finalized=false;}
    if(localState==='stale'){context.pay.exported=true;context.pay.exportedVersion=context.pay.version;context.pay.version++;context.pay.finalized=false;}
    const jError=$('[data-jinkyu-error]');if(jError)jError.hidden=localState!=='error';
    if(localState==='paid'){context.pay.paid=true;context.pay.finalized=true;}
    if(screen==='SCR-003'){const reportState=$('#field-scr-003-0-2');if(reportState)reportState.value=localState==='readonly'?'報告済み':'入力中';}
    const messages={normal:'通常の架空表示です。',initial:'職員・対象を選択してください。以前の結果は利用しません。',zero:'該当するデータは0件です。以前の詳細は表示しません。',loading:'処理中です。編集・提出・重複実行を停止しています。',error:'データを取得できませんでした。入力を保持し、再試行を待ちます。',readonly:'報告済みです。入力中へ戻すまで編集・取込はできません。',difference:'差分があります。原因を訂正して再計算・再照合してください。',clean:'最新の支給回全体で差分ゼロ。給与班確定が可能です。',stale:'出力後に計算結果が変更されています。旧差分ゼロは失効しました。',unknown:'未知職員が残っています。差分ゼロでも確定できません。',paid:'支払い済みの結果は訂正できません。追給・返納は別に扱います。'};
    status(messages[localState],localState==='error');updatePay();lockControls();
  });
  $('[data-review-reset]')?.addEventListener('click',()=>{try{sessionStorage.removeItem(key);}catch(_){} location.href=location.pathname;});
  window.addEventListener('beforeunload',event=>{if(dirty){event.preventDefault();event.returnValue='';}});
  const staffField=$('#field-scr-002-0-0');const nameField=$('#field-scr-002-0-1');if(staffField)staffField.value=context.staff;if(nameField)nameField.value=context.name;
  baseline=new Map($$('[data-editable]',app).map(input=>[input,input.value]));
  applyStaffFixture();drawContext();updatePay();lockControls();
})();

/* Optional diagram controls: never change workflow data or the surrounding page. */
(() => {
  document.querySelectorAll('[data-connected-workflow]').forEach(section => {
    const viewport = section.querySelector('.workflow-scroll');
    const svg = section.querySelector('svg');
    const tools = section.querySelector('[data-diagram-tools]');
    if (!viewport || !svg || !tools) return;
    tools.hidden = false;
    const baseWidth = svg.viewBox.baseVal.width;
    const baseHeight = svg.viewBox.baseVal.height;
    let scale = 1;
    function apply(value) {
      scale = Math.max(.15, Math.min(1.8, value));
      svg.style.minWidth = '0';
      svg.style.width = `${Math.round(baseWidth * scale)}px`;
      svg.style.height = `${Math.round(baseHeight * scale)}px`;
      tools.querySelector('[data-diagram-scale]').textContent = `${Math.round(scale * 100)}%`;
    }
    function fit() { apply(viewport.clientWidth / baseWidth); }
    tools.querySelector('[data-diagram-fit]').addEventListener('click', fit);
    tools.querySelector('[data-diagram-all]').addEventListener('click', () => {
      apply(Math.min(viewport.clientWidth / baseWidth, Math.max(350, window.innerHeight * .76) / baseHeight));
      viewport.scrollTop = 0; viewport.scrollLeft = 0;
    });
    tools.querySelector('[data-diagram-actual]').addEventListener('click', () => apply(1));
    tools.querySelector('[data-diagram-out]').addEventListener('click', () => apply(scale - .15));
    tools.querySelector('[data-diagram-in]').addEventListener('click', () => apply(scale + .15));
    // Keep mobile labels legible; the reader can deliberately fit the whole width.
    apply(Math.min(1, Math.max(.8, viewport.clientWidth / baseWidth)));
  });
})();
