# 使用说明

本文档补充 README 中省略的安装、运行和飞书配置细节。当前项目入口为 `main.py`，演示数据默认读取 `data/sample_bids.csv`。

## 安装

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

当前依赖保持轻量：

- `PyYAML` 读取规则配置；
- `python-dateutil` 解析日期；
- `requests` 调用飞书 Webhook。

## 运行命令

执行完整流程：

```bash
python main.py run
```

明确跳过飞书推送：

```bash
python main.py run --no-feishu
```

清空去重状态，便于重复演示：

```bash
python main.py reset-state
```

运行规则判断测试：

```bash
python -m unittest discover -s tests
```

## 输出文件

一次运行会生成或更新：

- `outputs/report.md`：线索分级、评分、命中关键词和判断原因；
- `outputs/state.json`：已经处理过的 bid id，用于减少重复推送。

报告每次都会生成。飞书推送只针对本次待关注且尚未在状态中记录的线索。

## 飞书 Webhook

环境变量名由 `config/rules.yaml` 中的 `feishu_webhook_env` 控制，当前配置为：

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

未配置 Webhook 时，程序会跳过飞书通知，报告和状态流程仍会继续完成。Webhook 请求失败时，主流程也会继续执行。

## 相关说明

- 评分项、分级约束和样例判断过程见 [decision_logic.md](decision_logic.md)。
- 上游搜索与候选公告整理的分工示例见 [openclaw_integration.md](openclaw_integration.md)。
