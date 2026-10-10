# Independent r6 E2E source and helper review

Result: PASS for the reviewed source and synthetic helper checks, subject to the unapproved UI contract and all remaining real-runtime gates. No browser was launched and no app was modified. The file registers12 named state-retention/layout cases; registration and helper execution are not live case passes.

Reviewed E2E SHA256:

`19aa1f2a076dbe9a0d76dee44538be9f88da1d6653f425ae794da287eb858287`.

## Meaningful test scope

- Existing ordinary1366/900/1920 cases retain fixed summary and body-scroll checks. Last-row field and rendered-text clipping checks are preserved and now also check iframe viewport bounds.
- The REFLOW candidate explicitly tests root panning at450/683 CSS widths, restores normal geometry after each, and checks fixed mode at960. SHORT adds590×378 and1366×320 CSS-size cases. These are pending-proposal expectations, not a claim that the prior always-fixed narrow-screen requirement passes unchanged.
- Each fallback checks all24 deduction name/basis/amount controls for September mock values and November registered-zero values. Both the control rectangle and rendered text rectangles must be unclipped. Individual fields may be reached at different horizontal positions, as explicitly stated in the proposed panning contract.
- All five buttons, month selection, selected staff label and three summary values are checked for pointer reachability. Only the three display actions and month selection are exercised in the fallback helper; there is no new save/export/data-write click.
- Collapse/expand must shrink and restore scroll extent, then expose every deduction again. Returning to normal dimensions must pass without explicitly resetting root offsets; both axes must clamp and the summary remain fixed during body scrolling.
- Native browser100→200→100 and real Tab/focus behavior are explicitly annotated NOT_RUN and remain separate mandatory acceptance gates. Pointer checks do not count as keyboard testing.

The mock deduction expectations were independently compared with the official v36 source fixture. September gross is `9750*20 - 1250*60/60 + 6250 = 200000`, deduction total48200 and net151800. These are existing synthetic UI values, not a validation of payroll policy.

## Scroll and coordinate safety

`rootPorts` selects only user-scrollable auto/scroll wrappers owned by the payroll root and containing all four immediate control subtrees. It supports separateX/Y wrappers and prefers the wrapper with actual range. It cannot silently choose a deduction or body descendant owned by another control.

Fallback movement uses mouse wheel input. It searches an exposed root-owned pointer target without wheeling through an active nested scroll region, confirms the main-page pointer hits the Player iframe, verifies the requested root axis moved, and rejects changed offsets for all nonselected root descendants and iframe-document ancestors. It also checks the outer window did not scroll. There is no hidden-ancestor offset assignment, scrollIntoView, synthetic focus, locator-hover autoscroll or style mutation in fallback navigation.

The pre-existing ordinary-mode helper assigns scrollTop only to an actual auto/scroll body-owned element. This remains explicitly separate from the root fallback's wheel-only path.

`portGeometry` combines frame-local client bounds and clipping ancestors with the locator's main-page bounding box. Frame translation is applied once. An outer iframe CSS scale is unsupported and now rejected by comparing main/frame rectangle dimensions, rather than silently directing input at incorrect coordinates. Native browser zoom remains a different gate.

Two source issues were corrected during review:

1. The wide-short case originally required horizontal range≤1. That contradicted the known scrollbar-gutter pan of the nine-property proposal. The final source permits an actual incidental range and, when present, requires both extremes and return to the left edge to be user-reachable. Narrow cases still require a genuine horizontal range.
2. Pointer-only checks could have been mistaken for keyboard coverage. Both candidate cases now explicitly mark mandatory Tab/focus acceptance NOT_RUN. No keyboard pass is claimed.

## Synthetic checks of the actual helper functions

The scripts use Node's built-in TypeScript stripping and execute the unchanged helper function bodies against synthetic DOM/locator objects. They do not install packages or invoke Playwright. Fake viewport assertions are not reported as browser success; the real helper's explicit clipping and routing assertions are what the fixtures isolate.

`test_e2e_clipping_mock.cjs`:13 fixtures PASS.

- Old wide/narrow clipping is rejected at scales1 and0.681.
- Correct intrinsic heights pass those model cases.
- Internal horizontal text clipping, vertical text clipping and absent rendered text are rejected.
- Geometry changes must settle for two repeated snapshots; missing required geometry is rejected.

`test_e2e_root_ports_mock.cjs`:8 fixtures PASS.

- Combined and split rootX/Y wrappers both translate iframe offsets137×83 correctly and route synthetic wheel deltas to the selected root ports.
- Both wrapper forms reach an offscreen field without moving hidden descendants.
- HiddenY scrolling, unexpected nested hidden-scroll movement, internal text overflow and unsupported outer iframe CSS scale are all rejected.

These fixtures are deliberately smaller than Power Apps. Actual DOM topology, hit testing, wheel timing, flyout behavior, focus, text rendering and host scrolling must still be verified in the authorized target app. Node syntax stripping is not TypeScript semantic type checking and not Microsoft Power Fx compilation.
