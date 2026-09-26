# 別件資料（③）

現行の自動化フローに直接関係しない資料の入口です。`docs/` は旧HTML等の参考文書、`src/` はハンドメイド版・試作品・DADSのソース、`e2e/` は別環境のハンドメイドアプリ用テストです。これらを現行 App ID の成功根拠として扱いません。

別アプリの定期E2Eを残すため、[`staff-master-e2e.yml`](../.github/workflows/staff-master-e2e.yml) の実行ファイルは `other/e2e/staff-master-p0.test.ts` を参照します。③に格納されても、この明示的な別アプリActionだけは継続して実行されます。新しい別件は `other/<project>/README.md` を付け、対象アプリと用途を明記してください。
