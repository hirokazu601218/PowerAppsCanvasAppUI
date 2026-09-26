# 実行結果と履歴（②）

`records/` は現行フローへの入力ではありません。旧版の要件・設計・テスト・移行前README/STATUS/手順、過去の公開・試験結果、旧アプリ用のActions定義やスクリプト・設定を保管します。旧ワークフローを `.github/workflows/` からここに移すと GitHub Actions としては起動されません。再稼働には対象App ID・権限・接続・復旧経路を再設計し、現在の手順で明示的に再導入してください。

| 場所 | 内容 |
|---|---|
| [`operations/migration/source-map.csv`](operations/migration/source-map.csv) | 移行前 → 移行後の全ファイル対照表。①の移設も含む |
| `docs/` | 旧仕様・公開記録・試験結果・STATUS全文・旧README索引 |
| `workflows/`, `automation/`, `config/`, `scripts/`, `tests/` | 実行停止した旧自動化の定義・補助コードと材料 |
| `changes/<change-id>/<run-id>/` | 今後の改修単位・run単位の結果。`record.json` と証跡文書を同じフォルダに格納 |

履歴に残る旧パス・旧App ID・当時の合格状態は当時の記録です。現行アプリの未実施項目を合格に読み替えないでください。実行ログに資格情報や個人データをアップロードしないでください。
