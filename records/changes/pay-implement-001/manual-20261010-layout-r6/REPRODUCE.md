# Reproduce the r6 local review

Use the candidate repository whose source hashes are recorded beside this document. Requirements are Python3, PyYAML, and Node24 for the synthetic E2E helper scripts (using built-in TypeScript stripping). No account, application, browser, network write or private export is required for these portable tests.

From the candidate repository root, replace `<review-directory>` with this directory's relative path:

```sh
PYTHONDONTWRITEBYTECODE=1 python <review-directory>/test_independent_r6_layout.py
PYTHONDONTWRITEBYTECODE=1 python <review-directory>/test_independent_helper_review.py
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests/automation -p 'test*.py' -v
node <review-directory>/test_e2e_clipping_mock.cjs
node <review-directory>/test_e2e_root_ports_mock.cjs
```

The first two scripts locate the repository from the current working directory or their own ancestors, and write their result JSON beside themselves. The helper test creates and removes a temporary fixture directory beside the review script. It does not mutate the candidate sources. Bytecode writes are disabled in the documented commands.

The portable layout test reverses the nine proposal properties, then verifies the frozen r5 root semantic SHA. This proves the candidate's declared change scope against the reviewed baseline identity. It does not freshly read the private baseline export. The original review separately verified the full actual r5 post-test readback against that baseline.

Expected local results are11 source/model tests,8 helper guard tests,85 existing/new automation tests,13 clipping/stability mock fixtures and8 root-port mock fixtures passing. The Node scripts read and execute the actual reviewed helper functions with synthetic objects; they register12 browser test names without running those cases. Power Fx compilation, app application/save/readback, browser200%, rendered text/clipping, scroll ownership, focus, pointer and keyboard behavior are not exercised by these commands. The proposal remains pending owner approval.

For copied or archived review locations, keep the candidate repository available and run from its root. No machine-specific absolute paths are embedded in the portable scripts or reports.
