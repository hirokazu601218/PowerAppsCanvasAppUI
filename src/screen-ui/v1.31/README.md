# v1.31 PAY-IMPLEMENT-001: r6 未承認レスポンシブ提案

**r6は未承認提案。適用・公開しない。** r5は保存37/Live36、通常900/1366/1920は末尾到達PASSだが実200%と450幅の文字切れはFAIL。現行要件が対象・summaryの固定を明記するため、狭い／短い画面だけrootスクロールへ退避する例外は本人確認待ち。通常幅の固定と業務式は維持する。詳細は[提案記録](../../../records/changes/pay-implement-001/manual-20261010-layout-r6/PROPOSAL.md)。

## r6候補の9プロパティ

- root: AlignItems Start、OverflowX Scroll、幅750未満または残り本文高が上下余白＋128未満の時だけOverflowY Scroll。
- header/targets/summary/body: Width Max(750,Parent.Width)。外枠の共通比率は変更しない。
- body: root-scroll時は可視7子の高さ＋可視間隔＋上下余白、通常時は従来の残り高さ。root-scroll時はOverflowY Hide、通常時Scroll。
- 750は対象欄の必要幅から導出。128は既存控除行の最大Height。任意の見切れ補償値ではなく、ソース定数が変われば静的guardで再設計を要求する。

## 生成・復旧・検証

- `apply_pay_implement_001.py`は公開v36の全10原本ファイルと全rootをguardして候補2画面をローカル生成するだけ。新規2overflowプロパティは元の不存在を厳密検証する。外部保存機能はない。
- r5適用済み版へはroot再配置や全体貼付を繰り返さない。承認後、proposal-delta.jsonの正確な前値とroot基準を照合し9プロパティだけ変更して、全量読戻しの唯一差分を検査する。
- 復旧は同試験アプリで9プロパティの前値／不存在を戻す。新たな表・アプリ・権限・フローは作成しない。r5の既知200%/450不具合が戻ることを隠さない。
- ローカル試験はPower Fxコンパイラ／Studio／Playerではない。現物Checker、通常3幅、450/683/960、実Chrome200%、全24控除欄の文字、対象職員、全ボタン、Tab/focus、折り畳みと100→200→100を別々に確認する。
- 狭い/短い時はsummary等もスクロールする。通常幅・十分な高さではこれを許さない。テストはhidden祖先を強制スクロールして成功に見せず、rootの正規の操作可能な縦横移動で確認する。Studio外側previewの既存スクロールはアプリ内の根拠へ混同しない。

## r4/r5の履歴

過去の候補・前値・レビュー・部分実機結果はrecords/changes/pay-implement-001/に残す。r5 intrinsic deduction Height、検索確定状態、履歴保持、根拠8件の失効guardは本提案でも不変。r4/r5のPASSはr6へ転記しない。
