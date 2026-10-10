# Helper and static-test independent review

Result: PASS for the local helper change and reviewed static tests. This does not approve or apply the UI proposal. Runtime Power Fx, native browser zoom, text fit, scrolling and keyboard/focus validation remain NOT_RUN.

## Helper change

The only helper change from the frozen r5 implementation is four lines inside the before-state validation pass. For a manifest entry with `before_absent:true`, the named property must not be present in its owner's Properties mapping. A present key with null, empty text, false, zero, Hide or Scroll is rejected. The helper validates all entries and the whole payroll root before making a deep copy or changing candidate properties.

Independently removing those four lines reproduces the original helper SHA:

`852a0763ca6d38e5f4cb9842c1c1151feb416dc88e2bb61270e8c0172ca7a2f1`.

The actual manifest uses this flag only for the payroll root's previously undefined LayoutOverflowX and LayoutOverflowY properties. The flag values are literal JSON true. Existing-property hash/equality checks, exact ten-file source set and content hashes, whole payroll-root semantic hash, duplicate-control checks, allowed property scope and report-destination preservation remain unchanged.

The helper is an offline generator. Its successful output does not save, import or publish an app, and does not establish user approval for this proposal.

## Independent guard coverage

The portable `test_independent_helper_review.py` passes8/8 groups:

1. Exact four-line-only source delta.
2. Exactly the two declared absent overflow properties.
3. Both axes reject six explicit values each and leave input untouched.
4. Truly absent properties succeed, produce the exact candidate root, and preserve input.
5. Unrelated root drift remains rejected.
6. Formula drift and duplicate controls remain rejected.
7. The ten-file guard accepts the exact fixture and rejects an extra file, a missing file and changed file content.
8. Existing report destination is preserved and unapproved output property changes are rejected.

One initial reviewer fixture assumed absent entries always included a `before:null` field. The manifest correctly omits it. The fixture was corrected to accept either omitted or null `before`; the helper and candidate source were unchanged. The final portable test passes.

## Existing and new layout tests

The r5 fixed-layout assertions were updated only where the r6 proposal introduces conditional behavior. They continue to require the original ordinary-mode body Height branch, summary sibling structure, no deduction scrollbar, and the correct inverse root/body scroll ownership. They do not call the exception approved or claim runtime success.

The new r6 suite includes an explicit proposal-not-approved assertion, exact nine-property reversal to the frozen r5 root hash, unchanged controls/tree, 750px/128px source contracts, deterministic boundary modes, visible-child/gap arithmetic and ordinary-mode restoration geometry.

During review, the wide-name arithmetic model used a proportional `.42` branch rather than the actual source's fixed260px branch. The implementation author corrected it to `row_width*.4 if row_width<750 else260` and added exact guards for all eight name Width formulas. The original estimate was conservative but not faithful; the corrected20-case suite was rerun successfully.

Independent reruns:

- New r6 suite:20/20 PASS.
- Full automation directory:85/85 PASS.
- Portable independent source/model review:11/11 PASS.
- Portable independent helper guards:8/8 PASS.

The locally generated payroll root from the official v36 input was separately compared with the complete r6 candidate and matched. That private input is not part of this portable review package. Source/model checks are not Microsoft compilation or app testing.

Final E2E source/helper review is recorded in `e2e-source-review.md`:13 clipping/stability and8 root-port synthetic fixtures passed. This does not execute the12 registered browser cases.
