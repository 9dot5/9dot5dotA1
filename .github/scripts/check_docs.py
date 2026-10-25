"""Documentation checks from CLAUDE.md "Checks before a change is ready".

1. Every relative Markdown link resolves inside the repository.
2. Every ADR has Status, Date, Deciders and Review by in its header.
3. No IP address or private key appears in a tracked text file (the repository is public, R-29).

Exit code 1 lists every failure.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LINK = re.compile(r"\]\(([^)#\s:]+)(?:#[^)]*)?\)")
IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
PRIVATE_KEY = re.compile(r"BEGIN [A-Z ]*PRIVATE KEY")
ADR_FIELDS = ("**Status:**", "**Date:**", "**Deciders:**", "**Review by:**")
TEXT_SUFFIXES = {".md", ".yml", ".yaml", ".json", ".py", ".ps1", ".j2", ".cfg", ".toml", ".txt", ""}


def tracked_files():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)
    return [ROOT / line for line in out.stdout.splitlines()]


def is_address(text):
    # A four-part version number with a part above 255 is not an address.
    parts = text.split(".")
    return all(0 <= int(p) <= 255 for p in parts) and not text.startswith("0.")


def main():
    failures = []
    for path in tracked_files():
        if path.suffix not in TEXT_SUFFIXES or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(ROOT).as_posix()
        for number, line in enumerate(text.splitlines(), 1):
            for match in IPV4.finditer(line):
                if is_address(match.group(0)) and match.group(0) not in ("127.0.0.1",):
                    failures.append(f"{rel}:{number}: IP address {match.group(0)}")
            if PRIVATE_KEY.search(line):
                failures.append(f"{rel}:{number}: private key marker")
        if path.suffix == ".md":
            for target in LINK.findall(text):
                if not (path.parent / target).exists():
                    failures.append(f"{rel}: broken link {target}")
            if rel.startswith("adr/ADR-") and "TEMPLATE" not in rel:
                head = "\n".join(text.splitlines()[:12])
                for field in ADR_FIELDS:
                    if field not in head:
                        failures.append(f"{rel}: header field {field} missing")
    for failure in failures:
        print(failure)
    print(f"{len(failures)} problem(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
