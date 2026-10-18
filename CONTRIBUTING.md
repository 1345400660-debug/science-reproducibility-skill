# 贡献指南：十分钟完成第一次改动

本仓库只有一套维护源：`skills/paper-repro-pipeline/`。`dist/`、ZIP、通用手册、清单和校验值都由构建脚本生成，不能手工编辑。

## 1. 获取仓库并确认环境

需要 Python 3.10 或更高版本。克隆仓库后进入项目目录：

```bash
git clone https://github.com/1345400660-debug/science-reproducibility-skill.git
cd science-reproducibility-skill
python --version
```

## 2. 运行现有检查

```bash
python scripts/build.py --check
python -m unittest discover -s tests -v
```

两条命令都通过后再修改文件。`build.py --check` 会发现生成产物是否过期，测试会检查构建是否可重复、引用是否完整，以及技能和通用资料是否来自同一套源文件。

## 3. 修改正确的位置

- 技能规则：修改 `skills/paper-repro-pipeline/SKILL.md`
- 方法论：修改 `skills/paper-repro-pipeline/references/workflow.md`
- 纪律资料：修改同目录下对应的 `references/` 文件
- 任务模板：修改 `skills/paper-repro-pipeline/templates/`
- 安装和使用说明：修改 `docs/`
- 不要直接修改 `dist/`、ZIP、`manifest.json` 或 `SHA256SUMS.txt`

每条相对链接都必须指向技能目录内存在的文件。修改后重新运行：

```bash
python scripts/build.py
python scripts/build.py --check
python -m unittest discover -s tests -v
```

## 4. 提交前自查

- 是否把实际验证、计划和推断分开？
- 是否新增了不受证据支持的“已复现”表述？
- 是否保留了现有用户授权范围，而不是无条件重新要求批准？
- 是否同步更新了必要的文档和变更记录？
- `git diff --check` 是否通过？

提交信息应说明行为变化，例如：

```text
docs: clarify evidence status for minimal runs
```

提交 Pull Request 时，请附上修改原因、运行过的检查命令和仍未验证的边界。
