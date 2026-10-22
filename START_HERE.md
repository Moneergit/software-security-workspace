# Start here on Windows

1. Extract the ZIP and open the `secure-workspace` folder.
2. Open PowerShell in that folder. Install Python 3.12 x64 if needed.
3. Run `py -3.12 run.py setup` once.
4. Run `py -3.12 run.py run` and keep that window open.
5. Open http://127.0.0.1:8000/docs.
6. In a second PowerShell window in the same folder, run `py -3.12 run.py demo`.
7. Run `py -3.12 run.py test` for the tests and `py -3.12 run.py check` for all analysis and test gates.

README.md explains each step briefly. No virtual-environment activation or Docker is needed. Setup installs the bundled dependencies and seeds the demonstration data automatically.

For publishing to GitHub and completing the assignment, follow docs/github_and_submission.md. Keep the supplied `.git` history. The editable report and PDF are in submission/; the declaration is a separate file there.

This is a Windows setup guide. The supplied execution evidence was produced on Linux; it is not evidence of a completed Windows run.
