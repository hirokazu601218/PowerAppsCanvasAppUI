# 現在の作業と読取り対象

## 2026-09-29 18:47 JST OneDrive修復成功・Dataverse読取権限不足を特定

- 安全な認証フォームにより、クラウド画面のキーボード操作なしで専用利用者と所有者の認証を完了。
- 公式診断に従い、専用利用者の個人用サイト機能フラグ32を空欄に修正して保存・読戻し。再診断と再読込み後、サービス側でフラグ4と有効な個人用サイトパスへ更新され、SPSSITEERRORは解消。個人用サイトURL自体は手動編集していない。
- 専用PlayerでOneDrive/Excel/Dataverseの接続済み表示と許可ボタン有効化を確認。許可後に同意画面が消え、SCR-003へ遷移できた。OneDrive接続阻害は解消。
- SCR-003のデータ取得はDataverseのprvReadcrb3c_AttendanceReportとprvReadcrb3c_AttendanceTargetMonth不足で失敗。画面は表示できてもデータ表示合格ではない。実効権限の修復範囲を次回確認し、必要最小限の試験用アクセスを整える。今回ロール変更なし。
- E2E run 36549616110の失敗ジョブを原因修復後に再実行（attempt 2）。18:47時点で実行中。公開後記録はBLOCKEDを維持。PR #122はDraft、未統合。
- 公開18:11版と718プロパティ読戻しPASS、要件・基本・詳細設計・結合仕様反映済み。次：再実行結果確認→対象2表の参照先と試験用ロール確認・修復→専用利用者E2E→公開後記録・最終照合→全必須チェック合格後PR統合。
- 17:49開始の60分制限に従い18:49までに停止・引継ぎ。詳細は `records/changes/change-20260929-scr003-attendance-import/manual-20260929-profile-repair/record.json`。


## 2026-09-29 18:30 JST OneDrive公式診断でプロファイル問題を検出

- Microsoft管理センターの標準セルフヘルプ `Diag: OneDrive Provisioning` を対象ユーザーへ実行。「このユーザーのプロファイルに問題が見つかりました」と判定し、「個人用サイトの機能」フラグをクリアする修復手順を提示。単なる時間待ちだけとは扱わない。
- 修復用SharePoint管理画面はテストアカウントでアクセス拒否。所有者管理者への認証切替が必要。認証フォームではテストアカウントが選択され、初期設定待ちへ戻った。フラグの値確認・変更はまだ実施していない。ロール追加で迂回しない。
- 18:11公開版のPR E2E run 36547558671は静的1件PASS、UI3件FAIL。認証自体はPASS、OneDrive WarningでAllow無効を再確認。
- 文書配置run 36547969133はPASS。公開後記録チェックは結合仕様の旧公開時刻残存でFAILしたため新時刻へ修正。PlayerはBLOCKEDのため最終ゲートは引き続き未完了。
- 次は所有者管理者でSharePointのユーザープロファイルを開き、公式診断が示す対象ユーザーのフラグを確認・修復→OneDrive実体と接続を確認→Player／最終E2E／文書照合→PR統合。

## 2026-09-29 18:14 JST 認証代替・OneDrive初期作成・再公開

- キーボードが表示されない手動操作を安全な認証フォームへ切替え、専用利用者のPower Automateサインインを確認。再接続では `No user OneDrive for Business account found` を再確認。ライセンス付与後も個人領域が未作成だった。
- 再ログイン後のアプリ起動ツールにOneDriveが出現。初回起動・本人認証を完了し、画面は「設定しています。しばらくお待ちください...」。作成完了や接続成立とは扱わない。
- 未公開下書きをダウンロードし、718プロパティ差分0とSCR002画面SHA一致を確認して同一アプリへ再公開。公開時刻 `2026-09-29T09:11:07.0090418Z`、最終下書き `2026-09-29T09:10:05Z`。読戻しAction 36547553342はPASS、パッケージSHA `01ece7bd31766f5ce5b17b75f4426281abfefe6c3342962b6a8b4625891f6d9c`。
- 新公開版の専用PlayerはOneDrive警告・許可無効のまま。公開後記録はBLOCKEDへ更新し、旧版のPlayer PASSを転用しない。要件・基本・詳細設計の公開版識別を更新。
- 文書配置チェックのFAIL原因は過去診断record.jsonのapp_id等不足と規定外status。診断内容は残し、BLOCKEDと必須メタデータを補完。最終E2E未完了のためPR #122はDraft、main未統合。
- 次：OneDrive作成完了→コネクタ作成・Player同意→新公開版Player検証→公開後記録更新と最終照合→全必須ゲート合格後にPR統合。

## 2026-09-29 17:47 JST ライセンス原因の確定と修復

- 管理センターで専用検証ユーザーがPower Apps for DeveloperとPower Automate Freeのみで、Business Basic未割当と確認。既存Business Basic (Teamsなし)は24/25席空き。OneDrive未検出エラーの前提不備を特定。
- 既存の空き1席を標準サービス設定で割り当て、保存成功とページ再読込み後の3製品割当・23/25席空きを確認。購入、ロール・共有変更はない。サービスの一括無効化案は自動承認審査で拒否され未実行。
- OneDrive初回利用は個人領域未確認。ライセンス修復後の接続作成で認証選択を要求したが中断され、元画面に「サインインできません。やり直してください。」。接続成立とは扱わない。
- 再開位置：専用ユーザーでOneDrive初期作成と接続認証を完了→接続済みとPlayer警告解消を確認→下書き版の扱い・公開読戻し→最終E2E・文書照合→PR統合。公開15:38版、未公開16:22:29下書き、PR #122 Draftを維持。
- 今回は新しいテストActionsを起動していない。詳細は `records/changes/change-20260929-scr003-attendance-import/manual-20260929-connection-diagnosis/license-remediation.json`。


## 2026-09-29 17:14 JST 接続追加の診断結果

- 利用者の追加承認後、専用検証アカウントでOneDrive接続作成を実行。Microsoftから `No user OneDrive for Business account found` が返り、作成失敗。新しい接続一覧にもOneDriveはない。ログイン失敗や単なるトークン期限切れとは扱わない。
- 原因の確定範囲：コネクタが専用ユーザーのOneDrive実体を取得できない。ライセンス未割当かプロビジョニング未完了かは未確定。管理者による既存SharePoint/OneDriveライセンスと初期作成状態の確認が必要。有料契約は追加していない。
- SCR003フローの接続設定変更をStudioへ更新し16:22:29に下書き保存済み。未公開。公開中は15:38版のまま。PoC設定・共有・実効ロールは変更していない。
- 次はOneDrive利用前提の確認・整備→接続作成→Player警告解消確認→必要な下書き公開と読戻し→最終E2E・文書照合→PR統合。PR #122はDraft、main未統合。
- 証跡：`records/changes/change-20260929-scr003-attendance-import/manual-20260929-connection-diagnosis/creation-error.json`。同フォルダの過去の再接続待ち記録は当時の観測であり、この結果が最新。


## 2026-09-29 SCR-003公開後の最終照合

- 15:13 JST開始、16:13 JST期限。利用者は公開とGitHub設計書等への反映を承認。権限判定は後工程、架空データのテスト環境。
- 同一アプリを15:22に公開後、公開Player固有の初期非表示ギャラリー幅1pxを修正し15:38に再公開。公開時刻 `2026-09-29T06:38:41.555451Z`。所有者Playerで架空10件、12桁番号、0/33.167、勤務期間、一覧開閉を確認。
- PACソース照合 Action 36532637596はPASS。718プロパティと上限2000を確認。SCR002のSHA差はNative CDS論理名/表示名への書換え。旧保存版＋v1.28の2式で全コントロールの意味上差分0を確認。
- 所有者Studioでは取込/編集/欠勤0.5拒否/報告/戻し/報告済拒否/再取込10件維持/6課室と2件絞込み/対象月解除と再設定を確認。フローはON。
- 最終Action 36533040055で公開版・SHA・718プロパティ・文書差分の照合はPASS。専用利用者E2Eは静的1件PASS、UI3件FAIL（OneDriveのRefresh connection警告でAllow無効）。SCR003フローの接続元を既存所有者に切替えて読戻したが、既存PoCの利用者接続依存も残り解消せず。PoC設定・共有・実効ロールは変更していない。PR #122はDraftのまま、main未統合。
- 未実施：999件境界、同時操作・途中障害、実効認可、業務受入・総合試験。一時Excel削除はロック400で残存。チェッカー数式エラー0、アクセシビリティ292/パフォーマンス13は未解消。
- 読取り対象：変更要求、v1.29、フロー生成/配布、選定記録、公開後記録、要件/基本/詳細設計と結合試験仕様。次は専用検証アカウントのOneDrive再接続→最終Actionの失敗ジョブ再実行→全必須ゲート合格後にPR統合。

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
