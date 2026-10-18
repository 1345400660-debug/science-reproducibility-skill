# 论文复现工作流 · paper-repro-pipeline

一套核心内容，两种接入方式：**安装为 Agent 技能**，或**直接使用生成的手册与提示词**。从取证、规格拆解、自实现与自证，到受控实验、结果核验和交付，所有入口共享同一份方法论。

版本：`2.0.0`。不再分别维护 B/C 正文。论文代码、数据、权重和计算环境需按实际任务准备。

## 用 npx 安装

在你希望开展论文复现的项目目录运行：

```bash
npx skills add 1345400660-debug/science-reproducibility-skill --skill paper-repro-pipeline
```

按安装器提示选择目标 Agent 和安装范围。不要在含旧同名技能的目录中直接覆盖本地修改；先备份并比较。

仅查看可安装的技能，不安装：

```bash
npx skills add 1345400660-debug/science-reproducibility-skill --list
```

要复用本次测试使用的安装器版本：

```bash
npx skills@1.7.2 add 1345400660-debug/science-reproducibility-skill --skill paper-repro-pipeline
```

本次测试的 `skills@1.7.2` 要求 Node.js `>=22.20.0`，可用 `node --version`、`npm --version` 检查本机环境。以后安装器版本的要求以其发布信息为准。

`npx` 运行的是 Vercel Labs 的 [skills 安装器](https://github.com/vercel-labs/skills)，它从 GitHub 查找 `SKILL.md` 并安装完整技能目录。本仓库不需要先发布 npm 包，也没有名为 `science-reproducibility-skill` 的自有 npm CLI。

**不要把命令改为 `npx science-reproducibility-skill`。** 那会查找同名 npm 可执行包，不是安装本仓库技能。

## 不安装也能用

- [下载完整通用资料包](dist/universal.zip)
- [直接阅读生成的完整手册](dist/universal/论文复现工作流-通用手册.md)
- [复制生成的精简指令](dist/universal/系统提示词-精简版.txt)
- [手动安装用技能 ZIP](dist/paper-repro-pipeline.zip)

把手册提供给会话或资料区，将精简指令放入可用的指令入口，再附上论文和任务。没有文件读取或终端能力时，只做当前工具能完成的分析，不把计划当作已运行结果。

| 入口 | 需要什么 | 得到什么 |
|---|---|---|
| `npx skills add` | Node.js、npm、网络与可用的 Git 获取方式；兼容的 Agent | 一个自包含技能目录 |
| 手动复制技能 | 支持技能格式的 Agent | 与 npx 相同的内容 |
| 通用资料 | 能读取文字/文件的环境，或人工阅读 | 从同一技能源生成的手册和提示词 |

## 使用前验收

在目标 Agent 中发出：

```text
请使用 paper-repro-pipeline 做只读验收，不安装依赖、不运行论文代码。
列出实际读取的技能入口、方法论与五份纪律资料；
定位方法论阶段1.4的代码可用性规则，并说明本轮未执行的操作。
如不能读取文件，报告具体路径，不要假装已加载。
```

安装成功只代表文件被放置好，不证明 Agent 已加载或遵守规则。通用入口无需技能机制，但同样需要确认手册可读。

## 开始一项复现任务

```text
使用论文复现工作流。
论文：[文件或论文编号]
目标：[指定表格、实验或待核验主张]
本轮范围：[只读分析 / 最小运行 / 已授权的有限实验]
代码与数据：[来源和位置；未知项写未知]
环境与预算：[系统、CPU/GPU、内存、最大时间]
允许操作：[联网、安装依赖、执行代码、训练的范围]
输出目录：[实际路径]

先读取现有日志与材料，核对规格和证据。
限定官方仓库时不要改成自实现；只做方案时不要运行。
已验证、未执行和无法判断分开记录。
```

更多例子：[八种任务模板](skills/paper-repro-pipeline/templates/task-prompts.md)。

## 文档

- [安装、更新与卸载](docs/安装.md)
- [普通对话和人工使用](docs/通用使用.md)
- [从旧 B/C 迁移](docs/迁移.md)
- [常见问题](docs/常见问题与升级.md)
- [维护与生成产物](docs/维护.md)
- [十分钟贡献指南](CONTRIBUTING.md)
- [验证记录](docs/文档验收记录.md)
- [版本记录](CHANGELOG.md)
- [下载校验值](SHA256SUMS.txt)

## 唯一维护源

```text
skills/paper-repro-pipeline/
├── SKILL.md                    # 可发现的技能入口
├── references/
│   ├── workflow.md             # 唯一方法论正文
│   └── 五份纪律资料
└── templates/
    ├── task-prompts.md
    └── AGENTS.md               # 可选工作区模板
scripts/build.py                # 生成通用资料、ZIP、清单和校验值
dist/                           # 自动生成，不手动修改
```

技能安装时不再依赖兄弟技能目录，也不再要求将方法论复制到项目根目录。参考链接相对于技能自身目录解析。

旧的 [B-DSH版.zip](B-DSH版.zip) 与 [C-通用平台版.zip](C-通用平台版.zip) 暂留兼容下载地址：分别是技能 ZIP 与通用 ZIP 的自动生成别名，使用同一版本号，不是两套源文件。B 包的内部布局已经改变，旧安装脚本需要迁移。

## 工作流程与证据

0 接收定位 → 1 取证 → 2 规格拆解 → 3 最小运行 → 4 实现 → 5 自证 → 6 受控实验 → 7 推断 → 8 核验 → 9 交付。

默认保留 `报告/`、`代码与图表/`、`过程记录/`；已有项目布局时沿用并记录映射。每次运行记录命令、环境、配置、种子、数据版本、日志与结果位置。

适合可通过数值实验核查的论文。专用硬件、纯理论或不可获取数据需要另定验证方法。历史案例数字属于对应配置和环境，不是新项目的预期结果。

规则审查、情景干跑、构建和安装验证都不能代替真实论文训练或结论复核。具体证据及未测试部分见验证记录。

## 当前案例：TTN-CP

本方法目前以 `Machine learning with tree tensor networks, CP rank constraints, and tensor dropout`
作为公开工作流案例。当前状态为 **A→B→C 最小验证已通过**：

- **A**：环境、核心数学路径和复数 CP 前向检查通过；
- **B**：梯度、dropout 无偏性、独立路径一致性和小规模学习检查通过；
- **C**：Fashion-MNIST 小样本训练入口完成 1 个 epoch，并写出结构化 JSON 结果。

这些检查证明工作流可以被重走，但不自动等于论文全部指标已经复现。论文指标、差异分析和仍无法判断的实验必须继续链接到各自的原始日志；短跑准确率不能替代论文级结果。
