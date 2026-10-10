# Reproduce independent r5 review checks

These scripts are archived review evidence. They do not modify Power Apps, GitHub, Dataverse, or browser state. Their results must not be described as actual Player or 200% zoom validation.

## Prerequisites

- Python 3 with PyYAML, as used by the repository's existing Python checks.
- Node.js with `node:module.stripTypeScriptTypes`; the recorded run used Node 24.19.0. No Playwright package, browser, or network access is needed for the helper mock.
- The candidate repository and the frozen r4 checkout at `422256dbe14cbbcf8cde1b6334f7924a7483c5cc`.
- The captured r4 payroll UI readback file for the complete source/readback-equality test. It is local evidence, not included in this archive. Do not manufacture it from the candidate or mark that evidence check passed when the input is unavailable.

## Commands

From the candidate repository root, set the following to actual local input locations. The scripts discover the repository from their ancestors by default, so copying this folder deeper under records does not break path resolution.

```sh
export PAY_REVIEW_ROOT="$PWD"
export PAY_REVIEW_BASELINE_ROOT="$FROZEN_R4_CHECKOUT"
export PAY_REVIEW_READBACK="$CAPTURED_R4_PAYROLL_READBACK"
export PAY_REVIEW_OUTPUT="$REVIEW_RESULT_DIR"
RECORD=records/changes/pay-implement-001/manual-20261010-layout-r5
PYTHONDONTWRITEBYTECODE=1 python "$RECORD/test_independent_layout_review.py"
node "$RECORD/test_e2e_helpers_mock.cjs"
```

The Python check requires both baseline and readback inputs and fails closed if either path variable is omitted. It writes its result JSON into PAY_REVIEW_OUTPUT (default: the script's own folder). The helper mock does not need the readback and can run independently. PAY_REVIEW_E2E_SOURCE can explicitly select a reviewed TypeScript file instead of the default repository path.

## Interpretation

- Python: 8 source/model tests, including actual r4 readback equality and exact one-property candidate difference.
- JavaScript: 13 synthetic helper cases; 11 E2E tests registered from the parsed source. Its viewport assertion is stubbed deliberately, isolating the explicit clipping calculations. The real Playwright viewport assertion has not been executed here.
- Neither script is an official Power Fx compiler, complete TypeScript typecheck, accessibility assessment, Player run, or actual browser 200% zoom test.
- Verify candidate identities against reviewed-source-test-hashes.json before reusing these reports. A changed candidate requires a new review/run; an old PASS must not be copied forward automatically.
