# OpenClaw 集成说明

## 分工原则

`telecom-bid-scout-lite` 适合放在招采搜索链路的稳定处理阶段。OpenClaw 可以负责更开放的网页探索，本项目负责更确定的规则执行。

## OpenClaw 负责

- 定时任务；
- 搜索招采信息；
- 读取网页；
- 初步整理候选公告；
- 调用本项目命令。

## 本项目负责

- 稳定规则判断；
- 线索打分；
- 去重；
- 报告生成；
- 飞书推送。

## 示例流程

每天早上，OpenClaw 可以围绕通信行业关注方向搜索：

- `语音线路 招标`
- `呼叫中心 采购`
- `短信通道 服务采购`
- `云通信 采购公告`
- `运营商专线 招标`

OpenClaw 读取搜索结果和候选网页后，先把字段整理为 CSV。当前演示可写入：

```text
data/sample_bids.csv
```

后续接真实候选池时，也可以扩展为：

```text
data/candidates.csv
```

候选数据至少建议包含：

- `id`
- `title`
- `publish_date`
- `deadline`
- `region`
- `source`
- `url`
- `summary`
- `official_entry`

整理完成后，OpenClaw 调用：

```bash
python main.py run
```

本项目会继续完成：

```text
候选 CSV
  -> 通信业务规则打分
  -> 三类决策
  -> outputs/report.md
  -> 可选飞书提醒
  -> outputs/state.json
```

## 一次日常任务示例

1. OpenClaw 在每天早上搜索通信行业关键词；
2. OpenClaw 读取公告标题、摘要、来源页面和报名入口；
3. OpenClaw 把候选公告整理成 CSV；
4. OpenClaw 在项目目录执行 `python main.py run`；
5. 业务人员在 `outputs/report.md` 查看完整解释；
6. 飞书收到“值得跟进”和“需人工复核”的未重复线索。

## 为什么这样拆分

搜索和网页读取会面对页面结构差异、结果噪音和上游信息变化，适合交给具备探索能力的 OpenClaw。评分、去重、报告和通知则需要稳定、可解释、可重复执行，适合放在本项目里。

这种拆分能让上游搜索继续迭代，同时让下游筛选结果保持稳定、可复核。
