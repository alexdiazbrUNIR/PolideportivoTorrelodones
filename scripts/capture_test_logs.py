"""Run pytest and store output in reports/pytest_output.txt"""
import subprocess
from pathlib import Path

out_dir = Path("reports")
out_dir.mkdir(exist_ok=True)

p = subprocess.run(["pytest", "-q"], capture_output=True, text=True)

log = p.stdout + "\n" + p.stderr

with open(out_dir / "pytest_output.txt", "w", encoding="utf-8") as f:
    f.write(log)

print("Wrote reports/pytest_output.txt")
