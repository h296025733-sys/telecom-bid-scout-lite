# telecom-bid-scout-lite

中文定位：**通信行业招采线索筛选与飞书推送工具**

`telecom-bid-scout-lite` 是一个轻量、可解释、可运行的招采线索处理项目。它把通信行业候选公告从“人工逐条扫标题”拆成稳定流程：读取候选数据、按规则判断价值、生成 Markdown 报告、按需推送飞书、记录处理状态。

它不是为了伪装成大型系统，而是用一个最小闭环展示：

- 对通信业务方向的理解，例如语音线路、短信通道、呼叫中心、外呼系统、运营商专线和号码资源；
- 把业务判断拆成可维护规则的能力；
- 将 AI 或搜索代理产出的候选信息落到自动化执行链路的能力；
- 面向真实协作场景的报告、通知和去重意识。

## 1. 项目背景

通信行业招采信息分散在政府采购、公共资源交易、运营商采购平台和行业转载页面中。真正值得销售、交付或解决方案团队关注的公告，往往需要同时满足几个条件：

- 公告主题与通信资源或通信服务相关；
- 报名窗口还有效；
- 来源足够可信；
- 能找到官方公告或报名入口；
- 不把办公采购、物业服务等无关内容混进待跟进池。

如果只靠关键词搜索，候选结果会很多；如果全靠人工判断，筛选成本又会升高。本项目提供一个透明的中间层，把候选线索变成可复核的决策结果。

## 2. 解决什么问题

本项目针对已整理好的候选招采数据，完成以下工作：

1. 读取 CSV 候选公告；
2. 加载 YAML 规则；
3. 检查行业关键词、排除词、日期有效性、来源可信度、官方入口和历史状态；
4. 输出三类结果：
   - 值得跟进
   - 需人工复核
   - 不建议跟进
5. 为每条线索保留评分、命中关键词和判断原因；
6. 生成可分享的 Markdown 报告；
7. 可选推送待关注线索到飞书；
8. 将处理过的 bid id 写入状态文件，避免重复推送。

## 3. 核心流程

```text
候选公告 CSV
  -> 加载规则 YAML
  -> 规则评分与原因生成
  -> 三类决策输出
  -> Markdown 报告
  -> 可选飞书推送
  -> state.json 去重记录
```

## 判断逻辑与项目边界

本项目不是完整招采平台，而是一个轻量可运行的招采线索筛选闭环。它完整覆盖了从候选数据读取、规则判断、线索分级、原因解释、报告生成、去重记录到飞书推送预留的流程。OpenClaw 可以负责定时搜索和网页读取，本项目负责稳定筛选、判断和输出。

当前判断逻辑以 `data/sample_bids.csv` 的候选公告为输入，读取标题、摘要、发布时间、截止时间、来源、链接和官方入口等字段，再按 `config/rules.yaml` 中的通信关键词、排除关键词、高价值关键词、可信来源和分数阈值打分。

评分不是唯一依据，代码还保留了明确的风险约束：

- 过期公告即使命中通信关键词，也会被判断为“不建议跟进”；
- 缺少明确官方入口的高分线索，会从“值得跟进”降级为“需人工复核”；
- 只命中排除关键词、没有通信关键词支撑的线索，会被判断为“不建议跟进”；
- `reasons` 和 `matched_keywords` 会随结果进入报告，方便复核为什么得出这个判断。

更细的分值说明、样例判断过程和测试覆盖见 `docs/decision_logic.md`。

## 4. 项目结构

```text
telecom-bid-scout-lite/
├── README.md
├── requirements.txt
├── main.py
├── config/
│   └── rules.yaml
├── data/
│   └── sample_bids.csv
├── outputs/
│   └── .gitkeep
├── src/
│   ├── __init__.py
│   ├── loader.py
│   ├── scorer.py
│   ├── reporter.py
│   ├── feishu.py
│   └── state.py
├── docs/
│   ├── decision_logic.md
│   └── openclaw_integration.md
└── tests/
    └── test_scorer.py
```

## 5. 安装方式

要求 Python 3.10+。

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS 或 Linux：

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

项目只依赖少量轻量库：

- `PyYAML` 读取规则配置；
- `python-dateutil` 解析日期；
- `requests` 调用飞书 Webhook。

## 6. 运行方式

执行完整流程：

```bash
python main.py run
```

明确跳过飞书推送：

```bash
python main.py run --no-feishu
```

清空去重状态，方便反复演示：

```bash
python main.py reset-state
```

运行规则判断测试：

```bash
python -m unittest discover -s tests
```

运行后会生成：

- `outputs/report.md`
- `outputs/state.json`

其中报告每次都会生成；飞书推送只针对本次待关注且尚未在状态中记录的线索。

## 7. 飞书 Webhook 配置

默认环境变量名由 `config/rules.yaml` 中的 `feishu_webhook_env` 控制，当前配置为：

```yaml
feishu_webhook_env: FEISHU_WEBHOOK_URL
```

Windows PowerShell 临时配置：

```powershell
$env:FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/your-token"
python main.py run
```

macOS 或 Linux 临时配置：

```bash
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/your-token"
python main.py run
```

如果没有配置 Webhook，程序会打印跳过提示，报告和状态流程仍会继续完成。Webhook 请求失败时，主程序也不会崩溃。

## 8. 示例输出

控制台日志示例：

```text
[INFO] 读取候选招采数据：.../data/sample_bids.csv
[INFO] 加载规则配置：.../config/rules.yaml
[INFO] 当前状态中已有 0 条已处理线索。
[INFO] 报告已生成：.../outputs/report.md
[INFO] 已按参数跳过飞书推送。
[INFO] 状态已更新：.../outputs/state.json
```

报告片段示例：

```markdown
### 1. 某市政务热线呼叫中心坐席扩容及外呼系统采购公告

- 地区：广东深圳
- 来源：公共资源交易中心
- 截止时间：2026-06-05
- 判断结果：**值得跟进**
- 评分：...
- 命中关键词：呼叫中心、外呼系统
- 判断原因：命中通信方向关键词；来源可信；仍在有效期内...
```

## 9. 和 OpenClaw 的关系

本项目适合作为 OpenClaw 后面的稳定执行器。

- OpenClaw 更适合负责定时搜索、网页读取、候选公告整理和调用命令；
- 本项目负责规则判断、评分解释、报告生成、去重和通知。

这样拆分后，上游可以逐步从样例 CSV 扩展到搜索 API、网页抓取和正文提取；下游的评分和通知逻辑仍然保持稳定、可复核。

详细示例见 `docs/openclaw_integration.md`。

## 10. 面向简历和面试的项目说明

可以把这个项目描述为：

> 设计并实现通信行业招采线索筛选工具，将候选公告处理拆解为 CSV 数据接入、YAML 规则评分、可解释决策、Markdown 报告、飞书 Webhook 推送和状态去重闭环；围绕语音线路、短信通道、呼叫中心、运营商专线等业务方向构建轻量规则体系，并预留与 OpenClaw 搜索自动化集成的接口。

面试展开点：

- 为什么用可解释规则先做最小闭环，而不是直接让模型黑盒判断；
- 如何处理低可信转载来源、过期公告和缺少官方入口的风险；
- 如何让 AI 搜索代理和稳定工程流程分工；
- 如何通过状态文件降低重复通知噪音；
- 后续如何引入正文抓取、LLM 摘要和人工反馈闭环。

## 11. 后续扩展方向

- 接入 OpenClaw 定时搜索；
- 接入 Brave Search API；
- 接入企业邮箱 SMTP 生成合规触达邮件；
- 增加网页正文抓取；
- 增加可视化面板；
- 支持更多候选 CSV 或数据库输入；
- 为不同省份、运营商和产品线拆分规则模板；
- 增加飞书卡片消息和人工反馈回写。

## 12. 当前规则边界

这是一个可解释的筛选器，不是招采事实核验系统。它会把缺少官方入口、来源不可信、日期异常的候选线索降级或拒绝，但不会代替人工确认资质要求、预算条款、投标主体限制和正式报名动作。
