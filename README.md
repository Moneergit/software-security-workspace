# Private Dataset Workspace

A small Python Software Security Assignment I project. Three independent FastAPI processes protect private synthetic datasets and CSV results. Ali and John are ordinary users; Admin can inspect metadata but cannot read their rows. No optional malicious-package experiments are included.

Start with `START_HERE.md` for a guided Windows walkthrough. This file is the exact build/run/test reference. The final application is fixed; four deliberately vulnerable implementations remain at the `vulnerable-lab` Git tag.

## Requirements

Install CPython **3.12 x64** and Git. Bundled wheels support **Windows x64** and **Linux x86_64 glibc**. The verified execution environment was Linux with CPython 3.12.14; Windows wheels are included but Windows execution was not available here. On Mac, use a Linux x86_64 VM or provide platform wheels through a reviewed dependency update. Do not install this project into your global Python environment.

## Windows PowerShell

Open PowerShell inside the extracted `secure-workspace` directory, where this README lives. Activation is unnecessary.

```powershell
py -3.12 -m venv .venv
py -3.12 scripts/check_artifacts.py
.\.venv\Scripts\python.exe -m pip install --no-index --find-links vendor --require-hashes -r bootstrap.lock
.\.venv\Scripts\python.exe -m pip install --no-index --find-links vendor --require-hashes -r requirements.lock
.\.venv\Scripts\python.exe scripts/check_environment.py
.\.venv\Scripts\python.exe scripts/run.py seed
.\.venv\Scripts\python.exe scripts/run.py serve
```

Open http://127.0.0.1:8000/docs. All three services run as separate processes on ports 8000, 8001 and 8002. Keep this terminal open. Ctrl+C stops the group. In a second terminal, from the same project directory:

```powershell
.\.venv\Scripts\python.exe scripts/run.py demo
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/ci.py
```

## Linux

```bash
python3.12 -m venv .venv
python3.12 scripts/check_artifacts.py
.venv/bin/python -m pip install --no-index --find-links vendor --require-hashes -r bootstrap.lock
.venv/bin/python -m pip install --no-index --find-links vendor --require-hashes -r requirements.lock
.venv/bin/python scripts/check_environment.py
.venv/bin/python scripts/run.py seed
.venv/bin/python scripts/run.py serve
```

Second terminal:

```bash
.venv/bin/python scripts/run.py demo
.venv/bin/python -m pytest -q
.venv/bin/python scripts/ci.py
```

`smoke` instead of `serve` starts a temporary cluster on free ports, demonstrates it, and stops it. `pytest` also creates fresh independent processes on free ports, so an existing demonstration server does not affect test data. No tests touch `.runtime`.

## Seeded demonstration accounts

| Username | Password | Role |
|---|---|---|
| ali | ali-demo-password | user |
| john | john-demo-password | user |
| admin | admin-demo-password | admin |

Passwords are public synthetic teaching credentials. Only salted scrypt digests are written to `.runtime/accounts.json`. Dataset 1 belongs to Ali; dataset 2 belongs to John. Seeding preserves existing data. To reset, stop the server and remove only this project's `.runtime` directory, then seed again. Restart generates new signing keys and invalidates existing sessions.

## API demonstration

1. POST `/login` with `{"username":"ali","password":"ali-demo-password"}`.
2. Copy the returned `access_token`. Swagger exposes an `authorization` header field for each protected route. Enter `Bearer YOUR_TOKEN` there. The PowerShell example below handles headers automatically.
3. GET `/datasets` lists only Ali's metadata. GET `/datasets/1` succeeds. GET `/datasets/2` returns 404.
4. POST `/datasets` with `{"title":"Trial","values":[4,8,12]}` creates an owned dataset.
5. POST `/datasets/1/export` executes API → Processor → Resource → installed helper → Resource. GET `/results/1` returns `{"csv":"value\n10\n20\n30\n"}`.
6. POST `/datasets/2/export` returns 404. GET `/admin/metadata` returns 403 for Ali.
7. Login as Admin: GET `/admin/metadata` succeeds, but GET `/datasets/1` still returns 404.

PowerShell requests are an easier alternative to copying headers in Swagger:

```powershell
$loginBody = @{username='ali'; password='ali-demo-password'} | ConvertTo-Json
$session = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/login -ContentType application/json -Body $loginBody
$authHeaders = @{Authorization="Bearer $($session.access_token)"}
Invoke-RestMethod -Uri http://127.0.0.1:8000/datasets -Headers $authHeaders
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/datasets/1/export -Headers $authHeaders
Invoke-RestMethod -Uri http://127.0.0.1:8000/results/1 -Headers $authHeaders
```

## Build and dependency policy

`requirements.lock` declares runtime, build and test dependencies, including `workspace-csv==1.0.0`. `vendor/` contains approved wheels; `dependencies.sha256.json` checks exact names and bytes. The helper is installed as a dependency rather than copied into a service. It is deliberately small and has no third-party dependencies.

```powershell
.\.venv\Scripts\python.exe -m build --wheel --no-isolation --outdir reports/helper-wheel helper
```

This rebuild is validation, not automatic approval of new bytes. Source must match the approved helper wheel. Wheels contain build metadata and are not claimed bit-for-bit reproducible after rebuilding; installation of the approved artifact is reproducible. To intentionally update dependencies, use a separate review branch, obtain compatible wheels, review source/version/advisories, regenerate the manifest and lock, and rerun gates. Never regenerate the approval manifest automatically during a build that consumes supplier input.

## Tests and release gates

`python scripts/ci.py` runs exact artifact and installed inventory checks, compilation, a helper wheel build, Ruff lint/format, Bandit, pip-audit, all HTTP/gate tests and a smoke demonstration. Any nonzero stage blocks release. All public advisories block, regardless of severity. Advisory lookup requires internet; lookup failure blocks rather than silently passing. The local helper is not in PyPI, so its known audit skip is handled by source inspection, Bandit and artifact verification. Unexpected skipped public packages block.

Results go into `reports/`; `evidence/` holds the actual supplied snapshot. Negative regression tests expected to fail on the vulnerable tag are evidence of exploitable flaws. A passing final suite means these concrete scenarios were rejected, not proof of universal security.

## Jenkins on each push and pull request

The provided Jenkinsfile is a **Multibranch Pipeline** definition. A file alone cannot configure a Jenkins server or GitHub webhook.

1. Use a disposable Linux agent labeled `python312-linux`, with Python 3.12 and Git. Install Pipeline, Git, GitHub Branch Source, JUnit and Credentials plugins in Jenkins. Isolate untrusted PR execution from production secrets and deployment hosts.
2. Create a Multibranch Pipeline, add GitHub as Branch Source, choose your repository and credentials. Enable branch discovery and pull request discovery from the origin. Enable fork PR discovery only with an appropriate trust policy. Ensure branch discovery is configured to include the intended branches.
3. Set the build configuration to the root `Jenkinsfile`. Configure GitHub webhook delivery to `https://YOUR-JENKINS/github-webhook/` for push and pull-request events, with webhook validation configured at the server.
4. Save and scan. Push a commit, then open a pull request; verify both branch and PR builds are scheduled. Retain the URLs and screenshots/logs of these **actual** runs.
5. Enable repository branch protection requiring the Jenkins status after confirming its exact reported status name. A failed gate must stop merge/release. Repository settings and Jenkins credentials are configured in your account, not embedded here.
6. The job removes its workspace, installs only approved wheels, starts temporary services, and archives analysis/test logs, JUnit and gate results. There is no production deploy stage in this assignment.

These setup steps are a configuration checklist; hosted webhook/PR execution was not performed in this environment. Exact Jenkins UI labels depend on installed plugin versions.

## Preserve history and push to GitHub

The ZIP includes the full `.git` directory. Do **not** run `git init` again and do not upload only files through the website: that loses the plan-before-code history. Create an empty repository on GitHub with no initial README or license, then:

```bash
git status
git log --oneline --all --decorate
git remote add origin https://github.com/YOUR-USERNAME/software-security-assignment.git
git push -u origin main
git push origin --tags
```

If Git asks for credentials, use GitHub's supported browser/token authentication. Your normal password is not a Git access token. If a remote already exists, inspect `git remote -v` and set the intended URL with `git remote set-url origin ...`. Do not force push. For future edits, set your own author identity, then `git add`, `git commit` and `git push`. Initial generated commits use an explicit placeholder author, not your identity.

For a failing-gate demonstration on Jenkins, create a branch, add a regression-breaking change, push it and open a PR. Inspect the failure, fix it, push again, and retain the two real build links. Do not claim these hosted runs happened before you do them.

## Reproduce the deliberately vulnerable milestone

Only use synthetic local data. Keep the final checkout on `main`; create a separate worktree:

```bash
git worktree add ../workspace-vulnerable vulnerable-lab
```

Run that worktree with the installed environment interpreter from the final checkout; the original code uses the same dependencies. From inside `../workspace-vulnerable` on Windows:

```powershell
..\secure-workspace\.venv\Scripts\python.exe -m pytest -q -k 'test_v1 or test_v2 or test_v3 or test_v4'
```

Linux: `../secure-workspace/.venv/bin/python -m pytest -q -k 'test_v1 or test_v2 or test_v3 or test_v4'`. These four security assertions intentionally fail on that tag. Use `git show vulnerable-lab:workspace_app/resource.py` to inspect the original source without running it.

## Repository map

| Path | Purpose |
|---|---|
| workspace_app/api.py | Login, user sessions and delegation |
| workspace_app/resource.py | SQLite ownership, authorization and result validation |
| workspace_app/processor.py | Scoped CSV workflow |
| workspace_app/common.py | Schemas, JWT handling, fixed HTTP requests |
| helper/ | Separate installable CSV package source |
| scripts/ | Seeding, service launcher, demo and gates |
| tests/ | Functional and negative tests |
| docs/initial_ssdlc_plan.md | Plan committed before application code |
| docs/security_design.md | Architecture, STRIDE, asset register and access matrix |
| docs/vulnerabilities.md | Four planted vulnerabilities and fixes |
| docs/oral_exam_guide.md | Explain and demonstrate the design |
| docs/AI_USE_DECLARATION.md | Accurate declaration draft to personalize |
| evidence/ | Actual local validation snapshot and Git references |
| submission/ | Word/PDF report and declaration |
| vendor/ | Offline Python 3.12 Linux/Windows dependency wheels |

## Limits and submission

This is a loopback teaching system. Same-user processes are not filesystem-isolated. Production requires TLS, OS/container isolation, key lifecycle, login rate limiting, backups, body limits before parsing and durable audit logging. See report for the full discussion. No public hosting is included.

Submit the repository URL with its history and tags, Word/PDF report as required, evidence artifacts and a personalized AI-use declaration. Read and understand the application and rerun it yourself before the oral exam. Add actual hosted Jenkins build URLs to the evidence and report once configured. The assignment links AU's AI policy; check the applicable course/exam rules before submitting generated material unchanged.

Jenkins reference: https://www.jenkins.io/doc/book/pipeline/multibranch/ and GitHub webhook reference: https://docs.github.com/en/webhooks/about-webhooks . PyJWT claim validation reference: https://pyjwt.readthedocs.io/en/latest/usage.html . Accessed 22 October 2026.
