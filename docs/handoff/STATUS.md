# 現在の作業と読取り対象

## 2026-09-28 SCR-002の添付4定義書反映（進行中）

- 変更要求：[`CHANGE-20260928-SCR002-HISTORY`](../changes/requests/change-20260928-scr002-history.json)。勤務条件15列、社会保険26列、税固定控除9列、住民税6列を対象とする。住民税は税固定控除タブ内で扱う。
- [列契約](../../config/dataverse/scr002-history-columns.json)に従って正式4表と隔離`_STUDIO`4表を作成し、列型、親職員Lookup、削除Restrictを[Action 36363649180](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36363649180)で読戻した。正式表へ職員データは投入していない。
- 現行App ID `204a48dc-7f23-43dd-b934-4654a3cfa306` のStudioで、エラーを含む未公開v23を公開v22からv24へ復元（v23は履歴に保存）。隔離4表を再接続し、[読込・表示の差分候補](../../src/screen-ui/v1.28/README.md)に勤務条件15・社会保険26・税固定控除9・住民税6項目を反映。StudioのApp Checkerで数式エラー0件、Maker版履歴で未公開v25（2026-09-28 04:07 UTC）と公開中v22を確認。架空職員011の隔離行を[Action 36376777042](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36376777042)で投入し、Studioプレビューで56項目と値・数値0、職員004への切替後の旧履歴消去を観察。専用利用者へ隔離4表のReadのみ付与する[Action 36377417327](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36377417327)も成功。**公開v22はそのまま。v25のソース読戻し、専用利用者E2E、公開・Player確認、NULL値の実表示は未完了**。公開v22の受入結果を本変更の結果へ転用しない。
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
