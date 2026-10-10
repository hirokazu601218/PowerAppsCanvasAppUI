# Independent r5 minimal payroll layout review

Result: PASS for the one-property local candidate, subject to Studio compilation, exact readback, and Player layout verification. No application, repository remote, data, or business-rule writes were performed during this review. Only this `review/` directory was written.

## Review scope and evidence

- Frozen source: `src/screen-ui/v1.31/payroll-root.pa.yaml`.
- Actual applied-r4 UI readback: `captured r4 payroll UI readback supplied through PAY_REVIEW_READBACK (local evidence, not tracked)`. Its complete screen Children equal the frozen source Children.
- Candidate: `src/screen-ui/v1.31/payroll-root.pa.yaml` and matching paste file.
- Latest task information overrides STATUS's older statement that Wave1 has not yet been applied. The review does not infer draft/publication state from STATUS.
- Exact semantic change across all 86 named controls: only `conPayDeductions.Height`. No control, parent, order, count, visibility, action, amount, basis, or business-calculation change.
- Both padding properties and all 11 child heights occur once in the new expression. Ten sibling gaps are included as `10*Self.LayoutGap`.
- The existing `If(Coalesce(varUiDeductionsOpen,true), ..., 0)` guard is preserved. The rows depend on parent width, not parent height, so the new dependency creates no height cycle.

## Independent height calculation

The deduction container has two 44px section headings, one 48px social total, eight rows, and ten 8px gaps. Current top/bottom padding is zero, consistent with the observed content heights.

- Wide rows: `2*44 + 48 + 8*64 + 10*8 = 728`.
- Narrow rows: `2*44 + 48 + 8*128 + 10*8 = 1240`.
- The old constants 698 and 1210 are each 30px short when branch selection agrees.
- At the observed 900px preview, the body width is 787.5 logical px, deductions 735.5, and rows 711.5. The old parent formula chooses 698 while its row children choose 128, requiring 1240: 542px is clipped. DOM client dimensions round these values to 788/736/712.

## Why the selected fix is the minimum reliable repair

1. Adding 30px to the two old constants fixes the ordinary wide/narrow cases but leaves 512px missing in the nested breakpoint-mismatch interval. Reject.
2. Using `Self.Width<750` and new constants can resolve the present branch mismatch, but duplicates row policy and hard-codes heights and gaps. Future padding or child height adjustments can break it again. It is less robust than direct aggregation.
3. Adding a deduction scrollbar exposes some clipped content but introduces a nested scroll interaction instead of allowing the existing body to own navigation. It also does not correct the intrinsic height. Reject for this scope.
4. The selected child-height sum plus actual padding and gap is a one-property repair. It delegates responsive row choices to the existing row formulas and gives the body the correct full extent.

`conPayEarnings` is deliberately unchanged. Its existing formula includes its eight child heights and seven gaps, totaling 540px at current values. The fact that it declares Scroll does not itself prove an actual second scrolling region. No speculative cleanup is included.

## Width boundary derivation

`UiOuterWidth=56/64` is verified in the official v36 App source. Existing runtime measurements give a 12px body scrollbar gutter. Let B be logical body width and S be actual scrollbar width:

- Deductions width = B - 40 body padding - S.
- Row width = deductions width - 24 deduction padding.
- The old deduction aggregate switches at B=750.
- Row Height switches at B=790+S. With S=12 this is B=802.
- The innermost name-width formula switches at B=814+S. With S=12 this is B=826.
- At a 12px gutter, the corresponding viewport boundaries are 857.142857, 916.571429, and 944px. Fractional values are deliberate; clientWidth rounding must not replace logical formula values at the boundary.
- The selected expression has no separate width predicate, eliminating the first mismatch. The existing innermost name-width predicate is preserved and requires actual runtime leaf-bound checks where relevant.

Static test coverage checks values immediately below, exactly on, and immediately above all three boundaries with scrollbar widths 0, 12, and 17. Scrollbar width is a model input, not a promised browser invariant.

## Requested viewport and zoom-width cases

With the observed 12px gutter:

- 900px at 100%: body787.5, deductions735.5, aggregate1240.
- 1366px at 100%: body1195.25, deductions1143.25, aggregate728.
- 1920px at 100%: body1680, deductions1628, aggregate728.
- 900px at 200% effective-width model: effective450, body393.75, deductions341.75, aggregate1240.
- 1366px at 200% effective-width model: effective683, body597.625, deductions545.625, aggregate1240.
- 1920px at 200% effective-width model: effective960, body840, deductions788, aggregate728.

These zoom cases model the CSS viewport being halved. They are not measurements of browser zoom, Studio preview scaling, or Player min-screen behavior. The actual runtime must establish the effective width.

## Validation result

`python test_independent_layout_review.py` with the required evidence environment variables: 8/8 PASS. The script verifies:

- Exact one-property difference and unchanged tree/control metadata.
- Actual-r4 readback identity and r5 paste/pa parity.
- Every direct child exactly once, no circular height dependency.
- Requested viewport/zoom-width matrix with 0/12/17px scrollbar assumptions.
- Every breakpoint edge described above.
- Independent reproduction of both known old defects.
- Padding, gap, and each individual child-height perturbation.
- Fixed summary sibling placement and unchanged body/earnings scroll properties.

Artifacts: `independent-review-test.log`, `independent-review-results.json`, and the rerunnable test script. These are source/model checks, not an official Power Fx compiler, accessibility assessment, or Player acceptance.

## Remaining runtime gates

- Studio Checker accepts the expression without introducing errors.
- Save/readback equals the reviewed formula and changes no other property.
- At900/1366/1920, open and collapsed deductions, scroll to the final deduction and verify all label/basis/amount bounds are reachable and unclipped.
- Confirm summary geometry remains fixed while only the actual body scrolling region moves.
- At narrow/200% conditions, inspect row leaves for wrapping, internal clipping, or loss of usable basis text; the aggregate expression alone cannot prove leaf readability.
- Verify the actual 200% effective viewport and repeat the bottom-of-content checks. Preview scaling alone is not browser 200% verification.

## Microsoft primary-source basis

Microsoft describes gap as the distance between children, the distinction between Hide/Scroll overflow, and the role of fill portions: [Vertical container control](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/control-vertical-container). Those semantics support adding child heights, sibling gaps, and container padding while keeping FillPortions 0.

Microsoft documents hierarchical Parent references and formula-driven dimensions: [Create responsive layouts](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/create-responsive-layout). This supports treating each nested Parent.Width as a different width rather than assuming one shared 750px decision.

Microsoft explains responsive auto-layout containers and recommends testing resize behavior in preview; it also documents interactions involving Wrap, alignment, and overflow: [Building responsive canvas apps](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/build-responsive-apps). Therefore the model does not substitute for final row-bound inspection in the target runtime.
