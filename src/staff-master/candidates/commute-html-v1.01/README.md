# 通勤手当認定簿 HTML版1.01

指定検証アプリの**ライブ版26へ反映済み**。実環境の帳票表示・Web API接続・Edge PDF保存は未確認のため候補扱い。既存PoCは保持。

- [設計・項目対応・試験・利用/復旧手順](docs/release-1.01.md)
- [要件と受入ID](docs/requirements.md)
- [配置証跡](docs/deployment.json)
- [単一HTML Webリソース](src/commute-ledger.html)
- [読取りJavaScript](src/report.js) / [HTMLビルダー](src/build.py)
- [追加ボタンYAML](src/btnLedgerHtmlReport.paste.yaml)（組織URLプレースホルダーは配置時に置換）
- [Studioヘッダー読戻し](qa/header-readback.yaml)（環境URLをプレースホルダー化）
- [ローカル組版結果](qa/layout-results.json)

`node --test tests/*.test.js`。ビルドは`python src/build.py`。詳細手順と未確認事項は上記記録を参照。
