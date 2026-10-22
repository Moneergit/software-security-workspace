# Oral exam guide

## A five minute demonstration
Run `py -3.12 run.py smoke` or use the README's Swagger walkthrough. Show the three independent process IDs, Ali's list, export of dataset 1, retrieval of the CSV, rejected dataset 2 read, and rejected dataset 2 export. Then show Admin metadata while explaining why admin cannot read other users' rows. Open the access-control matrix and the matching Resource checks.

## Questions to practise

**What is authentication versus authorization?** Login establishes Ali's identity. Resource ownership decides whether Ali may read dataset 1 or 2. A valid session alone does not answer that question.

**Why exactly three services?** API establishes identity and delegates; Resource owns records and authorizes access; Processor converts only an authorized dataset to CSV. SQLite and the browser do not count as application components.

**How do you know the services are separate?** scripts/run.py launches three uvicorn subprocesses with distinct PIDs and loopback HTTP ports. The HTTP test fixture verifies three PIDs and exercises the real interfaces.

**What is carried in a grant?** Subject, issuer, audience, action, exact dataset ID, issued time, expiry and a token ID. Resource checks those plus database ownership. A signature does not prove that an operation is appropriate.

**Can Processor read another dataset?** It has no Resource signing key. Its delegated Resource token covers one user, action, dataset and one minute. Changing the ID or signing with its own key fails. It runs as the same OS user here, so this is HTTP authorization containment, not an OS sandbox.

**Why use different HMAC keys?** They prevent Processor's signing/validation key from being accepted as a Resource credential. API and Resource still share a trusted signing domain. In production, asymmetric signatures would separate issuance from verification more strongly.

**Why is V4 different from V2?** V2 is a missing check on an ordinary dataset GET. V4 is a job workflow where one service treats another service's request as sufficient authority. Fixing the ordinary GET does not fix `/jobs/{id}`. Both need independent checks.

**How did you prove the vulnerabilities existed?** Four fixed security assertions were run before corrections. Each failed with an actual successful attack response in evidence/vulnerable-tests.txt. The same assertions pass in the final full suite. Use `git diff vulnerable-lab fixed-boundaries -- workspace_app` to inspect the fixes.

**Why is V3 a security issue?** It bypasses an explicit quota intended to bound processing/storage work. The experiment shows 101 rows accepted, not an actual outage. Availability beyond these application limits remains unproven.

**Why parameterized SQL?** It preserves the distinction between SQL structure and user data. Escaping selected characters or trusting authenticated input does not provide the same guarantee.

**What does Python protect, and what does it not protect?** Its managed memory reduces common manual-memory faults; FastAPI/Pydantic validate declared schemas; PyJWT handles token signatures and claim validation. Ownership, role decisions and delegation remain application responsibilities.

**Can CSV contain executable spreadsheet formulas?** Only bounded integers and a fixed header are accepted. Resource also compares returned CSV with its own deterministic expected serialization. There is no arbitrary text cell or filename input.

**Are tokens encrypted?** No. JWT signatures protect integrity and authenticity; payloads are readable. No password or row content goes into tokens. Local HTTP is a scope choice; production needs TLS.

**Are grants one-use?** No. They are reusable for the scoped operation until expiry. Export is deterministic and result writes are an upsert. Stronger one-time/revocation semantics need server-side state.

**What does the build gate reject?** Unexpected/missing wheel files, altered hashes, helper source/wheel mismatch, unknown installed distributions, failing tests/static checks and dependency advisories. The approval files themselves are trusted repository policy; an attacker editing those policy files is a separate trust problem.

**Did you do the optional supply-chain attack?** No. The helper dependency and ordinary artifact checks are required; no deliberately malicious helper version or optional experiments were included.

**What did Jenkins actually run?** Local scripts implement and exercised the same validation commands. The supplied Jenkinsfile archives the outputs on a configured Jenkins server. Hosted push/PR trigger evidence must be added after you configure the job. Do not confuse a Jenkinsfile with a real Jenkins run.

**What would change in production?** TLS; OS/container isolation; separate filesystem permissions; asymmetric service identity; secret rotation and revocation; bounded incoming bytes before parsing; login throttling; durable audit; backups; concurrency/load testing; dependency maintenance.

**How was AI used?** Read docs/AI_USE_DECLARATION.md. Be explicit about generated code/report and your own review, experiments and modifications. Explain the code from understanding, not memorized wording.

## Files to explain without notes
Read `common.py`, then `api.py`, then `processor.py`, then `resource.py`. Trace POST export from route to grant creation, scoped job read, helper import, scoped job save and final result read. Finally explain test_v4_confused_deputy_export and the gate results JSON.
