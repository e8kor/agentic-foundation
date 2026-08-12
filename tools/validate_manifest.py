#!/usr/bin/env python3
"""
Foundation manifest validator — stdlib-only (no third-party dependencies).

Validates every plugin.yaml in extensions/ against the core schema and the core
version gate, plus core-skills/ SKILL.md presence and frontmatter. Incompatible
or invalid plugins are reported and staged for quarantine (moved to
curator/archived/) -- never deleted.

Uses a small YAML-subset parser (sufficient for the flat/nested manifests this
framework defines) so it runs anywhere with Python, no pip installs.

Usage:
    python3 validate_manifest.py [--root <foundation-root>] [--quarantine]

Exit codes:
    0  all plugins valid
    1  one or more plugins invalid or incompatible
"""
import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

CORE_VERSION = "2.0.0"
KNOWN_POINTS = {"skill", "memory", "tool", "hook", "policy", "adapter", "mcp"}
KNOWN_PROVENANCE = {"agent", "user", "third-party", "core"}
REQUIRED_FIELDS = ["name", "version", "core", "extension_points", "provenance"]
HOOK_EVENTS = ("on-bootstrap", "on-load", "on-save", "on-curate", "on-shutdown")
ALLOWED_TOOL_EXAMPLES = {"bash", "python", "git", "gh", "curl", "node", "npx", "docker"}


# --- minimal schema-aware manifest parser (stdlib only) --------------------
# The manifest schema is small and fixed, so we parse it with a purpose-built
# line parser rather than a generic YAML subset. Handles flat scalars, simple
# lists (extension_points, allowed_tools), list-of-scalars (contributes),
# list-of-dicts (mcp_servers), and flat dicts (hooks, policy, env).

def _strip_comment(line):
    # strip an inline # comment, but not one inside quotes
    in_s = in_d = False
    for i, ch in enumerate(line):
        if ch == "'" and not in_d:
            in_s = not in_s
        elif ch == '"' and not in_s:
            in_d = not in_d
        elif ch == "#" and not in_s and not in_d:
            return line[:i]
    return line


def _scalar(s):
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        if len(s) >= 2:
            return s[1:-1]
    if s in ("true", "True"):
        return True
    if s in ("false", "False"):
        return False
    if s in ("null", "~"):
        return None
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [_scalar(x.strip()) for x in inner.split(",")]
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    return s


def parse_manifest(text):
    """Return (data, errors). Schema-aware, tolerant line parser."""
    data = {}
    errors = []
    lines = []
    for raw in text.splitlines():
        line = _strip_comment(raw).rstrip()
        if line.strip() and not line.strip().startswith("#"):
            lines.append(line)

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        indent = len(line) - len(line.lstrip(" "))
        content = line.strip()

        if content.startswith("- ") and ":" in content:
            # list-of-dicts item: e.g. "  - name: x" — find the owning list key
            # from the previously opened list (mcp_servers).
            k, v = content[2:].split(":", 1)
            obj = {_scalar(k.strip()): _scalar(v.strip())}
            # walk back to the parent list container we are filling
            owner = None
            for parent_key, parent_val in data.items():
                if isinstance(parent_val, list) and parent_val and isinstance(parent_val[-1], dict):
                    owner = parent_val
            if owner is None:
                # find any list value we could append to
                for parent_val in data.values():
                    if isinstance(parent_val, list) and parent_val:
                        owner = parent_val
                        break
            if owner is None:
                owner = []
            else:
                owner = owner  # reuse existing
            # Actually: mcp_servers is the only list-of-dicts. Locate it.
            mcp = data.get("mcp_servers")
            if mcp is None:
                mcp = []
                data["mcp_servers"] = mcp
            if isinstance(mcp, list):
                mcp.append(obj)
            else:
                errors.append("mcp_servers is not a list")
            # collect sub-keys (lines more indented than the "- " line)
            sub_indent = indent + 2
            j = i + 1
            while j < n:
                sline = lines[j]
                s_indent = len(sline) - len(sline.lstrip(" "))
                if s_indent <= indent:
                    break
                scontent = sline.strip()
                if scontent.startswith("- "):
                    # nested list under this obj (e.g. args, or a key: [] already handled)
                    pass
                elif ":" in scontent and not scontent.startswith("#"):
                    sk, sv = scontent.split(":", 1)
                    sk = _scalar(sk.strip())
                    sv = sv.strip()
                    if sv == "":
                        # nested block: collect until dedent
                        block = {}
                        obj[sk] = block
                        jj = j + 1
                        while jj < n:
                            bline = lines[jj]
                            b_indent = len(bline) - len(bline.lstrip(" "))
                            if b_indent <= s_indent:
                                break
                            bcontent = bline.strip()
                            if ":" in bcontent:
                                bk, bv = bcontent.split(":", 1)
                                block[_scalar(bk.strip())] = _scalar(bv.strip())
                            jj += 1
                        j = jj - 1
                    else:
                        obj[sk] = _scalar(sv)
                j += 1
            i = j
            continue

        if ":" not in content:
            errors.append(f"unparseable line: {content}")
            i += 1
            continue
        k, v = content.split(":", 1)
        key = _scalar(k.strip())
        v = v.strip()
        if v == "":
            # nested block: could be a list or dict
            block_lines = []
            j = i + 1
            while j < n:
                bline = lines[j]
                b_indent = len(bline) - len(bline.lstrip(" "))
                if b_indent <= indent:
                    break
                block_lines.append(bline)
                j += 1
            i = j - 1
            if block_lines and any(bl.lstrip().startswith("- ") for bl in block_lines):
                # list of scalars, or list of dicts
                is_dict_list = any(":" in bl.lstrip("- ").lstrip() for bl in block_lines)
                if is_dict_list:
                    # list of dicts (mcp_servers)
                    sub = []
                    bi = 0
                    while bi < len(block_lines):
                        bl = block_lines[bi]
                        bcontent = bl.lstrip()
                        if bcontent.startswith("- "):
                            head = bcontent[2:]
                            item = {}
                            if ":" in head:
                                hk, hv = head.split(":", 1)
                                item[_scalar(hk.strip())] = _scalar(hv.strip())
                            b_indent = len(bl) - len(bl.lstrip(" "))
                            bj = bi + 1
                            while bj < len(block_lines):
                                bl2 = block_lines[bj]
                                b2_indent = len(bl2) - len(bl2.lstrip(" "))
                                if b2_indent <= b_indent:
                                    break
                                b2content = bl2.lstrip()
                                if ":" in b2content and not b2content.startswith("-"):
                                    b2k, b2v = b2content.split(":", 1)
                                    b2k = _scalar(b2k.strip())
                                    b2v = b2v.strip()
                                    if b2v == "":
                                        item[b2k] = {}
                                        bj2 = bj + 1
                                        while bj2 < len(block_lines):
                                            bl3 = block_lines[bj2]
                                            b3_indent = len(bl3) - len(bl3.lstrip(" "))
                                            if b3_indent <= b2_indent:
                                                break
                                            b3content = bl3.lstrip()
                                            if ":" in b3content:
                                                k3, v3 = b3content.split(":", 1)
                                                item[b2k][_scalar(k3.strip())] = _scalar(v3.strip())
                                            bj2 += 1
                                        bj = bj2 - 1
                                    else:
                                        item[b2k] = _scalar(b2v)
                                bj += 1
                            sub.append(item)
                            bi = bj
                        else:
                            bi += 1
                    data[key] = sub
                else:
                    data[key] = [_scalar(bl.lstrip("- ")) for bl in block_lines]
            else:
                block = {}
                bj = 0
                while bj < len(block_lines):
                    bl = block_lines[bj]
                    bcontent = bl.lstrip()
                    if ":" in bcontent:
                        bk, bv = bcontent.split(":", 1)
                        bk = _scalar(bk.strip())
                        bv = bv.strip()
                        if bv == "":
                            block[bk] = {}
                            bj2 = bj + 1
                            while bj2 < len(block_lines):
                                bl3 = block_lines[bj2]
                                b3_indent = len(bl3) - len(bl3.lstrip(" "))
                                if b3_indent <= len(bl) - len(bl.lstrip(" ")):
                                    break
                                b3content = bl3.lstrip()
                                if ":" in b3content:
                                    k3, v3 = b3content.split(":", 1)
                                    block[bk][_scalar(k3.strip())] = _scalar(v3.strip())
                                bj2 += 1
                            bj = bj2 - 1
                        else:
                            block[bk] = _scalar(bv)
                    bj += 1
                data[key] = block
        else:
            data[key] = _scalar(v)
        i += 1
    return data, errors


def _load_manifest(path):
    text = path.read_text()
    if path.suffix == ".json":
        try:
            return json.loads(text), []
        except Exception as e:
            return {}, [str(e)]
    return parse_manifest(text)


# --- core range ------------------------------------------------------------
def parse_core_range(spec):
    m = re.match(r"^(>=|>|\^)?(\d+)\.(\d+)\.(\d+)$", str(spec).strip())
    if not m:
        return None
    op, maj, mi, pa = m.group(1) or "=", int(m.group(2)), int(m.group(3)), int(m.group(4))
    return op, (maj, mi, pa)


def core_satisfies(core_range, current=CORE_VERSION):
    cur = tuple(int(x) for x in current.split("."))
    parsed = parse_core_range(core_range)
    if parsed is None:
        return False
    op, bound = parsed
    if op == "=":
        return cur == bound
    if op == "^":
        return cur[0] == bound[0] and cur >= bound
    if op == ">":
        return cur > bound
    if op == ">=":
        return cur >= bound
    return False


# --- validation ------------------------------------------------------------
def validate_plugin(plugin_dir):
    path = plugin_dir / "plugin.yaml"
    if not path.is_file():
        return [f"missing plugin.yaml in {plugin_dir.name}"]
    errors = []
    data, parse_errors = _load_manifest(path)
    errors.extend(parse_errors)
    if parse_errors:
        return errors
    if not isinstance(data, dict):
        return ["manifest is not a mapping"]
    for f in REQUIRED_FIELDS:
        if f not in data:
            errors.append(f"missing required field: {f}")
    eps = data.get("extension_points", [])
    if isinstance(eps, list):
        for ep in eps:
            if ep not in KNOWN_POINTS:
                errors.append(f"unknown extension point: {ep}")
    elif eps not in ("", None):
        errors.append("extension_points must be a list")
    if "core" in data and not core_satisfies(data["core"]):
        errors.append(f"core range {data['core']} not satisfied by core {CORE_VERSION}")
    prov = data.get("provenance")
    if prov not in ("", None) and prov not in KNOWN_PROVENANCE:
        errors.append(f"invalid provenance: {prov}")
    # hooks must point at real files
    hooks = data.get("hooks") or {}
    if isinstance(hooks, dict):
        for ev in HOOK_EVENTS:
            hook = hooks.get(ev)
            if hook:
                if not (plugin_dir / hook).is_file():
                    errors.append(f"hook {ev} -> {hook} not found")
    # mcp_servers must be a list of dicts with name+command
    mcp = data.get("mcp_servers")
    if mcp:
        if not isinstance(mcp, list):
            errors.append("mcp_servers must be a list")
        else:
            for srv in mcp:
                if not isinstance(srv, dict) or not srv.get("name") or not srv.get("command"):
                    errors.append(f"mcp_servers entry missing name/command: {srv}")
    # allowed_tools must be known tools if present
    at = data.get("allowed_tools")
    if at:
        if not isinstance(at, list):
            errors.append("allowed_tools must be a list")
        else:
            for t in at:
                if t not in ALLOWED_TOOL_EXAMPLES:
                    errors.append(f"allowed_tools unknown tool: {t}")
    # contributed dirs must exist
    cont = data.get("contributes") or {}
    if isinstance(cont, dict):
        for kind, paths in cont.items():
            if not isinstance(paths, list):
                continue
            for p in paths:
                if not (plugin_dir / str(p)).exists():
                    errors.append(f"contributes.{kind} missing dir: {p}")
    return errors


def validate_core_skill(skill_dir):
    errors = []
    path = skill_dir / "SKILL.md"
    if not path.is_file():
        return [f"core skill missing SKILL.md: {skill_dir.name}"]
    text = path.read_text()
    if not text.startswith("---"):
        errors.append(f"{skill_dir.name}: SKILL.md missing YAML frontmatter")
    else:
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm = parts[1]
            if "name:" not in fm or "description:" not in fm:
                errors.append(f"{skill_dir.name}: frontmatter missing name/description")
            if "provenance: core" not in fm and "provenance: \"core\"" not in fm:
                errors.append(f"{skill_dir.name}: core skill must set provenance: core")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=Path(__file__).resolve().parent)
    ap.add_argument("--quarantine", action="store_true",
                    help="move invalid plugins to curator/archived/")
    args = ap.parse_args()

    root = Path(args.root)
    archive_dir = root / "curator" / "archived"
    failed = []

    # core skills
    core_skills = root / "core-skills"
    if core_skills.is_dir():
        for skill_dir in sorted(core_skills.iterdir()):
            if skill_dir.is_dir():
                errs = validate_core_skill(skill_dir)
                if errs:
                    failed.append(skill_dir.name)
                    print(f"  INVALID core-skill {skill_dir.name}:")
                    for e in errs:
                        print(f"    - {e}")
                else:
                    print(f"  OK     core-skill {skill_dir.name}")

    # extensions
    ext_dir = root / "extensions"
    if ext_dir.is_dir():
        for plugin_dir in sorted(p for p in ext_dir.iterdir() if p.is_dir()):
            errors = validate_plugin(plugin_dir)
            name = plugin_dir.name
            if errors:
                failed.append(name)
                print(f"  INVALID {name}:")
                for e in errors:
                    print(f"    - {e}")
                if args.quarantine:
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    dest = archive_dir / name
                    if not dest.exists():
                        shutil.move(str(plugin_dir), str(dest))
                    print(f"    quarantined -> {dest}")
            else:
                data, _ = _load_manifest(plugin_dir / "plugin.yaml")
                core = data.get("core", "?")
                points = ",".join(data.get("extension_points", []) or [])
                print(f"  OK     {name} (core={core}, points={points})")

    if failed:
        print(f"\n{len(failed)} item(s) invalid/incompatible.")
        return 1
    print("\nAll items valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
