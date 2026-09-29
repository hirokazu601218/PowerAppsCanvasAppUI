# 現在の作業と読取り対象

## 2026-09-29 SCR-003フロー実装候補・実環境保存エラー

- ユーザーは13:35 JSTに既存PR #122への送信と無効な開発用フローへの反映を明示承認。Git CLI認証がなく、接続済みGitHubツールで同ブランチへ送信した。最新実装候補コミットは `8c9f74d36952e7ee230d78d7738a4c7ad11aa2e7`。
- 所有者のDataverse接続完了を画面で確認。従来の読取用下書きに対象月表を設定して保存。フローチェッカーはエラー0・無条件一覧警告1。これは新しい保存処理の合格ではない。
- 候補コード：`scripts/automation/build_scr003_flow.py`、`powerapps/flows/scr003/definition.json`。全行検証、先頭0埋め、対象月照合、バッチ保存、報告・戻し、対象月設定を実装。`tests/automation/test_scr003_flow.py` の静的8件はActionsでもPASS。ただし実機試験ではない。
- `scripts/automation/deploy_scr003_flow.py` は既存の無効なSCR003フロー1件と承認済み接続を照合し、バックアップ後にETag付き更新を試行。認証・読取・バックアップは成功。更新はPower Automate検証で拒否。
- 最初の [run 36522420673](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36522420673) で `null()` 構文エラーを特定し、`null`へ修正。
- 修正後の [run 36522487189](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36522487189) は `InvalidConcurrencyConfiguration`：Requestトリガーの同時実行制御と同期Responseを併用できないためFAIL。候補定義の反映・読戻しは未達。単に同時実行制御を削除すると更新競合を招くため、修正していない。
- 次工程：アプリへの同期応答を維持できる排他制御または非同期ジョブ方式を設計し、競合・途中失敗を試験。その後SCR003呼出し/編集/報告/戻しとSCR006対象月設定を配線。架空Excel取込、再取込、対象外月、報告済拒否、画面再表示、公開Playerとソース照合は未実施。
- 権限判定はユーザー指示で後工程。テスト環境・架空データ専用。アプリ公開・フロー有効化・共有やロール変更は今回行っていない。
- 12:41開始の継続作業は13:41までの停止ルールを適用。読取り対象は本節、上記コード、変更要求・設計候補・列契約と `docs/operations/current-app-request-to-release.md`。

## 2026-09-29 SCR-003 Excel取込の正式設計準備（未実装）

- [変更要求](../changes/requests/change-20260929-scr003-attendance-import.json)、[設計候補](../changes/scr003-attendance-import-design-candidate.md)、[20列の列契約](../../config/dataverse/scr003-attendance-columns.json)をDraft PR #122に記録。局×勤務月の状態、入力中の全件置換、報告済取込不可、給与班だけの戻し、対象月設定、0と12桁番号の扱いを整理した。
- 添付の架空Excel「テストデータ」シート／TestData（20列10行、6課室）を検査し、先頭0を含む職員番号、欠勤時間整数、0・33.167の表示値を確認。小数欠勤と13桁番号の模擬不正値は契約検査で拒否。実際の取込処理の単体試験ではない。
- StaffMaster-Automation-TestのMakerで「勤務時間」「報告」の既存表0件。「勤務」は給与勤務条件2表のみ。既存の勤務時間報告表との差分判断は発生していない。Dataverse新規3表は候補で、作成・データ登録・アプリ保存／公開をしていない。
- アカウントから局・会計課給与班を判定する正本（属性・グループ・実値）と、Excel所属部局名から局識別子への対応が未確定。D-01の実効権限を解決してからサーバー側権限・保存を実装する。SCR-006の対象月設定も未実装。PoC受入成功を正式版の合格へ転用しない。

## 2026-09-28 SCR-002の添付4定義書反映（公開v25）

- 変更要求：[`CHANGE-20260928-SCR002-HISTORY`](../changes/requests/change-20260928-scr002-history.json)。勤務条件15列、社会保険26列、税固定控除9列、住民税6列を対象とする。住民税は税固定控除タブ内で扱う。
- [列契約](../../config/dataverse/scr002-history-columns.json)に従って正式4表と隔離`_STUDIO`4表を作成し、列型、親職員Lookup、削除Restrictを[Action 36363649180](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36363649180)で読戻した。正式表へ職員データは投入していない。
- 現行App ID `204a48dc-7f23-43dd-b934-4654a3cfa306` のStudioで、エラーを含む未公開v23を公開v22からv24へ復元（v23は履歴に保存）。隔離4表を再接続し、[読込・表示の差分候補](../../src/screen-ui/v1.28/README.md)に勤務条件15・社会保険26・税固定控除9・住民税6項目を反映。StudioのApp Checkerで数式エラー0件、Maker版履歴で未公開v25（2026-09-28 04:07 UTC）と公開中v22を確認。架空職員011の隔離行を[Action 36376777042](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36376777042)で投入し、[Action 36377952175](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36377952175)でその他備考をNULLへ変更。Studioプレビューで56項目と値・数値0と空欄の区別、職員004への切替後の旧履歴消去を観察。専用利用者へ隔離4表のReadのみ付与する[Action 36377417327](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36377417327)も成功。ユーザーの置換承認後、同じApp IDのv25を公開（メタデータ時刻 `2026-09-28T05:00:02.0455229Z`）。所有者の新規Playerで勤務条件15項目、0とNULL空欄を観察し、専用利用者の選定4単体・2結合ケースは[Action 36380881898](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36380881898)で6/6 PASS。[PAC読戻し](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36380763781)でパッケージSHAとSCR-002画面SHAを取得。旧v22のSHAを期待したチェックは失敗したためv25の確認値へ更新。[公開後記録](../verification/postpublish/change-20260928-scr002-history.json)を[最終照合Action 36381505625](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36381505625)で版・パッケージSHA・文書差分と専用利用者6ケースを再検証し、全ジョブPASS。編集・保存、他所属の実効権限、業務受入と総合試験は未判定。公開v22の受入結果を本変更の業務受入へ転用しない。
- 読取り対象：[変更要求](../changes/requests/change-20260928-scr002-history.json)、[データ設計](../design/basic/data-model.md)、[選定記録](../testing/change-records/change-20260928-scr002-history.json)、[単一アプリ公開手順](../operations/current-app-request-to-release.md)。D-02の編集対象列・入力検証・権限は未決のまま。

以下の既存記録は2026-09-27更新。過去の時系列全文は[移行前STATUS](../../records/docs/handoff/STATUS-history.md)へ保管。

## 現行の対象

- 継続対象：App ID `204a48dc-7f23-43dd-b934-4654a3cfa306` の単一アプリ。旧配布対象 `362ac991-eead-4f07-8373-afdb3ebfdba1` は現行ではない。
- 現行の[要件](../requirements/requirements.md)、[基本設計](../design/basic/basic-design.md)、[詳細設計](../design/detailed/detailed-design.md)、[試験方針](../testing/test-policy.md)、[未決一覧](../requirements/open-decisions.md)を基準にする。
- 旧v20の専用利用者の検索FAIL／結合BLOCKEDは当時の履歴。今回のv22は選定5ケースが専用利用者のE2EでPASSし、SCR-002画面定義の公開版SHAは保存版と一致した。全画面・接続・画面／データ権限、SCR-005計算元などは未解消。今回の5件だけで全要件完了とはしない。
- 旧配布・復元・認証診断のActions定義30本は `records/workflows/` に保管し停止する。現行の読み取り専用テスト2本と別アプリ用定期E2E1本は継続する。現行アプリの公開・データ・権限はこの移行では変更しない。
- 現行アプリの共有は所有者と「Power Apps 自動テスト」共同所有者の2件、招待待ち0件（2026-09-27確認）。共有上限が表示されてもサービスプリンシパルを追加せず、既存のテストアカウントで公開後読戻しとE2Eを続ける。403等では共有を変更せず停止する。[固定手順](../operations/single-app-workflow.md#共有と読戻しの固定手順)。

## SCR-002画面改修（2026-09-27 12:01 JST 公開）

- 2026-09-27 15:24 JST、利用者がSCR-002公開v22の受入テスト完了・修正点なしと本Workで報告。[実施記録](../../records/changes/change-20260927-scr002-ui/manual-20260927-scr002/record.md)に利用者受入PASSを追記。詳細な受入ケースの証跡は提供されておらず、全163項目末尾・複数履歴・他所属権限およびアプリ全体の総合テストは引き続き未判定。アプリへの再公開はしていない。

- 同じApp IDのライブv22にSCR-002の年月欄削除、4タブの長文履歴カード縮小、給与簿の余白・配色、ホームと画面IDの位置を反映。Studioの公開成功通知とPlayer再読込みで新画面を観察。[変更要求](../changes/requests/change-20260927-scr002-ui.json)、[実施記録](../../records/changes/change-20260927-scr002-ui/manual-20260927-scr002/record.md)。
- 保存版の画面定義差分とSHAは[ソース差分](../../src/screen-ui/v1.24/studio-readback/scr002-ui-20260927.delta.json)。[PR #87](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/pull/87)で要件・基本／詳細設計・結合テスト仕様を更新し、[Action 36293464353](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36293464353)で単体3件・結合2件がPASS。初回の結合FAILはテストの全角空白照合を修正して再実行。文書配置と公開後照合ルールの静的チェックもPASS。
- [Action 36298591428](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36298591428)で既存の共同所有者専用アカウントが同じApp IDの公開版をPAC読戻し。公開時刻`2026-09-27T03:01:06.626618Z`、パッケージSHA-256`478c74dd382bdd975af3eb651d0710eeb5ce1d49edeb3e0be30b8694201869b6`を取得し、SCR-002画面定義SHA-256`12be61ecf5fb0ba69e21cb6c4598d69a6c2058bb7512c158cf8ef9c025310b0c`が保存版と一致した。[公開後照合記録](../verification/postpublish/change-20260927-scr002-ui.json)。[最終照合Action 36299222521](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36299222521)は同じパッケージSHAと公開メタデータ、要件／設計／結合ケース仕様の差分を再検証し、専用利用者の5ケースも5/5 PASS。全163項目末尾・複数履歴・他所属権限と総合テストは未判定。以下のv20／v21記載は改修前の調査履歴。

## 改修前の公開版86行の照合（2026-09-27）

- [86行対応表](../requirements/traceability-matrix.md)の各行にライブv20の当日判定、[操作証拠](../../records/changes/requirements-audit-20260927/manual-20260927-v20/audit.md)のID、未試験条件を記録。[未決一覧](../requirements/open-decisions.md)へ再現した差分と公開版ソース照合の阻害条件を反映。文書変更のためテスト仕様書全体は対象外。相対リンク・行数・記述整合と配置検査を確認する。
- Maker版履歴ではv20（2026-09-25）がライブ。Studioの閲覧・退出でv21（2026-09-27）が未公開の自動保存版として作られた。意図的なアプリ編集・公開は行っていない。v20とv21のソース一致は未確認。**改修前の注意事項。今回v21の保存ソースをダウンロードして変更箇所を比較してから保存・公開したが、v20とv21の全ソース一致や公開パッケージSHAはなお未照合。**
- 所有者の隔離職員011でSCR-002、003、004、005と認定簿HTMLの一部を観察。検索結果保持、SCR-005固定サマリー、未登録月の説明文残留に再現差分。専用利用者の検索FAIL、保存／認可／独立給与計算、全163列、PDF、同月複数、公開v20ソース、前後性能は未解消。86行全条件の合格ではない。

## 今回の文書移行の読取り対象

[三分法](../operations/document-organization.md)、[対照表](../../records/operations/migration/source-map.csv)、[現行の手順](../operations/current-app-request-to-release.md)、[配置検査](../../scripts/governance/validate_document_placement.py)。移行PRの静的チェック結果とGitHub側必須チェック設定はPRで確認し、未設定を合格扱いしない。
