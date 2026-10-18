"""Build all delivery forms from the self-contained skill; Python standard library only."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile

SKILL_PATH = Path("skills/paper-repro-pipeline")
RESOURCE_ORDER = [
    "references/workflow.md",
    "references/agent-operating-principles.md",
    "references/research-rigor-principles.md",
    "references/deep-learning-experiment-principles.md",
    "references/research-safety-principles.md",
    "references/research-pitfall-checklist.md",
    "templates/task-prompts.md",
    "templates/AGENTS.md",
]
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def zip_bytes(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_STORED) as z:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_STORED
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            z.writestr(entry, data)
    return buffer.getvalue()


def source_files(root: Path) -> dict[str, bytes]:
    base = (root / SKILL_PATH).resolve()
    files = {
        p.relative_to(base).as_posix(): p.read_text(encoding="utf-8").encode("utf-8")
        for p in sorted(base.rglob("*"), key=lambda p: p.relative_to(base).as_posix()) if p.is_file()
    }
    expected = {"SKILL.md", *RESOURCE_ORDER}
    if set(files) != expected:
        raise ValueError(f"Unexpected or missing skill resources: {set(files) ^ expected}")
    entry = files["SKILL.md"].decode("utf-8")
    if not re.match(r"^---\nname: paper-repro-pipeline\ndescription: .+\n---\n", entry):
        raise ValueError("Skill name/description frontmatter missing or invalid")
    for relative, data in files.items():
        text = data.decode("utf-8")
        for _, target in LINK.findall(text):
            if "://" in target or target.startswith("#"):
                continue
            path = (base / relative).parent / target.split("#")[0]
            resolved = path.resolve()
            if not resolved.is_relative_to(base) or not resolved.is_file():
                raise ValueError(f"Invalid packaged resource: {relative} -> {target}")
    return files


def render(root: Path) -> dict[str, bytes]:
    files = source_files(root)
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    body = files["SKILL.md"].decode("utf-8").split("---", 2)[2].lstrip()

    def inline_link(match: re.Match) -> str:
        label, target = match.groups()
        if target in files:
            return f'{label}（见完整手册的“资源：{target}”章节）'
        return match.group(0)

    prompt = f"<!-- Generated from skills/paper-repro-pipeline/SKILL.md; version {version}. Do not edit. -->\n\n"
    prompt += LINK.sub(inline_link, body)
    handbook = f"# 论文复现工作流 · 完整资料\n\n版本：{version}。自动生成，请修改仓库中的 skills/paper-repro-pipeline/ 源文件。\n\n"
    handbook += "与技能安装入口使用相同规则和参考资料。先读入口，再按当前阶段查资源；无需把整份手册每次重复读入。\n\n"
    handbook += "## 使用入口\n\n" + LINK.sub(inline_link, body) + "\n\n## 资源目录\n\n"
    handbook += "\n".join(f"- `{name}`" for name in RESOURCE_ORDER) + "\n\n"
    for name in RESOURCE_ORDER:
        handbook += f"---\n\n## 资源：{name}\n\n" + files[name].decode("utf-8").strip() + "\n\n"
    universal = {
        "论文复现工作流-通用手册.md": handbook.encode("utf-8"),
        "系统提示词-精简版.txt": prompt.encode("utf-8"),
        "README-怎么用.md": (root / "docs/通用使用.md").read_text(encoding="utf-8").encode("utf-8"),
    }
    install_files = {f"paper-repro-pipeline/{name}": data for name, data in files.items()}
    install_files["安装说明.md"] = (root / "docs/安装.md").read_text(encoding="utf-8").encode("utf-8")
    skill_zip = zip_bytes(install_files)
    universal_zip = zip_bytes(universal)
    output = {
        "dist/paper-repro-pipeline.zip": skill_zip,
        "dist/universal.zip": universal_zip,
        # Compatibility downloads are generated aliases, never independent editions.
        "B-DSH版.zip": skill_zip,
        "C-通用平台版.zip": universal_zip,
        **{f"dist/universal/{name}": data for name, data in universal.items()},
    }
    manifest = {
        "version": version,
        "source": SKILL_PATH.as_posix(),
        "files": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()},
    }
    output["dist/manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    archives = [name for name in output if name.endswith(".zip")]
    output["SHA256SUMS.txt"] = "".join(
        f"{hashlib.sha256(output[name]).hexdigest()}  {name}\n" for name in sorted(archives)
    ).encode("utf-8")
    return output


def build(root: Path, check: bool = False) -> None:
    output = render(root)
    stale = [
        name for name, data in output.items()
        if not (root / name).is_file() or (root / name).read_bytes() != data
    ]
    if check:
        if stale:
            raise ValueError("Generated files out of date: " + ", ".join(stale))
        print(f"PASS: {len(output)} generated outputs match source.")
        return
    for name, data in output.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(f"Built {len(output)} outputs from one skill source.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare artifacts to source without writing")
    args = parser.parse_args()
    build(Path(__file__).resolve().parents[1], args.check)
