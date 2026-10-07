# ChatGPT Library資料索引

> 対象アプリ：共通（自動テスト／ハンドメイド）

更新日：2026-10-07

## 目的

ChatGPT Libraryに保管する資料の所在、用途、関連機能、読取り条件を管理する。資料の内容はLibraryに置き、この索引には複製しない。

YAML、Power Fx、要件、設計、テスト仕様、運用方針、進捗、変更履歴はGitHubを正本とする。Library内のMarkdownがGitHubの文書と重複する場合、そのLibraryファイルは参考・検討用・非正本として扱う。Libraryの「skills」フォルダ内のMarkdownは保管ルール文書であり、自動実行される正式なSkillまたはSKILL.mdではない。

## 資料一覧

| Library資料 | Library内パス | 区分 | 用途・関連機能 | 読む条件 | 正本の扱い |
|---|---|---|---|---|---|
| 職員マスタ_検索ダッシュボード_v0.807.html | `/非常勤給与/検索ダッシュボード/` | HTML原本 | 旧検索ダッシュボードの画面・機能参照 | 旧HTMLとの表示・機能比較、移植仕様の確認時 | Library原本 |
| 職員マスタ_検索ダッシュボード_v0.807_基本設計書.md | `/非常勤給与/検索ダッシュボード/` | 参考Markdown | 旧HTMLの基本設計参照 | GitHubの現行資料だけで旧仕様を確認できない時 | 非正本。GitHub `docs/reference/html-v0.807-basic.md` を優先 |
| 職員マスタ_検索ダッシュボード_v0.807_詳細設計書.md | `/非常勤給与/検索ダッシュボード/` | 参考Markdown | 旧HTMLの詳細設計参照 | GitHubの現行資料だけで旧仕様を確認できない時 | 非正本。GitHub `docs/reference/html-v0.807-detailed.md` を優先 |
| 採用から退職までの共済・保険タイムライン.png | `/非常勤給与/法定控除・社会保険/` | 画像資料 | 共済・保険の時系列確認 | 共済・保険区分、加入・喪失、控除時期を扱う時 | Library原本 |
| PowerApps_UI試作ルール.md | `/非常勤給与/PowerApps_UI試作/` | 旧ルール | 過去の運用経緯 | 運用変更の履歴確認時だけ | 非正本。GitHub `docs/operations/work-policy.md` を正本とする |
| 非常勤給与_ファイル格納ルール.md | `/非常勤給与/skills/` | Library保管ルール | 非常勤給与プロジェクト全体の格納先判断 | Libraryへ成果物を保存・整理する時 | Library側の管理ルール。ただし本リポジトリの正本区分はGitHub運用方針を優先 |
| T_通勤_テーブル定義書.xlsx | 添付ID `libfile_7d3a1d264cc0819195f053d0522a3a83`（フォルダ未確認） | Excel原本 | 通勤84項目・作成条件、COM-DV-001～003 | 通勤テーブルの作成・項目変更時 | 原本は添付。実装対応表はGitHub `config/dataverse/commute-columns.json` |
| 05_基準給与簿DB_v0.1 (3)_テーブル定義書.xlsx | 添付ID `libfile_83586a2630948191b1204fa937bb6cec`（フォルダ未確認） | Excel原本 | 基準給与簿163項目、PAY-DV-001～005 | 基準給与簿テーブルの作成・項目変更時 | 原本は添付。実装対応表はGitHub `config/dataverse/payrollledger-columns.json` |

| 勤務報告_給与試算_2画面_v0.1.md | `/非常勤給与/` | 参考Markdown（内容v0.3） | 勤務報告入力・給与計算過程表示の独立プロトタイプ | 過去の検討経緯確認時。開発時はGitHub正本を読む | 非正本。GitHub `docs/prototypes/attendance-payroll-prototype.md` を優先 |

| PowerApps-lightweight-v1.27-recovery-20260924.zip | `/非常勤給与/`、`libfile_01c27280e03481918efa159544b696c5` | アプリ復旧用パッケージ | 軽量版移行前の公開msapp・保存下書き・軽量版検証済み下書きとSHA256台帳 | 軽量版の復旧、保存内容の再照合時 | 非公開のバイナリ保全。仕様・ソース・判定記録の正本はGitHub。収録時点で軽量版安定アプリは未公開 |

## 更新ルール

- PowerAppsCanvasAppUIに関係するLibrary資料を追加、移動、改名、削除または役割変更した場合は、この索引を更新する。
- 現在の作業で読むLibrary資料が変わる場合は、STATUSも更新する。STATUSには実際に読むLibrary資料だけを記載し、関係しない資料は読まない。
- Library資料が不要になっても、削除判断はこの索引だけで行わず、利用箇所を確認する。


### 2026-09-29 SCR-003公開確認画像

`/非常勤給与/scr003-published-20260929.jpg`（`libfile_df82021399d081918917d417bff0f0bb`）。公開版 `2026-09-29T06:38:41.555451Z` の所有者Playerで架空明細を表示した画像。画面の外観証跡であり、取込・権限・全ケースの合格証明ではない。読取りはこの公開版の表示調査時に限定する。


## 2026-09-29 OneDrive接続診断

- `onedrive-test-connection-confirm-20260929.jpg`：専用検証アカウントのOneDrive接続作成前の確認画面。Library ID `libfile_7cbd438864a48191ac3fe146ad1d8d88`、所在 `/非常勤給与/onedrive-test-connection-confirm-20260929.jpg`。接続新設の確認時に読む。完了証跡ではない。

- `onedrive-test-account-missing-20260929.jpg`：OneDrive接続追加時の実エラー。Library ID `libfile_5b205db8d1488191bf14ee3faee063a1`、所在 `/非常勤給与/onedrive-test-account-missing-20260929.jpg`。専用ユーザーのOneDrive未検出の証跡。接続成立の証跡ではない。

- `test-user-license-assigned-20260929.jpg`：専用ユーザーへの既存ライセンス割当と23/25席空きの読戻し。Library ID `libfile_6e26e8b6e0d881919730c0fd052f2304`、所在 `/test-user-license-assigned-20260929.jpg`。OneDrive接続成立の証拠ではない。

### 2026-09-29 OneDrive初回作成中の確認画像

`/非常勤給与/onedrive-first-run-20260929.jpg`（`libfile_02fee80b9a948191bfec37e0fdf956c5`）。専用検証ユーザーが安全な認証フォームでサインインした後のOneDrive初回設定画面。設定中の証跡であり、作成完了・コネクタ接続成功を示さない。接続阻害の調査時に参照する。

### 2026-09-29 OneDrive公式プロファイル診断

`/非常勤給与/onedrive-profile-diagnosis-20260929.jpg`（`libfile_4020f1b54e6c81918f75972e459f2ed2`）。Microsoft管理センターの標準診断が対象ユーザーのプロファイル問題と個人用サイト機能フラグの修復手順を示した画像。修復完了の証跡ではない。OneDrive作成阻害の修復時に参照する。

### 2026-09-29 OneDrive修復・接続回復

- `/非常勤給与/onedrive-profile-flag-cleared-20260929.jpg`（`libfile_b64665bb26648191a7023cb2209f7d40`）：機能フラグを空欄へ保存した読戻し。後のサービス値4への更新は診断記録を参照。
- `/非常勤給与/scr003-connected-permission-block-20260929.jpg`（`libfile_65ced903580c819196255d2001246196`）：接続同意解消後の専用Player SCR-003画面。データ参照権限不足はDOM観測で記録、画像自体にエラー文は写っていない。接続・権限調査時に参照。

### 2026-09-29 専用利用者の読戻し成功

`/非常勤給与/scr003-test-reader-pass-20260929.jpg`（`libfile_7cd38c08170c8191874647b6947b5425`）。18:11公開版を専用利用者で開き、Read修復後の架空明細を表示した画像。10件の番号・値はDOMでも照合。全業務・認可の合格証跡ではない。今回の公開版読戻しの調査時に読む。


## CHANGE-20261003-COMMUTE-OFFICIAL／通勤認定簿公式様式 v1.02（業務受入完了）

確認画像：/非常勤給与/commute-uat-ready-20261004.jpg（libfile_afd6a8505d008191a316f8e9eacaf6bf）。同一公開Playerの通勤タブに旧新ボタンが共存することを示す。様式移行・受入入口確認時のみ参照。画像だけをデータ一致・印刷成功の根拠にしない。

## 2026-10-07のモデル・テーブル比較資料

| 資料 | 識別情報・所在 | 用途・読む条件 | 正本の扱い |
| --- | --- | --- | --- |
| 非常勤職員給与支給アプリ_概念データモデル図_作成中-260930.md | libfile_623069634fe08191883e48b05ece2c04（フォルダ未確認） | 現行16テーブルとアプリ式参照の比較原文。変更理由を確認する時 | 添付原文。変更後要件はGitHub |
| 非常勤職員給与支給アプリ_テーブル定義書_作成中-260930.md | libfile_a01586b6d2f48191ae6dfaef4321fc03（フォルダ未確認） | 列名・型・制約・備考の修正前を確認する時 | 添付原文。変更後定義はGitHub設計で管理 |
| 添付Markdown2文書_修正一覧_20261007.md | /非常勤給与/、libfile_2f1711582f4481919c782ce35594fc2e | 10グループ59項目の作成時点の修正指示・原文抜粋 | 参考・非正本。GitHub [変更対応](../changes/payroll-markdown-change-list-20261007.md)を優先 |

給与要件の正本は[確定要件](../requirements/payroll-confirmed-20261007.md)。画像「採用から退職までの共済・保険タイムライン」は今回の文書更新では読んでおらず、制度ルールを同画像から検証済みとは扱わない。


### 2026-10-07 通勤新様式の受入結果

2026-10-07（日本時間）、ユーザーから通勤認定簿の新様式の受入テスト完了の申告を受領し、CHANGE-20261003-COMMUTE-OFFICIALの業務受入をPASSとして記録した。対象は並行配置した公式様式v1.02（公開版 `2026-10-03T18:31:30.4607518Z`）。申告受領日を記録しており、実際の試験日時・確認レコード・項目別操作ログは未入力。個別の実機印刷設定や全データ組合せの実測証跡へ読み替えない。総合試験D-07と今後の給与モデル再構成の受入は別判定。旧様式の削除・通常ボタンの切替は今回実施しない。


## 2026-10-07 通勤切替の復元材料

- `/非常勤給与/commute-cutover-before-20261007.msapp`（libfile_c78d037cc0e0819196fe695bbe19062a）：変更前Studio保存内容。SHA256 8ec9e0ed40b1bed72d21b5d1afb72abcf19cb3bd7f6ab85ddadac0312d80d7d5。
- `/非常勤給与/commute-cutover-recovery-20261007.zip`（libfile_4897ec03b94081919392b6328ec5595d）：変更前後msapp、新旧HTML全文、入口・新様式画像。復元または今回の差分再照合時に読む。画像だけをPDF成功の根拠にしない。ソース・要件・判定の正本はGitHub。

- `/非常勤給与/commute-legacy-delete-confirm-20261007.jpg`（libfile_6ba82a8805f08191a351a001d2b53633）：旧Studio HTMLだけを選んだ環境削除の直前確認画面。削除成功の証跡ではない。

- `/非常勤給与/commute-legacy-removed-20261007.jpg`（libfile_219bac5c99f48191a4f9272aefae5878）：旧Studio HTMLの削除成功通知と残存2件の確認画像。不存在の機械読戻しはActions37566672250。
