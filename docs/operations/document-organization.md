# ドキュメントの配置・GitHub投稿規則

対象：現行 App ID `204a48dc-7f23-43dd-b934-4654a3cfa306` と、それとは独立した履歴・別件。配置対照表は [`source-map.csv`](../../records/operations/migration/source-map.csv)、機械判定の正本は [`document-routing.json`](../../config/document-routing.json)。

| 区分 | 配置 | 作成・アップロードの判断 |
|---|---|---|
| ① 自動化に必要 | `docs/` と現行コード・Actions・設定 | 変更要求、要件定義、基本／詳細設計、単体・結合・総合の計画と仕様、受入、未決、現行作業・確認入力。フロー開始前に参照するもの |
| ② 自動化の結果・過去の入力 | `records/` | run結果、公開後の観測、失敗・停止理由、過去の版と旧フロー定義。過去には①だったが現在不要な資料もここ |
| ③ 無関係の別件 | `other/` | ハンドメイド版や試作品、DADS参考設計。別アプリActionは専用ファイルへの参照を持つ |

新しい改修では、依頼文と要件ID・受入条件を `docs/changes/requests/<change-id>.json`、テスト選定を `docs/testing/change-records/<change-id>.json` に同じPRで保存します。要件、設計、テスト・受入、未決事項は対応する既存文書に反映します。実行後の結果は `records/changes/<change-id>/<run-id>/` に保存し、`record.json` に `change_id`、`run_id`、`app_id`、`status`（PASS/FAIL/BLOCKED/NOT_RUN/PARTIAL）、`observed_at`、`source_commit`、`version` を記載します。失敗も記録し、成功へ置換しません。公開後のチェックが読む `docs/verification/postpublish/<change-id>.json` は入力・照合用の①であり、詳細な証跡や実測結果は②に置きます。秘密情報・実利用者データはアップロードしません。

Codexや他の作成者がGitHubへ上げる際は、対象App IDと利用目的を確認し、該当区分に置き、関連する相対リンクを直し、移動は同じPRで `source-map.csv` に追記します。新しい①の文書種別は `config/document-routing.json` に同じPRで登録し、追加理由を説明します。新しい③は `other/<project>/README.md` で対象・用途を明記します。②の新規run結果は上記メタデータで検査し、別形式の歴史的移行は対照表が必要です。自動生成フローも同じパスとメタデータを使ってPRを作成し、実行ログだけを①へ自動コミットしないでください。

GitHub Actions の `Document placement validation` はPRと`main`へのpushで配置・メタデータを検査します。チェック成功だけではブロックできないため、運用開始時はリポジトリ設定で `main` のPR必須チェックとしてこの名前を登録します。設定前、または管理者による直接pushでは予防できないため、設定済みと確認できるまで「強制済み」と報告しません。`records/workflows/` はGitHub Actionsとして実行されません。旧フローを現行App IDへ読み替えて復活させないでください。

検証例：`python3 -m unittest discover -s tests/governance -v`、`python3 scripts/governance/validate_document_placement.py --base <mainのSHA>`。PRでは変更した相対リンク、対象ID、動作対象の3本のワークフローも確認します。
