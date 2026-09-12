# Work / Codex共通ルール

着手時はREADME、docs/handoff/STATUS.md、要件・基本設計・詳細設計・デザイン基準・受入基準を読む。チャット記憶だけを仕様根拠にしない。

## 優先順位

最新ユーザー指示 → docs/requirements/ → docs/design/ → 現行ソース → docs/reference/。矛盾はSTATUSに記録する。画像で省略した業務項目を削除しない。

## 役割

- Work：要件・設計・変更要求・レビュー。
- Codex：YAML/Power Fxの開発・試験・証跡・PR。
- ユーザー：業務判断・受入・マージ指示。接続不可時のStudio実機操作。

## 実装

UI成果物はSource Code形式YAMLとPower Fx。HTML/React代替アプリは作らない。画像等のイメージ提示は明示依頼時のみ。
利用可能なモダンコントロールを優先し、機能・互換性上の例外を記録。B案に未対応のv1.08を起点とし、次はv1.09、以降v1.10、v1.11とする。
通常利用者にはpaste.yamlだけ案内。pa.yamlの画面Childrenとpaste.yamlは一致させる。
Classic/Button@2.2.0にAccessibleLabelを入れない。PDFViewerをGroupContainerの子にしない。GroupContainer@1.5.0を現行環境の起点として検証する。
表示をOnVisible/OnStart/タイマーだけの初期化に依存させない。検索0件時に旧職員の詳細や帳票を残さない。

## 検証と引継ぎ

ブランチで変更、要件ID・差分・テストコマンド・結果・未実施をPRへ記載。設計変更はWorkへ理由を返す。
ローカル検査はStudio試験ではない。実機が使えなければ未実施と明記する。スクリーンショットだけで検索/PDFを合格にしない。
新成果物の参照更新後、同一画面の旧版を削除し変更履歴へ記載。別アプリや無関係の変更を削除しない。
実データ、資格情報、環境固有URLを追加しない。試作は架空データ。
