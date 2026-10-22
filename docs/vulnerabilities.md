# Four planted vulnerabilities

The catalog source is the uploaded CWE student reading. `vulnerable-lab` (dcabff9) preserves actual vulnerable service code. `fixed-boundaries` (716e188) preserves the corrections. Four unchanged tests were executed at the vulnerable milestone: all four security assertions failed. Raw responses are in evidence/vulnerable-tests.txt and JUnit XML. Final full-suite evidence is separate.

| ID | Catalog or composition | Incorrect assumption | Trigger and original observation | Fix and regression |
|---|---|---|---|---|
| V1 | CWE-89 SQL injection | An authenticated search string remains SQL data | Ali searches `' OR 1=1 --`; both owners' metadata returned | Parameter binding for owner and LIKE; test_v1_sql_injection |
| V2 | CWE-862 missing authorization | A valid read grant proves ownership | Ali GET /datasets/2 returned John's numeric rows, HTTP 200 | Resource owned() on direct read; test_v2_cross_user_read |
| V3 | CWE-20 improper input validation | Declaring list[int] enforces bounded size | POST dataset containing 101 rows accepted, HTTP 201, violating 100-row quota | Strict bounded list and numeric ranges at API and Resource; test_v3_row_quota and test_resource_schema_independently |
| V4 | Additional composition flaw, confused deputy | A permitted processing job may fetch any requested dataset | Ali export dataset 2 crosses all three components and returns ready, HTTP 200; John's data is saved as Ali's result | Keep subject/action/resource/expiry through delegation and check ownership on both Resource job endpoints; test_v4_confused_deputy_export and test_job_save_owner_and_content |

V3 demonstrates a quota violation and a resource-exhaustion precondition, not an observed service outage. It is prioritized below the observed cross-user disclosures. V4 is a separate `/jobs` route and an end-to-end authority failure; it persists if only V2's ordinary read route is fixed. It maps to missing/incorrect authorization at the underlying boundary, but is counted separately because the assignment requires an additional flaw caused by service composition.

V1 and V2 are high priority because ordinary authenticated users obtain foreign information. V4 is high priority because it turns an apparently legitimate service workflow into unauthorized access. V3 is medium priority in this local synthetic setting. These are qualitative contextual priorities, not calculated CVSS scores or claims of public exploitation.

The final checkout has no runtime switch that enables the planted vulnerabilities. The local public demo credentials and same-OS-user limitation remain documented teaching constraints. Optional malicious-package experiments A and B were not attempted.
