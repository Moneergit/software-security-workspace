# Start here on Windows

Student: Moneer

1. Extract the ZIP and open the secure-workspace folder.
2. Open PowerShell there and check that Python 3.12 x64 is installed.
3. Run `py -3.12 run.py setup` once. This needs internet and installs everything into .venv.
4. Run `py -3.12 run.py run` and open http://127.0.0.1:8000/docs.
5. In a second PowerShell window, run `py -3.12 run.py demo`.
6. Run `py -3.12 run.py test`, then `py -3.12 run.py check`.

README.md explains each step. The Windows GitHub and submission guide is in docs/ and submission/. Keep .git because the assignment requires the history. The one helper .whl is a required installable package; its editable code is in helper/src/.

The supplied execution evidence was produced on Linux. Collect actual Windows outputs by following the guide.
