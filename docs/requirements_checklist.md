# Assignment requirement checklist

| Mandatory requirement | Delivered location or evidence |
|---|---|
| Functional/nonfunctional requirements before implementation | Initial plan commit faf9582; docs/security_design.md |
| Three separately running application components | API, Resource and Processor; cluster fixture and process test |
| Authentication and authorization | common.py, api.py, resource.py; HTTP tests |
| At least three functionalities | Login, create/list/read, export/result, admin metadata |
| One function using all three components | CSV export; smoke output and export test |
| Two ordinary users and one privileged role | Ali, John, Admin; role and cross-user tests |
| Declared installed helper package | helper/; workspace-csv in requirements.lock and vendor/ |
| Three course-catalog flaws plus composition flaw | docs/vulnerabilities.md; vulnerable-lab Git tag; baseline evidence |
| Investigate and correct violations | fixed-boundaries tag; 40 final passing tests |
| Three secure design principles with evidence | Least privilege, complete mediation, fail-safe defaults; security_design.md |
| All four SSDLC phases and initial plan commit | docs/initial_ssdlc_plan.md and Git history |
| Asset register, trust boundaries, matrix and STRIDE | docs/security_design.md |
| Reproducible installation and unapproved artifact rejection | vendor/, hash lock, manifest and gate tests |
| Jenkins build, static and dependency checks | Windows Jenkinsfile, run.py and scripts/ci.py |
| Fresh test environment and artifacts | Temporary process fixture; reports archived by Jenkinsfile |
| Pipeline on pushes and PRs | Multibranch/webhook setup documented; hosted configuration still needed |
| Gate decisions and production discussion | Pipeline failure policy, report sections 5–7 |
| Around 2000–2500 narrative words | Report narrative 2469 words; seven main pages plus references/navigation |
| Source history, README and submission artifacts | ZIP includes .git, source, evidence and submission/ |
| AI declaration | submission/AI_Use_Declaration.docx and PDF; personalize before submitting |

Optional malicious helper, Experiment A and Experiment B were excluded as requested. Ordinary hash verification is a required build control, not a claim that the optional supply-chain experiments were performed.

External remaining steps: publish the existing history to your GitHub repository, configure Jenkins discovery/webhooks, execute actual push and pull-request builds, fill in identity and build URLs, and review the AI-use declaration against course rules. These account-dependent actions are documented, not claimed completed.
