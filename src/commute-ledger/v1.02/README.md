# 通勤認定簿 v1.02 並行配置版（業務受入完了）

設計・残工程は[候補設計](../../../docs/changes/commute-official-design-candidate.md)。旧版に上書きせず、独立出力を作るビルダー。PythonとPyMuPDFが必要。

```sh
python src/commute-ledger/v1.02/build.py --baseline <配置済みHTML読戻し> --expected-baseline-sha256 <読戻しSHA256> --pdf <000015000.pdf> --output <独立した候補HTML>
python -m unittest discover -s tests/commute-ledger -v
```

公式PDFはsource.jsonのSHA256に固定。旧保管v1.01を入力にする場合は必ず--reference-onlyを付け、配置しない。出力隣の.build.jsonはビルド履歴であり、配置・公開成功の証跡ではない。隔離版の実体SHAを照合済み。公開Playerの新旧71欄一致・2ページPDF出力・枠超過検知はActions37158642318でPASS。業務受入は2026-10-07のユーザー申告によりPASS。

静的描画の再現（PyMuPDF・WeasyPrint・NumPy・Node.js、日本語フォントが必要）：

```sh
python tests/commute-ledger/render_official_layout.py --pdf <000015000.pdf> --font <日本語OTF> --output tmp/commute-review
```

この描画はJavaScriptを実行しない。表示値は旧保管版の架空6レコードから生成し、空欄と合わせて7ケースを比較する。ブラウザの実印刷・実環境取得の代用にはならない。


### 2026-10-07 通勤新様式の受入結果

2026-10-07（日本時間）、ユーザーから通勤認定簿の新様式の受入テスト完了の申告を受領し、CHANGE-20261003-COMMUTE-OFFICIALの業務受入をPASSとして記録した。対象は並行配置した公式様式v1.02（公開版 `2026-10-03T18:31:30.4607518Z`）。申告受領日を記録しており、実際の試験日時・確認レコード・項目別操作ログは未入力。個別の実機印刷設定や全データ組合せの実測証跡へ読み替えない。総合試験D-07と今後の給与モデル再構成の受入は別判定。旧様式の削除・通常ボタンの切替は今回実施しない。
