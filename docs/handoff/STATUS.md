# 現在の作業と読取り対象

## 2026-10-10 PAY-IMPLEMENT-001 確定済み未反映機能の実装・試験・同一試験アプリ公開

- 最新依頼：要件定義・設計済みの未反映部分をアプリへ実装し、テスト・公開・文書反映・再照合まで行う。下記10月8日の文書のみ依頼より本依頼を優先する。
- 対象：StaffMaster-Automation-Test、既存App ID `204a48dc-7f23-43dd-b934-4654a3cfa306` と隔離架空データのみ。同試験アプリの公開は今回依頼に含む。本番・元テーブル・旧App ID・権限変更・main統合・未決業務判断は含めない。
- 読取り対象：PAY-IMPLEMENT-001変更要求／試験選定、src/screen-ui/v1.31、画面要件のSCR002-LT-002/005/007・UI-004/010・COMMON-NAV-003・SCR005-ACT-005/006/008・UI-004/015、詳細設計10.6/10.8/11章、対応する未決一覧と公開後手順。
- 第1波：検索確定条件・結果・選択・ページの往復保持、区分別履歴保持、控除根拠の失効、サマリー固定。取得失敗時の詳細消去と成功時刻／エラー区別も維持する。計算式・業務制度・接続先は変更しない。
- 現在の証拠：未編集ドラフト36の公開・公式Exportを確認。msapp SHA `f3af186814e138f60fe8e2848ccecdafd7db4af6d1454a852be815ca5e33266c`。全10 Src YAMLは監査済みv35と同一で、v36から再生成した2画面もr4と同一。名前付き部品・接続・列定義に意味差分はなく、内部ID再採番と集計／時刻等のメタデータ差だけと確認。v35監査記録は履歴として保持し、最新証跡はrecords/changes/pay-implement-001/manual-20261010-v36-baseline/へ追加した。第1波の修正適用・公開・変更後Playerは未実施。
- 関連試験：state-retention.test.tsの9単体／結合ケース、既定回帰。将来操作59件・明示要件240件・決定136件の準備状況をrecords/changes/pay-implement-001/manual-20261010-readiness/へ記録。総合D-07は未決のまま。
- 次の候補：選択認定GUID＋職員番号による既存通勤保存先の再照合。第1波と分けて変更前値・書込対象・読戻し・完全復元を検証する。未検証の保存式を第1波と一括公開しない。
- Issue #51はopenの元M_職員基本への列追加残件。元テーブルは今回範囲外なので完了扱いにしない。追加する際は対象承認・正式列型／精度・独立期待値・実列読戻しを先に確認する。


## 2026-10-08 人給連携モック・I1～I12の文書反映

- 最新依頼：承認モックとI1～I12をGitHubの画面要件・設計へ反映。文書のみでアプリ・Dataverse・公開版は変更しない。
- 確定：同一画面3タブ、対象・A/M指定、Excel出力前確認、最新版データ照合、変更通知、差分6列と表示切替、差分対応明細の再出力、取込成否の手入力なし、確定ダイアログなし。I1～I3はモック承認を根拠とする。
- 読取り対象：画面要件のJLINK節→決定台帳I1～I12→人給連携詳細設計7章→未決事項の最新残件→試験仕様JLINK-T01～08。
- 残件：I8エラー情報取得方式、給与簿照合キー・出力行対応、最新結果の識別と同時更新の物理方式、正式画面ID、Excel生成方式・配布先・性能。D9以降の計算式は保留を維持する。
- 文書整合・配置を検証する。IF-T・JLINK-Tの業務試験は未実施。過去の受入結果・Issue #51・総合試験D-07の判定は維持する。

## 2026-10-08 人給Excel出力・給与簿CSV照合の文書反映

- 最新依頼：確定内容をGitHubへ反映。計算式精査は後回し。従来の通勤作業とは異なるため本依頼を優先する。通勤の最新受入・撤去完了は下記履歴を維持。
- 出力xlsx237列・11キー・文字列形式・職員判断A/M・空欄0化を確定。給与簿戻りはCSV。D1～D8確定、D9～D12未回答・保留。
- 読取り対象：[出力仕様](../design/detailed/payroll-jinkyu-interface.md)→[決定台帳](../requirements/payroll-interface-decisions-20261008.md)→給与確定要件・未決PD-02/03→基本／データ／詳細設計の人給節→試験仕様のIF-T項目。
- 今回は文書のみ。関連テスト：動作変更は対象外。リンク・用語・文書配置のみ検証。アプリ・Dataverse・Power Automate・公開版・既存受入結果は変更しない。IF-T全件未実施。
- 次：生成方式・操作・給与簿照合キーと行対応・エラー受渡方式の詳細化。式精査再開はD9から。複数過去月集約と対象日、賞与・法改正の割当ては未入力。Issue #51、総合試験D-07は未完了。
- Library資料は参考・非正本。利用制限のある実取込ExcelをGitHubへ追加せず、個別値を転記しない。


## 2026-10-07 12:49 JST 通勤切替後の業務受入PASS

- 2026-10-07 12:49 JST、ユーザーから「受入テスト終了。okです。進めてください」と申告を受領。CHANGE-20261007-COMMUTE-CUTOVERの切替・旧様式撤去後の業務受入をPASSとして記録する。対象はApp ID `204a48dc-7f23-43dd-b934-4654a3cfa306`、公開版 `2026-10-07T01:17:13.7960236Z`、通常「認定簿表示」から開く新様式v1.02。旧公開版の受入記録とは別の今回の申告である。
- 申告受領日時を記録した。実際の試験日時・確認レコード・項目別操作ログ・個別の印刷設定は未提供。ユーザーの総合的な受入PASSを、未提供の操作ログや全データ組合せ・総合試験D-07の実測合格へ読み替えない。
- 読取り対象：docs/acceptance/user-acceptance.mdの当受入節、records/changes/change-20261007-commute-cutover/manual-20261007-acceptance/。今回は受入申告の文書記録のみ。アプリ・HTML・公開版は変更しない。関連テスト：文書配置・記述整合。

## 2026-10-07 通勤新様式への通常入口切替・旧リソース撤去・main統合完了

- 最新依頼を優先し、下記給与文書更新から通勤切替へ作業対象を変更。初回開始10:02 JST。削除承認後の再開12:17 JST、今回期限13:17 JST。
- 対象は既存App ID `204a48dc-7f23-43dd-b934-4654a3cfa306` のみ。公開版 `2026-10-07T01:17:13.7960236Z`。通常入口切替と試験ボタン撤去は保存・公開済み。
- 読取り対象：CHANGE-20261007-COMMUTE-CUTOVER要求／選定JSON、src/commute-ledger/v1.03、今回の公開後JSON、要件・基本／詳細設計・試験仕様の当変更節、records/changes/change-20261007-commute-cutover/。旧受入PASSは2026-10-03公開版に対する履歴として保持。
- 復元材料：Library資料索引のcommute-cutover-before-20261007.msappとcommute-cutover-recovery-20261007.zip。必要時だけ参照。無関係な保険画像は読まない。
- 保存前後全Source YAMLを比較し、OnVisibleのURL置換と試験ボタン削除以外の差分0。通常ボタン全プロパティと新旧HTMLの受入時SHA一致。公開Playerで単一入口・別タブ・架空009900000004／TK-910003・71欄・16,800円・枠超過0を確認。
- Actions37556764035：公開版読戻し、正常状態、ボタン式、旧参照なし、新HTML SHA、別commute-ledger.html保持PASS。旧Studioリソースは削除前なので存在を照合（削除完了PASSではない）。
- 2026-10-07 12:22頃 JST、操作時承認後に旧Studio HTML1件を環境から削除。削除後読戻しActions37566672250 PASS：旧リソース不存在、新HTML SHA不変、通常ボタン全プロパティ一致、別リソース保持。公開Player別タブ・71欄・2ページ・TK-910003を再確認。
- 最終Actions37567285581：公開版／パッケージSHA／文書差分／選定6ケース／統合ゲートPASS。37567285358旧リソース不存在・新HTML SHA・ボタン照合PASS、37567285395通常E2EとPDF保存PASS、37567285369文書配置PASS。PDFはA4横841.92×594.96pt・2ページ、両ページ描画確認PASS。
- PR #130をmainへ統合済み（39a59d23f306b3d98d18ad1aaa3dae29c2d363b5）。今回の7工程は完了。完了詳細はrecords/changes/change-20261007-commute-cutover/manual-20261007-cutover/。
- 修復前結果も保持：37557608249は試験6件PASSだがPDF保存先エラーで全体FAIL、reporter保存処理修正後に成功。クラウドOS印刷ダイアログは未確認、Chromiumの印刷PDFは今回新規に検証。全組合せ・総合試験D-07を今回合格と扱わない。
- 下記の過去STATUSにある「今回は切替しない」は当時の記録。現時点の実施状況は本節を優先する。

## 2026-10-07 給与要件確定・GitHub文書反映

- 最新依頼：公開掲載の承認を受領し、作成済みの給与要件文書と通勤新様式の受入完了をGitHubへ反映する。
- [確定要件](../requirements/payroll-confirmed-20261007.md)：Q1～Q60・R1～R21、PAYREQ-01～10。人給CSV往復・差分ゼロ確定、支払済不訂正、最終計算根拠・照合履歴保持、勤怠取込更新方式、局別権限、分割返納、業務／システム管理分離を反映。
- [添付２文書の変更対応](../changes/payroll-markdown-change-list-20261007.md)：10グループ59項目。原文の位置・修正前後・理由・会話根拠を保持。不明な理由・物理名・式は未入力。
- 今回は文書のみ。要件・業務・画面・非機能・基本／詳細設計・データモデル・対応表・未決一覧・資料索引を整合。新しい文書種別の現行入力登録はconfig/document-routing.json。
- 関連テスト：動作変更は対象外。リンク・記述整合と文書配置を確認する。アプリ・Dataverse・フロー・機械可読列契約・公開版・既存の実測結果を変更しない。新業務の実装・業務受入・性能試験は未実施。
- 残件：[PD-01～09](../requirements/open-decisions.md)。人給CSV仕様・現行Excel等の資料確認、物理設計・ローコード復旧・性能・権限・保存期間が必要。Issue #51、総合試験D-07は未完了。通勤新様式v1.02の業務受入は下記のユーザー申告でPASS。
- 通勤受入：2026-10-07（日本時間）、ユーザーから通勤認定簿の新様式の受入テスト完了の申告を受領し、CHANGE-20261003-COMMUTE-OFFICIALの業務受入をPASSとして記録した。対象は並行配置した公式様式v1.02（公開版 `2026-10-03T18:31:30.4607518Z`）。申告受領日を記録しており、実際の試験日時・確認レコード・項目別操作ログは未入力。個別の実機印刷設定や全データ組合せの実測証跡へ読み替えない。総合試験D-07と今後の給与モデル再構成の受入は別判定。旧様式の削除・通常ボタンの切替は今回実施しない。
- 読取り対象：確定要件→対象グループの変更対応→業務／画面／非機能→基本／データ／詳細設計→未決一覧。Libraryの添付2原文・修正一覧は必要時の参考で、正本はGitHub。無関係な保険画像を読み直す必要はない。


## 2026-10-04 通勤新様式の並行配置・受入準備完了

- 同一アプリ公開版 2026-10-03T18:31:30.4607518Z。旧Webリソースと通常ボタンを維持し、新様式試験ボタンを追加。新旧ボタン以外の全画面YAML差分0。
- 公開Player変更範囲E2E4件PASS（37158642318）：71欄一致、別タブ、各2ページPDF、枠超過印刷停止。PAC読戻し・新旧ボタン全プロパティ・Webリソース両SHA照合PASS（37159201219）。
- 要件・基本／詳細設計・結合仕様・受入手順に確定反映。最終Actions37159537696は公開版・文書差分・選定6ケース・最終ゲートすべてPASS。PR #127をmainへ統合済み（dcf621a17df5c8d7b5dde43856727fcf52f0b49b）。受入を開始できる状態。旧版への通常経路切替なし。
- 受入入口：いつものPlayer→職員マスタ検索→架空009900000004→通勤→「新様式（受入テスト）」。当時は業務受入・実機印刷設定・総合試験が未実施。後続2026-10-07のユーザー申告で通勤新様式の業務受入はPASS（上記参照）。
- 読取り対象：docs/verification/postpublish/change-20261003-commute-official.json、docs/acceptance/user-acceptance.md、src/commute-ledger/v1.02、当変更の選定JSONとrecords/changes/change-20261003-commute-official/manual-20261004-deployment/。確認画像はLibrary資料索引。

## 2026-10-03 通勤認定簿の公式様式・並行配置候補（認証待ち）

- ユーザー指示：受入前まで実装・試験を進める。受入合格までは現行様式と通常ボタンを残す。開始23:28 JST、期限00:28 JST。
- [候補設計](../changes/commute-official-design-candidate.md)、src/commute-ledger/v1.02、[ローカル記録](../../records/changes/change-20261003-commute-official/manual-20261003-local-candidate/result.md)。新様式2ページ、71表示欄、既存script保持。単体3件・旧処理10件PASS、空欄＋架空6件の静的描画済。
- 現行隔離版HTML・Launch式は未読戻し。Power Apps所有者のMicrosoftパスキー認証でBLOCKED。新リソース・試験ボタンは未配置、既存アプリは未変更。受入準備完了ではない。
- 再開：認証完了→現行実体と版・SHA取得→取得した隔離版をベースに生成→UT/IT選定JSONと実画面ケース・ゲート対象パス追加→並行配置・同一アプリ試験ボタン公開→読戻し・新旧表示/印刷・回帰検証→設計確定と受入案内。旧v1.01をそのまま配置しない。通常ボタンの切替と旧版削除は行わない。

## 2026-10-01 SCR001～003 UI変更・公開後照合・main統合完了

- CHANGE-20261001-SCR001-003-UI。現行同一App IDへ09:26:01 JST公開。公開時刻 `2026-10-01T00:26:01.1961006Z`、パッケージSHA `2f0b2447f3744157fa538d095830990157602f5e1fc596396266b4f5d9c78ff5`。
- 最終Action [36797346142](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36797346142)は公開メタデータ・パッケージSHA・要件／設計／結合仕様差分・選定単体／結合E2E・最終ゲートすべてPASS。最新PRチェックE2E36797350878、文書照合36797351099、文書配置36797350890もPASS。
- [PR #124](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/pull/124)を2026-10-01 11:05 JSTにmainへmerge。マージコミット `1e0b2b39df99542970ed057494fa65a040256a0e`。今回の要求・実装・試験・公開・文書反映・統合の6工程は完了。
- 初回E2E7件PASS／3件FAILは履歴。起動待ち、破棄確認ボタン名、描画CSS要素、Confirm後のARIA名消失に対するテスト修正後、最終E2E成功。アプリソースと公開版は維持。
- 所有者Studioで架空10件の備考保存・再表示・空欄への完全復元、公開Playerで3画面・モード切替・未保存変更破棄を確認。
- 業務受入：2026-10-01 11:55 JST、ユーザーが今回のSCR001～003 UI変更について「受け入れテスト完了。okです。」と申告、PASS。項目別操作ログは未提供。総合試験D-07、実データ運用、業務認可、999件境界、同時更新・途中障害は別判定。
- 読取り対象：新たな変更指示があるまで、要求・v1.30・[公開後記録](../verification/postpublish/change-20261001-scr001-003-ui.json)・選定ケース・最終Actions結果。完了詳細は[実施記録](../../records/changes/change-20261001-scr001-003-ui/manual-20261001-completion/completion.md)。
- 統合後E2E [36804181953](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36804181953)は初回9件PASS／1件起動待ち時間超過、attempt 2で成功。完了記録PR #125もmainへ統合済み。
- 受入記録と3文書の最終結果更新：[受入記録](../../records/changes/change-20261001-scr001-003-ui/manual-20261001-acceptance/acceptance.md)。今回の文書記録作業は11:55 JST開始、12:55 JST期限。関連テスト：動作変更なしにつき対象外。リンク・記述整合と文書配置を確認。

## 2026-09-29 20:30 JST 専用ユーザーのRead修復・公開Player読戻しPASS

- 開始20:25 JST、期限21:25 JST。ユーザーが検証環境3表へのRead追加を明示承認。
- Action 36561770802 PASS：専用ユーザーだけの既存Readerロールへ3表Readのみを追加。実効Read、他権限不変、Create/Write/Deleteなしを確認。別環境・共有ロール・チーム付与・既存書込権限を拒否するローカル5ケースもPASS。
- 同一18:11公開版を専用Playerで再読込み、OneDrive警告なし、局×月の一覧と架空10件、勤務期間、12桁番号、0、33.167、備考を確認。公開後記録のPlayer判定を対象範囲に限りPASSへ更新。
- 要件・基本・詳細設計へ試験用Readの範囲を追記。業務認可は後工程。所有者フロー経由の更新経路をReadロールだけで制限済みとは扱わない。
- テストDOM診断で月・局名と状態が同一要素に含まれる完全一致の不具合を修復（53cb534）。Power Fx・公開版・期待値は不変。最終照合をmarker attempt 3で起動。公開版・パッケージSHA・718プロパティ・文書差分・選定4ケースを実環境で再照合し、最新HEADのチェック合格後にPR #122を統合する。下記の過去BLOCKEDは修復前の履歴。
- 証跡：`records/changes/change-20260929-scr003-attendance-import/manual-20260929-read-repair/record.json`。未実施：999件、同時更新・障害、業務認可、業務受入、総合試験。一時Excelロック残件も維持。


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
