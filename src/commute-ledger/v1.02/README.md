# 通勤認定簿 v1.02 並行配置版（受入待ち）

設計・残工程は[候補設計](../../../docs/changes/commute-official-design-candidate.md)。旧版に上書きせず、独立出力を作るビルダー。PythonとPyMuPDFが必要。

```sh
python src/commute-ledger/v1.02/build.py --baseline <配置済みHTML読戻し> --expected-baseline-sha256 <読戻しSHA256> --pdf <000015000.pdf> --output <独立した候補HTML>
python -m unittest discover -s tests/commute-ledger -v
```

公式PDFはsource.jsonのSHA256に固定。旧保管v1.01を入力にする場合は必ず--reference-onlyを付け、配置しない。出力隣の.build.jsonはビルド履歴であり、配置・公開成功の証跡ではない。隔離版の実体SHAを照合済み。公開Playerの新旧71欄一致・2ページPDF出力・枠超過検知はActions37158642318でPASS。業務受入は未実施。

静的描画の再現（PyMuPDF・WeasyPrint・NumPy・Node.js、日本語フォントが必要）：

```sh
python tests/commute-ledger/render_official_layout.py --pdf <000015000.pdf> --font <日本語OTF> --output tmp/commute-review
```

この描画はJavaScriptを実行しない。表示値は旧保管版の架空6レコードから生成し、空欄と合わせて7ケースを比較する。ブラウザの実印刷・実環境取得の代用にはならない。
