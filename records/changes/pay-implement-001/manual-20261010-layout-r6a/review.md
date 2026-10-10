# Independent r6a review

Result: PASS for the reviewed source clarification, local tests and complete saved-screen comparison. This is not a runtime acceptance, publication approval or independent verification of browser actions.

## Exact source scope

- Compared with frozen r6, both payroll source forms add only four explicit `AlignInContainer.SetByContainer` properties: header, targets, summary and body.
- All86 controls retain identity, type, hierarchy, order and all other property values. Paste/screen Children are equal. Compared with r5, the declared source delta now contains exactly13 properties.
- The manifest and thirteen-entry delta record the four prior Source YAML properties as absent, while separately recording official v36 DynamicProperties values as Stretch. They do not claim that Stretch and SetByContainer were equivalent defaults under the new parent Start setting.
- The new test reverses exactly the four child entries back to the frozen r6 semantic hash. The thirteen-property test still reverses the complete delta to the frozen r5 hash. No business formula change is included.

## Evidence for the limited normalization

The official v36 package independently showed25 GroupContainer1.5.0 controls with a raw root/parent alignment rule Start but omitted Source YAML property. It also showed43 GroupContainers with raw child alignment Stretch and omitted Source YAML property, and no GroupContainer SetByContainer examples. These are different findings: root Start omission is specifically evidenced; omission of child alignment is not safely normalized to SetByContainer.

The new checker permits only omission of `conscrPayrollRoot.LayoutAlignItems=Start`, requires the expected source to explicitly declare that root value and all four child SetByContainer values, and otherwise compares the entire parsed documents. Wrong/null root values, missing/changed child alignment, extra or reordered content and unrelated screen properties remain failures. It deep-copies actual input and does not mutate it.

## Independent executions

- Final automation suite:94/94 PASS, including the newly added frozen-r6 reversal test.
- Correct full-screen comparison using the helper-generated complete payroll screen: PASS, with only the one documented root Start omission and zero other differences.
- Independent expectation assembled from the official frozen v36 screen properties/metadata plus current r6a candidate Children: the same PASS. Expected screen properties were not taken from the actual readback.
- Four additional malformed-input checks rejected child null, duplicate root, an extra screen and an expected root alignment other than Start. Actual input remained unchanged after a successful comparison.

The initial review invocation incorrectly supplied the root-distribution `.pa.yaml` to the full-screen comparator. It correctly rejected the actual screen's additional Properties. The invocation was corrected to the generated complete-screen input; neither the checker nor source was weakened. Distribution root source and complete generated source are intentionally different artifacts.

Full expected SHA256: `92f657a8483bc617e20c497e1da74a1b56407ed9ec0171b7c49b35ce87868740`.

Actual saved-screen SHA256: `07fea705cc9caa9bd807e955e7f9f22559c944b6b2735182bcd7f902a407d07f`.

## Limits

The implementation record reports owner approval of A and browser confirmation of root Start, four inherited child settings and Checker0. This reviewer performed local, read-only assessment only. Native200%, rendered geometry/text, pointer/Tab/focus, mode restoration, saved-version identity and eventual Player validation must retain their own evidence and gates. No app, frozen-r6 source, external repository or candidate source was modified by this reviewer.
