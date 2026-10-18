# B 版安装与验收

本文适用于 `B-DSH版.zip`。先在独立论文工作区安装。是否自动发现技能、是否读取工作区约定，取决于 Agent 宿主。

## 1. 安装前确认

需要一个能读取本地 Markdown 的 Agent、已确认的技能根目录及加载方式、一个论文项目目录。没有技能机制时使用 C 版。

安装本包无需先训练。具体论文的代码、数据、运行依赖及计算资源需另行准备。

## 2. 下载与解压

下载 `B-DSH版.zip`，解压到暂存目录。Windows PowerShell 示例，在 ZIP 所在目录执行：

```powershell
Expand-Archive -LiteralPath '.\B-DSH版.zip' -DestinationPath '.\B-DSH-unpacked'
```

其他系统可用归档管理器，或在具备 `unzip` 时执行：

```bash
unzip 'B-DSH版.zip' -d B-DSH-unpacked
```

使用尚不存在的目标，避免新旧文件混合。解压后应直接看到：

```text
安装说明.md
AGENTS.md模板.md
复现工作流/
  速查卡.md
  复现工作流.md
  实测记录.md
  README.md
skills/
  paper-repro-pipeline/SKILL.md
  ai-research-reproduction/references/
    agent-operating-principles.md
    research-rigor-principles.md
    deep-learning-experiment-principles.md
    research-safety-principles.md
    research-pitfall-checklist.md
```

只看到另一个 ZIP 时，说明还需要解压 B 分发包。

## 3. 放置文件

### 方法论

把整个 `复现工作流/` 复制到论文项目根目录，例如：

```text
D:/research/my-reproduction/复现工作流/速查卡.md
D:/research/my-reproduction/复现工作流/复现工作流.md
```

让 Agent 打开 `D:/research/my-reproduction` 作为工作区。工作区根目录和技能目录是两个不同位置。

### 技能与参考文件

把 `skills/` 内两个目录复制到宿主支持的技能根目录，保持：

```text
<技能根目录>/
├── paper-repro-pipeline/SKILL.md
└── ai-research-reproduction/references/五份文件
```

宿主支持项目级 `.agents/skills/` 时，可用 `<论文项目>/.agents/skills/`。其他宿主使用其实际支持的路径，本说明不保证所有平台都扫描这个目录。

- 不要复制成 `<技能根目录>/skills/paper-repro-pipeline/`，除非宿主明确支持额外层级。
- 本包 `ai-research-reproduction/` 只有参考材料，没有独立 `SKILL.md`，这是包的设计。
- 已有同名完整技能时先备份、比较并合并，不要替换整个目录。
- 项目级和用户级存在两份同名技能时，确认宿主究竟读取哪份。

### 工作区约定

没有 `AGENTS.md` 时，将 `AGENTS.md模板.md` 复制到项目根目录并改名为 `AGENTS.md`。

已有该文件时合入论文复现条款，保留原项目约定。宿主不使用这个文件名时，把规则放入它实际使用的工作区指令入口。

它表达“复现前应读什么”的约定，不会改变工具权限，也不保证模型一定遵守，所以还需要验收。

## 4. 替换路径

打开安装后的 `paper-repro-pipeline/SKILL.md`：

1. 将 `<工作区根目录>` 替换为实际论文项目路径，例如 `D:/research/my-reproduction`。
2. 确认方法论指向该项目的 `复现工作流/`。
3. 保留 `../ai-research-reproduction/references/`，它相对于 `paper-repro-pipeline/` 目录解析，不是 shell 当前目录。
4. 检查合入的工作区约定，清除路径占位符。

不要把示例用户名、盘符或历史案例路径当作本机路径。

## 5. 必需材料与可选增强

| 材料 | 是否随包 | 缺失时怎么办 |
|---|---|---|
| `paper-repro-pipeline/SKILL.md` | 是 | 恢复文件，确认技能识别路径 |
| 方法论速查卡、详细文档 | 是 | 停止实质复现，修复路径 |
| 五份 `references/*.md` | 是 | 任一不可读都先修复，不凭记忆跳过 |
| `实测记录.md` | 是 | 案例参考；具体任务需要时应保证可读 |
| `safe-debug`、`run-train`、`ai-research-explore` 等增强技能 | 否 | 按映射表的可选降级说明使用方法论，不声称加载了未安装技能 |

不要为了读五份纪律文件而启动另一套编排流程。本包参考目录不等于完整的 `ai-research-reproduction` 技能。

旧安装说明中“五份纪律文件缺失可跳过”的说法已撤销。B 版必须先修复必读文件；C 版的安装契约不同。

## 6. 验收第一步：检查路径

以下 PowerShell 命令适用于项目级 `.agents/skills/` 布局，在论文项目根目录执行。技能根不同则先修改 `$skillRoot`：

```powershell
$skillRoot = Join-Path (Get-Location) '.agents/skills'
$required = @(
    (Join-Path (Get-Location) '复现工作流/速查卡.md'),
    (Join-Path (Get-Location) '复现工作流/复现工作流.md'),
    (Join-Path $skillRoot 'paper-repro-pipeline/SKILL.md')
)
$referenceNames = @(
    'agent-operating-principles.md',
    'research-rigor-principles.md',
    'deep-learning-experiment-principles.md',
    'research-safety-principles.md',
    'research-pitfall-checklist.md'
)
foreach ($name in $referenceNames) {
    $required += Join-Path $skillRoot "ai-research-reproduction/references/$name"
}
$missing = @($required | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
if ($missing.Count -gt 0) {
    $missing
    throw '安装文件缺失，请先修复路径。'
}
'PASS：8个核心文件存在。下一步验证Agent实际读取。'
```

此步骤只确认文件存在，不验证宿主注册或模型遵从。

## 7. 验收第二步：实际读取

在目标工作区向 Agent 提问：

```text
请做只读安装验收，不运行论文代码、不安装依赖：
1. 用宿主支持的方式加载 paper-repro-pipeline；
2. 报告实际读取的SKILL.md、速查卡和五份纪律文件路径；
3. 每份给一个可定位的小节名或简短要点；
4. 说明哪些增强技能已安装、哪些未安装；
5. 说明核心文件缺失如何处理，以及本轮未执行的操作。
发现失败时报告路径和错误，不要假装已加载。
```

通过条件：读取的是新副本；参考材料和方法论实际可读；可选增强缺失不会误报核心安装失败；没有擅自安装环境、下载数据或训练。

识别失败时检查目录、宿主配置与格式支持；按宿主要求刷新或重开会话后再验收。无法确认兼容性时用 C 版。

## 8. 开始使用与升级

验收后先选择小目标：规格核对、官方入口审查或最小运行。完整训练需要给出计算预算和执行范围。

升级前备份本地修改，在新目录解压，并一起比较技能、方法论、参考文件和模板。保留本地路径替换后重新验收，不覆盖自己的报告、代码或数据。

最终研究结论以真实命令、配置、日志和独立验证为依据。
