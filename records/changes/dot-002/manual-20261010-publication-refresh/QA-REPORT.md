# DOT-002 追加：DOT-001正式公開情報の選択反映

状態：静的検証PASS、実動検証待ち（PARTIAL）。既存docs/requirements-html-20261010／Draft PR #136へ反映。baseはdocs/pay-html-001-review-20261009を維持。

## 確認した入力と取得結果

- 着手時PR136 head：c6d1c7edb2999a08c96d29343dfd9f4385cecd5b。
- 着手時PR137 head：a05450bc479a666cc73e8b265fbd7b3189d71d27。両PRのAGENTS・STATUS・台帳と文書差分、採取記録を確認。
- 現行正本の出典：4928decc67fdc6baa0f3f83300eca2c3760669cf（必要文書／採取記録の選択保存）。モデルとsource_commit対応生成器はこの版を参照。
- [採取run 38049776822](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/38049776822)：workflow head 949a0b5、readback_only=true。今回手動起動していない。
- 正式公開日時 P：2026-10-10T09:28:28.7479961Z。
- 独立PACアプリ本体SHA-256 H：7877bb8d4729f687b94dcaf3e3ade0e33849218a7a1454e7852a9cfe4568dd3f。
- 最終下書き：2026-10-10T09:27:24Z。metadata Ready・固定App・前後一致、下書き<=Pの既存採取根拠を確認。
- P/H採取成功とrun/job全体のFAILは別。旧v25画面SHA guard不一致でFAIL。GitHub APIでもfailure、後続文書照合・選定E2E・最終ゲートのskippedを確認。

採取QA／record.json／readback-summary.jpgの3点をPR137と全バイト一致で保持。根拠画像のP/H・FAIL表示を確認し、資格情報や生バックアップを追加していない。採取QA末尾の旧62資料HTML検査はPR137側の当時の履歴であり、現在のPR136の構成ではない。

## 差分反映と保全

要件・基本／詳細設計・試験仕様・台帳・STATUSの現在状態を「P/H採取済み、旧guard FAIL、選定E2E・最終照合未実施」へ更新。採取前の未取得状態は履歴と明記し、過去DOT-001 QAの全本文を保持して再開後注記だけを追記。過去DOT-002検証記録・旧保全比較manifestは変更していない。

モデル／生成器／HTMLをPR137から一括コピーしていない。既存モデルの変更は出典・公開情報とSCR-005の状態注記だけ。操作契約100件・画面12件・業務15件・要件ID139件の構造、SCR005-UI-004／015参照、承認A本文を維持。ポータルCSS／JS・短い要約の包装スクリプトは変更0。

P/H・FAILの値は表示入力／モデル／ポータルで一致を検証。採取recordの全ファイルSHA不一致は生成器が拒否する。アプリ公開情報とHTML Web未公開を別フィールドで保持。

補足20項目の本文・未決・状態と全53引用の文字列は前版と同一。最新正本で行位置を検索し、全参照ファイルSHA・出典commitを再計算。旧行番号を別commitへ付け替えるだけにしていない。canonical-preservation-baseline.jsonは更新済み160入力を生成前に固定した比較基準。

## 検証結果

| 検査 | 結果 |
|---|---|
| ポータル静的検査 | PASS_STATIC：31検査、492 HTML、15,855相対参照。リンク・画像・ID・出典・操作契約・A本文・公開状態 |
| 原本構造 | PASS：148上位見出し・173下位項目、旧140 ID＋追加8、56表・11図の目的・132記入要領 |
| 補足引用 | PASS：20項目・53引用、本文／未決／状態不変、行・引用・全ファイルSHA一致 |
| 正本保全 | PASS：選択更新後の160入力。旧DOT-002記録は不変、旧DOT-001 QAは原文prefixを保持 |
| 生成一致 | PASS：46レビューHTML、452ポータル出力、27,699バイトの短い要約、モデルの生成一致 |
| 模擬JS | PASS：11件。検索・解除・戻り先・図拡大等。実ブラウザーではない |
| 負例ガード | PASS：引用変更／引用不変の参照ファイル変更／採取record変更を隔離環境で拒否 |
| 配置・範囲 | PASS：全変更パスを配置検査。追加画像は要件assets内の当jpgだけを許可 |

static-validation.json、supplement-audit.json、test-results.json、placement-validation.jsonを参照。画像根拠確認は実ブラウザーのHTML表示試験には読み替えない。

## 残件・NOT_RUN

選定22pathの実比較証拠・正式postpublish JSON・選定自動E2E・最終照合は未完了。取得値と二画面の引継ぎ観測だけで全選定pathのMATCHや業務受入PASSを宣言しない。focus見切れ・履歴AX差、Issue #51・D-07・制度式・実効認可も継続。

実ブラウザー表示・開く／戻る・履歴・検索解除・図拡大・キーボード・JavaScript無効時、375/390幅、iPhone/Safari/Quick LookはNOT_RUN。ブラウザー実行ファイルがない（browser-environment.json）。短い要約はFilesプレビューの対話機能を保証しない。統合版PDF再作成・業務受入もNOT_RUN。

アプリ・src・workflow・期待SHA設定・資格情報・権限の変更、Actions手動起動、main統合、Web公開は行わない。次は別途実動検証環境で同じ版を確認する。
