# PAY-IMPLEMENT-001 独立適用前レビュー

> 最新基準追補：2026-10-10 01:14 UTCにv36へ基準を再関連付け。末尾の「v36基準の独立追補レビュー」を参照。初回v35レビューは当時の記録として保持する。修正候補のStudio型検証・Player試験・公開は未実施。

## 結論

2026-10-10 UTC、r4候補の**限定ソースレビューは適用前ゲートを通過**。未解消のソース上のブロッカーはない。これはStudio、Power Fxコンパイラ、Player、保存・公開、PAC公開後読戻し、業務受入のPASSではない。実行担当が同じ試験App IDと最新編集版に変化がないことを再確認し、承認範囲内で適用・実機試験するための結果である。

対象：StaffMaster-Automation-Test / App ID `204a48dc-7f23-43dd-b934-4654a3cfa306`。本番、安定版、実データ、main統合、新規制度判断は対象外。

## 独立に確認した基準版

- 現行v35の公式Export内msapp SHA-256：`465dcdc2eec6deb181f8df811558bdade4f0b6494675346e1cac700d90f1a740`。
- 8画面、App、EditorStateの計10 YAMLは、既存の2026-10-07監査スナップショットとすべてバイト一致。現行版と旧資料の同一性を推定で済ませていない。
- 改訂パッチャーは10ファイルの名前集合と各raw SHAを検証し、追加・欠落・変更を拒否する。全画面をまたぐ重複コントロール名、画面とコントロール名の衝突も拒否する。CLIはこのload_readbackを経由してからapplyする。
- rawバックアップと展開済み全ソースは接続参照・環境固有値を含むため、リポジトリ提出物に含めない。

## 発見し修正を確認した項目

1. **全量前値ガード不足：解消。** 初期パッチャーは変更対象の前値と給与rootしか検証せず、無関係な職員画面のItems変更、給与画面OnVisible変更、重複名を受け入れた。メモリ上で再現し報告した。r4は全10ファイルのraw SHA・集合照合と全体名前検査を追加した。
2. **取得失敗が遅延Selectで成功表示へ戻る可能性：解消。** 初期OnVisibleは失敗処理でbtnLoadDetailsをSelectし、その後にエラーと空時刻を設定していた。Selectは同期実行を保証せず、後続の詳細取得がエラーを消し、空選択に成功時刻を付け得る。r4は成功・失敗式の内部からSelectを除去し、失敗時に詳細を直接消去、IfError終了後のエラーなし条件でのみSelectする。btnLoadDetailsの失敗処理でも取得時刻を明示的に空にした。これはソースと公式仕様に基づく指摘であり、障害注入の実機再現結果ではない。
3. **実画面テスト範囲不足：追加済み、未実行。** ページ2往復、幅900×高さ600、A→B→0件→Aの履歴初期化を追加した。新しい接続同意は自動承認せずBLOCKEDとする。

根拠：[Microsoft Select](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-select)、[Microsoft IfError](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-iferror)。Selectの遅延実行と、チェーン式のエラー範囲を区別して評価した。

## 確定要件との対応

- SCR002-LT-002 / COMMON-NAV-003：検索時に入力・所属・在籍状態を確定変数へ保存。再入場は同一所属の確定条件で再取得し、有効な職員キーとページを保持する。未確定の入力を条件へ混ぜない。新規起動・検索クリア・所属変更は初期集合の分岐を使う。ホーム経由の再入場も同じ保持契約を使い、単なるホーム往復を新規検索扱いしない。
- SCR002-LT-005 / 007、詳細設計10.8：履歴キーを区分別に保持し、現在の区分・履歴集合内にあるキーだけ復元する。職員変更・空選択でキャッシュを消去する。住民税のR:接頭辞、GUID、12桁文字列キーは既存どおり。新たな重複ID生成、循環参照、型混在はソース上認めなかった。
- SCR005-ACT-005 / 006 / 008：8つの控除根拠を既存金額と同じUiReadyで失効させる。登録済み0円の仮例は維持。App.Formulas、仮額・料率、金融計算、勤務単価、制度判断を変更しない。
- SCR005-UI-004 / 015：既存サマリーを本文の外のroot直下へ移し、本文の高さからヘッダー・対象操作・サマリーを差し引く。固定高さと参照関係に循環はない。最終貯金行は同じ本文に残る。実寸重なり・可視性はPlayer測定待ち。
- 取得上限500の既存ガードは残る。500件超の取得やサーバーページングを新たに実装・合格扱いしていない。

## 独立差分照合

同じ現行読戻しからr4パッチを再計算し、実行担当のr4出力とYAML全体を照合した。

- 全コントロール351、追加・削除・改名なし。職員画面74、給与画面86を維持。
- 変更は14プロパティ（職員側4ハンドラー＋OnVisible、給与側8根拠Text＋本文Height）と、conPaySummaryの親1件だけ。
- 他6画面は変更なし。対象2画面内も許可した部品・プロパティ以外は不変。
- payroll-rootのpaste形式とpa形式のChildrenは同一。
- r4生成画面raw SHA：
  - scrStaffMasterSearch.pa.yaml：`25d2c1a753cc15a436d689d34f69aaf2ec03ca7d651e2a20f7b0735baaa300f3`
  - scrPayroll.pa.yaml：`c841beab9cdc5d865c2b7e03c9613112d5f464ebc80d5526ae98092d82266ac3`

## 実行した検査

- Python automation：49件PASS（当候補のfocused 14件を含む）。
- Python governance：3件PASS。
- 既存commute layout：2件PASS、1件SKIP（必要な固定版PDF未取得）。給与改修の実機試験には読み替えない。
- Node v24.19.0の型除去後syntax check：state-retention / attendance-uiともPASS。TypeScript型検査、Playwright実行ではない。
- git diff --check：PASS。
- 試験選定JSON：17ソースファイルを12件（状態保持9件＋既定ホーム2件＋SCR003契約1件）へ対応付ける検証PASS。変更ファイル全体を対象にしたゲートは、attendance-ui変更の既存4件も追加し、計16件を選定する。
- 既存ゲートの差分はv1.31を検知対象へ追加したもの。旧拒否条件・必要単体／結合条件を削除していない。attendance-uiの同意自動クリック除去は権限付与をfail-closedにする変更。

## 残る実機確認・制限

- Studio読込み・App checker・式コンパイル、保存、公開、公開版の全量読戻し、9件のPlayer試験と既定スモークはこのレビューでは未実施。
- E2Eの期待値は独立した架空職員番号、件数、年月、項目名、151,800円／0円、位置条件を使い、候補ソースを読んで期待値を生成しない。Python構造検査は候補から一部baselineを再構成するため、業務結果の独立オラクルではない。
- 通信障害・権限拒否・履歴削除・取得途中の件数減少に伴うページclamp・入力登録版更新・200%拡大の実機確認は別途必要。通常再入場と検索0件の実行だけで、これらをPASSとしない。
- 取得エラー経路は修正と静的回帰検査を確認した。実際の障害注入は未実施。
- UI変更後の現物を再読戻し、下記hash対象との差分がないことを確認する。適用直前に新しい編集ドラフト・別の公開が見つかった場合は停止し、再レビューする。

## レビュー対象の固定

各候補・テスト・ゲート・要求/選定ファイルのSHA-256は [reviewed-file-hashes.json](reviewed-file-hashes.json) に記録する。これらの後続変更に本レビューは自動適用されない。実施ログは [automation-tests.txt](automation-tests.txt)、[governance-tests.txt](governance-tests.txt)。

## 送信前追加レビュー（2026-10-10 00:35 UTC）

- r4の全FX・YAML・パッチャー・ガードは前回hashから変更なし。変更済み3ファイル（要求、選定、state-retention）を再確認し、SD-06契約JSON、attendance-contract、既定navigationテストもhash対象に追加した。
- SD-06の変更はimport_contract.replacementの説明1項目だけ。旧データの削除記述を既存の非破壊バッチ動作へ合わせ、旧行保持・不完全ステージング未活性化・一時Excel削除との区別を明示した。既存フロー定義と生成スクリプトは変更なし。既存10件のフローソーステストを独立に再実行してPASS。ランタイムフローの新規実行結果ではない。
- attendance-contractの4追加assertは説明内容の固定であり、元の列順・型・キー・対象環境のassertを削除していない。説明assert自体を実フローの挙動証明とはしない。
- 40件は内蔵メモリfixtureのまま。最後に新しいPlayer読込みで通常7件、空入力、既存架空004の存在、内蔵021の不存在を確認する追加assertをレビューした。Dataverseに40行を作らず、DB性能・委任の試験とも表示しない。
- 投稿後選定12件／PR選定16件を独立に検証してPASS。2つの変更TypeScriptファイルはNode syntax check PASS。git diff --check PASS。実画面試験は引き続き未実施。
- 追加差分にソース適用を妨げるブロッカーなし。更新後のreviewed-file-hashes.jsonは31ファイルを固定する。

## v36基準の独立追補レビュー（2026-10-10 01:14 UTC）

結論：**基準証跡のみの更新にソース上のブロッカーなし。** 初回r4の条件付きソース適用判定を、公開36から読戻した同一ソースへ関連付ける。これは現行Studioで修正候補の型が検証済みという判定でも、修正機能の公開許可・公開完了でもない。公開36は未編集ドラフトの公開であり、PAY-IMPLEMENT-001の4修正を適用した版ではない。

- 現物msappのSHAを独立再計算し、`f3af186814e138f60fe8e2848ccecdafd7db4af6d1454a852be815ca5e33266c`に一致。旧35のSHAも既存記録に一致した。
- Srcの8画面＋App＋EditorState、計10ファイルは名前集合・全バイトが35と36で一致。**CanvasManifest.jsonは双方に存在せず、比較対象ファイルなし。** 一致ファイルに含めない。
- Controls JSONを名前で対応付け、372部品を両版で確認。318件のControlUniqueId再採番を除けば全構造・プロパティが一致した。ここでの372はパッケージControls JSONの集計で、前記YAML Childrenの351とは表現と集計範囲が異なる。
- DataSourcesを入れ子JSON展開し、MetadataId付きオブジェクト配列だけ順序を正規化して独立比較。全体が一致した。接続参照を含むraw内容は本記録へ転記していない。
- 更新はmanifestの現行基準・証跡、READMEの版説明、STATUSの現行作業証拠、テストの旧35期待値を36＋正確なmsapp SHAへ更新したもの。候補FX/YAML、ヘルパー、E2E、選定は前回hashと不変。テスト条件を削除・緩和していない。
- `load_readback`を正しいv36 Srcディレクトリへ実行して10ファイルガードPASS。再計算した2候補画面は35基準r4と36基準r4の両方にrawバイト一致。14プロパティ＋1親移動、未承認差分0を再確認。確認初回はSrcの親ディレクトリを渡して全10ファイル欠落として正しく拒否され、正しいSrcを指定し直して成功した。ガードは変更していない。
- 独立focused 14件PASS、diff check PASS。計画担当の更新後49 automation／3 governance PASSログを確認。旧35期待値1件の初回失敗ログはv36基準記録に保存されており、成功へ上書きしていない。
- v36未編集版のChecker 0エラー証拠は修正候補の型検証へ転用しない。修正候補のStudio型検証、保存後全量読戻し、Player、修正候補公開後検証は引き続き未実施。適用直前の編集版チェックも必要。
- SD-06説明変更の送信承認状況は親担当の管理事項であり、本ソースレビューで承認済みにはしない。

履歴：[旧v35 hash](reviewed-file-hashes-v35.json)、[旧v35 record](record-v35.json)。現在のhash対象は34ファイル。基準詳細：[source rebind](../manual-20261010-v36-baseline/source-rebind-verification.json)、[publication baseline](../manual-20261010-v36-baseline/publication-baseline-summary.json)。
