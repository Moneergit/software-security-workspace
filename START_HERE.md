# Start here

This package includes the complete small Python application, three services, helper wheel, Git history, tests, security design, Jenkinsfile, report and AI-use declaration draft.

1. Extract the entire ZIP. Keep the `secure-workspace` folder together, including its `.git` directory.
2. Open `submission/Software_Security_Report.pdf` for the report. The Word version is editable.
3. Install Python 3.12 x64 and Git if needed. Open PowerShell in the folder containing README.md.
4. Copy the **Windows PowerShell** commands in README.md to build, seed and start all three services. You do not need Docker or three terminal windows.
5. Open http://127.0.0.1:8000/docs to see the API. In a second PowerShell window run ` .\.venv\Scripts\python.exe scripts/run.py demo ` for a complete automatic example, including denied cross-user requests.
6. Run ` .\.venv\Scripts\python.exe -m pytest -q ` to run the tests. The supplied final snapshot contains 40 passing tests. Then run ` .\.venv\Scripts\python.exe scripts/ci.py ` for all checks; the advisory check needs internet.
7. Read docs/oral_exam_guide.md and explain each part in your own words. Review the four vulnerable implementations with `git show` or the separate worktree instructions.
8. Create an empty GitHub repository and follow README.md's push instructions. The `.git` history already contains the initial plan, deliberate vulnerabilities and fixes; do not start a new repository history.
9. Connect Jenkins to GitHub using the README checklist. Capture the actual push and pull-request build links. The local gate was run, but hosted Jenkins was not connected here.
10. Fill in your name, student number, repository URL and actual Jenkins evidence in the report's submission note. Personalize the separate declaration, check course AI rules and submit the repository URL, report and required artifacts.

If a port is busy, stop the old `serve` terminal with Ctrl+C. `scripts/run.py smoke` uses temporary free ports and is useful for checking whether installation works. If Windows says a file is missing, check that PowerShell is inside `secure-workspace` rather than its parent folder.
