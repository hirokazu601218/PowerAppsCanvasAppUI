# 現行アプリの変更要求

修正・機能追加の指示は、実装前に`<変更ID>.json`として記録する。ファイル名は小文字の変更ID（例：`CHANGE-123` → `change-123.json`）。[試験選定記録](../../testing/change-records/README.md)と同じ変更ID、固定環境ID・App IDを使用し、元の指示、該当要件ID、受入条件を明示する。秘密情報や実在の職員データは記載しない。

ソース変更PRでは`docs/changes/requests/<変更ID>.json`と`docs/testing/change-records/<変更ID>.json`を一緒に追加・更新する。Actionsが両者のIDと対象を照合する。業務判断が未決なら勝手に確定せず[未決事項一覧](../../requirements/open-decisions.md)へ記録し、確定範囲だけで改修する。

[記入例](../../testing/templates/current-app-change-request.example.json)。実行指示後の工程は[現行アプリの変更要求から公開・文書反映まで](../../operations/current-app-request-to-release.md)を参照する。
