# Verification evidence

The final/ folder contains the latest actual local test and analysis outputs. All 40 tests pass and all ten gates return zero. resource.log records synthetic resource denials without passwords or bearer tokens. The four deliberate attacks were also rerun against the anonymized vulnerable-lab milestone; vulnerable-tests.txt and XML show four expected security-assertion failures with John fixtures.

Execution was on Linux. It does not establish Windows or hosted Jenkins execution. Follow the Windows guide to run your own checks and save their results under evidence/windows/.

The repository keeps its development sequence and milestone tags, with fixture names anonymized and large third-party distributions removed from historical trees. Commit identifiers changed during that maintenance. See docs/history_note.md. The initial plan still precedes feature implementation.
