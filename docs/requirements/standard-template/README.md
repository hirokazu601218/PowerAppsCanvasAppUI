# 非常勤給与 要件定義レビュー・ポータル

依頼 **DOT-002 / PAY-REQ-HTML-REWORK-001**。状態は **確認待ち・非正本・未公開**。

[入口](index.html)から業務、画面、標準の章立て、要件ID、要件未設定へ進みます。既存Markdownを正本として保持します。今回の変更は閲覧・追跡の改善です。給与計算、制度判断、アプリ、Dataverse、Power Automate、公開版、権限を変更していません。

## 読む目的

- 業務利用者: [業務の流れ](journeys.html) → [画面一覧](screens/index.html)。どこから始め、何を入力・確認し、何をもって完了するかを読みます。
- 設計・構築者: [標準の章立て](chapters.html) → [要件ID・操作](requirements/index.html)。担当、対象範囲、前提、データの参照・変更、失敗・取消、根拠を追跡します。
- 判断する人: [要件未設定](open-items.html)。記載の不足を実装・試験の状態と分けて確認します。

関連資料は通常のHTMLページで開きます。冒頭の戻りリンクで参照元の要件・画面へ戻れます。元要件IDは安全なローカル識別子としてURLに渡します。JavaScriptなしでも、通常リンクと静的な参照元一覧を利用できます。iframe閲覧枠は使いません。

## 閲覧方法と検証の限界

### PCの通常ブラウザー

配布フォルダーを展開し、`index.html`をChrome・Edge・Safari等で開きます。フォルダー構造を保持してください。外部CDNや本文の動的取得は不要です。環境のローカルファイル制限がある場合は、PC内のHTTPサーバーを使います。GitHubのblob画面はHTMLソースの表示です。

本文・リンクは静的HTMLです。JavaScriptは検索、絞込み、図の拡大・縮小、参照元の戻り先補助に使用します。図は拡大後に縦横スクロールできる構成です。下段には同じ工程・全経路を文字でも表示します。

### iPhone

Safariで閲覧可能なURLを開く方式を主な閲覧先とします。今回Web配置、Sites登録、公開、権限変更は実施していません。URL提供には公開先と閲覧範囲の承認が別途必要です。PCのlocalhostをiPhone用URLとは案内しません。

「ファイル」のQuick Lookは通常ブラウザーではありません。別HTML移動、同一ページのアンカー、JavaScript、検索、図の操作は保証しません。[単独ファイルの要約](index-mobile.html)は、上から読むだけの補助資料です。従来の62資料連結版を廃止し、全体像・役割・確定境界・主な未設定事項に絞りました。全要件・全操作を読める代替版ではありません。

### 今回の実施・未実施

- 実施: 生成一致、全相対リンク・アンカー・ID、原本階層、内容保持、出典行対応、JavaScriptのロジック単体試験。
- 未実施: Chromiumでの実表示・クリック・狭幅描画、実機iPhone・Safari・Quick Look。環境ではブラウザーからローカルHTTPへ到達できず、許可された転送経路もありませんでした。
- 静的検査・DOMの代用オブジェクトによる単体試験は、実ブラウザーの操作試験やアクセシビリティ適合の証拠にはしません。
- HTML画面例は架空データです。Power Appsの保存・業務認可・性能・業務受入を確認した意味ではありません。

詳細な手順は[閲覧方法](reading-guide.html)と検証記録を参照してください。

## 標準テンプレートの構造

公式DS-120第5章Wordの表紙版は **2026-06-12**、ZIP掲載更新は **2026-07-15**。両日を区別します。

- 従来の140項目: 3章、31節、106小項目。既存IDと意味を保持。
- 原本の別スタイルのアウトライン: 上位見出し8件を補完。実効上位3階層は **148見出し**。
- 下位見出し・条文例: 第4階層173段落を保持。全実効アウトライン **321段落**。
- 表56件（Word表49、画像内表7）、図11件の目的、記入要領132件を別枠で参照。
- 3.14は原本(1)「移行に関する前提条件」、原本(2)「移行計画の作成」。旧資料ID `3.14.1`は後者の意味を維持し、表示に原本番号`3.14.2`を併記します。新しい前提条件は`template-sections/3.14.1.html`です。
- `index.html#section-*`の旧アンカーも同じ意味で残します。

[原本階層と既存IDの対応](template-details.html)と`template-detail-map.json`に根拠と対応を記載しています。原本の例文・数値・契約条項を本アプリの要件へ自動採用しません。補完した8見出しは別枠で評価し、7項目に正本の部分条件を記載、1項目（オープンデータ化）は要件未設定です。

本文対象109項目の現在の記載充足は10記載済み・51一部設定・48要件未設定です。旧版の10・38・61から、全61旧未設定項目を正本と再照合し、直接の根拠がある13項目を一部設定へ直しました。保存対象と保存期間、採用方式と本番構成、取込失敗制約と復旧目標を分けて記載しています。補助見出し・記入例を足して充足率を水増ししていません。実装率・検証率でもありません。

## 出典と状態

受領ZIPの作成時点の履歴：PR #136 `38362c8cf7ded201b1d185eeaccf2892f40c5f51`、元main `252abe4aa5d3b1d99a584a30c97d9b48153c91f5`。現在は末尾のDOT-002 Work統合版を使用します。

2026-10-07給与確定要件と2026-10-08人給決定を優先。D9以降の式・端数・符号等は保留を維持します。

記載充足、要件判断、実装、実機検証を別に表示します。I12の確定を、関連する個別確定操作の未決へ読み替えません。I8は表示要件確定と取得方式未設定を併記します。操作・配置の提案を業務要件そのものの提案へ読み替えません。

Work統合版ではDOT-001の承認A・Live38引継ぎ観測と、後続run 38049776822で採取済みの正式P/Hを選択反映して再生成しました。採取runは旧v25 guard FAIL。選定自動E2E・最終照合は未実施。受領時点の生成HTMLで正本や最新観測を上書きしません。

## ファイル構成

- `requirements-data.json`: 従来140項目の本文・未設定条件。原本から維持。
- `section-supplements.json`: 旧HTMLで未設定扱いだった13節と補完見出し7件の確定事項、残る未設定、正確な出典行、補足理由。
- `template-detail-map.json`: 原本全構造・コメント・図表・番号対応。案件要件とは別。
- `portal-data.json`: 章・要件ID・操作・画面・業務・出典行の生成済み対応表。
- `sections/`: 既存IDを維持した要件本文。
- `template-sections/`: 補完した8見出し。7項目に正本の部分条件を記載、1項目は要件未設定。
- `requirements/`, `operations/`, `screens/`, `workflows/`: 粒度別の静的本文。
- `sources/`: 正本のHTMLビュー。STATUSだけは指定した4節の選択抜粋で、その範囲を明記。他の対象資料は全文。
- `assets/`: 読みやすく整形したCSS・JavaScript、出典図1件。CDNなし。
- `index-mobile.html`: 独立した読み物用要約。操作機能なし。
- `../../review/pay-html-001/`: 既存の詳細図・画面モック。生成器で要件側への戻りリンクと要件IDリンクを付加。業務モデルは不変。

## 再生成と検証

Node.js、`marked` 17.0.5、Python 3、`lxml`を使用します。現在環境は`CODEX_PRIMARY_RUNTIME_NODE_MODULES`からmarkedを解決しています。他環境では同じNode環境でmarkedを解決可能にしてください。生成後HTMLの閲覧にNodeやPythonは不要です。

リポジトリのルートで実行:

```text
python scripts/review/generate_payroll_review.py
node scripts/review/generate_requirements_html.mjs
python scripts/review/generate_payroll_review.py --check
node scripts/review/generate_requirements_html.mjs --check
python scripts/review/package_requirements_mobile.py --check
python scripts/review/validate_requirements_portal.py
node --test scripts/review/requirements_portal/test_portal_logic.mjs
python scripts/review/validate_payroll_review.py
python scripts/governance/validate_document_placement.py --base <比較元コミット> --head HEAD
```

先に旧レビュー生成器を実行するのは、接続図を同じモデルから再生成してからポータルに取り込むためです。`build_payroll_model.py`は入力モデル自体を変更するため、通常の表示再生成には不要です。

出典が更新されたら、本文・出典SHA・要件の状態・未決を見直し、基準コミットとアプリ観測の時点を明示して再生成します。HTMLの生成一致だけで新しい仕様を確定してはいけません。補足20項目の出典行が引用と一致しない場合は生成器が停止します。最新正本と補足本文を再照合し、行番号だけを機械的に合わせないでください。

## 構成確認用PDF

`records/changes/pay-req-html-rework-001/manual-20261010-portal/requirements-structure-preview.pdf`は、HTML本文・生成データから作成した4ページの構成確認用PDFです。Web画面の見た目の再現、ブラウザー操作の証拠、全要件の代替ではありません。

必要な場合の再作成には、PythonのPyMuPDF・fontToolsと日本語Noto Sans CJKフォントを使います。表示生成の必須依存ではありません。`python scripts/review/create_requirements_preview.py --help`で出力先を確認してください。PDFの再作成後は全ページを画像化し、日本語・改ページ・欠けを目視確認してください。

## 利用条件

出典: デジタル庁「DS-120 第5章 要件定義書標準テンプレート」（2026/06/12、2026/07/15掲載更新）をもとに、この確認資料用に構造を抽出・再整理。デジタル庁が作成した案件要件ではありません。構造抽出・再整理はdot（DOT-002）。

[公共データ利用規約 第1.0版](https://www.digital.go.jp/resources/open_data/public_data_license_v1.0)、[著作権・利用条件](https://www.digital.go.jp/copyright-policy)を参照。原本Word、第三者図版、ロゴは再配布しません。

## DOT-001 更新（採取前の履歴）

正本文書出典：`6064ca820553511e1d52b19f896a063213eb88c8`。10月10日承認A・引継ぎ公開38観測を反映。元main・既存PRのSHAは作成時点の履歴。生成HTML・出典ハッシュを再生成し、正式P/H未取得・focus／AX制限を維持する。アプリ・業務仕様の新規確定・全要件合格を意味しない。

## DOT-002 Work初回統合版（採取前の履歴）

統合文書出典：`b5e5d460fe19169252de05bb02bafc9461120540`。PR #137の文書差分だけを選択統合して再生成。承認A・Live38引継ぎ観測を含み、正式P/H・選定自動E2E・最終照合は未完了。旧DOT-002 ZIPの静的結果は受領時点の証拠として保持し、今回の結果は`records/changes/dot-002/manual-20261010-integration/`を参照。実ブラウザー・iPhone検証待ち。

## DOT-002 追加・正式公開情報の選択反映（現在状態）

最新の統合文書出典：`4928decc67fdc6baa0f3f83300eca2c3760669cf`。正式P `2026-10-10T09:28:28.7479961Z`、独立PAC H `7877bb8d4729f687b94dcaf3e3ade0e33849218a7a1454e7852a9cfe4568dd3f`を採取済み。run 38049776822全体は旧v25画面SHA guard不一致でFAIL。選定E2E・最終照合はNOT_RUN、実ブラウザー・375/390幅・iPhone確認もNOT_RUN。過去の未取得は上記履歴として保持。

分割ポータル、短いモバイル要約、source_commit対応生成器、SCR005-UI-004／015と承認A本文を保持。追加検証記録：`records/changes/dot-002/manual-20261010-publication-refresh/QA-REPORT.md`。
