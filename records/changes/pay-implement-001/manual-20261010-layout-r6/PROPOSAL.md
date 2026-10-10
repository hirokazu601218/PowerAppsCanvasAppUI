# r6提案：狭い／短い画面で情報と操作を切らない

状態：未承認のUI例外案。アプリ未適用・未公開。確定要件の変更として扱わない。

## 今回の実機不具合

r5は保存37で2画面読戻し一致、Checker0。通常900/1366/1920は末尾到達と固定summaryを確認した。一方、実Chrome200%（590×378）では本文が1.328pxになり、450幅では根拠文字160pxが128px枠で切れる。Live36のまま公開を止めた。詳細はr5-runtime-failure-summary.json。

## 本人判断が必要な点

現行SCR005-UI-004は本文スクロール中もsummaryを固定し、UI-015は対象・操作欄を本文の外に固定すると明記する。狭幅では折返す設計で、狭い／短い場合の固定解除は未定義。共通設計は必要な横移動を許すが、本提案を既に確定した例外とは扱わない。

- A（推奨）：通常幅・高さでは現在の固定表示を維持し、狭い／短い場合だけ画面内全体を縦横に移動して読む。文字・項目・ボタンは消さず、縮小しない。本書の9プロパティ候補。
- B：どの寸法でも固定表示を優先し、ヘッダー・対象欄・summaryをコンパクトに再構成する。少なくとも固定276pxを縮め、本文1行を確保する必要がある。操作44px、文字サイズ、全情報の保持と狭幅折返しの両立を別途設計・実測する。Bの実装候補・合格結果はまだない。

Aの例外と、exact packageの公開GitHub保存・同試験アプリへの適用／架空データ検証・合格後公開の承認を確認してから外部作業へ進む。B選択時はAを適用しない。本書は承認を代替しない。

## Aの正確な変更

|対象|プロパティ|変更|
|---|---|---|
|conscrPayrollRoot|LayoutAlignItems|Stretch→Start。子Widthの最小幅を明示的に保持|
|conscrPayrollRoot|LayoutOverflowX|未定義→Scroll。必要な場合だけ横移動可能|
|conscrPayrollRoot|LayoutOverflowY|幅750未満、または固定領域を引いた本文高が上下余白＋128未満ならScroll。それ以外Hide|
|conscrPayrollHeader|Width|Parent.Width→Max(750,Parent.Width)|
|conPayrollTargets|Width|同上|
|conPaySummary|Width|同上|
|conPayBody|Width|同上|
|conPayBody|Height|root-scroll時は可視7子の実Height＋可視間隔＋上下余白。通常時は従来の残り高さ|
|conPayBody|LayoutOverflowY|root-scroll時Hide、通常時Scroll。縦方向の主要scroll所有者を1つにする|

変更前後の正確な式、未定義guard、SHAはproposal-delta.json。新しいコントロール、文字・業務計算・金額・状態・権限・データ操作の変更は0。外枠の共通比率と並び順も維持する。

750は対象欄の116＋150＋最低職員幅260＋検索168＋3間隔24＋左右余白32から導く。128は既存控除行の最大Height。どちらも任意の見切れ補償ではなく、元の寸法が変わればソースguardが再検討を要求する。

rootの実Widthと固定領域だけでmodeを決める。スクロールバーの有無で変わる子幅・行Heightを分岐条件にしないため、境界の履歴依存を避ける。狭い場合は高い画面でも例外modeとする。短い広幅でroot縦スクロールバーの幅分だけ横移動が生じる場合も含め、正規操作で到達可能か確認する。

## 通常表示との境界

通常900×600／1366×768／1920×1080は、モデル上の幅・固定領域・本文高がr5と同じ。450/683はroot退避、960×768は通常固定。正確な幅750、残り本文高160では通常modeを維持する。

最低内容幅により、控除根拠はモデル上247px以上を確保し、3操作ボタンは一列分を確保できる。これはPower Appsの実描画・文字可読性の合格ではない。横移動では項目を順に読むことになり、3欄が常に同時表示されるとは約束しない。

## 承認後の必須ゲート

1. 同試験App IDと最新保存版を再確認。最新r5全rootと正確な前値に一致した場合だけ9プロパティを適用。
2. Studio型検査／Checker、保存、全root読戻し。他86部品の構造・非対象プロパティの不変確認。
3. 通常3幅の固定summaryを再検証。450/683/960と実Chrome200%は別ケースとして実効viewport・スクロール所有者・文字範囲を採取。
4. 9月仮例と11月登録済み0で控除24欄の枠と内部文字を確認。末尾、対象職員、summary3値、月選択、ホーム、職員検索、3操作ボタンが正規pointer／Tab／focusで到達すること。hidden祖先の強制スクロールで合格にしない。
5. 展開／折り畳みと100→200→100でデータ状態が残り、通常固定表示と不要なscroll offsetが戻ること。Power Appsの実動作を未検証のモデルから推定しない。
6. Studio外側preview自体の既存スクロールとアプリ内を区別。必要な外側移動は通常ユーザー操作で行い、公開後Playerでも再確認。
7. 合格後、承認対象の同試験アプリだけ公開し、公開版読戻し・Player・文書整合を行う。実データ・本番・権限設定へ範囲を広げない。

## ローカル検査と復旧

静的・モデル・構文検査は同フォルダのログと独立レビューに記録する。現物型検査・Player・実200%はNOT_RUN。既存固定要件を削除してテスト成功に見せず、提案用選定を承認待ちとして分離する。

復旧は9プロパティの前値へ戻す。追加したroot OverflowX/Yは変更前の未定義状態へ戻す必要があり、単に異なる式へ置き換えない。r5の既知不具合も戻るため公開可にはしない。元のroot全量は私的バックアップで保持し、raw sourceや接続情報は公開ZIPへ含めない。

## 公式仕様と限界

Microsoftの[Vertical container](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/control-vertical-container)に記載されたStart/Stretch、Scroll/Hide、Fill portionsを用いる。[Responsive layouts](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/create-responsive-layout)の親寸法参照を維持する。新規preview機能や設定を使わない。公式記述だけでこの組合せの現在Studioでの型・レイアウト合格とはしない。
