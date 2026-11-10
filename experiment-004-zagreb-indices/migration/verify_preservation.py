from pathlib import Path
import hashlib, json, subprocess
root = Path(__file__).resolve().parents[1]
audit = "68a494573fdbd2e629c620a263dafed5853ac26e"
def git(*args):
    return subprocess.check_output(["git", "-C", str(root), *args])
subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", audit, "HEAD"], check=True)
for name, digest in json.loads((root / "migration/source-file-hashes.json").read_text()).items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name
names = git("ls-tree", "-r", "--name-only", audit).decode().splitlines()
checked = [p for p in names if p.endswith(".lean") or p in ["lean-toolchain", "lakefile.toml", "lake-manifest.json"]]
for name in checked:
    assert (root / name).read_bytes() == git("show", audit + ":" + name), name
print("PASS: audited commit reachable; 82 original files preserved; all Lean files and pins identical to audit.")
