# PAY-HTML-001 非常勤給与レビューHTML

入口は [`index.html`](index.html)。ローカルへ取得後、そのファイルをブラウザーで開く。外部配信・インストール・ネットワーク接続は不要。GitHubのHTMLソース表示はクリック式プレビューではない。

**非正本・レビュー用（未承認）。Markdown要件・設計は正本のまま。** 現行実装の観測、確定改修要件、提案、未決を分離する。Power Apps・Dataverse・Power Automate・公開版を変更せず、実際の給与計算・保存・取込・振込を実行しない。架空の職員と固定値のみを使う。

- 版：0.2-review（PAY-HTML-002 接続図改訂） / 2026-10-09
- 元main：`252abe4aa5d3b1d99a584a30c97d9b48153c91f5`
- 読取り優先：2026-10-07確定要件、2026-10-08人給I1～I12。D9以降の式は保留
- 適用対象：6現行画面、承認された将来画面／業務、外部境界。正式ID未定は仮識別子
- HTMLのレイアウト・模擬操作はPower Appsの実現方式や業務受入の合格ではない

## 構成

```
index.html                    入口・版・状態・出典
navigation.html               ① 全体画面遷移図＋同一データの表
workflows/index.html          ② 業務フロー索引
workflows/<業務ID>.html       業務ごとの図・分岐・例外・工程表
operations/index.html         ③ 画面／業務／役割／状態の操作索引
operations/<画面ID>.html      操作単位の詳細契約と受入観点
wireframes/index.html         ④ クリック式ワイヤー索引
wireframes/<画面ID>.html      PC構成例・静的状態定義・項目台帳
coverage.html                 全画面／業務と4資料の対応
design-notes.html            実装・未決・設計注記（業務画面外）
assets/review.css             共通B案トークン・文書用応答配置
assets/review.js              任意の操作補助。ネットワークなし
data/model.json              4資料共通のレビュー用構造データ
```

## IDと状態

画面はSCR-001～006を維持。FUT-JLINK、FUT-IMPORT、SCR-007、EXT-*はレビュー上の仮識別・外部境界であり、正式画面名・実装の新設を承認するものではない。

操作IDは`OP-<対象>-<動詞>`、遷移IDは`TR-*`、業務IDは`WF-*`、工程IDは業務内の固定ID。HTMLでは`id`、`data-screen-id`、`data-operation-id`、`data-requirement-id`を使う。見出し文言変更でIDを変えない。新しい操作は新しいIDを追加し、既存IDを別目的に再利用しない。

区分は「現行実装」「確定改修要件」「提案」「未決」。現行画面に将来操作が載る場合は操作の区分を優先する。モック全体の作成状態は未承認。未決をHTMLの便利な動作で確定済みにしない。

## 更新・再生成

1. 変更されたMarkdown正本の要件・優先順位・未決を確認する。
2. `scripts/review/build_payroll_model.py` の共通レビュー定義と参照箇所を更新し、`data/model.json`を生成する。HTMLを直接修正しない。
3. 項目・画面構成は `scripts/review/payroll_wireframes.py`、ページ・表は `scripts/review/generate_payroll_review.py`、接続図の表示定義と決定的な配置は `scripts/review/payroll_flow_diagrams.py`、操作補助は共通CSS/JSを更新する。
4. 以下を実行し、生成済みHTML・データ・スクリプトを同じPRへ含める。

```sh
python3 scripts/review/build_payroll_model.py
python3 scripts/review/generate_payroll_review.py
python3 scripts/review/generate_payroll_review.py --check
python3 scripts/review/validate_payroll_review.py
python3 -m unittest discover -s tests/review -v
python3 -m unittest discover -s tests/governance -v
node --check docs/review/pay-html-001/assets/review.js
python3 scripts/governance/validate_document_placement.py --base 252abe4aa5d3b1d99a584a30c97d9b48153c91f5
```

配置検査はコミット済み差分を読むため、未コミット段階ではPythonの`validate(repo, changes)`へ実際の変更パスを渡して検査する。コミット後にCLIを再実行する。

## 表示・検証の境界

文書本文、図の代替表、操作の詳細、項目定義はJavaScript・ネットワークなしでHTMLソースに存在する。JavaScriptを無効にすると全タブを表示し、フィルター・モーダル・模擬状態変更・図の拡大縮小は動かない。SVGは共通データの工程・辺から図と表を生成する。業務図は各工程を一度だけ置き、責任範囲のレーンと連結した分岐・合流・復路で示す。開始・終了・合流は操作とは別の表示要素。BPMN風レビュー表記であり、BPMN 2.0準拠の実行定義ではない。Canvas・画像だけの仕様は使わない。

文書はモバイル対応。接続図はPCの幅に収め、狭い画面では図の枠内だけをスクロールする。「全体を見る」「幅に合わせる」「100%」「±」を切り替えられる。PCワイヤーは900px以上の内部幅を保ち、狭い画面では枠内スクロールする。これはモバイルアプリの完成形ではない。操作の一時状態は架空データのみを同一タブのsessionStorageへ保存し、初期化で削除する。ローカルファイルの状態共有が制限されるブラウザーではURLパラメーターによる引継ぎも使う。実データを入力しない。

検証結果・スクリーンショットは `records/changes/pay-html-001/` 以下へ結果として分離する。モックのブラウザーテストをPower Apps・業務認可・制度計算・実データ処理・性能・総合試験D-07の合格へ転用しない。

## PRの検査

`Payroll review static validation`はHTML生成一致、ID・相対リンク・出典、6タブ／3タブ、I決定の追跡とJavaScript構文を確認する読み取り中心の検査。アプリ接続・公開・外部APIは実行しない。ブラウザーの見た目・操作とPower Apps実機検証をこのチェックで合格にしない。検査をmainの必須チェックに設定する権限変更は本作業では行わない。

配布ZIPは次のコマンドで、レビューHTML・生成コード・引用した既存正本のみを含めて作成できる。履歴・隠しディレクトリ・Office原本・実データは含めない。

```sh
python3 scripts/review/package_payroll_review.py --output /tmp/PAY-HTML-001-review.zip
```

ZIP内のSTART.htmlから開く。ZIP自体はGitHubへコミットしない。

## PAY-HTML-002 接続図改訂

- 15業務図を、一工程一ノードの縦方向主線・役割別レーン・条件付き分岐・合流・訂正／再試行ループへ改訂した。
- 方向別画面経路は起点ごとの1:Nへ改訂した。同じ行先への複数操作は、行先を重複させず個別の操作リンクとして保持する。
- アプリ内移動、認定簿の別タブ起動、利用者によるタブ復帰、人給との手動システム切替／ファイル受渡し、方式未決の情報受渡しを区別する。
- WF-15にPAY-02／AD-10で確定している通常の新期間適用の確認区間を補完した（h、e→h）。新しい承認状態や操作は追加していない。それ以外の元工程・経路・操作ID・区分は維持する。
- WF-02の並行する後続関係、WF-04の行別分類・正常行先行取込を排他的な分岐へ変えない。
- 今回の結果は `records/changes/pay-html-002/` に分離する。過去の検証結果は書き換えない。
