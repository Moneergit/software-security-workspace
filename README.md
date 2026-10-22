# Private Dataset Workspace

**Windows setup — Python 3.12 x64 and PowerShell**

A small Python application for storing private numeric datasets and exporting them as CSV. This guide is written for running the project on a Windows computer. The supplied automated evidence was produced on Linux; a Windows execution has not yet been verified.

## Quick start on Windows

### 1. Open the project folder

Extract the ZIP. Open the `secure-workspace` folder, where this README and `run.py` are located. In File Explorer, click the address bar, type `powershell`, and press Enter.

If you already have the project on GitHub, you can clone it instead:

```powershell
git clone https://github.com/YOUR-USERNAME/software-security-assignment.git
cd software-security-assignment
```

### 2. Check Python

Install **Python 3.12, 64-bit**, including the Python launcher. Then check:

```powershell
py -3.12 --version
```

Expected: `Python 3.12.x`. You also need Git when publishing the repository. Docker is not required for the local application.

### 3. Set up once

```powershell
py -3.12 run.py setup
```

This creates `.venv`, verifies the bundled dependency files, installs them, and seeds the three demonstration accounts and two datasets. The helper package is installed too. You do not need to activate the virtual environment or install packages manually. Existing datasets are retained if you repeat setup.

### 4. Run the application

```powershell
py -3.12 run.py run
```

This starts **all three services as separate processes**. Keep this window open. Open [the API documentation](http://127.0.0.1:8000/docs) in your browser. Press **Ctrl+C** in PowerShell to stop all services.

### 5. Try the demonstration

Open a second PowerShell window in the same project folder:

```powershell
py -3.12 run.py demo
```

This logs in as Ali, lists Ali's datasets, creates a CSV export and retrieves it. It also tries to read and export John's dataset. Those last requests should return **404**, showing that cross-user access is denied.

### 6. Run the tests

```powershell
py -3.12 run.py test
```

This runs the functional and security tests against a fresh temporary environment. The supplied snapshot has **40 passing tests**. Test results are saved in `reports/tests.xml`. Tests use free ports and their own database, so the demonstration server can stay open.

For the complete static analysis, dependency analysis, helper build and test checks:

```powershell
py -3.12 run.py check
```

This saves logs and analysis results in `reports/`. A successful run returns exit code 0; the `check` command also writes `reports/gates.json`, where every stage should have value 0. **The dependency advisory lookup needs internet access.** A failed or unavailable check blocks the gate.

## What the application does

| Function | Behavior |
|---|---|
| Login | Authenticate using a seeded account |
| Create and search datasets | Store and list your own datasets |
| Read a dataset | Retrieve your own numeric rows |
| Export CSV | Generate and save an export through all three services |
| Retrieve a result | Read your own saved CSV |
| Admin audit | Inspect global dataset metadata without access to other users' rows |

Each dataset has a title and 1–100 integers. The system has two main entity types: datasets and export results.

## Architecture

![Three separately running services and the installed helper](docs/architecture.png)

| Component | Address | Responsibility |
|---|---|---|
| Application API | `http://127.0.0.1:8000` | Login, user sessions and request coordination |
| Resource Service | `http://127.0.0.1:8001` | Dataset ownership, storage and authorization |
| Processing Service | `http://127.0.0.1:8002` | One authorized CSV export at a time |

The services exchange JSON over HTTP. Export follows API → Processor → Resource → CSV helper → Resource. SQLite is storage, not one of the three application components. The helper is a separate installed Python package in `helper/`.

## Demonstration accounts

| Username | Password | Role |
|---|---|---|
| `ali` | `ali-demo-password` | User |
| `john` | `john-demo-password` | User |
| `admin` | `admin-demo-password` | Admin |

Dataset 1 belongs to Ali; dataset 2 belongs to John. Admin can see owner and title metadata but cannot read their rows or CSV results. These are public synthetic credentials for a local teaching project.

## Try individual API requests

In the browser at `/docs`:

1. Open `POST /login`, choose **Try it out**, and use `{"username":"ali","password":"ali-demo-password"}`.
2. Copy `access_token` from the response.
3. For a protected endpoint, enter `Bearer YOUR_TOKEN` in its `authorization` header field.
4. `GET /datasets/1` should return Ali's data; `GET /datasets/2` should return 404.
5. `POST /datasets/1/export` should return `ready`. `GET /results/1` should return the CSV in JSON.

The `demo` command performs this workflow automatically.

## Command reference

Run these from the folder containing `run.py`:

| Command | Purpose |
|---|---|
| `py -3.12 run.py setup` | Create the virtual environment, install approved dependencies and seed data |
| `py -3.12 run.py run` | Start all three services; also seeds missing demonstration data |
| `py -3.12 run.py demo` | Demonstrate a running server |
| `py -3.12 run.py test` | Run functional/security tests and save JUnit results |
| `py -3.12 run.py check` | Run all local release gates and save analysis output |
| `py -3.12 run.py build` | Rebuild the separate helper wheel into `reports/helper-wheel/` |
| `py -3.12 run.py seed` | Seed demonstration data without starting servers |
| `py -3.12 run.py smoke` | Start a temporary cluster, demonstrate it, then stop it |

Running `py -3.12 run.py` without an argument also starts the application. Setup installs the already built approved helper wheel; `build` demonstrates how to rebuild it from source. New build bytes are not automatically approved for installation.

## Security work and evidence

The project applies least privilege, complete mediation and fail-safe defaults. Resource checks ownership even when another service sends a request. Service grants carry the user, target service, action, dataset and expiry. The four deliberate vulnerabilities and their fixes are documented in [the investigation](docs/vulnerabilities.md).

| File or folder | Contents |
|---|---|
| [Security design](docs/security_design.md) | Requirements, assets, STRIDE, trust boundaries and access matrix |
| [Initial SSDLC plan](docs/initial_ssdlc_plan.md) | Plan committed before application implementation |
| `evidence/final/` | Supplied local test and analysis results |
| `reports/` | Results generated when you run your own checks |
| `Jenkinsfile` | Jenkins pipeline that builds/validates, analyzes, tests and archives results |
| [Submission guide](docs/github_and_submission.md) | GitHub, Jenkins and submission steps |
| [Oral exam guide](docs/oral_exam_guide.md) | Demonstration and explanation questions |
| `submission/` | Report in Word/PDF and the separate AI-use declaration |

The `vulnerable-lab` tag preserves the original flaws. The final branch contains the fixes. The ZIP preserves `.git` and the full history; do not delete it or start a new history. Optional malicious-package experiments were excluded.

## Troubleshooting

| Problem | Action |
|---|---|
| `py` is not recognized | Install Python 3.12 with the Python launcher, then reopen PowerShell |
| `run.py` cannot be found | Open PowerShell inside the extracted `secure-workspace` folder |
| Setup has not been run | Run `py -3.12 run.py setup` first |
| A port is already in use | Stop the previous server with Ctrl+C; use `smoke` to try temporary ports |
| Token stops working after a restart | Log in again; service keys rotate on restart |
| An advisory check fails | Inspect `reports/dependency-audit.txt`; internet lookup errors also fail the gate |

The application uses loopback HTTP and is intended for local synthetic data. Production changes and remaining limitations are discussed in the report. Further build and pipeline details are in [the technical notes](docs/build_and_pipeline.md). The README layout takes inspiration from the [course example](https://github.com/Abhi-Vaish/ISRM_Group-4/blob/main/README.md); the application and commands here are specific to this project.
