# Initial SSDLC plan

Recorded before application implementation. Domain: private research datasets and CSV exports. No GUI, registration, public hosting, or optional supply-chain experiments.

## Requirements gate
FR1 seeded user login; FR2 create and list private datasets; FR3 read own dataset; FR4 export through API → processing → resource; FR5 admin metadata only.
Assets: passwords, user sessions, private rows, CSV results, service grants, dependency artifacts and evidence.
Services: API establishes identity; resource owns SQLite records and enforces ownership; processor handles only a delegated export. Separate HTTP processes; database is not a component.
Roles: Ali and John are users; Admin audits metadata but cannot read other users' rows or results.
Trust boundaries: client/API, API/resource, API/processor, processor/resource, processor/helper installation. See final threat model and access matrix for detailed review.
STRIDE: spoofed identity → validated sessions; tampered inputs → strict schemas and SQL parameters; repudiation → metadata logs; information disclosure → ownership and scoped grants; denial of service → bounded rows and timeouts; elevation → role checks and delegation scope.
Gate: every operation has an authority and control; all three services participate in export.

## Implementation and build gate
Use Python, FastAPI, PyJWT, SQLite and an installable local CSV helper wheel. Lock all resolved dependencies with hashes. Reject unlisted artifacts using exact offline wheel inventory plus digest manifest. Isolate intentionally vulnerable milestone in Git history and fix before release.

## Testing gate
Run real HTTP tests against three new processes and a temporary database. Demonstrate three catalog flaws (SQL injection, missing authorization, improper input validation) and one composition flaw (confused-deputy export). Keep the same regression tests before/after fixes. Required functional and authorization tests, static checks and dependency review must pass; malformed data and tokens must fail closed. Preserve logs and JUnit evidence.

## Release deploy and operation
Jenkins multibranch pipeline validates each push and pull request after webhook configuration. Archive test/static/dependency output. Any test failure, static security finding, unknown artifact, digest mismatch or vulnerability advisory blocks. Production requires TLS, separate OS identities/containers, protected keys, durable logging, backups, login throttling and ongoing updates. No production deployment in scope.

Trace: private rows → cross-user disclosure → ownership/scoped grant → design and implementation → HTTP negative tests → block on failure. Build artifacts → tampered dependency → hash verification → build → manifest rejection test → block on mismatch.
