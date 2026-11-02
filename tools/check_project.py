#!/usr/bin/env python3
# Copyright 2026 James E. Dunn
# SPDX-License-Identifier: Apache-2.0
"""Offline local-link/common-leak checks and an allowlisted source ZIP builder.

This is a useful preflight, never a privacy guarantee or publication action.
"""
import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".git", ".private", "private", "workspaces", "packets", "checkpoints", "__pycache__", ".venv", ".pytest_cache"}
ALLOWED_SUFFIXES = {".md", ".py", ".json", ".txt", ".yml", ".yaml"}
ALLOWED_NAMES = {".gitignore", "VERSION"}


def source_files(root):
    files=[]
    for p in sorted(Path(root).rglob("*")):
        if not p.is_file() or any(part in EXCLUDED for part in p.relative_to(root).parts):
            continue
        if p.is_symlink():
            raise ValueError("Source symlinks are not allowed in the release archive.")
        if p.suffix in ALLOWED_SUFFIXES or p.name in ALLOWED_NAMES:
            files.append(p)
    return files


def privacy_findings(text):
    findings=[]
    # Construct path prefixes so this scanner's own source is not a false positive.
    for prefix in ("/"+"Users/", "/"+"home/"):
        if re.search(re.escape(prefix)+r"[^/\s]+/",text):
            findings.append("Personal absolute home path")
    for pattern,label in ((r"sk"+r"-(?:proj-)?[A-Za-z0-9_-]{16,}","Possible API key"),
                          (r"gh"+r"[opusr]_[A-Za-z0-9]{20,}","Possible GitHub token"),
                          (r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----","Private key block")):
        if re.search(pattern,text):findings.append(label)
    emails=re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",text)
    for address in emails:
        if not address.lower().endswith((".invalid","@example.com","@example.org","@example.net")):
            findings.append("Non-example email address")
    return sorted(set(findings))


def local_links(path,root):
    findings=[]
    text=path.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)",text):
        target=target.strip().split(" ",1)[0].strip("<>")
        if not target or target.startswith("#") or urlsplit(target).scheme:
            continue
        relative=unquote(target.split("#",1)[0])
        resolved=(path.parent/relative).resolve()
        try:resolved.relative_to(root.resolve())
        except ValueError:
            findings.append("Link escapes project: "+target);continue
        if not resolved.exists():findings.append("Broken local link: "+target)
    return findings


def check(root=ROOT):
    root=Path(root)
    findings=[]
    files=source_files(root)
    for p in files:
        text=p.read_text(encoding="utf-8")
        for issue in privacy_findings(text):findings.append({"file":str(p.relative_to(root)),"issue":issue})
        if p.suffix==".md":
            for issue in local_links(p,root):findings.append({"file":str(p.relative_to(root)),"issue":issue})
        if p.suffix==".json":
            try:json.loads(text)
            except json.JSONDecodeError:findings.append({"file":str(p.relative_to(root)),"issue":"Invalid JSON"})
    for license_file in ("LICENSE.md", "LICENSE-CODE.txt", "LICENSE-CONTENT.txt", "NOTICE.txt"):
        if not (root/license_file).is_file():
            findings.append({"file":license_file,"issue":"License scope/text/notice missing"})
    return {"source_files_checked":len(files),"findings":findings,"ok":not findings,
            "limits":"Common-pattern scan and local-link existence only; human content/permission/license review still required."}


def build_zip(destination,root=ROOT):
    root=Path(root)
    destination=Path(destination)
    if destination.exists():raise ValueError("Refusing to overwrite an existing release ZIP.")
    report=check(root)
    if not report["ok"]:raise ValueError("Project preflight failed; inspect findings before packaging.")
    files=source_files(root)
    destination.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(destination,"w",zipfile.ZIP_DEFLATED) as archive:
        for p in files:archive.write(p,root.name+"/"+str(p.relative_to(root)))
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip():raise ValueError("ZIP integrity test failed")
        names=archive.namelist()
        if any(part in EXCLUDED for name in names for part in Path(name).parts):raise ValueError("Excluded runtime data in archive")
        for name in names:
            issues=privacy_findings(archive.read(name).decode("utf-8"))
            if issues:raise ValueError("ZIP privacy preflight failed: "+name)
    return {"zip":destination.name,"files":len(files),"sha256":hashlib.sha256(destination.read_bytes()).hexdigest(),"preflight":report,"published":False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip",dest="zip_path",help="Create a local ZIP after checks; never uploads")
    args=p.parse_args()
    try:
        result=build_zip(args.zip_path) if args.zip_path else check()
        print(json.dumps(result,indent=2))
        return 0 if result.get("ok",result.get("preflight",{}).get("ok",False)) else 1
    except (OSError,ValueError) as exc:
        print("Error: "+str(exc),file=sys.stderr);return 2


if __name__=="__main__":sys.exit(main())
