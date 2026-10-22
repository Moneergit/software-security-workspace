"""Seed synthetic data and manage three independent HTTP processes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager

import httpx

ROOT = Path(__file__).resolve().parents[1]


def seed(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    accounts = {}
    for name, role in [("ali", "user"), ("john", "user"), ("admin", "admin")]:
        salt = secrets.token_bytes(16)
        # Public teaching passwords, never a production credential.
        digest = hashlib.scrypt((name + "-demo-password").encode(), salt=salt, n=16384, r=8, p=1)
        accounts[name] = {"role": role, "salt": salt.hex(), "digest": digest.hex()}
    (directory / "accounts.json").write_text(json.dumps(accounts), encoding="utf-8")
    with sqlite3.connect(directory / "workspace.db") as connection:
        connection.executescript("""
        CREATE TABLE IF NOT EXISTS datasets(
            id INTEGER PRIMARY KEY, owner TEXT NOT NULL, title TEXT NOT NULL, values_json TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS results(
            dataset_id INTEGER NOT NULL, owner TEXT NOT NULL, csv TEXT NOT NULL,
            PRIMARY KEY(dataset_id, owner));
        """)
        if connection.execute("SELECT count(*) FROM datasets").fetchone()[0] == 0:
            connection.executemany("INSERT INTO datasets(owner,title,values_json) VALUES(?,?,?)",
                                   [("ali", "Ali measurements", "[10,20,30]"),
                                    ("john", "John measurements", "[40,50]")])


def free_port():
    with socket.socket() as handle:
        handle.bind(("127.0.0.1", 0))
        return handle.getsockname()[1]


@contextmanager
def cluster(directory: Path, ports=None):
    seed(directory)
    ports = ports or [free_port() for _ in range(3)]
    urls = [f"http://127.0.0.1:{port}" for port in ports]
    keys = {name: secrets.token_urlsafe(48) for name in ["USER_KEY", "RESOURCE_KEY", "PROCESSOR_KEY"]}
    environments = [
        {**keys, "RESOURCE_URL": urls[1], "PROCESSOR_URL": urls[2], "ACCOUNTS": str(directory / "accounts.json")},
        {"RESOURCE_KEY": keys["RESOURCE_KEY"], "DATABASE": str(directory / "workspace.db")},
        {"PROCESSOR_KEY": keys["PROCESSOR_KEY"], "RESOURCE_URL": urls[1]},
    ]
    processes, logs = [], []
    try:
        for service, port, extra in zip(["api", "resource", "processor"], ports, environments, strict=True):
            log = open(directory / (service + ".log"), "w", encoding="utf-8")
            logs.append(log)
            # Remove signing keys and resource paths inherited from the parent.
            env = {k: v for k, v in os.environ.items() if k not in {
                "USER_KEY", "RESOURCE_KEY", "PROCESSOR_KEY", "DATABASE", "ACCOUNTS"}}
            env.update(extra)
            processes.append(subprocess.Popen([sys.executable, "-m", "uvicorn",
                f"workspace_app.{service}:app", "--host", "127.0.0.1", "--port", str(port)],
                cwd=ROOT, env=env, stdout=log, stderr=log))
        with httpx.Client(trust_env=False, timeout=0.5) as client:
            for url in urls:
                deadline = time.monotonic() + 20
                while True:
                    try:
                        if client.get(url + "/health").status_code == 200:
                            break
                    except httpx.HTTPError:
                        pass
                    if time.monotonic() > deadline or any(p.poll() is not None for p in processes):
                        raise RuntimeError("Service startup failed; inspect " + str(directory))
                    time.sleep(0.05)
        yield {"api": urls[0], "resource": urls[1], "processor": urls[2], "keys": keys,
               "pids": [p.pid for p in processes], "directory": directory}
    finally:
        for process in processes:
            process.terminate()
        for process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        for log in logs:
            log.close()


def demo(base):
    with httpx.Client(base_url=base, trust_env=False, timeout=10) as client:
        response = client.post("/login", json={"username": "ali", "password": "ali-demo-password"})
        response.raise_for_status()
        client.headers["Authorization"] = "Bearer " + response.json()["access_token"]
        for method, path in [("GET", "/datasets"), ("POST", "/datasets/1/export"), ("GET", "/results/1"),
                             ("GET", "/datasets/2"), ("POST", "/datasets/2/export")]:
            result = client.request(method, path)
            print(method, path, result.status_code, result.json())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["serve", "demo", "seed", "smoke"])
    args = parser.parse_args()
    if args.command == "demo":
        demo("http://127.0.0.1:8000")
    elif args.command == "seed":
        seed(ROOT / ".runtime")
        print("Seeded .runtime; existing datasets retained")
    elif args.command == "smoke":
        with tempfile.TemporaryDirectory() as temporary:
            with cluster(Path(temporary)) as services:
                print("Independent service PIDs:", services["pids"])
                demo(services["api"])
    else:
        with cluster(ROOT / ".runtime", [8000, 8001, 8002]):
            print("API docs http://127.0.0.1:8000/docs — Ctrl+C stops all services", flush=True)
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
