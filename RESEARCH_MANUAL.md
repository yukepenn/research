# 四篇高价值 Agent 论文：Claude 全自主研究作战手册

> 用法：把本文件完整交给 Claude。不要让它只给出计划；要求它在有 Web、Shell、Git、容器、模型 API 与计算资源的环境中，按照状态机持续执行，直到形成可复现结果、完整论文和投稿包。

## 0. Claude 的总任务

你是这个研究计划的 Research Director、实验负责人和论文工程负责人。目标不是“生成四篇看起来像论文的文本”，而是并行完成四个可证伪、可复现、可投稿的研究项目：

1. **ToolMorph**：工具接口的语义等价性与 Agent 鲁棒性；
2. **CrossCheck**：异构模型代码审查的错误互补性与预算感知路由；
3. **DeltaResearch**：证据更新下 Deep Research 报告的选择性修订；
4. **HarnessGuard**：Agent Harness 自动修改后的隐藏回归预测与 Canary 选择。

你的默认行为是直接执行所有可逆、合规的内部动作，不要停在建议、头脑风暴或“下一步可以做什么”。创建仓库、检索论文、实现代码、构造任务、运行 pilot、分析结果、写作、做反向审稿。只有下列事项需要人类明确确认：

- 对外正式投稿、公开发布、联系作者或机构；
- 超出预设经费上限的付费 API/云资源；
- 涉及许可、隐私、人体参与者或法律风险的动作；
- 最终中心 claim、作者名单与投稿 venue；
- 任何不可逆删除、覆盖或公开动作。

“激进”意味着快速并行、早测、早杀、证据优先；不意味着夸大结果、伪造引用、泄漏测试集、违反网站条款或把弱结果包装成顶会贡献。

---

# 1. 不可违反的研究规则

## 1.1 证据规则

- 论文中的每个数字必须来自不可变实验账本，禁止手写结果。
- 每张表和图必须由脚本从原始账本重新生成。
- 每个事实性文献 claim 必须链接到原论文中的具体章节、表、图或实验，而不是只看搜索摘要。
- 不允许引用不存在、未打开、未核验或无法定位原文的论文。
- 任何 LLM judge 只能作为次级指标；主要结论必须至少有一种确定性 oracle、隐藏测试、状态差分、结构化 gold label 或人工双标支持。
- 负结果必须保留。不得在看到完整结果后重写假设并伪装成预注册结论。

## 1.2 实验完整性规则

- 全部实验记录精确模型快照、日期、system prompt hash、harness commit、工具版本、随机种子、温度、预算、费用、延迟和原始轨迹 hash。
- 任务、仓库、工具族、证据来源和 Harness edit 必须按组切分，不能随机把同一来源的近重复样本分到 train/test。
- Pilot 只用于估算效应和方差；完整实验前冻结 primary endpoint、分析计划和 kill criterion。
- 重复运行属于同一任务下的嵌套观测，不能当作独立样本扩大显著性。
- 对二元成功率优先使用 paired design、cluster bootstrap、McNemar 或分层 logistic model；聚类单位分别是 task、repository、evidence world 或 harness edit。
- 多重次级检验使用 Benjamini–Hochberg；primary hypothesis 不做事后替换。
- 如果 effect 只在某个模型版本、某个 prompt 或某个 benchmark 上成立，必须降级 claim。

## 1.3 信息隔离规则

- 每篇论文建立 `dev`, `validation`, `sealed_test` 三套数据。
- 方法开发 Agent 不得读取 sealed test 的标签、隐藏测试或任务答案。
- Test Custodian 只返回聚合指标与错误代码，直到 protocol freeze。
- 对模型生成任务，生成者、执行者和评分者不能是同一个上下文中的同一个模型实例。
- 对 CrossCheck，reviewer 不能看到 author 的隐藏 reasoning；只看到规范允许的 issue、diff、仓库上下文和可见测试。
- 对 DeltaResearch，更新 Agent 不得看到 gold affected-claim set。
- 对 HarnessGuard，canary selector 不得读取 full-suite regression labels of held-out edits。

## 1.4 安全与权限边界

允许使用 Web、Shell、Git、Docker、数据库、模型 API 和云计算，但：

- 只测试自有、公开许可或明确授权的代码与服务；
- 不扫描或攻击第三方生产系统；
- 不使用泄漏的 reviewer 信息、隐藏 benchmark 测试或私有数据；
- 不把 API key、个人数据、模型未公开 prompt 写入 artifact；
- 代码缺陷研究以通用正确性和可靠性为主，不以真实目标漏洞利用为目标；
- 所有可能破坏环境的 Agent 行为只在容器、快照或 disposable VM 内运行。

---

# 2. 研究项目状态机

每篇论文只能处于以下状态之一：

```text
IDEA
→ NOVELTY_AUDIT
→ NOVELTY_PASS
→ PILOT_RUNNING
→ PILOT_PASS
→ PROTOCOL_FROZEN
→ FULL_STUDY
→ REPRODUCED
→ DRAFTED
→ REDTEAM_PASS
→ SUBMISSION_READY
→ SUBMITTED

任何阶段均可进入：KILLED 或 MERGED
```

进入下一阶段必须生成相应 artifact：

| Gate | 必需输出 |
|---|---|
| Novelty Pass | `related_work.csv`, `novelty_matrix.md`, `research_contract.yaml` |
| Pilot Pass | pilot 原始账本、效应图、power analysis、go/no-go memo |
| Protocol Frozen | `preregistration.md`, sealed test manifest、统计脚本空壳 |
| Full Study | 完整原始账本、失败样本、成本报告 |
| Reproduced | 独立 worktree 重跑、hash 对照、复现报告 |
| Drafted | 主文、附录、数据卡、模型卡、限制与伦理 |
| Redteam Pass | 三轮拒稿模拟及逐项修复记录 |
| Submission Ready | 匿名 PDF、artifact、checklist、LLM 使用披露、投稿元数据 |

禁止为了“凑四篇”跳过 kill gate。顶级研究的激进打法是尽早杀死没有信号的方向。

---

# 3. 统一仓库与运行基础设施

创建 monorepo：

```text
agent-research-lab/
├── CLAUDE.md
├── pyproject.toml
├── Makefile
├── program/
│   ├── board.yaml
│   ├── decisions.md
│   ├── budget.yaml
│   ├── risks.md
│   └── status/
├── core/
│   ├── adapters/              # 模型/API/CLI 适配
│   ├── agents/                # 统一 agent loop
│   ├── tracing/               # event schema, trajectory hash
│   ├── environments/          # Docker/VM/状态重置
│   ├── oracles/               # 确定性评分
│   ├── experiment_registry/   # manifest 和账本
│   ├── statistics/            # paired bootstrap, mixed models
│   ├── plotting/              # 仅由账本生成
│   └── anonymization/
├── papers/
│   ├── p1_toolmorph/
│   ├── p2_crosscheck/
│   ├── p3_deltaresearch/
│   └── p4_harnessguard/
├── artifacts/
├── sealed_tests/
└── releases/
```

每篇论文再建立独立 Git worktree 和 issue board。共享基础设施可以复用，但四篇的中心命题、主数据、primary endpoint、main figure 和结论必须可独立成立。

## 3.1 运行账本 schema

每次模型调用或完整 episode 至少记录：

```json
{
  "run_id": "uuid",
  "paper_id": "p1|p2|p3|p4",
  "git_commit": "sha",
  "task_id": "stable-id",
  "task_group": "repo/tool-family/world/edit-family",
  "environment_hash": "sha256",
  "model_provider": "provider",
  "model_exact_id": "snapshot-id",
  "agent_harness": "name",
  "harness_commit": "sha",
  "system_prompt_hash": "sha256",
  "tool_schema_hash": "sha256",
  "seed": 0,
  "temperature": 0.0,
  "max_tokens": 0,
  "input_tokens": 0,
  "output_tokens": 0,
  "usd_cost": 0.0,
  "latency_ms": 0,
  "status": "success|fail|timeout|invalid",
  "oracle_version": "sha",
  "raw_trace_uri": "content-addressed-path",
  "result": {},
  "created_at_utc": "ISO-8601"
}
```

账本使用 append-only Parquet/JSONL；每次分析先验证 hash。建立 `make reproduce-main-tables`，从空的 `generated/` 目录重建论文所有表图。

## 3.2 Agent 团队

每篇建立独立角色，角色之间使用不同上下文：

- **PI Orchestrator**：维护状态机、依赖、预算和最终决策包。
- **Literature Scout**：只找原论文、代码和官方 venue 规则。
- **Novelty Prosecutor**：目标是证明选题不新，寻找最强撞题。
- **Protocol Designer**：定义可证伪假设、主要指标、样本单位和停止规则。
- **Dataset Engineer**：构建数据、许可证清单、去重和 sealed split。
- **Codex Builder**：实现 runner、环境、oracle、数据流水线。
- **Independent Reproducer**：在全新 worktree/容器中盲复现。
- **Statistician**：在看 sealed-test 结果前冻结分析。
- **Failure Auditor**：抽样阅读轨迹，寻找替代解释。
- **Reviewer 2**：以拒稿为目标，不能参与原始实现。
- **Citation Auditor**：逐条核验引用和 related-work claim。
- **Paper Writer**：只能读取冻结的 claim registry 和结果表，不得发明结果。

## 3.3 Claim registry

每篇维护 `claims.csv`：

```text
claim_id,claim_text,claim_type,required_evidence,evidence_files,status,allowed_strength,notes
```

状态只允许：`UNTESTED`, `SUPPORTED`, `PARTIAL`, `REFUTED`, `DROPPED`。正文只能出现 `SUPPORTED` 或明确标为限制/负结果的 `PARTIAL/REFUTED`。

---

# 4. 四线并行调度

## Sprint A：共同基础设施与撞题审计

四线同时执行：

1. 每篇检索至少 40 篇近邻原论文；前 15 篇必须精读方法和实验，而不是只读摘要。
2. 建立 novelty matrix：问题、数据、方法、指标、模型、贡献、与本项目重叠程度。
3. 建立统一 agent runner、模型适配、容器、账本和统计库。
4. 创建每篇的最小任务集与 deterministic oracle。
5. 输出 `fatal_overlap.md`：若任何近邻论文已覆盖核心 claim，立即重写 claim 或 kill。

## Sprint B：四个决定生死的 pilot

同时运行四个小规模实验。Pilot 的任务不是得到漂亮平均分，而是回答：

- 现象是否真实；
- effect 是否大到值得继续；
- oracle 是否可靠；
- 主要替代解释是否可排除；
- 全量实验是否在预算内。

## Sprint C：冻结协议与扩展方法

只对 Pilot Pass 的方向：

- 冻结 primary endpoint；
- 锁定 sealed split；
- 完成 power analysis；
- 实现强基线和 proposed method；
- 先在 dev 上调试，不看 sealed test。

## Sprint D：完整实验与独立复现

- 并行跑 full matrix；
- 运行中只允许检查故障率和基础设施健康，不允许根据 test 效果改方法；
- 完成后一次性解封；
- 独立复现主表和 main figure；
- 人工审计关键成功、失败和异常样本。

## Sprint E：论文与投稿包

每篇同时启动写作、artifact 和 reviewer red-team。写作顺序必须是：

```text
主图 → 结果表 → claim registry → 论文大纲 → 方法/实验 → 引言/摘要
```

禁止先写宏大引言再寻找支持证据。

---
# 5. Paper 1 — ToolMorph

## 5.1 暂定标题

**ToolMorph: Metamorphic Testing and Semantic Normalization for Tool-Using Agents**

备选标题：

- *Do Tool-Using Agents Respect Semantic Interface Equivalence?*
- *Interface Invariance for LLM Agents*
- *Semantic ABI for Reliable Tool-Using Agents*

不要在标题中承诺“universal”或“formal guarantee”，除非完整结果支持。

## 5.2 一句话中心命题

在底层工具状态转换完全相同的情况下，仅改变模型可见的接口表示，就会显著改变 Agent 的成功率、错误类型、成本甚至模型排名；一个不依赖具体变换标签、可在 held-out 工具和变换上工作的语义规范化层，可以降低这种敏感性。

## 5.3 与最近工作的边界

必须明确避开以下已有贡献：

- 只研究工具描述如何改写；
- 只研究 JSON schema 压缩或文本化；
- 只研究工具数量扩张下的发现/检索；
- 只构建 MCP 工具使用 benchmark；
- 只证明 schema drift 会造成失败。

本论文的唯一核心边界是：

1. **以环境状态转换为准定义接口等价**，而不是以名称或 schema 相似度为准；
2. **使用 metamorphic paired evaluation**，同一任务、同一初始状态、同一模型，只替换等价接口；
3. **测量模型排名稳定性和错误机制**；
4. **提出在未知变换上仍工作的 semantic normal form / ABI**，而不是为每个接口手工改 prompt。

重点核对并引用：TSCG、工具描述重写、MCP-Atlas、MCP-Bench、ToolSandbox/τ-bench 类工作、工具 schema 鲁棒性工作。`Novelty Prosecutor` 必须制作一张“我们没有重复什么”的表。

## 5.4 形式化

定义状态型工具环境：

- 环境状态 `s ∈ S`；
- 抽象语义动作 `a ∈ A*`；
- 环境转移 `T(s, a) -> (s', o)`；
- 工具接口 `I` 将模型输出 `x` 解码为抽象动作，并将观察编码给模型。

接口 `I1` 与 `I2` 在状态 `S_valid` 上严格等价，当存在可逆 codec，使得对所有有效 `s` 和抽象动作 `a`：

```text
T1(s, encode_I1(a)) == T2(s, encode_I2(a))
```

且观察解码后保留完成任务所需的信息。对随机性工具，比较转移分布或固定共同随机种子。

区分两种层级：

- **Strict interface equivalence**：一次逻辑动作对应一次调用，资源需求近似相同；作为主实验。
- **Workflow equivalence**：一个接口把动作拆分/合并，语义可达状态相同但交互成本不同；只作为扩展实验，不能与 strict 结果混为一谈。

## 5.5 研究问题与假设

### RQ1：等价接口会不会改变 Agent 能力？

- H1：至少一种严格等价变换在 paired task 上造成显著成功率下降。
- H2：接口效应与模型家族、任务长度和工具歧义存在交互。

### RQ2：影响是否只是 token 长度或 prompt 风格？

- H3：在 schema token 数、描述长度和信息量匹配后，结构变换仍有独立效应。

### RQ3：模型排名是否对接口不稳定？

- H4：同一组模型在不同等价接口上的排名存在可复现翻转；Kendall rank correlation 显著低于 1。

### RQ4：语义规范化能否恢复鲁棒性？

- H5：自动 semantic normalizer 在未见工具族与未见变换族上，改善 success、call validity 和 ranking stability。

### RQ5：哪些变换最伤害哪些模型？

这是机制性次级问题，不得替代 primary endpoint。

## 5.6 数据与环境

### 主任务集

建立 6 个状态型微型业务域，每域 12–20 个任务：

1. Calendar：创建、移动、取消、冲突检查；
2. Email：搜索、草拟、回复、附件、线程；
3. CRM：客户、机会、状态、备注；
4. Inventory/Orders：库存、订单、退款、批次；
5. Helpdesk：ticket、priority、assignment、status；
6. Files/Workspace：文件、权限、目录、元数据。

每个任务满足：

- 3–8 个真实状态转换；
- 有明确初始状态 snapshot；
- 有确定性最终状态 oracle；
- 有至少一种合法多解时，oracle 按不变量而不是固定轨迹评分；
- 不依赖外网实时状态；
- 可在 Docker 中重置。

完整任务目标：72–120 个。Pilot 只用 24–30 个，且覆盖所有域。

### 可选外部验证

在自建环境稳定后，选择一个公开 stateful agent benchmark 做外部验证。外部 benchmark 只承担 generalization，不承担主要变换开发，避免针对 benchmark 过拟合。

## 5.7 Tool Transformation DSL

实现 `transform.yaml`：

```yaml
id: nested_to_flat_v1
family: structural
strict_equivalence: true
preconditions:
  - no_ambiguous_field_collision
request_codec:
  type: flatten
  mapping:
    customer.name: customer_name
    customer.id: customer_id
response_codec:
  type: identity
error_codec:
  type: identity
property_tests: 1000
```

主实验至少包含 6 个 strict families：

1. **Lexical aliasing**：工具名和参数名使用不同但清楚的同义表达；
2. **Structural nesting**：嵌套对象与平铺字段之间可逆转换；
3. **Enum encoding**：自然语言枚举、短代码、整数枚举之间无损映射；
4. **Optional/default exposure**：隐式默认与显式必填值之间等价转换；
5. **Response representation**：字段重命名、层级变化、表格/JSON 的无损结构转换；
6. **Error representation**：结构化错误码、typed exception 和等价自然语言错误之间转换。

扩展 families：

- 日期、时区和单位的无损标准化；
- pagination 的等价封装；
- batch vs sequential；
- split/merge tool granularity；
- MCP/function-call/code API 外壳转换。

扩展 family 必须单独报告交互成本，不得声称严格等价。

### 等价性验证

每个 transform 必须通过：

- property-based request round-trip；
- response round-trip；
- 随机状态下 1,000 次以上状态转移对照；
- failure path 对照；
- 信息保留测试；
- 人工抽查 20 个边界案例。

任何 transformation 若存在非零 semantic mismatch，先修复，不能把 benchmark bug 当模型错误。

## 5.8 Proposed Method：Semantic Tool Normal Form（STNF）

不要只做 oracle inverse mapping。实现两个层次：

### Upper bound：Oracle Canonicalizer

利用已知 transform mapping 把所有接口还原成 canonical schema。它只用于回答“接口归一化理论上能恢复多少”，不能作为最终方法贡献。

### 实用方法：Automatic STNF Compiler

输入：工具名、描述、JSON/OpenAPI schema、少量安全 probe 示例或本地类型信息；不能读取 transform ground truth。

输出统一 contract：

```json
{
  "intent": "calendar.event.create",
  "arguments": [
    {"semantic_type":"person_or_email", "role":"attendee", "cardinality":"many"},
    {"semantic_type":"datetime", "role":"start", "timezone_policy":"explicit"}
  ],
  "effects": ["calendar.event.created"],
  "preconditions": [],
  "idempotency": "non_idempotent",
  "errors": ["conflict", "permission", "invalid_argument", "not_found"],
  "returns": ["event_id", "normalized_start", "attendees"]
}
```

Compiler pipeline：

1. 静态解析 schema；
2. 语义类型推断；
3. 同类参数与效果映射；
4. probe executor 验证返回与错误；
5. contract consistency checker；
6. 生成模型可见的统一 schema；
7. runtime codec 将 canonical call 映射回原始接口。

需要三种版本做消融：

- static only；
- static + LLM semantic inference；
- static + LLM + executable probes。

## 5.9 Baselines

至少比较：

- 原始接口；
- 变换接口，无修复；
- token/长度匹配后的描述重写；
- few-shot tool-call examples；
- deterministic schema text/compiler baseline；
- LLM 重写工具描述；
- Oracle Canonicalizer；
- Automatic STNF。

公平性要求：

- 所有方法记录额外 token、额外 probe、延迟和费用；
- 不允许 STNF 获得基线看不到的任务答案；
- prompt 内容和 tool ordering 固定；
- 对各模型使用同一 agent loop；
- Claude Code/Codex CLI 的产品级结果只能作为生态验证，不能作为主因果证据，因为产品 harness 不同。

## 5.10 Pilot

建议 pilot matrix：

```text
24 tasks
× 2 model families
× (original + 4 strict transforms)
× 3 repetitions
= 720 episodes
```

Pilot 还需：

- 选 8 个任务跑 Oracle Canonicalizer；
- 对失败轨迹做 50 个样本的人工分类；
- 对 transformation property tests 做零容忍验证。

### Pilot Pass 条件

同时满足：

- 至少一个 strict family 出现稳定、非微小的 paired degradation；
- effect 不完全由 token 长度解释；
- 至少两个模型或两个任务域表现出该现象；
- oracle canonicalization 恢复明显比例的损失；
- 主要错误可以被分类为接口理解/调用/反馈问题，而非环境 bug。

### Pilot Kill/Rewrite 条件

- 所有 strict effects 都接近噪声；
- 只有工具重命名这类表面现象；
- property tests 证明“等价”实际不等价；
- 增加极少 few-shot 就完全消除现象且无 generalization 问题；
- 自动 STNF 在 held-out 上无法超过简单描述重写。

## 5.11 Full Study

建议最小强版本：

```text
72 tasks
× 3 model families
× (original + 6 strict transforms)
× 2 repetitions
≈ 3,024 paired episodes
```

再对最有伤害的 3 个 transform families 做方法比较：

```text
72 tasks × 3 models × 3 transforms × 5 methods × 2 repeats
```

使用 sequential elimination：若某基线在 dev 上明确支配，可减少 sealed-test 运行，但规则必须预先写入 protocol。

### Split

- dev/test 按完整 tool family 切分；
- held-out transform family 至少 1 个；
- held-out domain 至少 1 个；
- 自动 compiler 的任何 prompt/example 不得引用 test 工具。

## 5.12 Primary 与 Secondary Metrics

### Primary

- Paired task success difference：`P(success|mutated) - P(success|original)`；
- STNF 对 held-out mutation 的 recovery ratio；
- task-clustered 95% CI。

### Secondary

- invalid call rate；
- semantic argument error；
- error recovery rate；
- token/cost/latency；
- model ranking Kendall τ；
- interface sensitivity per task/model；
- compiler contract accuracy；
- state-transition correctness。

不要创造十几个相似综合指标。主文只保留最易解释的 4–6 个。

## 5.13 统计方案

- 成功率使用 task-level paired bootstrap 与 mixed-effects logistic regression；
- fixed effects：transform、model、task length、schema length；
- random intercept：task、tool family；
- 交互：transform × model；
- 排名稳定性通过 bootstrap over tasks 给 Kendall τ CI；
- compiler 消融使用 held-out tool family；
- 明确区分 confirmatory 与 exploratory 分析。

## 5.14 必须出现的图表

1. **Figure 1**：同一抽象工具在多种等价接口下的状态转换示意；
2. **Figure 2**：Transformation DSL 与 property-test 流程；
3. **Figure 3**：模型 × transform 的 paired degradation heatmap；
4. **Figure 4**：接口变化导致的模型排名翻转；
5. **Figure 5**：STNF 在 held-out transform/tool 上的 recovery–cost frontier；
6. **Table 1**：任务、工具、变换和 oracle 统计；
7. **Table 2**：主结果；
8. **Table 3**：compiler 消融与错误分类。

## 5.15 论文结构

1. Introduction：接口不应成为隐藏 benchmark variable；
2. Formal Problem：state-transition equivalence；
3. ToolMorph Benchmark：任务、DSL、验证；
4. Empirical Study：敏感性与 ranking reversal；
5. STNF Method；
6. Experiments；
7. Failure Analysis；
8. Related Work；
9. Limitations/Ethics；
10. Conclusion。

## 5.16 预判审稿攻击

- **“你们只是改 schema”**：强调状态转移等价、paired design、held-out transformations。
- **“变换是人工的”**：加入真实 MCP/OpenAPI schema 变体和外部 benchmark。
- **“canonicalizer 知道答案”**：严格区分 oracle upper bound 与 automatic compiler。
- **“只对某个模型有效”**：至少三家族与 model × transform interaction。
- **“split/merge 不等价”**：主结论只基于 strict families。
- **“统计伪重复”**：task 为聚类单位。

## 5.17 最小可投稿与旗舰版本

- **最小可投稿**：严谨的 metamorphic benchmark + 多模型 ranking instability + 强 failure analysis，可投 TMLR。
- **旗舰版本**：Automatic STNF 在 held-out tool/transform/model 上显著恢复鲁棒性，可冲 MLSys/ICLR。

## 5.18 输出清单

```text
p1_toolmorph/
├── research_contract.yaml
├── related_work.csv
├── novelty_matrix.md
├── transforms/
├── property_tests/
├── environments/
├── compiler/
├── protocols/
├── experiments/
├── analysis/
├── paper/
└── artifact/
```

# 6. Paper 2 — CrossCheck

## 6.1 暂定标题

**CrossCheck: Error-Correlation-Aware Heterogeneous Review for Coding Agents**

备选：

- *When Does a Second Coding Model Actually Help?*
- *Budget-Matched Cross-Model Review for Repository-Level Coding Agents*
- *ReviewRoute: Routing Coding Patches by Predicted Error Complementarity*

## 6.2 一句话中心命题

异构模型互审并不天然优于同模型自审或给作者更多计算；它的净收益取决于作者—审查者在具体缺陷类型上的错误互补性。通过严格预算匹配、双向 author–reviewer 矩阵和 held-out repository 路由，可以预测什么时候调用第二模型真正值得。

## 6.3 与最近工作的边界

不能把以下内容当作新贡献：

- 多 Agent 或 cross-model critic 能发现错误；
- LLM 可以做 code review；
- 多数投票或模型 ensemble 有时提升；
- 让另一个模型看 diff 再给建议；
- 只展示 Claude 与 Codex 的 anecdotal case study。

论文必须包含四个不可缺少的差异：

1. **严格预算匹配**：cross-review 与同模型加倍预算、重采样、独立重做进行公平比较；
2. **双向、全矩阵设计**：每个模型既做 author 又做 reviewer，避免把“更强模型”误认为“异构互补”；
3. **缺陷类型级 error correlation**：解释何时互补，而不是只报平均分；
4. **预先路由**：在真正花第二份预算前预测 `no review / self / same-family / cross-family / test generation / reimplementation`。

重点精读并区分：Refute-or-Promote/Cross-Model Critic、code-review benchmarks、multi-agent team failures、LLM ensemble complementarity、SWE-bench 类 coding-agent evaluation。

## 6.4 研究问题与假设

### RQ1：异构 review 在等预算下是否有效？

- H1：平均而言，异构 review 不一定支配所有基线；收益集中在特定 defect/category/task 区域。
- H2：至少存在稳定的 author–reviewer pair，在相同费用或 token 下优于 author extra-compute 和 same-family review。

### RQ2：收益是否来自模型更强，而不是互补？

- H3：控制 reviewer 单独解决能力后，pair-specific complementarity 仍能解释 review gain。

### RQ3：review 会不会引入新回归？

- H4：某些 review workflow 会提高发现率但同时引入非零 regression rate；最终 patch correctness 必须优于 detection-only 指标。

### RQ4：能否在调用 reviewer 前做路由？

- H5：使用任务、diff、测试和 author trace 特征的 router，在 held-out repositories 上改善 cost–correctness Pareto frontier。

## 6.5 主实验必须区分两个层次

### Level A：模型层实验（主因果证据）

使用统一 agent harness、统一工具、统一容器，只替换底模。至少三个独立模型家族。这样能把 model family 与产品 harness 分开。

### Level B：产品层生态验证（次级）

Claude Code、Codex CLI 或其他完整 coding agent，保留其原生 harness。该层回答现实工作流的外部有效性，但不能用于声称底模互补的因果结论。

## 6.6 数据集设计

构造两个互补集合。

### Dataset A：Controlled Defect Patches

从许可清晰、可容器化的真实仓库抽取任务，注入或保留结构化缺陷。每个样本包含：

```text
repository snapshot
issue/specification
candidate patch
defect_id
exact defect location or invariant
visible tests
hidden tests
defect category
gold correction constraints
```

缺陷类别至少覆盖：

1. 边界条件遗漏；
2. API/库误用；
3. 跨文件不一致；
4. 状态更新或顺序错误；
5. 异常处理遗漏；
6. 数据类型/序列化错误；
7. 需求理解偏差；
8. 不必要修改或 collateral regression；
9. 测试遗漏；
10. 性能或资源退化（只在可稳定测量时）。

每个缺陷必须有 deterministic hidden test 或 invariant。不要以 LLM 判断“这可能是 bug”作为 gold。

### Dataset B：Agent-Generated Near-Miss Patches

从 repository-level tasks 中让各 author model 生成 patch。筛选：

- 编译/基础检查通过；
- 至少一个隐藏测试失败；
- 不是纯格式或无法运行；
- 能明确定位根因；
- 不向 reviewer 暴露隐藏测试结果。

这部分更真实，能够观察不同 author model 的自然错误分布。

### 数量目标

Pilot：30–40 个 task，产生 60–100 个 candidate patches。

Full：

- 80–120 个独立 tasks；
- 200–300 个 candidate patches；
- 至少 20 个 repositories；
- Python 为主，可加入 JavaScript/TypeScript 作为外部验证；
- train/dev/test 按 repository 完整切分。

## 6.7 Review Workflow 标准化

所有 reviewer 首先执行 detection-only 阶段：

```json
{
  "verdict": "correct|defective|uncertain",
  "findings": [
    {
      "file": "path",
      "line_range": "...",
      "defect_type": "enum",
      "claim": "what is wrong",
      "evidence": "code/test/spec evidence",
      "confidence": 0.0
    }
  ],
  "recommended_tests": [],
  "estimated_risk": "low|medium|high"
}
```

随后进入 repair 阶段。Detection 与 repair 分开计分，避免“碰巧重写正确”被当作审查能力。

### 比较条件

每个 author patch 至少比较：

1. `NO_REVIEW`：原 patch；
2. `AUTHOR_MORE_COMPUTE`：相同作者获得与 reviewer 等量额外预算；
3. `SELF_REVIEW`：同一上下文自查；
4. `SAME_FAMILY_FRESH`：同家族独立上下文 reviewer；
5. `CROSS_FAMILY_REVIEW`：不同模型家族 reviewer；
6. `TEST_GENERATION_ONLY`：第二模型只写测试，不直接给修复；
7. `INDEPENDENT_REIMPLEMENTATION`：第二模型从 issue 重做，再比较/选择；
8. `ROUTER`：本文方法动态选择。

可加：多 reviewer voting，但不作为核心。

### 信息暴露消融

对部分样本比较 reviewer 是否看到：

- 仅 diff + issue；
- diff + issue + visible test logs；
- 再加入 author 的自然语言 rationale。

主设置不暴露私有 reasoning，以减少 anchoring 和不可控泄漏。

## 6.8 预算匹配

至少提供两种公平视角：

### Token-matched

每个 workflow 的总输入/输出 token 上限近似相等。

### Dollar-matched

根据运行时实际价格，限制总成本。模型价格变动时，使用 exact run date 与价格 snapshot。

同时报告 wall-clock，因为并行 reviewer 可能增加费用但降低延迟。

不能只比较“作者一次”与“作者 + reviewer”而忽略额外计算。

## 6.9 Error Complementarity 定义

对 author `a`、reviewer `r`、defect class `d`：

```text
DetectionComplementarity(a,r,d)
= P(r detects d | a produced d)
```

但这仍受 reviewer 强度影响。进一步计算：

```text
ResidualComplementarity
= observed cross-review gain
  - expected gain from reviewer standalone strength
  - expected gain from extra compute baseline
```

可用分层 logistic model：

```text
fixed: author, reviewer, defect_type, author×reviewer, reviewer_strength
random: repository, task
```

author×reviewer interaction 是 pair-specific complementarity 的关键证据。

额外输出：

- pairwise error correlation；
- defect-category confusion matrix；
- same-family vs cross-family correlation；
- review-induced regression matrix。

## 6.10 Proposed Method：ReviewRoute

目标是在调用昂贵 reviewer 之前，选择最有价值策略。

### 输入特征

只允许使用 review 前可得信息：

- repository language/size；
- issue 类型；
- diff size、文件数、模块跨度；
- 是否触及 API/状态/并发/序列化；
- visible test coverage 和失败日志；
- author model family；
- author trajectory 中的重试、测试、异常、上下文压缩；
- patch static signals；
- author 的校准置信度（只作为特征，不当真值）。

### 动作

```text
NO_REVIEW
SELF_REVIEW
SAME_FAMILY_FRESH
CROSS_FAMILY_X
TEST_GENERATION
INDEPENDENT_REIMPLEMENTATION
```

### 目标

在预算 `B` 下最大化最终 correctness，或优化：

```text
U = P(final_correct) - λ_cost * cost - λ_latency * latency
```

至少实现：

- interpretable logistic/gradient-boosted baseline；
- cost-sensitive contextual bandit 或离线 policy learning 版本；
- uncertainty-aware abstention：无法可靠选择时走强 reviewer 或 full test。

不要一开始就用复杂深度模型。先证明简单 router 有稳定 transfer。

## 6.11 Pilot

建议：

```text
30 tasks
× 2 author families
→ 60+ candidate patches
× 5 core review conditions
```

Pilot 必须回答：

- 隐藏测试与 defect labels 是否可靠；
- cross-family 与 same-family 的差异是否大于运行噪声；
- review-induced regression 是否存在；
- 预算匹配后还有没有净收益；
- 是否能观察到至少两个稳定 defect-category differences。

### Pilot Pass

- 至少一种 cross-family pair 在某些类别上有明显互补，而不是纯 reviewer 强度；
- overall 或 subgroup 上存在可操作的路由空间；
- objective hidden tests 能覆盖主结论；
- reviewer false-positive 不至于使数据不可用；
- repository-level split 可行。

### Kill/Rewrite

- 所有收益在 budget matching 后消失且置信区间足够窄；
- 结果完全由一个明显更强模型支配；
- defect labels 无法可靠对应实际 patch；
- router 只能记 repository，held-out repo 失效；
- review 建议质量只能靠同一 LLM judge 判断。

若得到严格、广泛且有机制解释的“异构 review 并不比加计算更好”，可转成高价值负面实证论文；但必须有足够样本和窄 CI。

## 6.12 Full Study

建议结构：

1. 3 个模型家族完整 author–reviewer 矩阵；
2. 80–120 tasks；
3. 200–300 near-miss patches；
4. 每个 patch 跑核心 5–7 条 workflow；
5. held-out repositories 评估 router；
6. 10–20% 样本由两名人工审计 finding 的正确性；
7. 产品层 Claude Code/Codex 生态验证 20–30 tasks。

若成本过高，优先保证：

- 全 pair matrix；
- equal-budget baseline；
- held-out repo；
- objective final correctness。

不要牺牲这些去增加无关模型数量。

## 6.13 Metrics

### Primary

- equal-budget final patch correctness；
- ReviewRoute 在 held-out repos 的 correctness–cost frontier；
- cluster bootstrap CI over repositories/tasks。

### Secondary

- defect recall/precision；
- false-positive findings；
- review-induced regression；
- cost per corrected patch；
- latency；
- pair-specific complementarity；
- defect-category heterogeneity；
- test-generation yield。

## 6.14 统计方案

- 成功率：task/repository clustered paired bootstrap；
- 全矩阵：mixed-effects logistic regression；
- router：nested cross-validation，外层按 repository；
- 只在 validation 上选超参数；
- 比较 Pareto frontier 时报告 paired differences，而非只报最优点；
- 人工标注报告 Cohen’s κ 或 Krippendorff’s α；
- 对多 defect category 做 FDR 控制。

## 6.15 必须出现的图表

1. author × reviewer final correctness matrix；
2. defect category complementarity heatmap；
3. equal-budget workflow comparison；
4. review-induced regression 桑基图或流图；
5. ReviewRoute cost–correctness Pareto；
6. held-out repository calibration/utility；
7. 主结果表、人工审计表、产品层外部验证表。

## 6.16 论文结构

1. Introduction：第二模型不应被默认视为免费可靠性；
2. Study Design：模型层与产品层；
3. Dataset：controlled + natural near-miss；
4. Empirical Complementarity Study；
5. ReviewRoute；
6. Experiments；
7. Failure/Regression Analysis；
8. Threats to Validity；
9. Related Work；
10. Conclusion。

## 6.17 预判审稿攻击

- **“就是 ensemble”**：强调 review workflow、defect-level pair interaction、预算和路由。
- **“Reviewer 更强而已”**：全双向矩阵、standalone strength control、extra-compute baseline。
- **“Synthetic bugs 不真实”**：controlled 与 natural near-miss 双数据集。
- **“只测 Python”**：至少一个第二语言外部验证；若没有则明确限制。
- **“Hidden tests 不等于 review quality”**：分开报告 detection 与 final repair，人工审计 finding。
- **“Claude/Codex harness 不同”**：主实验统一 harness，产品层仅生态验证。
- **“路由器泄漏”**：完整 repository split 与 sealed test。

## 6.18 投稿定位

首选 **FSE 2027 Research Track**。论文要以软件可靠性、代码审查、测试和 cost-aware workflow 为主叙事。准备完整 replication package、Data Availability 和 artifact scripts。

若方法更偏通用 Agent routing，可顺序考虑 MLSys/TMLR；同一版本不得平行双投。

## 6.19 输出清单

```text
p2_crosscheck/
├── repositories/
├── task_mining/
├── mutations/
├── candidate_patches/
├── hidden_tests/
├── review_protocols/
├── router/
├── annotations/
├── experiments/
├── analysis/
├── paper/
└── artifact/
```

# 7. Paper 3 — DeltaResearch

## 7.1 暂定标题

**DeltaResearch: Selective Revision of Deep-Research Reports under Evidence Updates**

备选：

- *Which Claims Must Change? Evidence-Delta Reasoning for Deep Research Agents*
- *ClaimPatch: Dependency-Aware Maintenance of Long-Form Research Reports*
- *From Regeneration to Revision: Provenance-Guided Report Updates*

## 7.2 一句话中心命题

当底层证据发生局部更新、修正、撤回或冲突时，Deep Research Agent 往往遗漏失效结论，或破坏大量原本正确的内容。把报告表示为带时间、计算和支持关系的 claim–evidence dependency graph，并生成受约束的最小 patch，可以同时提高“该改的都改了”和“不该改的保持不变”。

## 7.3 与已有多轮修订工作的边界

已有工作已经研究用户反馈驱动的多轮报告修订，并观察到非目标内容和引用质量会回归。因此本论文不能只做：

- “请根据反馈修改报告”；
- 一般的 report revision benchmark；
- citation correctness 检测；
- 普通 RAG 或 GraphRAG；
- 只测文章 diff 大小。

本论文必须锁定以下新对象：

1. **输入变化发生在证据世界，而不是用户写作反馈**；
2. 每次更新有明确的 `evidence delta` 和 gold affected/unaffected claim set；
3. 研究多跳派生结论、计算和时间有效性；
4. 方法输出 claim-level patch 与 audit trail；
5. 评价同时惩罚 stale claims 和 spurious revision。

## 7.4 形式化

定义证据世界：

```text
W_t = {evidence item e_i, content, source, timestamp, validity interval}
```

报告：

```text
R_t = {claims c_j, sections, citations, calculations}
```

更新：

```text
ΔW = W_{t+1} - W_t
```

Gold impact：

- `A`：必须更新、删除、降级或重新计算的 claims；
- `U`：在更新后仍应保持语义不变的 claims；
- `N`：因新证据应新增的 claims；
- `C`：出现冲突、应标注不确定或无法决断的 claims。

目标不是最小字符 diff，而是：

```text
Correctly update A and N
Preserve U
Represent C honestly
Maintain citation and calculation validity
Minimize unnecessary semantic drift
```

## 7.5 研究问题与假设

### RQ1：局部证据更新会造成多大报告回归？

- H1：全量重生成和普通“更新这份报告”提示都会产生明显的 stale residual 或 unaffected drift。

### RQ2：claim–evidence ledger 是否足够？

- H2：仅记录 claim 到 citation 的直接边优于无结构 baseline，但对派生计算和多跳结论仍不足。

### RQ3：typed dependency graph 是否进一步有效？

- H3：加入 `supports / derives / qualifies / contradicts / temporal-validity` 类型边，提高 affected-claim recall 和 derived-claim correctness。

### RQ4：最小 patch 是否比重写更可靠且更便宜？

- H4：受约束 patch generation 在不降低整体报告质量的前提下，减少无关语义漂移、token 和延迟。

### RQ5：是否跨领域、跨 Agent 泛化？

- H5：在一个领域开发的方法能在 held-out source/update family 上保持收益。

## 7.6 数据集：DeltaBench

构建两层数据，避免纯 synthetic 或纯人工都不可扩展。

### Layer A：Controlled Evidence Worlds

从结构化 facts、规则和计算模板生成可完全验证的 evidence worlds。每个 world 包含 8–25 个 evidence items、10–30 个 atomic claims、1–5 个派生结论。

领域可选：

- 公司/产品指标的非真实但结构化案例；
- 软件版本、API 与兼容性；
- 科学实验摘要与统计结果；
- 宏观指标与修订；
- 政策条款和生效日期。

更新类型至少包含：

1. 数值修订；
2. 日期或有效期变化；
3. 来源撤回；
4. 新增更权威来源；
5. 两来源冲突；
6. 定义改变；
7. 上游事实变化触发下游重新计算；
8. 局部表格行变化；
9. 来源仅改变限定条件；
10. 证据删除但结论仍由其他证据支持。

Controlled worlds 由程序维护 gold graph，主评分尽量确定性。

### Layer B：Real Versioned Evidence

构建真实、公开、时间戳明确的版本对。优先来源：

- 官方软件文档与 release notes 的版本历史；
- 公开政府或机构数据的历史 vintage/revision；
- 公开标准、政策或产品文档的修订；
- 论文版本、勘误或撤回通知，在许可证允许时使用。

不要直接抓取不可再分发的全文。保存 URL、hash、许可与必要的可引用片段；artifact 中遵守来源许可。

建议：

- Controlled：200–400 worlds；
- Real：50–100 worlds；
- Pilot：40 worlds，其中至少 10 个 real；
- 每个 real world 由两名独立 annotator 标注 affected/unaffected claims，并由第三方或 PI adjudicate 分歧。

## 7.7 数据样本 schema

```json
{
  "world_id": "...",
  "domain": "software_docs",
  "initial_evidence": [
    {
      "evidence_id": "e1",
      "source_uri": "...",
      "snapshot_time": "...",
      "content_hash": "...",
      "text": "...",
      "validity": ["start", "end"]
    }
  ],
  "initial_report": "...",
  "initial_claims": [
    {
      "claim_id": "c1",
      "text": "...",
      "type": "fact|comparison|calculation|recommendation",
      "support": ["e1"],
      "dependencies": ["c0"],
      "validity": ["start", "end"]
    }
  ],
  "evidence_delta": {
    "added": [],
    "removed": [],
    "modified": []
  },
  "gold_impact": {
    "affected": [],
    "unaffected": [],
    "new": [],
    "conflicted": []
  },
  "gold_constraints": []
}
```

## 7.8 初始报告生成

为避免 baseline 质量差异污染 revision，建立两种设置：

### Fixed-report setting

所有方法从同一份人工/高质量初始报告开始。主因果比较使用这个设置。

### End-to-end setting

每个 Deep Research Agent 自己生成初始报告，然后处理更新。用于生态有效性。

Fixed-report 必须包含：

- 可原子化的 claims；
- 正确 citations；
- 至少一部分 derived claims；
- 明确 section structure；
- 不把 gold impact 暴露给更新 Agent。

## 7.9 Proposed Method：ClaimPatch

### Stage 1：Claim Atomization

把报告拆成 atomic claim，但保留：

- section/span location；
- claim type；
- quantitative expression；
- modality/uncertainty；
- citation links；
- downstream claims。

### Stage 2：Evidence Ledger

每条 evidence 保存：

- immutable snapshot/hash；
- source authority；
- publication/update time；
- exact supporting span；
- scope and qualifiers；
- validity interval。

### Stage 3：Typed Dependency Graph

边类型：

```text
DIRECT_SUPPORT
DERIVED_FROM
NUMERIC_DEPENDENCY
TEMPORAL_DEPENDENCY
QUALIFIED_BY
CONTRADICTED_BY
ALTERNATIVE_SUPPORT
```

### Stage 4：Impact Analysis

证据 delta 到 claims 的传播算法：

1. 直接内容 hash/change detection；
2. 判断变化是否触及支持 span；
3. 标记直接 affected claims；
4. 按 typed edges 向下游传播；
5. 若仍有 alternative support，则不必失效；
6. 对冲突改为 contested，而不是强行二选一；
7. 生成需要重新检索/重算的 action list。

### Stage 5：Constrained Patch Generation

模型只允许编辑：

- affected claim spans；
- 必要的过渡语句；
- citations/figures/tables 中受影响部分。

输出结构化 patch：

```json
{
  "operations": [
    {
      "op": "replace|delete|insert|downgrade_confidence",
      "claim_id": "c7",
      "old": "...",
      "new": "...",
      "reason": "evidence e3 revised",
      "evidence": ["e3_v2"]
    }
  ],
  "untouched_claims": ["..."],
  "unresolved_conflicts": []
}
```

### Stage 6：Post-update Verification

- 每个 affected claim 是否有新支持；
- 旧 citation 是否 stale；
- 数值重新计算；
- unaffected claims 是否被误改；
- 全文一致性；
- 输出 audit trail。

## 7.10 Baselines

至少比较：

1. 从头重新检索并生成整份报告；
2. 直接 prompt：“根据新证据更新报告”；
3. 局部 diff prompt，但无 claim ledger；
4. 普通 citation checker 后修订；
5. direct claim–citation ledger，无 typed dependencies；
6. ClaimPatch full；
7. Oracle impact set upper bound。

Oracle upper bound 用 gold affected claims，只用于衡量 impact detection 的损失，不作为实用方法。

## 7.11 评价指标

### Primary

- **Affected Claim Recall (ACR)**：该改的 claim 被正确处理比例；
- **Unaffected Claim Preservation (UCP)**：不该改的 claim 保持语义正确比例；
- 二者的联合报告，不建议简单合成一个可被掩盖的平均分。

### 关键错误

- **Stale Residual Rate**：失效 claim 仍保留；
- **Spurious Revision Rate**：未受影响 claim 被错误改动；
- **Unsupported New Claim Rate**；
- **Citation Freshness/Alignment**；
- **Calculation Correctness**；
- **Conflict Honesty**：冲突时是否表达不确定。

### 效率

- 更新 token、费用、延迟；
- 修改 claim 数；
- 人类核验时间的代理指标：audit trail completeness。

### 全文质量

在 real subset 上由双盲人工评价 factuality、coherence、completeness。LLM judge 只做补充，并报告与人工一致性。

## 7.12 Pilot

建议：

```text
40 worlds
  - 30 controlled
  - 10 real
× 2 research-agent families
× 4 methods
```

Pilot 必须验证：

- gold impact 可可靠构造；
- full regeneration 是否确实造成非局部 drift；
- direct ledger 与 typed graph 是否有可区分空间；
- metrics 能在无需 LLM judge 时覆盖大部分主结论；
- patch application 不会因工具 bug 失败。

### Pilot Pass

- baseline 同时存在 stale residual 与 spurious revision 中至少一种显著问题；
- ClaimPatch 在 ACR 或 UCP 上有稳定改善，且另一项不明显恶化；
- typed dependency 对 derived/temporal claims 有额外价值；
- real subset 方向与 controlled subset 基本一致；
- 人工标注一致性达到可接受水平。

### Kill/Rewrite

- 从头重生成在准确性、稳定性和成本上全面支配；
- claim dependency 无法稳定标注；
- synthetic gain 完全不能迁移到 real；
- 所有主要分数依赖同一 LLM judge；
- typed graph 没有超过 direct ledger；
- 更新 Agent 只需一个极简单 prompt 就达到天花板。

若方法不强但发现广泛、稳定的 evidence-update failure，可转为 benchmark/analysis paper，但必须与普通多轮 revision 工作清楚区分。

## 7.13 Full Study

建议：

```text
240 controlled worlds
+ 60 real worlds
× 3 agent/model families
× 5 practical methods
```

为控制成本：

- controlled worlds 主要用固定报告和较低温度；
- real worlds 只跑核心方法；
- 先根据 pilot power analysis 决定重复次数；
- held-out split 按 source/update family，而不是随机 world。

### Generalization Tests

- held-out domain；
- held-out update type；
- held-out source organization；
- end-to-end initial report setting；
- 长报告与多跳派生 claim 子集。

## 7.14 统计方案

- world-level paired bootstrap；
- ACR/UCP 用 mixed model，random intercept 为 world/source family；
- human annotation 报 Krippendorff’s α；
- 对 claim-level 指标用 cluster-robust SE，不能把同一 world 中 claims 当独立；
- controlled 与 real 分开报告，再做 pooled exploratory analysis；
- pre-register primary method comparison。

## 7.15 必须出现的图表

1. evidence delta → typed dependency → report patch 的系统图；
2. update type × baseline failure heatmap；
3. ACR–UCP 二维 Pareto 图；
4. stale residual 与 spurious revision 分解；
5. typed-edge ablation；
6. controlled-to-real transfer；
7. 成本与修改范围；
8. 一个完整可审计案例，展示 evidence 变化如何传播到下游 claim。

## 7.16 论文结构

1. Introduction：报告维护不是再生成；
2. Problem Definition：evidence-world delta；
3. DeltaBench；
4. ClaimPatch；
5. Experimental Setup；
6. Main Results；
7. Dependency/Failure Analysis；
8. Human Evaluation；
9. Related Work；
10. Limitations/Ethics；
11. Conclusion。

## 7.17 预判审稿攻击

- **“已有多轮 revision benchmark”**：强调 evidence delta、gold impact 和 dependency propagation。
- **“Synthetic 数据太多”**：real versioned subset 与跨来源验证。
- **“Graph 是 LLM 自己编的”**：controlled gold graph、edge accuracy 与 ablation。
- **“最小 diff 不等于更好”**：primary 是 correctness/preservation，不是字符 diff。
- **“全量重生成更简单”**：严格比较正确性、drift、费用和审计性。
- **“Claim extraction 不稳定”**：固定报告、人工抽查、atomic claim guidelines。
- **“时效事实有 web leakage”**：使用冻结 source packets 与明确 snapshot time。

## 7.18 投稿定位

若 benchmark、方法和语言生成分析最强，走 **ACL Rolling Review**。当前应以 2026 年 10 月 cycle 为默认目标；只有在完整实验、人工标注和正文提前冻结时才考虑更早 cycle。

若贡献更偏通用 Agent provenance、continual update 或系统，可顺序改投 TMLR/ICLR，不得同时送审。

## 7.19 输出清单

```text
p3_deltaresearch/
├── source_registry/
├── controlled_worlds/
├── real_worlds/
├── annotations/
├── claim_graph/
├── impact_analyzer/
├── patcher/
├── verifier/
├── protocols/
├── experiments/
├── analysis/
├── paper/
└── artifact/
```

# 8. Paper 4 — HarnessGuard

## 8.1 暂定标题

**HarnessGuard: Edit-Conditioned Canary Testing for Evolving LLM-Agent Harnesses**

备选：

- *Predicting Hidden Regressions in Automatically Evolving Agent Harnesses*
- *Canary Selection and Risk-Controlled Deployment for Agent Harness Updates*
- *Before You Ship the New Harness: Regression Foresight for Agent Systems*

## 8.2 一句话中心命题

Agent Harness 的 prompt、tools、middleware、memory、retry、verifier 或 stopping rule 被自动修改后，局部提升常伴随跨任务隐藏回归。通过结构化表示 edit 的预期行为影响、结合历史任务轨迹选择少量高风险且多样的 canary，并在不确定时升级到 full evaluation，可以以远低于全量 benchmark 的成本发现大部分危险回归。

## 8.3 与现有 Harness 自动演化工作的边界

不能重复：

- 自动修改 Harness 以提升 benchmark；
- 记录 edit 的自我预测；
- 一般的 self-evolving agent；
- 简单 smoke test 或随机 canary；
- 只证明 Harness 会影响模型排名。

本论文的对象不是“如何提出更好的 edit”，而是：

1. 已经有一个候选 Harness edit；
2. 在部署或昂贵 full suite 前，预测它会让哪些任务退化；
3. 在固定 canary 预算下最大化 regression detection；
4. 对无法保证安全的 edit 明确 abstain/escalate；
5. 在 held-out edit type、task family 和 model family 上验证。

重点精读：Agentic Harness Engineering、ANNEAL/类似 governed adaptation、self-evolving agent evaluation、evaluation harness regression alerting、canary testing 与 test selection 文献。

## 8.4 形式化

给定：

- 模型 `M`；
- 原 Harness `H`；
- 候选 edit `e`，新 Harness `H' = e(H)`；
- 完整任务集合 `D = {t_i}`；
- 每个任务在旧/新 Harness 下的结果 `y_i(H), y_i(H')`。

定义 regression：

```text
r_i(e) = 1 if y_i(H)=pass and y_i(H')=fail
```

可扩展到连续 reward、成本或安全指标，但主分析先用明确 pass→fail。

目标是在只能运行 `k << |D|` 个 canary 时选择集合 `S_e`，并输出：

```text
ACCEPT
REJECT
ESCALATE_TO_FULL_SUITE
```

关键损失：

- false safe：实际存在超过阈值的危险回归却 ACCEPT；
- unnecessary escalation：本可安全接受却跑 full suite；
- missed regression tasks；
- 评测成本。

## 8.5 研究问题与假设

### RQ1：Harness edits 的隐藏回归有多常见？

- H1：看似提高平均分的 edits 中，存在非平凡比例的 task-level pass→fail regression。

### RQ2：随机/固定 smoke tests 是否足够？

- H2：回归具有结构性，集中在与 edit 影响相关的能力与轨迹模式，因此随机 canary 在小预算下漏检严重。

### RQ3：edit-conditioned selection 是否更有效？

- H3：使用 edit + task + historical trace 的 risk model，在相同 k 下显著提高 regression recall。

### RQ4：能否安全地自动决定？

- H4：加入校准和 abstention 后，系统降低 false-safe rate，同时仍节省大量 full-suite 成本。

### RQ5：是否跨模型/任务/编辑类型泛化？

- H5：至少部分风险结构能从 seen edits 转移到 held-out edit types、models 或 task families。

## 8.6 Harness Edit Corpus

需要混合三类 edits，避免只用自动生成修改。

### A. Real Historical Edits

从公开 agent harness、coding agent 或 self-evolving harness 仓库挖掘：

- system prompt；
- tool descriptions/implementations；
- context construction/compression；
- retry/recovery；
- memory；
- verifier；
- stopping；
- subagent routing；
- permissions/confirmation。

筛选条件：

- edit 可独立复现；
- old/new commit 能运行；
- 修改目的可解释；
- 不包含大规模底模更换；
- 许可证允许研究和再分发必要 patch。

### B. Controlled Atomic Edits

在自建 modular harness 上生成单一组件 edit，确保能定位机制。例如：

- 增加/删除 read-after-write verification；
- 改 retry 次数或错误分类；
- context truncation 从尾部改为摘要；
- tool description 更具体/更抽象；
- stopping rule 更激进；
- memory retrieval top-k 变化；
- verifier threshold 变化；
- tool ordering 或 availability 变化。

### C. Optimization-Generated Edits

让一个独立 optimizer 根据 dev failures 自动提出 edits。优化 Agent 不得看到 sealed task labels。保留所有候选，不只保留成功 edit，以避免 selection bias。

### 数量目标

Pilot：12–16 个 edits，至少覆盖 4 个组件类。

Full：30–60 个独立 edits，其中：

- 至少 10 个 real；
- 至少 10 个 controlled；
- 至少 10 个 optimizer-generated；
- 每类包含 improvement、neutral 和 harmful edits。

如果无法获得至少约 25 个真正独立、会产生可测回归的 edits，旗舰版本不可成立。

## 8.7 Task Suite

建立两个主域：

### Coding/Terminal Tasks

- 可容器化；
- deterministic verifier；
- 需要多步工具使用；
- 覆盖测试、文件、命令、恢复和停止。

### Stateful Tool/Workspace Tasks

- 使用 Paper 1 的部分共享环境代码，但任务集合和主变换不能与 ToolMorph 主实验完全重叠；
- 关注恢复、验证、记忆、权限和状态维护。

完整目标：60–120 tasks。Pilot：30 tasks。

每个 task 预先生成 task descriptor：

```json
{
  "capabilities": ["multi_tool", "error_recovery", "verification"],
  "required_tools": [],
  "trajectory_length_baseline": 0,
  "historical_failure_modes": [],
  "risk_tags": [],
  "cost": 0.0
}
```

## 8.8 Harness Edit Representation

每个 edit 建立结构化 contract：

```yaml
edit_id: retry_classifier_v3
component: retry_recovery
change_scope: local
code_diff_hash: sha256
natural_language_intent: distinguish transient from permanent errors
expected_improvements:
  - transient_tool_failures
expected_risks:
  - extra_cost
  - duplicate_non_idempotent_actions
behavioral_signals:
  - retry_count
  - post_action_state_check
  - idempotency_handling
static_features:
  lines_changed: 42
  prompt_tokens_changed: 0
  tools_affected: 2
```

`natural_language_intent` 可以由 edit author 生成，但不能当真值。必须同时提取：

- code/AST diff；
- prompt diff；
- tool schema diff；
- config changes；
- historical trace signals；
- component category。

## 8.9 Ground Truth Full-Suite Evaluation

对每个 edit：

1. 冻结 model snapshot 和任务初始状态；
2. old/new harness 使用 paired runs；
3. 至少对不稳定设置做重复；
4. 记录 pass→fail、fail→pass、成本和 latency；
5. 人工审计异常 regression；
6. full suite 结果仅由 Test Custodian 持有，canary 方法开发者不能看 held-out edit labels。

需要定义危险 edit：例如任一高风险任务回归，或总体 regression rate 超过预注册阈值。阈值在 full test 前冻结。

## 8.10 Baselines

- 随机选择 k 个 canaries；
- 固定 smoke suite；
- 按历史难度选择；
- 按任务覆盖/能力标签 stratified selection；
- 按 edit 文本与 task 描述 embedding 相似度；
- 静态 diff-size/rule heuristic；
- 每次跑 full suite（成本 upper baseline）；
- edit author 自我预测；
- HarnessGuard。

若已有公开方法做 canary/test selection，必须实现最强可复现版本。

## 8.11 Proposed Method：HarnessGuard

### Module 1：Edit Impact Encoder

融合：

- component type；
- AST/config/prompt/tool diff；
- declared intent；
- changed behavioral contracts；
- historical edits 的 outcome。

输出 edit representation `z_e`。

### Module 2：Task Risk Encoder

使用：

- task capability tags；
- baseline traces；
- tool usage；
- failure signatures；
- cost；
- task embedding。

输出 `z_t`。

### Module 3：Pairwise Regression Risk Model

预测：

```text
p(r_i(e)=1 | z_e, z_t, model, baseline_trace)
```

先实现可解释模型：logistic/gradient boosting；再考虑 neural pair encoder。

### Module 4：Diverse Canary Selector

不能只选最高风险的近重复任务。选择目标：

```text
maximize expected regression coverage
+ diversity across capability/tool/failure groups
subject to cost budget B
```

可用贪心 submodular/facility-location 或 budgeted maximum coverage。

### Module 5：Sequential Decision

运行第一批 canaries 后更新风险：

- 明确回归 → REJECT 或 FULL_SUITE；
- 无回归且风险低 → ACCEPT；
- 不确定 → 追加下一批 canary；
- 达到预算仍不确定 → ESCALATE。

### Module 6：Calibration/Abstention

在 validation edits 上选择阈值，目标控制 false-safe。若使用 conformal 方法，必须陈述 exchangeability 假设，不得把经验覆盖率夸成无条件安全保证。

## 8.12 Pilot

建议：

```text
12 edits
× 30 tasks
× 2 model families
old/new paired
≈ 1,440 task episodes（按是否重复调整）
```

Pilot 分析：

- 每个 edit 的 improvement/regression map；
- random k=3/5/10 的 detection；
- edit-aware heuristic 是否超过 random；
- regression 是否与 component/task capability 有结构；
- author prediction 是否校准。

### Pilot Pass

- 至少 25–30% edits 产生一个以上真实 pass→fail regression，或存在足够连续性能退化；
- 回归不是纯随机噪声；
- 小 canary budget 下 random 明显漏检；
- 简单 edit-aware selector 有超越 random 的信号；
- full-suite oracle 稳定。

### Kill/Rewrite

- edits 几乎不产生隐藏回归；
- regression 完全由运行噪声造成；
- 简单固定 smoke suite 已近乎完美；
- 需要跑接近 full suite 才能检测；
- held-out edit type 上风险模型接近随机；
- edit corpus 太小或高度相关。

## 8.13 Full Study

建议强版本：

```text
36+ edits
× 60+ tasks
× 2–3 model families
old/new paired
```

为降低计算：

- 先用一个主模型得到所有 edit × task ground truth；
- 在第二/第三家族上验证代表性 edit 子集；
- 预先定义子集选择规则，不能看结果后挑；
- 重复只用于不稳定 task/模型组合。

### Generalization Splits

至少三种：

1. leave-one-edit-component-out；
2. leave-one-task-family-out；
3. leave-one-model-family-out。

主文至少报告两种；第三种可在附录，但结果必须诚实。

## 8.14 Metrics

### Primary

- regression recall at fixed canary budget；
- false-safe rate；
- full-suite cost saved；
- risk–coverage curve（自动决定比例 vs 错误风险）。

### Secondary

- precision of regression alarm；
- average canary cost；
- time to detection；
- worst-group regression recall；
- calibration error；
- ACCEPT/REJECT/ESCALATE 分布；
- improvement preserved；
- model/edit/task transfer。

## 8.15 统计方案

- edit 为主要独立单位；
- bootstrap over edits，不得把数千 task runs 当独立 edit 样本；
- 比较 selector 使用相同 edits、相同 k 的 paired bootstrap；
- sequential policy 在完全 held-out edits 上评估；
- threshold 只在 validation 调；
- 分别报告 real、controlled、optimizer-generated edits；
- 对 false-safe 给 Wilson/Clopper–Pearson 或 bootstrap CI；
- 若样本有限，降低 claim，不依赖 p-value 包装。

## 8.16 必须出现的图表

1. Harness edit → risk model → canary → decision 系统图；
2. edit × task regression matrix；
3. 不同 selector 的 recall@budget 曲线；
4. risk–coverage / false-safe 曲线；
5. held-out edit type/model transfer；
6. component-specific regression；
7. 成本节省表；
8. 两个真实案例：平均分提高但关键任务回归，以及 HarnessGuard 如何捕获。

## 8.17 论文结构

1. Introduction：自动优化若无 regression foresight 不可部署；
2. Problem/Formalization；
3. Edit Corpus and Task Suite；
4. Empirical Characterization of Hidden Regressions；
5. HarnessGuard；
6. Evaluation；
7. Generalization and Calibration；
8. Failure Analysis；
9. Related Work；
10. Limitations/Ethics；
11. Conclusion。

## 8.18 预判审稿攻击

- **“已有自演化系统做 canary”**：强调 edit-conditioned selection、full regression ground truth、held-out generalization 和 false-safe。
- **“Edit 数据是人为造的”**：real + controlled + optimizer-generated 三类分开报告。
- **“只是普通 regression testing”**：说明 stochastic agent、trajectory features、model × harness interactions 和 cost constraints 的特殊性，同时认真比较 SE test selection。
- **“样本只有几十个 edits”**：edit 是昂贵独立单位；扩大 real corpus，给 CI，避免过度模型化。
- **“风险模型只记 edit 类型”**：leave-one-component-out。
- **“Canary 运行后才预测，不算预测”**：明确 pre-run selection 和 sequential update 两阶段。
- **“安全保证过度”**：只在满足假设时谈统计覆盖，其他情况称 empirical risk control。

## 8.19 投稿定位

旗舰首选 **MLSys / ICLR**，因为核心是 Agent 系统测试、监控、部署和通用方法。若 automatic method 未达到旗舰强度，但数据与分析可靠，可顺序投 TMLR。

不要假设尚未发布的 2027 deadline；Research Director 每次会话检查官方 CFP，并更新 `program/deadlines.yaml`。

## 8.20 输出清单

```text
p4_harnessguard/
├── edit_mining/
├── edit_corpus/
├── task_suite/
├── full_suite_ground_truth/
├── feature_extraction/
├── risk_model/
├── canary_selector/
├── sequential_policy/
├── calibration/
├── experiments/
├── analysis/
├── paper/
└── artifact/
```


---

# 9. 四篇之间的边界、共享资产与禁止切香肠规则

## 9.1 四篇唯一中心问题

| Paper | 唯一中心问题 | 主要干预单位 | 主要结果单位 | 主要方法贡献 |
|---|---|---|---|---|
| ToolMorph | 等价工具语义的不同接口表示，是否改变 Agent 行为；如何归一化 | tool interface transformation | task × model × transformation run | semantic normalizer + metamorphic protocol |
| CrossCheck | 哪类 reviewer 在何种任务上能补作者模型的残余错误 | review workflow | defective patch × reviewer condition | complementarity model + router |
| DeltaResearch | 证据局部更新后，哪些 claim 应变、哪些不应变 | evidence delta | report claim × update | dependency ledger + selective patch |
| HarnessGuard | Harness edit 上线前，如何用少量 canary 预测隐藏回归 | harness edit | edit × task regression pair | edit-conditioned canary selector + abstention |

任何时候若两个项目开始共享同一中心命题、同一主表或同一决定性实验，Research Director 必须触发 `MERGE_REVIEW`，写一页合并判定，不得靠重命名继续拆稿。

## 9.2 可以共享的资产

允许共享：

- 模型 adapter；
- sandbox/environment runner；
- trace schema；
- token、费用和延迟采集；
- statistical utilities；
- reproducibility container；
- artifact packaging；
- 文献数据库和 citation verifier；
- 通用任务环境，但必须为各篇建立独立 sample split 和独立主指标。

不允许直接共享为各自“独立贡献”的资产：

- 同一实验结果重复作为两篇主结果；
- 同一 benchmark 只改名称；
- 同一个 learned model 作为两篇核心方法而无独立科学问题；
- 一篇的消融拆成另一篇；
- 一篇的附录分析包装成另一篇。

## 9.3 Cross-paper contamination 防护

建立以下数据访问权限：

```text
shared_public_tasks/       所有项目可读
p1_sealed_test/            仅 P1 Test Custodian 可读标签
p2_sealed_test/            仅 P2 Test Custodian 可读标签
p3_sealed_test/            仅 P3 Test Custodian 可读 gold impact
p4_sealed_test/            仅 P4 Test Custodian 可读 full-suite regressions
```

每篇的 method-building agents 不得读取其 sealed test 的标签、人工评论或 full-suite outcome。Research Director 只在 protocol freeze 后授权执行。

## 9.4 一稿一投规则

- 一篇稿件在正式 archival review 期间，不得同时投另一 archival venue。
- 不同稿件可以同时投稿，前提是贡献独立、互相披露 concurrent work、实验与文本重叠透明。
- 若一个项目被拒，可在正式 withdraw/reject 后修改并顺序改投。
- arXiv/preprint、公开仓库、非 archival workshop 是否允许，逐 venue 查官方规则并记录。
- Research Director 在投稿前生成 `overlap_matrix.md`，逐对列出四篇的共享文本、数据、代码和贡献。

---

# 10. 全局自动化执行架构

## 10.1 Claude 作为 Research Director 的职责

Claude 不只是聊天式建议者，而是维护一个可审计研究程序。每轮执行必须：

1. 读取 `program/status.yaml`；
2. 读取每篇 `research_contract.yaml`；
3. 检查当前 gate；
4. 找出所有无依赖、可并行、可逆任务；
5. 为每个任务创建 issue；
6. 分配给隔离 subagent/worktree；
7. 运行验收测试；
8. 合并通过的结果；
9. 更新状态与风险；
10. 继续到下一个可执行任务，而不是停在“下一步建议”。

仅以下情况暂停并请求人类决策：

- 需要购买或调用超过预设预算的服务；
- 需要接触真实个人数据或招募人类参与者；
- 需要接受网站、数据集或 API 的特殊法律条款；
- 需要公开发布、联系作者/编辑、注册研究或正式投稿；
- 两个研究方向必须合并或停止，且取舍涉及作者目标；
- 关键结果存在不可消除的真实性争议；
- 最终中心 claim、作者名单、披露声明和投稿版本。

## 10.2 Subagent 隔离

每个 issue 使用独立 git worktree 或容器：

```text
worktrees/
  p1-lit-001/
  p1-build-004/
  p2-stats-003/
  p3-audit-007/
  p4-reproduce-002/
```

命名规则：`<paper>-<role>-<issue_id>`。

Subagent 只能获得完成任务所需的最小上下文；不要把完整主张、期待结果和 sealed labels 全部泄露给执行者。尤其：

- Dataset generator 不知道最终方法输出；
- Judge 不知道方法名称；
- Reproducer 不知道原始运行是否“应该成功”；
- Reviewer 2 不读作者 rebuttal 后再给第一轮意见；
- Statistician 在主结果解封前冻结分析计划。

## 10.3 Issue 模板

```yaml
issue_id: P1-BUILD-004
paper: toolmorph
role: builder
objective: "实现 strict structural-nesting transformation 及逆变换"
inputs:
  - specs/toolmorph_dsl.md
  - environments/calendar_v1/
allowed_paths:
  - papers/p1_toolmorph/transforms/structural_nesting/
forbidden_paths:
  - sealed_tests/
  - papers/p1_toolmorph/results/full/
acceptance_tests:
  - "property test >= 10,000 generated calls, zero state mismatch"
  - "round-trip encode/decode exact for valid inputs"
  - "invalid inputs preserve error class"
artifacts:
  - code
  - unit tests
  - brief.md
failure_policy: "return FAIL with minimal counterexample; do not silently weaken spec"
```

## 10.4 Done 定义

任务只有满足全部条件才算 Done：

- 代码提交；
- 测试通过；
- 运行命令可复现；
- 生成 artifact；
- 无新增 secret；
- 文档说明假设和限制；
- 结果写入 ledger；
- 独立 Agent 可从 README 重跑；
- 不含未经核验的数字和引用。

“写完一段分析”“看起来可行”“模型说成功”均不算 Done。

## 10.5 统一实验命令

```bash
# 注册实验
python -m core.experiment_registry.create \
  --paper p1_toolmorph \
  --config papers/p1_toolmorph/configs/pilot_v1.yaml

# dry run
python -m core.runner.run --config <config> --dry-run

# 正式运行
python -m core.runner.run --config <config> --sealed --write-ledger

# 完整性检查
python -m core.audit.verify_run --run-id <id>

# 统计分析
python -m core.statistics.analyze --analysis-plan <yaml> --freeze-check

# 自动生成论文表格和图
python -m core.plotting.build_all --paper <paper_id> --from-ledger

# artifact 重现
make reproduce PAPER=<paper_id> PROFILE=main
```

## 10.6 统一 CI

每次合并触发：

- unit tests；
- schema validation；
- deterministic smoke tasks；
- data leakage scan；
- citation key validation；
- secret scan；
- results-to-ledger consistency；
- manuscript number consistency；
- anonymization scan；
- license compatibility scan。

---

# 11. 预算、资源与停止策略

## 11.1 三层计算预算

所有项目使用分层预算，不允许直接大规模烧 API：

### Tier 0：本地与确定性验证

用途：

- 单元测试；
- 环境正确性；
- metamorphic oracle；
- synthetic data；
- schema validator；
- static analysis；
- plot/code generation。

目标：在调用付费模型前消灭绝大多数工程错误。

### Tier 1：Pilot

用途：判断现象是否真实、估计方差、发现设计漏洞。

规则：

- 只用最少模型和最小任务集；
- 不做结论性显著性检验；
- pilot task 不进入 sealed confirmatory set；
- 设项目级硬预算；
- 先运行 5% canary，检查输出和费用，再放行全部 pilot。

### Tier 2：Confirmatory full study

只有通过 `PILOT_PASS + PROTOCOL_FROZEN` 才可运行。

规则：

- 冻结配置；
- 预先定义 stopping rule；
- 不根据中途结果修改 primary endpoint；
- 所有异常、重跑和排除记录在案；
- 先小批分层执行并进行数据质量审计，再继续。

## 11.2 预算账本

每篇维护：

```yaml
paper: p1_toolmorph
currency: USD
limits:
  literature_search: 100
  pilot_api: 500
  full_api: 5000
  storage_compute: 500
  contingency: 500
current:
  committed: 0
  spent: 0
alerts:
  - at_fraction: 0.50
  - at_fraction: 0.80
  - at_fraction: 1.00
```

金额只是模板，Research Director 根据可用资源填写。任何 Agent 不得绕过总预算或拆单规避。

## 11.3 高效率原则

- 先验证 phenomenon，再造复杂模型；
- 先做强 heuristic baseline，再训练 learned method；
- 先验证 oracle，再测 Agent；
- 先做 paired design，减少方差；
- 先收集一次轨迹，尽量离线复用；
- 只为回答 RQ 运行实验；
- 所有长任务先运行 miniature equivalent；
- 用 adaptive allocation 把更多重复给高方差 cell，但 confirmatory 分析须预注册；
- 对明显无希望的 cell 依据预定义 futility rule 停止，而不是事后选择性删除。

## 11.4 项目级 Kill / Pivot / Merge

### KILL

在以下情形立即停止独立论文：

- 中心现象在两个模型/两个任务族上均不存在；
- 强基线轻易完全解决；
- 最近工作已经覆盖同一核心贡献；
- deterministic oracle 无法建立，主结论完全依赖不稳定 judge；
- 预期 effect 小到实际意义不足；
- full study 成本超过价值且无可信缩减方案；
- 结果无法在 sealed split 复现。

### PIVOT

允许在不改变研究主题的情况下：

- 从平均性能转向可靠性或机制分析；
- 从普遍正面结果转向边界条件/负面结果；
- 从 learned method 转向更简单且可靠的 protocol；
- 从宽泛任务域缩到一个有真实价值的领域。

Pivot 必须保留旧 contract，并写 `pivot_memo.md` 说明为何不是 HARKing。

### MERGE

若两个项目的主证据高度重叠，则合并为一篇更强论文。禁止为维持“四篇”目标牺牲科学独立性。

---

# 12. 文献检索与新颖性审计协议

## 12.1 Literature Scout 任务

每篇至少建立 60–100 篇相关工作记录，分三层：

1. **Nearest neighbors**：直接解决相同问题；
2. **Method ancestors**：可借鉴方法，如 metamorphic testing、test selection、causal attribution；
3. **Evaluation context**：Benchmark、Agent systems、软件工程/信息检索相关评估。

记录字段：

```yaml
paper_id:
title:
authors:
year:
venue_or_status:
primary_url:
version_date:
problem:
unit_of_analysis:
intervention:
method:
data:
main_claim:
evidence:
limitations:
relation_to_ours:
collision_risk: low|medium|high
verified_by_human_or_agent:
```

## 12.2 检索方式

对每篇使用：

- exact phrase 搜索；
- concept synonyms；
- backward citations；
- forward citations；
- recent arXiv monthly sweep；
- OpenReview/venue accepted list；
- Semantic Scholar/Google Scholar 等索引；
- GitHub benchmark/tool search；
- 相关作者主页；
- 软件工程、NLP、MLSys 等邻域术语搜索。

每周/每个 major gate 重新运行 nearest-neighbor sweep，特别关注最近 60 天预印本。

## 12.3 Novelty Prosecutor 输出

必须写 `novelty_attack.md`：

```text
1. 最可能让审稿人说“already done”的 10 篇工作
2. 每篇与我们的逐项重叠
3. 哪个 claim 不能再说
4. 哪个实验必须加入以证明差异
5. 最坏情况下我们的贡献会被降级为什么
6. 建议：PASS / NARROW / MERGE / KILL
```

Research Director 只有在 Novelty Prosecutor 尝试“杀死”选题后，才能签 `NOVELTY_PASS`。

## 12.4 Citation 真实性规则

- 只引用已实际打开并核验的原始来源；
- 不根据搜索片段、博客摘要或另一个模型的文字直接引用；
- 每个 factual claim 在 `claim_registry.csv` 关联来源页码/段落；
- arXiv 版本记录版本号和日期；
- 会议状态必须核验：submitted、under review、accepted、published 不得混用；
- 不写无法访问全文却声称具体实验细节的引用；
- 引文只支持其实际论点，不扩大解释；
- 论文完成前运行 citation entailment audit 和人工抽查。

---

# 13. 数据、任务与 benchmark 构建共同标准

## 13.1 数据卡

每个数据集必须包含：

- 来源；
- 许可证；
- 构造过程；
- 包含/排除标准；
- 去重；
- train/dev/test split 单位；
- contamination 风险；
- 人工标注流程；
- inter-annotator agreement；
- 隐私与安全；
- 已知偏差；
- 版本号和 hash；
- 更新政策。

## 13.2 Split 原则

必须按真正独立单位分组：

- ToolMorph：按 base tool/task family 分组，不能让同一模板的变体跨 split；
- CrossCheck：按 repository/issue family 分组，不能同 repo 的近重复 patch 跨 split；
- DeltaResearch：按 evidence world/source family/event 分组，不能同一事件的不同 wording 跨 split；
- HarnessGuard：按 edit lineage/task family 分组，不能把同一 edit 的小改版跨 split。

## 13.3 去污染

- 对公开 benchmark 检查训练语料暴露风险；
- 优先使用可程序生成、状态型、隐藏 oracle 任务；
- 对 coding task 使用新构造或时间后切分；
- 记录模型是否可能见过题目；
- 公开结果同时报告 public 和 freshly generated/private test；
- 不把“模型可能记住”误写成推理能力。

## 13.4 LLM 生成任务的审核

LLM 可以生成候选，但必须：

1. 通过 schema validator；
2. 通过 deterministic oracle；
3. 运行至少一个 reference solver；
4. 检查歧义；
5. 检查 trivial shortcut；
6. 去重；
7. 人工抽查；
8. 封存后不得按方法结果改题。

## 13.5 Human annotation

需要人工标注时：

- 写 annotation manual；
- 进行训练轮；
- 盲化方法名称；
- 至少双标关键样本；
- 预定义 adjudication；
- 报告 agreement；
- 保存匿名 decision log；
- 若涉及真实参与者，先完成伦理/IRB 和同意流程。

---

# 14. 统计分析共同标准

## 14.1 Primary endpoint 只设一个主结果

每篇必须在 full study 前冻结一个 primary endpoint：

- ToolMorph：held-out transformation 下，automatic STNF 对 success sensitivity 的降低；
- CrossCheck：held-out repository 下，ReviewRoute 在预算约束下的 utility 改善；
- DeltaResearch：affected-claim recall 与 unaffected-claim preservation 的预定义组合分数；
- HarnessGuard：固定 canary budget 下的 dangerous false-acceptance rate 或 regression recall。

其余结果为 secondary/exploratory，不能在看完结果后升格。

## 14.2 推荐模型

### ToolMorph

二元成功：

```text
logit(P(success)) ~ method * transformation * model
                    + task_difficulty
                    + (1|task_family)
                    + (1|base_task)
```

成本/延迟采用适合分布的 GLMM 或 bootstrap。排名稳定性用 Kendall/Spearman，并用 task-cluster bootstrap。

### CrossCheck

```text
logit(P(final_correct)) ~ workflow * author_model * reviewer_model
                          + defect_type + budget
                          + (1|repository)
                          + (1|task)
```

Defect detection 使用 precision/recall；router 使用 held-out group evaluation。误差相关性报告 phi/tetrachoric 或 residual correlation，并明确条件。

### DeltaResearch

claim-level 指标存在 report 内相关性，使用 report/world cluster bootstrap 或多层模型：

```text
outcome ~ method * update_type * domain
          + initial_report_quality
          + (1|world)
          + (1|report)
```

### HarnessGuard

edit 是关键独立单位：

```text
regression_detected ~ method * budget * edit_type
                      + (1|edit_lineage)
                      + (1|task_family)
```

对 false-safe 采用 exact/binomial interval 或 hierarchical estimate；risk–coverage curve 用 edit-group bootstrap。

## 14.3 多重比较

- 主假设不做数据驱动挑选；
- secondary families 分别用 Holm 或 Benjamini–Hochberg；
- exploratory 结果明确标注；
- 不只报告 p-value，必须给 effect size 和 confidence interval；
- 不把“未显著”写成“等价”，除非预注册 equivalence margin 并做相应检验。

## 14.4 Power 与样本量

Pilot 用于估计：

- task-level base rate；
- random-effect variance；
- within-task paired correlation；
- API failure rate；
- expected practical effect。

Statistician 根据模拟 power 而不是简单公式决定 full sample。脚本必须存为：

```text
papers/<paper>/statistics/power_simulation.py
papers/<paper>/statistics/power_assumptions.yaml
```

对昂贵 Agent 实验，优先设计 paired/blocking 和 group-balanced allocation，而不是盲目扩大重复次数。

## 14.5 Missingness 与失败运行

预先定义：

- API timeout；
- provider outage；
- malformed response；
- sandbox crash；
- task environment bug；
- model refusal；
- cost limit termination；
- true agent failure。

不得把真实 Agent failure 当作基础设施错误删除。所有排除需在 `exclusions.csv` 写原因、证据和决定者。

## 14.6 Robustness suite

每篇至少做：

- alternate model family；
- alternate task family；
- alternate reasonable metric；
- judge-free core metric；
- seed/repeat sensitivity；
- budget sensitivity；
- provider/version sensitivity；
- data split sensitivity；
- strong baseline sensitivity；
- negative control；
- placebo intervention；
- leave-one-group-out。


---

# 15. Paper 1 ToolMorph：逐项执行票据

本节覆盖从零开始到 submission-ready 的精确任务顺序。Claude 应将每一条转换为 issue，并尽可能并行执行无依赖项。

## 15.1 Phase P1-A：问题与新颖性冻结

### P1-LIT-001：建立最近工作地图

搜索簇：

```text
LLM tool schema robustness
function calling schema perturbation
MCP tool interface benchmark
tool description sensitivity
schema drift agent tools
metamorphic testing LLM agents
semantic equivalence API interfaces
API wrapper normalization language models
tool-use compiler LLM
state transition equivalence tool agents
```

验收：

- ≥80 个候选，≥30 个深读；
- 10 个 nearest neighbors；
- 逐项比较：是否含 semantic equivalence oracle、held-out transformations、stateful tasks、rank reversal、normalizer；
- 明确 TSCG 等 schema compiler 与本项目的差异；
- 输出 `literature_matrix.csv` 和 `novelty_attack.md`。

### P1-SPEC-001：冻结“等价”定义

必须回答：

- 相同最终状态是否足够？
- 中间副作用、权限、时间、不可逆性是否也必须相同？
- 错误行为何时算等价？
- split/merge 工具是否属于严格等价还是工作流等价？
- 调用次数不同如何处理成本与语义？
- 非确定性工具如何定义 observational equivalence？

输出：

- 数学定义；
- strict/extended 两级 taxonomy；
- 10 个正例、10 个反例；
- 每类转换的证明义务；
- 审稿人可复核的测试规则。

### P1-CONTRACT-001：冻结 Research Contract

中心 claim 必须写成可被证伪的形式：

> 在预定义的 state-transition-equivalent interface transformations 和 held-out task families 上，automatic STNF 相比最强 non-oracle baseline，显著降低 transformation-induced success degradation，且不会以不可接受的成本换取。

预先指定 practical margin，例如：

- success degradation 绝对减少 ≥5 个百分点；或
- sensitivity AUC 改善 ≥20%；
- 且 token overhead ≤某阈值。

具体阈值由 pilot 和领域价值决定，不能在 full results 后改。

## 15.2 Phase P1-B：环境与 oracle

### P1-DATA-001：实现六个状态型微环境

每个环境要求：

- deterministic reset；
- hidden authoritative state；
- transaction log；
- role/permission model；
- idempotency semantics；
- error injection；
- final-state oracle；
- reference client；
- human-readable state diff。

环境最少包括：

1. Calendar；
2. Email；
3. CRM；
4. Inventory/Orders；
5. Helpdesk；
6. Files/Workspace。

每个环境先建立 12–20 个 base tasks，难度层级：

- single-call；
- multi-call dependency；
- conditional branch；
- partial failure recovery；
- permission-aware；
- verification-required。

### P1-DATA-002：建立 reference solver

每个任务至少一个 deterministic reference plan。它不是要求 Agent 复现相同轨迹，而用于验证：

- 任务可解；
- 转换前后环境语义一致；
- hidden oracle 正确；
- 没有 shortcut；
- reset 可复现。

### P1-DSL-001：实现 ToolMorph DSL

最小 schema：

```yaml
transform_id:
family:
strictness: strict|workflow
preconditions:
request_map:
response_map:
error_map:
state_relation:
roundtrip_property:
negative_properties:
metadata:
```

每个 transform 必须可组合，但 full study 先分析单一变换，组合变换作为 stress test。

### P1-DSL-002：property-based equivalence

对每个工具随机生成合法和非法输入，验证：

- request round trip；
- response round trip；
- same authorized state transition；
- same forbidden transition；
- same error class；
- no hidden extra side effects；
- idempotency preserved；
- concurrent conflict behavior preserved，若适用。

目标：每个 strict transform ≥10,000 property cases，零未解释 mismatch。

任何 mismatch 必须产出最小反例并修 spec；禁止通过忽略字段“让测试通过”。

## 15.3 Phase P1-C：Agent harness 与 pilot

### P1-RUNNER-001：统一 Agent tool-use harness

要求：

- 相同 system instruction；
- 相同任务文本；
- 只替换接口 representation；
- 记录模型看到的完整 tool schema；
- 记录每次 call、error、retry、state snapshot；
- 不向模型暴露 transform 名称；
- 固定模型参数；
- 记录 exact model identifier/date。

### P1-PILOT-001：运行等价性现象 pilot

设计：

- 24 base tasks，跨 4 个环境；
- 2 个模型家族；
- original + lexical + nesting + enum + response + error；
- 3 repeats；
- 完整 paired randomization。

分析：

- 每个 base task 原始和变换接口配对；
- 计算 per-transform degradation；
- 找 rank reversal；
- 分类 failure：selection、argument、interpretation、recovery、stopping；
- 检查是否只是 token length 或 description quality。

### P1-PILOT-002：反事实控制

必须加入：

- 等长度但语义不变的 padding control；
- 随机字段顺序 control；
- 给更多 token budget 的 control；
- 人工优化变换 schema 的 control；
- reference program client 证明非 Agent 执行不受影响。

### P1-GATE-001：Pilot 判定

PASS 需要：

- 至少两类 strict transformations 在两个模型/两个环境产生实质影响；
- 至少一个模型排序或 task-level outcome 发生明显变化；
- effect 不能被 token、长度或明显低质量描述完全解释；
- oracle 可靠；
- 存在 automatic normalization 的改善空间。

否则 KILL 或缩为 benchmark note。

## 15.4 Phase P1-D：STNF 方法

### P1-METHOD-001：Oracle canonicalizer

人工提供完美语义映射，作为 upper bound。若 oracle canonicalizer 都不能恢复，则问题不在 interface normalization，需重新解释。

### P1-METHOD-002：Static canonicalizer

仅使用 machine-readable schema：

- normalize names；
- flatten/nest canonicalization；
- type normalization；
- enum normalization；
- standard error envelope；
- response table normalization。

### P1-METHOD-003：LLM-assisted semantic compiler

输入：schema、description、少量 documentation。

输出 canonical tool contract：

```yaml
intent:
arguments:
preconditions:
effects:
returns:
errors:
idempotency:
permissions:
examples:
```

要求：

- compiler 与执行 Agent 可使用不同模型；
- 编译一次，运行多次；
- 输出通过 static validator；
- 不允许读取 task answer；
- 失败时 abstain，不生成危险 mapping。

### P1-METHOD-004：Probe-assisted compiler

允许在 sandbox 中执行有限安全 probes，推断：

- response shape；
- error classes；
- optional/default semantics；
- idempotency；
- pagination；
- state effects。

记录 probe cost。任何 destructive probe 必须在 disposable state 中运行。

### P1-METHOD-005：Ablation

- names only；
- types only；
- errors only；
- responses only；
- no probes；
- no LLM；
- no examples；
- oracle mapping；
- fully combined。

## 15.5 Phase P1-E：Full study

### P1-PROTOCOL-001：冻结分析计划

冻结：

- task split；
- transform split；
- model list；
- primary endpoint；
- exclusions；
- repeats；
- statistical model；
- practical margin；
- figure/table specs。

### P1-FULL-001：运行完整矩阵

推荐最低：

- 72–120 base tasks；
- 6 environments；
- ≥6 strict transform families；
- 3 model families；
- 2 repeats，关键高方差 cell 增至 3–5；
- held-out transforms/tools/model family。

先运行 5% sealed canary，检查环境和 ledger，不能看主结论后再改协议。

### P1-FULL-002：Generalization

- train on four transform families, test on two unseen；
- train on four environments, test on two unseen；
- compiler model 与 agent model 不同；
- future or newly sampled tools；
- tool description paraphrase shift；
- composed transformations stress test。

### P1-ANALYSIS-001：Mechanism

分析错误发生在哪一层：

1. 工具选择；
2. 参数生成；
3. response interpretation；
4. error recovery；
5. planning/stopping。

做中介/分解时谨慎，只称 decomposition，不轻易称 causal mediation。

## 15.6 Phase P1-F：论文与 artifact

### P1-WRITE-001：先做主图

主图建议为：

- x：transform family；
- y：success degradation relative to original；
- 每个 model 一组；
- 原始、最强 baseline、STNF；
- held-out 部分醒目标记。

### P1-ARTIFACT-001

发布：

- transform DSL；
- environments；
- task generator；
- property tests；
- adapters；
- raw traces（按许可证/隐私处理）；
- aggregate ledger；
- reproduction scripts；
- model/API cost manifest。

### P1-REDTEAM-001

Reviewer 2 必须回答：

- 是否只是 prompt engineering？
- semantic equivalence 证明是否可信？
- transform 是否人为且不现实？
- normalizer 是否只是把接口改回原始接口？
- held-out 是真 held-out 吗？
- success 改善是否来自更多 token/描述？
- 是否跨模型和环境？
- 是否有安全风险？

---

# 16. Paper 2 CrossCheck：逐项执行票据

## 16.1 Phase P2-A：新颖性与任务定义

### P2-LIT-001

检索：

```text
cross-model critic LLM
heterogeneous model review coding agents
LLM code review self review
multi-agent code repair budget matched
error correlation language models
LLM ensemble correlated errors
critic model routing code
agent generated patch review benchmark
```

必须覆盖：

- multi-agent debate/review；
- self-refinement；
- code review benchmark；
- test generation as review；
- mixture-of-experts/routing；
- ensemble diversity/error correlation；
- budget-matched agent evaluation。

输出至少 10 个直接竞争工作，特别标出已有 Cross-Model Critic 结果。我们的 novelty 只能来自完整因子矩阵、残余错误互补性、严格预算匹配和预执行 router。

### P2-SPEC-001：定义 defect 与 review success

区分：

- latent defect：patch 中实际存在；
- detected defect：reviewer 正确指出；
- false alarm：指出不存在的问题；
- actionable localization：给出足够位置/条件；
- successful repair：最终通过 hidden oracle；
- regression introduced：修复引入新失败；
- spurious edit：无必要修改。

Review detection 与 repair 必须分开评分，避免“没指出但偶然改对”。

## 16.2 Phase P2-B：数据集

### P2-DATA-001：Controlled Defect Corpus

选择小到中型真实开源 repository，要求：

- 可容器化；
- 单测可重复；
- 许可证允许；
- 不依赖秘密服务；
- 运行时间合理；
- 具有多文件和真实 API。

注入 defect 的规则：

- 每个 defect 有 deterministic hidden test；
- mutation 不改变无关行为；
- 保留 ground-truth location 和 trigger；
- 至少一个独立 validator；
- 难度分层；
- 同一 base task 的 mutations 不跨 split。

至少 8 类 defect，每类 15–25 个候选。删除 trivial、歧义或无法稳定复现的样本。

### P2-DATA-002：Agent Near-Miss Corpus

让 author models 在真实 issue 上生成 patch；只保留：

- visible tests 通过或接近通过；
- hidden tests 暴露明确 defect；
- patch 可编译/运行；
- 缺陷不是基础设施错误；
- 有独立修复或 oracle。

避免 cherry-pick：保存所有生成尝试和筛选规则，报告 retention funnel。

### P2-DATA-003：Repository split

- train/dev/test 按 repository；
- sealed test 采用全新 repositories；
- 路由器不读 test repo 名称作为 shortcut；
- 检查模型可能见过公开 issue 的风险；
- 加一批新合成 issue 或 post-cutoff commits。

## 16.3 Phase P2-C：统一 review protocol

### P2-HARNESS-001：Author stage

统一输入：

- issue text；
- repository snapshot；
- visible tests；
- 工具权限；
- 时间/token budget。

记录：

-完整 trajectory；
- tests run；
- files read/modified；
- self-reported confidence；
- final patch。

### P2-HARNESS-002：Detection-only reviewer

Reviewer 输入：

- issue；
- repository；
- patch/diff；
-允许的 test budget；
- 不看 author hidden reasoning；
- 不看 hidden tests；
- 不知 author identity，除非该实验显式研究 identity effect。

输出结构：

```yaml
verdict: accept|reject|uncertain
findings:
  - file:
    line_or_symbol:
    defect_type:
    trigger:
    explanation:
    suggested_test:
confidence:
```

### P2-HARNESS-003：Repair stage

三种 repair：

- author receives review and repairs；
- reviewer directly repairs；
- independent reimplementation。

主比较必须预定义，不能把最好的一种事后选为主结果。

## 16.4 Phase P2-D：预算匹配

### P2-BUDGET-001

至少报告三种视角：

1. equal total tokens；
2. equal dollar cost；
3. natural provider usage。

主分析选择一种，另两种作为 robustness。

作者加预算 baseline 必须允许同模型：

- 更长思考；
- 再跑测试；
- 第二次独立尝试；
- 自我 review。

否则“第二模型更好”可能只是多花计算。

### P2-BUDGET-002：Latency

异构 reviewer 可并行或串行，分别报告：

- end-to-end latency；
- critical path；
- compute sum；
- provider queue effect。

## 16.5 Phase P2-E：Pilot

### P2-PILOT-001

- 40–60 defective patches；
- 至少 4 defect types；
- 两个 author models 双向；
- no review、extra author compute、self、same-family fresh、cross-family、test-generation；
- detection-only + repair 分开。

### P2-PILOT-002：Complementarity 分析

构造每个 reviewer 对 author residual defect 的检出矩阵。检查：

- reviewer overall strength；
- conditional complementarity；
- defect-type-specific advantage；
- false alarm correlation；
- repair regression。

不要把简单 accuracy 差异误称互补性。

### P2-GATE-001

PASS 要求：

- 至少一种 defect/context 下异构 reviewer 在预算匹配后仍有实质增益；
- 存在可预测的 heterogeneity，而不是所有任务同一最强 reviewer；
- reviewer false alarms 可控制；
- held-out routing 有合理信号。

若单一 reviewer 全面占优，则论文改为 reviewer selection/strength study；若额外作者预算全面更好，则考虑负面结果但需机制足够强。

## 16.6 Phase P2-F：ReviewRoute

### P2-METHOD-001：Feature freeze

路由决策发生在调用第二策略前，可用：

- issue length/类型；
- repo language/size；
- diff size/entropy；
- files touched；
- test outcomes；
- author trajectory；
- tool errors；
- author confidence；
- static analysis；
- model identity。

不可用：

- hidden test；
-最终 reviewer outcome；
- sealed defect label。

### P2-METHOD-002：Utility

```text
utility = final_correct
          - lambda_cost * normalized_cost
          - lambda_latency * normalized_latency
          - lambda_regression * new_regression
```

至少给多组合理 λ 的 Pareto 分析；不要只挑最有利权重。

### P2-METHOD-003：Baselines

- always no review；
- always self review；
- always strongest reviewer；
- always cross-model；
- random policy；
- uncertainty threshold；
- static risk score；
- learned router；
- oracle router upper bound。

### P2-METHOD-004：Modeling

先从 interpretable baseline 开始：

- logistic/multinomial regression；
- gradient-boosted trees；
- contextual bandit 仅在数据量足够时；
- calibrated probabilities；
- abstain/escalate。

避免小数据训练复杂神经网络。

## 16.7 Phase P2-G：Full study

### P2-PROTOCOL-001

冻结：

- author/reviewer models；
- model snapshots；
- repositories；
- defect categories；
- workflows；
- cost accounting；
- primary utility；
- router train/test split；
- hidden tests；
- analysis plan。

### P2-FULL-001

推荐：

- 150–250 tasks/patches；
- ≥3 model families 或至少 3 model snapshots；
- 8 defect types；
- 10+ repositories；
- full author-reviewer directional matrix；
- 关键条件多次重复。

若成本受限，优先扩大独立 repositories/tasks，而非同一 patch 大量重复。

### P2-FULL-002：Generalization

- held-out repositories；
- held-out defect categories；
- held-out author model；
- language shift；
- real vs controlled defect transfer；
- model version update。

### P2-ANALYSIS-001：Mechanism

回答：

- 互补来自知识、搜索行为、test strategy 还是 reasoning style？
- 同模型 fresh context 与异构模型差别多大？
- reviewer 是否只更保守？
- 哪类 finding 最可执行？
- cross-review 是否增加无谓改动？

## 16.8 Phase P2-H：FSE 稿件与 artifact

### P2-WRITE-001 主图

推荐：cost–correctness frontier，按 workflow；再叠加 ReviewRoute 和 oracle router。

### P2-WRITE-002 主表

按 defect category 报告：

- author residual rate；
- reviewer detection recall；
- false alarm；
- final repair success；
- new regression；
- cost。

### P2-ARTIFACT-001

- containerized repos；
- mutation scripts；
- hidden tests（如可发布，否则提供 evaluation server/加密 artifact）；
- review prompts/protocol；
- trajectories；
- cost accounting；
- router code；
- full reproduction；
- artifact README。

### P2-REDTEAM-001

- 是否只是模型 A 比模型 B 强？
- 预算真的匹配吗？
- reviewer 是否看到额外信息？
- defect 是人工玩具吗？
- router 是否数据泄漏？
- 同 repo 泄漏？
- 结果会随模型更新消失吗？
- 为什么不是简单多采样？
- software engineering insight 是什么？

---

# 17. Paper 3 DeltaResearch：逐项执行票据

## 17.1 Phase P3-A：定义与新颖性

### P3-LIT-001

检索：

```text
deep research report revision benchmark
multi-turn research agent report update
claim evidence dependency graph
citation post-rationalization LLM
selective document revision evidence update
temporal RAG knowledge update
fact revision long-form generation
minimal edit factual update LLM
versioned evidence benchmark
```

必须区分：

- 初次生成报告；
- 普通 follow-up revision；
- citation correctness；
- temporal factual QA；
- model editing；
- document-level selective revision。

重点核对 Mr. DRE 等多轮报告修订工作，明确我们的 unit 是 evidence delta → claim impact，而不是“改稿能力”。

### P3-SPEC-001：Claim taxonomy

每个 claim 分类：

- direct factual；
- numeric；
- comparative；
- causal；
- forecast/uncertain；
- synthesis；
- recommendation；
- attribution；
- methodological。

Dependency 类型：

- direct support；
- numeric derivation；
- conjunctive；
- disjunctive；
- defeater/conflict；
- temporal validity；
- contextual only。

### P3-SPEC-002：Affected set 定义

Claim 在 update 后属于：

- `must_change`；
- `may_change`；
- `must_preserve`；
- `newly_supported`；
- `now_conflicted`；
- `unsupported_but_unchanged_evidence`。

主指标只对明确 `must_change` 和 `must_preserve` 计算；模糊 claim 单独分析。

## 17.2 Phase P3-B：DeltaBench

### P3-DATA-001：Controlled Evidence Worlds

每个 world 由结构化事实和版本化 documents 渲染。生成流程：

1. 先生成 latent fact graph；
2. 从图生成多个来源，含支持、冗余和冲突；
3. 生成 initial question；
4. 用 reference generator 生成可核验 report；
5. 施加 evidence delta；
6. 自动传播 gold affected set；
7. 人工抽查 narrative 是否自然。

优点：gold impact 可程序确定；缺点：合成性。必须用真实层补足。

### P3-DATA-002：Real Versioned Worlds

候选来源优先：

- 官方经济数据不同 vintage；
- 软件/技术官方文档版本；
- 标准或法规版本；
-论文 corrigendum/retraction；
- 产品规格/政策更新；
- 公共统计修订。

要求：

- 可证明的发布时间；
- archived snapshot；
- 更新前后内容；
- 许可证允许；
- 不依赖动态网页当前状态；
- 专家或双人标注 affected claims。

避免高风险个人医疗/法律建议作为首批领域。

### P3-DATA-003：Question/report construction

问题必须要求多来源综合，不能一个事实替换即可。报告建议 800–2000 words，包含 12–30 atomic claims。

保留：

- source bundle W0；
- initial report R0；
- source delta ΔW；
- W1；
- claim graph；
- gold affected/preserved；
- expected numeric recalculations；
- update rationale。

### P3-DATA-004：Gold validation

对 real worlds：

- 两名标注者独立标 claim；
- 盲于方法输出；
- adjudication；
- agreement；
- domain expert 抽查高风险 numeric/technical cases。

## 17.3 Phase P3-C：Initial report quality control

### P3-REPORT-001

只纳入初始报告达到最低质量的 world：

- 初始 factual correctness；
- citation validity；
- claim atomicity；
- 足够 coverage；
- 无严重 unsupported claim。

否则 update performance 无法解释。

建立两种轨道：

1. fixed high-quality R0；
2. end-to-end agent-generated R0。

主实验优先 fixed R0，隔离 revision 能力；end-to-end 做外部有效性。

## 17.4 Phase P3-D：ClaimPatch 方法

### P3-METHOD-001：Claim atomizer

输入报告，输出 atomic claim ledger：

```yaml
claim_id:
span:
normalized_proposition:
claim_type:
certainty:
time_scope:
source_ids:
derivation:
dependencies:
```

评估 atomization precision/coverage，不把解析错误藏在最终指标里。

### P3-METHOD-002：Evidence ledger

对每个 source：

- version/date；
- authority；
- relevant spans；
- fact triples/numeric values；
- validity interval；
- supersedes/retracts relation；
- conflicts。

### P3-METHOD-003：Dependency linker

方法层级：

1. citation proximity baseline；
2. semantic entailment；
3. LLM structured linker；
4. linker + counterfactual deletion；
5. oracle gold graph upper bound。

### P3-METHOD-004：Impact analyzer

输入 delta，输出：

- directly affected claims；
- propagated downstream claims；
- preserved claims；
- uncertain claims requiring re-research。

必须允许 abstain，不强行二分。

### P3-METHOD-005：Constrained patcher

只允许修改被授权的 spans，除非 verifier 发现依赖扩散。策略：

- minimal span edit；
- paragraph-level regeneration；
- graph-subtree regeneration；
- full regeneration baseline。

### P3-METHOD-006：Post-update verifier

检查：

- updated claims supported；
- stale values removed；
- preserved claims unchanged in meaning；
- citation versions correct；
- numeric consistency；
- cross-section contradictions；
- change log complete。

## 17.5 Phase P3-E：Pilot

### P3-PILOT-001

- 30 controlled + 10 real worlds；
- 2 domains；
- 2 research agents；
- methods：full regenerate、naive revise、citation-aware revise、ClaimPatch；
- 1–3 delta types/world。

### P3-PILOT-002：Judge validation

主指标尽量用 gold graph 和 deterministic string/numeric checks。对语义变化：

- 两个独立 judges；
- 人工样本；
- agreement；
- judge prompt perturbation；
- 方法名盲化。

### P3-GATE-001

PASS：

- naive/full regeneration 确实出现 stale claims 或无关漂移；
- dependency ledger 能改善 affected recall 或 preservation；
- real worlds 也有信号；
-主结果不依赖单一 judge；
- full regenerate 不是全面占优。

## 17.6 Phase P3-F：Full study

### P3-PROTOCOL-001

冻结：

- world split；
- update taxonomy；
- claim labels；
- agents/models；
- methods；
- primary combined score；
- human evaluation sample；
- exclusions；
- statistical analysis。

### P3-FULL-001

最低目标：

- 240 controlled worlds；
- 60 real worlds；
- 3 domains（至少两个真实）；
- 3 agents；
- 5 methods；
- 单次和多次连续 updates。

连续 update 场景测累积漂移，但作为 secondary，避免范围失控。

### P3-FULL-002：Stress tests

- contradictory update；
- source retraction；
- numeric revision with downstream calculations；
- new source without direct citation；
- source authority reversal；
- ambiguous update；
- irrelevant source update negative control；
- multiple simultaneous deltas；
- report with cross-section dependencies。

### P3-FULL-003：Generalization

- held-out domain；
- held-out update type；
- held-out source style；
- initial report from unseen model；
- long reports；
- different report organization。

## 17.7 Phase P3-G：分析与写作

### P3-ANALYSIS-001

错误分类：

- missed direct update；
- missed downstream update；
- over-propagation；
- semantic drift in preserved claim；
- stale citation；
- calculation inconsistency；
- conflict suppression；
- unjustified confidence；
- report coherence break。

### P3-WRITE-001 主图

二维图：

- x：unaffected-claim preservation；
- y：affected-claim correction；
- bubble：cost 或 report quality；
- 方法位于 Pareto frontier 才有说服力。

### P3-ARTIFACT-001

- DeltaBench controlled generator；
- real source snapshot metadata；
- claim/evidence annotations；
- update evaluator；
- ClaimPatch；
- anonymized trajectories；
- reproduction scripts；
- data/license card。

### P3-REDTEAM-001

- 是否只是 diff/编辑距离？
- Gold affected set 主观吗？
- 合成数据是否太容易？
- Full regenerate 为什么不够？
- Claim graph 是否由模型自说自话？
- 是否与 temporal RAG/model editing 重复？
- Report 初始质量是否偏置方法？
- LLM judge 是否偏好 minimal edits？
- 多领域泛化是否真实？

---

# 18. Paper 4 HarnessGuard：逐项执行票据

## 18.1 Phase P4-A：新颖性与编辑语义

### P4-LIT-001

检索：

```text
automatic agent harness optimization
agent harness evolution regression
LLM agent prompt optimization regressions
test selection for stochastic systems
regression test prioritization ML systems
canary testing AI agents
model upgrade regression agent
edit conditioned test selection
risk controlled deployment LLM agents
```

邻域包括：

- automatic prompt/harness evolution；
- agent optimization；
- software regression test selection；
- ML model regression monitoring；
- canary deployment；
- conformal risk control/abstention；
- benchmark subset selection。

必须明确：AHE 已解决“如何自动改 Harness”，本项目解决“改完后如何低成本预见隐藏回归”。

### P4-SPEC-001：Harness edit ontology

Harness component：

- system prompt/instructions；
- context construction；
- tool description/schema；
- tool routing；
- memory/retrieval；
- planner；
- verifier；
- retry/recovery；
- stopping；
- permissions/confirmation；
- middleware/runtime。

Edit operation：

- add/remove；
- modify threshold；
- reorder；
- compress/expand；
- replace model/module；
- change tool exposure；
- change retry/timeout；
- change memory policy；
- change verification frequency。

Impact mechanism：

- intended target behavior；
- plausible collateral behavior；
- likely task features affected；
- expected cost/latency effect。

## 18.2 Phase P4-B：Edit corpus

### P4-DATA-001：Real historical edits

来源可包括：

- 自建 agent runtime git history；
- 公开 agent frameworks/benchmarks 的可复现版本；
- 公开 prompt/harness evolution artifacts；
- 公开 issue/commit 中明确修复行为的 edits。

纳入标准：

- old/new revision 可运行；
- edit effect 可隔离或记录；
- 同一 task suite 可跑；
- 许可证允许；
- 没有不可用商业秘密。

### P4-DATA-002：Controlled atomic edits

为获得覆盖，系统构造合理 edits：

- verifier removal/addition；
- retry count；
- context truncation；
- tool description rewrite；
- memory retrieval top-k；
- stop condition；
- approval threshold；
- error handling；
- planner prompt；
- tool result summarization。

每个 edit 都应有 intended benefit，不能只造明显破坏。

### P4-DATA-003：Optimizer-generated edits

使用一个或多个 automatic optimization agents，在 dev tasks 上改 Harness。保留：

- proposal；
- rationale；
- diff；
- dev gain；
- accepted/rejected；
- full test outcome。

这类 edit 最贴近真实自演化，但必须防止 optimizer 接触 test set。

### P4-DATA-004：Edit lineage split

同一优化序列的相邻 edits 高度相关，必须作为同一 lineage 分组。Train/test 按 lineage 和 component 双重检查。

## 18.3 Phase P4-C：Task suite 与回归 ground truth

### P4-TASK-001

两大类：

1. coding/terminal；
2. stateful workspace/tool tasks。

每类 30–60 tasks，覆盖：

- easy/hard；
- tool-heavy；
- verification-heavy；
- long-context；
- recovery；
- permissions；
- irreversible action；
- sparse feedback。

### P4-GT-001：Old/new paired execution

对每个 edit × task × model：

- old harness 与 new harness 使用同 task snapshot；
- paired seeds/randomization；
- 多次运行估计 stochastic success；
- 记录 success、cost、latency、safety violations；
-定义 meaningful regression margin。

回归不是单次 `old pass, new fail` 就结束。可以定义：

- binary paired regression；
- success probability drop；
- cost blow-up；
- safety regression；
- worst-group regression。

Primary 选择一种，其他 secondary。

### P4-GT-002：Full-suite ground truth seal

完整运行结果由 Test Custodian 保存。Risk model/selector 只能看 train/dev full outcomes；sealed test 只在 protocol freeze 后解封。

## 18.4 Phase P4-D：Edit contract 与 features

### P4-METHOD-001：Edit parser

输入 code/prompt/config diff，输出结构化 edit contract。必须同时保留：

- automatic parse；
- edit author rationale；
- static diff features；
- changed runtime paths；
- dependencies。

### P4-METHOD-002：Task fingerprint

从历史 old-harness trajectory 提取，不运行 new harness：

- tool usage；
- errors/retries；
- context length；
- verification actions；
- state changes；
- action entropy；
- plan depth；
- permission usage；
- task semantics embedding。

### P4-METHOD-003：Pair risk model

预测 `P(regression | edit, task, old trace)`。

先做：

- component × task heuristic；
- keyword/static rules；
- linear model；
- tree model；
- learned joint embedding，数据足够才做。

必须 calibration。

### P4-METHOD-004：Diverse canary selection

给定预算 k，选择高风险且多样的任务：

```text
maximize sum predicted_risk
         + alpha * coverage
         - beta * redundancy
```

比较 greedy、submodular、uncertainty sampling、random、difficulty。

### P4-METHOD-005：Sequential policy

运行 canary 后更新 decision：

- `REJECT`：发现明确严重回归；
- `ACCEPT`：证据支持在定义风险范围内上线；
- `ESCALATE`：不确定，跑更多 canary/full suite。

不要声称绝对安全；输出经验/统计风险界限和适用假设。

## 18.5 Phase P4-E：Pilot

### P4-PILOT-001

- 12–16 independent edits；
- 30 tasks；
- 2 models；
- old/new paired；
- 2 repeats 起步；
- random、difficulty、component heuristic、edit-conditioned selector。

### P4-PILOT-002：必要性检查

先回答：

- edits 是否真的产生隐藏回归？
- 回归是否集中在少数 task traits？
- dev gain 与 test regression 是否存在 tradeoff？
- edit metadata 是否能预测？
- task history 是否增加信息？

### P4-GATE-001

PASS：

- ≥25% edits 有至少一个 meaningful hidden regression，或存在足够连续 regression signal；
- random small suite 漏掉实质回归；
- edit-conditioned feature 有可迁移信号；
- full suite 昂贵到 canary 有意义；
- 可收集至少 30 个独立 edits。

否则 KILL，或改为 descriptive corpus/benchmark，但不要包装成预测论文。

## 18.6 Phase P4-F：Full study

### P4-PROTOCOL-001

冻结：

- edit corpus；
- lineage split；
- task suite；
- models；
- regression definition；
- canary budgets；
- baselines；
- primary risk metric；
- calibration method；
- escalation policy。

### P4-FULL-001

最低：

- 36 independent edits，最好 50–60；
- 60–120 tasks；
- 2–3 models；
- 3 edit sources；
- task-level paired repeats；
- leave-one-component-out；
- leave-one-lineage-out；
- held-out model/task domain。

### P4-FULL-002：Risk–coverage

对每个 canary budget：

- 1、2、4、8、16、full；
- regression recall；
- dangerous false acceptance；
- false reject；
- escalation；
- cost saved；
- latency；
- worst-group coverage。

### P4-FULL-003：Ablation

- no edit text；
- no code diff；
- no task semantics；
- no old trajectory；
- no diversity；
- no calibration；
- no abstention；
- static smoke suite；
- oracle selector upper bound。

### P4-FULL-004：Deployment simulation

按时间/optimization sequence 顺序模拟：

- edit proposed；
- selector chooses canaries；
- policy decides；
- accepted edit changes future baseline；
- accumulated cost/regressions。

这一分析能显示长期价值，但必须保留独立 test lineage。

## 18.7 Phase P4-G：分析、写作和 artifact

### P4-ANALYSIS-001

错误分类：

- edit parser miss；
- task fingerprint miss；
- unseen interaction；
- stochastic variance；
- calibration failure；
- canary redundancy；
- false alarm from noisy task；
- compound edit ambiguity。

### P4-WRITE-001 主图

Risk–coverage/cost curve：

- x：full-suite cost fraction；
- y：hidden regression recall 或 false-safe；
- methods：random、smoke、difficulty、HarnessGuard；
- shaded CI by edit bootstrap。

### P4-ARTIFACT-001

- edit corpus；
- old/new harness snapshots；
- task suite；
- full outcomes；
- feature extraction；
- selector；
- sequential policy；
- reproduction profile（small/full）；
- model/cost ledger；
- anonymized artifact。

### P4-REDTEAM-001

- edit 数量是否足够？
- 是否只学会 component label？
- full-suite ground truth 是否稳定？
- 相同 optimization lineage 泄漏？
- canary 是否只是选最难题？
- 运行 canary 后“预测”是否太晚？
- risk guarantee 是否过度？
- 与普通 test selection 的差异是什么？
- 真实部署是否有价值？


---

# 19. 四线并行依赖图与首批任务队列

## 19.1 依赖图

```text
COMMON-001 repo scaffold
  ├── COMMON-002 run ledger
  ├── COMMON-003 model adapters
  ├── COMMON-004 container runner
  ├── COMMON-005 citation database
  └── COMMON-006 experiment CI

P1 ToolMorph
  LIT/SPEC ─┬─> environments ─> DSL/oracle ─> pilot ─> STNF ─> full ─> paper
            └─> task design ────────────────────┘

P2 CrossCheck
  LIT/SPEC ─┬─> repo/task corpus ─> author patches ─> review matrix ─> router ─> full
            └─> budget accounting ────────────────────────────────────────────┘

P3 DeltaResearch
  LIT/SPEC ─┬─> controlled worlds ─> claim gold ─> pilot ─> ClaimPatch ─> full
            └─> real versioned worlds ───────────────────────────────────────┘

P4 HarnessGuard
  LIT/SPEC ─┬─> edit corpus ─┬─> full old/new outcomes ─> selector ─> full
            └─> task suite ──┘
```

## 19.2 首批可以立即并行的 issues

Claude 启动后不等待额外批准，创建并执行以下可逆任务：

### Common

- `COMMON-001` 初始化 monorepo、license、pre-commit、CI；
- `COMMON-002` 定义 run ledger schema 和 validator；
- `COMMON-003` 实现 provider-agnostic model adapter interface；
- `COMMON-004` 实现 containerized task runner；
- `COMMON-005` 建立 SQLite/BibTeX 文献库与 source verifier；
- `COMMON-006` 建 claim registry 和 manuscript consistency checker；
- `COMMON-007` 建预算账本和 dry-run cost estimator；
- `COMMON-008` 建 sealed split access controls；
- `COMMON-009` 建 reproducibility profile；
- `COMMON-010` 建 automatic status dashboard。

### ToolMorph

- `P1-LIT-001` 最近工作地图；
- `P1-SPEC-001` 等价定义；
- `P1-DATA-001A` Calendar environment；
- `P1-DATA-001B` Email environment；
- `P1-DSL-001` transformation DSL schema；
- `P1-DSL-002A` lexical transform；
- `P1-DSL-002B` structural nesting transform；
- `P1-ORACLE-001` state relation checker。

### CrossCheck

- `P2-LIT-001` 最近工作地图；
- `P2-SPEC-001` defect taxonomy；
- `P2-DATA-REPO-001` 候选 repo 筛选；
- `P2-MUT-001` API misuse injector；
- `P2-MUT-002` boundary-condition injector；
- `P2-HARNESS-001` author stage schema；
- `P2-HARNESS-002` detection-only review schema；
- `P2-BUDGET-001` token/dollar accounting。

### DeltaResearch

- `P3-LIT-001` 最近工作地图；
- `P3-SPEC-001` claim taxonomy；
- `P3-WORLD-001` latent fact graph schema；
- `P3-WORLD-002` numeric revision generator；
- `P3-WORLD-003` source retraction generator；
- `P3-REAL-001` versioned official source inventory；
- `P3-EVAL-001` affected/preserved evaluator；
- `P3-ANNOT-001` annotation guide draft。

### HarnessGuard

- `P4-LIT-001` 最近工作地图；
- `P4-SPEC-001` edit ontology；
- `P4-EDIT-001` real edit mining tool；
- `P4-EDIT-002` controlled verifier edits；
- `P4-EDIT-003` controlled retry/context edits；
- `P4-TASK-001` candidate task inventory；
- `P4-GT-001` old/new paired runner；
- `P4-FEAT-001` edit diff feature extractor。

## 19.3 优先级调度

Research Director 使用：

```text
priority = scientific_value
           × probability_of_information_gain
           × dependency_unblocking
           ÷ expected_cost
```

优先做能让项目早死或早通过的任务，而不是优先写论文文字。

顺序原则：

1. 新颖性碰撞检测；
2. oracle/ground truth 可行性；
3. 最小 phenomenon pilot；
4. 强 baseline；
5. 方法；
6.规模化；
7. 写作。

---

# 20. 每日/每轮运行报告格式

Claude 每个工作周期结束时更新，不需要向人类逐项请求许可，但必须留下：

```markdown
# Research Status — YYYY-MM-DD

## Portfolio
- P1: <state>, confidence <0-1>
- P2: <state>, confidence <0-1>
- P3: <state>, confidence <0-1>
- P4: <state>, confidence <0-1>

## Completed evidence
- issue / artifact / commit / acceptance result

## Strongest new finding
- finding
- evidence
- alternative explanations
- whether confirmatory or exploratory

## Failures and counterexamples
- what failed
- why
- impact on claim

## Novelty changes
- new nearest paper
- collision risk
- required response

## Budget
- spent / committed / projected

## Decisions made
- continue / narrow / pivot / kill / merge
- justification

## Next executable queue
- ranked issues with dependencies

## Human decisions required
- only true gated decisions
```

禁止写空泛状态如“取得良好进展”。每个进展必须链接 artifact/commit/run ID。

---

# 21. 论文写作流水线

## 21.1 先冻结 Evidence Package

写正文前，每篇必须有：

```text
main_figure.pdf
main_table.csv
secondary_tables/
analysis_report.md
failure_taxonomy.md
claim_registry.csv
limitations.md
reproducibility_report.md
novelty_matrix.csv
```

没有 Evidence Package，不允许 Paper Writer 起草强结论。

## 21.2 一句话贡献测试

每篇必须通过：

### ToolMorph

> 我们证明并量化了工具接口等价表示导致的 Agent 能力不稳定，并提出能迁移到未见工具/变换的语义归一化方法。

### CrossCheck

> 我们证明异构 review 的价值由条件性错误互补决定，并给出在预算约束下选择 review 策略的方法。

### DeltaResearch

> 我们提出证据更新驱动的报告选择性修订任务，并通过 claim–evidence dependency 实现“该改的改、不该改的不漂移”。

### HarnessGuard

> 我们提出 edit-conditioned canary testing，在远低于完整评测成本时发现自动 Harness edit 的隐藏回归。

若 full evidence 不支持句中任一成分，就删除或降级，不得继续宣传。

## 21.3 Abstract 模板

```text
Context: 一个重要且具体的问题。
Gap: 现有工作未测量/解决的精确缺口。
Approach: 我们提出的数据/协议/方法。
Study: 模型、任务、条件的具体规模。
Primary result: 带不确定性的主结果，不只写最高提升。
Mechanism/analysis: 为什么或何时成立。
Artifact: 发布什么。
Scope: 最重要的边界条件。
```

禁止在 abstract 使用：

- “revolutionary”；
- “solves agent reliability”；
- 没有定义的 “robust”；
- 只报最好 cell；
- 没有 baseline/context 的百分比；
- 把相关性称因果。

## 21.4 Introduction 五段法

1. 现实问题与科学问题；
2. 为什么现有评估/方法不够；
3. 一个具体反例或失败图；
4. 本文方法与实验；
5. 3–4 条可核验贡献。

贡献列表每条必须映射到一个 artifact/section/result。

## 21.5 Related Work

按问题维度组织，不写论文流水账。每段结尾明确：

- 已有工作解决什么；
- 没解决什么；
- 我们新增什么；
- 差异是否经过实验验证。

Novelty 不应依靠“据我们所知第一个”这一句；若使用，必须经系统检索且仍谨慎。

## 21.6 Methods

要求别人能实现：

- 输入/输出；
- 算法；
- pseudocode；
- model prompts；
- training/tuning；
- budget；
- failure/abstention；
-复杂度；
- safety constraints。

LLM component 必须给 exact model/date/settings，且说明不可复现 provider updates 的风险。

## 21.7 Experiments

顺序：

1. RQs/Hypotheses；
2. datasets/tasks；
3. models/harnesses；
4. baselines；
5. metrics；
6. protocol；
7. statistics；
8. main results；
9. ablations；
10. generalization；
11. failure analysis；
12. cost；
13. limitations。

不要把全部实现细节藏在附录；影响有效性的设置必须正文出现。

## 21.8 Limitations

必须具体说明：

- 模型/API 随时间变化；
- 任务域覆盖；
- 数据合成比例；
- judge/human annotation 限制；
- 成本；
- 因果解释边界；
- 部署外推；
- 安全与滥用；
- 独立作者/实验室复现尚缺什么。

主动写 limitations 不降低论文价值；过度声称会。

## 21.9 自动 consistency checks

CI 检查：

- PDF 中每个数字能否追踪 ledger；
- abstract 数字是否与表一致；
- model 名称和版本一致；
- task 数量一致；
- 图注自包含；
- table row totals；
- confidence interval 与 source data；
- reference key 存在；
- claim 有证据；
- anonymization；
- appendix links；
- artifact hash。

---

# 22. 三轮论文红队

## 22.1 Round 1：Fatal Novelty Review

Reviewer 2 prompt：

```text
Assume this paper should be rejected as already done. Find the closest work,
construct the strongest overlap argument, identify every contribution that is
merely engineering, and state the minimum experiment or reframing required for
novelty. Do not be polite. Cite original sources and separate verified facts
from conjecture.
```

输出：score、fatal overlap、surviving contribution、required action。

## 22.2 Round 2：Methodology Review

```text
Assume all reported effects may be artifacts. Attack data leakage, unit of
analysis, budget matching, oracle validity, judge bias, model versioning,
multiple comparisons, missing baselines, group splits, and alternative
explanations. For each concern, propose a falsification test.
```

所有 fatal concerns 必须通过新增实验、修正分析或降低 claim 关闭。

## 22.3 Round 3：Top-venue Simulation

至少三个独立 reviewer personas：

- 领域专家；
- 方法/统计专家；
- 怀疑型系统/复现专家。

每人给：

- summary；
- strengths；
- weaknesses；
- questions；
- score distribution；
- confidence；
- accept condition。

再由 Meta-review Agent 综合，但不允许自己“投票覆盖”具体问题。

## 22.4 Rebuttal rehearsal

对每个预计问题：

- 先看能否在投稿前修复；
- 再准备 150–250 字证据型回答；
- 不承诺无法在 rebuttal 完成的新大实验；
- 不攻击 reviewer；
- 引用 paper section/table；
- 明确承认限制。

---

# 23. 独立复现与 artifact 评估

## 23.1 Reproducer 隔离

Independent Reproducer：

- 只获得匿名 repository release；
- 从干净机器/container 开始；
- 不看开发者私有笔记；
- 按 README 重跑；
- 记录所有偏差；
- 对主表抽样重现；
- 检查随机性与 seed；
- 检查费用估算；
- 检查 sealed 数据未泄漏。

## 23.2 两个 reproduction profiles

### Small

- 低成本；
- 数小时/合理资源内；
- 复现一张核心图的趋势；
- 使用开源或 mock model；
- 用于 artifact evaluator。

### Full

- 完整模型矩阵；
- exact manifests；
- 可选 API keys；
- 预计费用和运行时；
- 分批恢复；
- ledger verification。

不得把小 profile 的不同结果冒充完整数字。

## 23.3 Artifact checklist

- README 从零开始；
- license；
- data license；
- environment lockfile；
- container；
- expected hardware；
- API prerequisites；
- command examples；
- expected output；
- checkpoint/hash；
- troubleshooting；
- privacy redaction；
- no secrets；
- archival release/DOI，投稿规则允许时。

---

# 24. 投稿路线与当前已知时间点

> 本节以 2026-06-25 为基准。Research Director 在每次投稿前只以 venue 官方页面为准，更新日期、格式、匿名、LLM、dual-submission 和 artifact 规则。

## 24.1 CrossCheck

首选：**FSE 2027 Research Papers**。

当前官方关键日期：

- Full paper submission：2026-10-02 AoE；
- Author response：2026-12-14 至 2026-12-18；
- Initial notification：2027-01-22；
- Major revision：2027-03-05；
- Final notification：2027-03-31。

投稿前：

- 使用官方模板；
- 严格匿名；
- 检查页数；
- open science 包；
- 与软件测试/演化/AI for SE 的贡献对齐；
- 不把产品对比写成营销报告。

## 24.2 DeltaResearch

首选：**ARR**，预计更现实的完整周期是 2026-10-12；只有在数据、实验和稿件都达到 gate 时才考虑 2026-08-03。

当前官方 ARR 日期：

- August cycle submission：2026-08-03，cycle end 2026-10-11；
- October cycle submission：2026-10-12，cycle end 2026-12-20；
- EACL 2027 接受 August cycle 作为 final ARR submission，commit date 2026-10-11。

注意：

- ARR 只提供 review，之后要 commit 到 participating venue；
- 全体作者 reviewer registration/服务义务须按当期规则履行；
- 不允许 dual submission；
- AI writing/coding assistance 按 ACL/venue 当期规则披露；
- entirely AI-generated、hallucinated citations、thin slicing 有 desk-rejection/制裁风险。

## 24.3 ToolMorph

两条路线：

- 若方法、跨模型/环境 generalization 和系统贡献强：等待 **MLSys 2027 / ICLR 2027** 官方 CFP；
- 若实证和方法可靠但不必追 deadline：**TMLR rolling**。

不得虚构 MLSys/ICLR 2027 截止日期。MLSys 适配点是 autonomous agent systems、测试/调试/监控和系统评估。

## 24.4 HarnessGuard

首选：**MLSys 2027 / ICLR 2027**；备选 TMLR。

只有达到以下 flagship gate 才冲顶会：

- ≥30 independent edits；
-真实 + controlled + optimizer-generated；
- held-out component/lineage/model/task；
- 明显优于 random/difficulty/static smoke；
- risk–coverage 和 false-safe 可靠；
- artifact 可复现。

## 24.5 TMLR 路线规则

- rolling submission；
- 技术正确性与证据是核心；
- 不与其他正式 venue 平行投稿；
- 不重复发表有重叠的已发表工作；
- LLM 只能辅助，作者对全部内容负责；
- 关注年度 authorship quota；
- OpenReview 讨论和修订应持续响应。

## 24.6 Submission packet

每篇提交前生成：

```text
submission/
├── paper_anonymous.pdf
├── source_anonymous.zip
├── supplementary.pdf
├── artifact_anonymous/
├── reproducibility_statement.md
├── ethics_broader_impact.md
├── llm_disclosure.md
├── author_contribution_private.md
├── overlap_matrix_private.md
├── citation_audit_report.md
├── plagiarism_self_check.md
├── anonymity_audit.md
├── venue_compliance_checklist.md
└── final_sha256.txt
```

---

# 25. LLM 使用、作者责任与披露

## 25.1 原则

Claude、Codex 和其他模型可用于：

- 文献候选发现；
- 代码实现；
- 测试；
- 数据候选生成；
- 语言润色；
- 图表脚本；
- 失败分类候选；
- 模拟审稿。

但人类作者必须：

- 做实质性智力贡献；
- 审核全部中心 claim；
- 核验引用；
- 核验主结果；
- 决定研究设计；
- 对错误、伦理和完整性负责；
- 满足目标 venue 的作者资格。

LLM 不列为作者。

## 25.2 研究日志

记录：

```yaml
tool:
model_version:
date:
purpose:
input_data_classification:
output_used_in:
human_verification:
known_limitations:
```

## 25.3 披露模板

具体文字按 venue 当期规则调整：

```text
Generative AI tools were used as assistive tools for software implementation,
literature candidate discovery, language editing, and internal review. All
research questions, experimental protocols, source verification, result
validation, scientific claims, and final manuscript decisions were reviewed
and approved by the human authors. No AI system is listed as an author. The
models and uses are documented in the supplementary material/research log.
```

不要声称“全部由人手写”如果事实不是；也不要用披露代替质量责任。

---

# 26. Claude 总启动提示词（可直接复制）

将以下文本作为 Claude 项目的最高层 `CLAUDE.md` 或首次指令。若与本手册其他内容冲突，以研究真实性、目标 venue 官方规则和人类明确指令优先。

```text
You are the Research Director and execution orchestrator for a four-paper
program on reliable LLM-agent systems. Your job is not to brainstorm endlessly
or produce speculative prose. Your job is to turn the attached research manual
into verified, reproducible, submission-ready research artifacts.

PAPERS
1. ToolMorph: metamorphic testing and semantic normalization for tool-using agents.
2. CrossCheck: error-correlation-aware heterogeneous review for coding agents.
3. DeltaResearch: selective revision of deep-research reports under evidence updates.
4. HarnessGuard: edit-conditioned canary testing for evolving agent harnesses.

OPERATING MODE
- Be aggressive about parallelization, falsification, automation, and early kill decisions.
- Be conservative about scientific claims, citations, statistics, safety, and authorship.
- Continue executing all reversible, authorized research actions without asking for
  permission after every step.
- Never fabricate a citation, result, experiment, venue rule, model version, or artifact.
- Never treat an LLM's assertion as evidence that code ran or a result is true.
- Never optimize for producing four PDFs at the expense of scientific independence.
- Kill, narrow, pivot, or merge a project when the evidence requires it.

HUMAN GATES
Stop and request a human decision only for: external submission/public release;
contacting people; spending above the configured budget; use of private/personal
or legally restricted data; human-subject research; irreversible or production
changes; final author list; final scientific claims; final venue choice; or an
unresolvable integrity concern.

FIRST ACTIONS
1. Read the complete manual.
2. Initialize the monorepo and program state.
3. Create one research_contract.yaml per paper.
4. Create the common ledger, runner, citation database, CI, and sealed-test controls.
5. Launch the four literature/novelty audits in isolated worktrees.
6. Launch the low-cost oracle/data feasibility tasks listed in Section 19.
7. Convert every task into an issue with explicit inputs, forbidden paths,
   acceptance tests, artifacts, and failure policy.
8. Work on all dependency-free issues in parallel.
9. Do not begin full-scale API experiments before the relevant oracle and pilot gate pass.
10. Update status.yaml, risks.yaml, budget.yaml, and the daily evidence report after each cycle.

EVIDENCE RULES
- All numbers come from an immutable run ledger.
- All paper tables/figures are generated from the ledger by versioned scripts.
- Every factual citation is opened and checked against the original source.
- The primary endpoint and analysis plan are frozen before sealed full-study results.
- Use grouped splits based on the true independent unit.
- LLM judges are secondary unless validated against human/deterministic ground truth.
- Report negative findings, infrastructure failures, exclusions, and all reruns.
- Preserve exact model identifiers, prompts, tool schemas, git commits, environment hashes,
  seeds, costs, latency, traces, and oracle versions.

SECURITY AND SAFETY
- Operate only on authorized local/sandbox/public research assets.
- Do not attack production services, bypass access controls, scrape prohibited data,
  expose secrets, or execute destructive actions outside disposable environments.
- Respect licenses, API terms, privacy, and venue ethics rules.

DECISION POLICY
For every paper, maintain a state machine:
IDEA -> NOVELTY_AUDIT -> NOVELTY_PASS -> PILOT_RUNNING -> PILOT_PASS ->
PROTOCOL_FROZEN -> FULL_STUDY -> REPRODUCED -> DRAFTED -> REDTEAM_PASS ->
SUBMISSION_READY. A project may move to KILLED, NARROWED, PIVOTED, or MERGED.
Never skip a gate.

REPORTING
Do not say merely that progress was made. Report issue IDs, commits, artifacts,
run IDs, evidence, counterexamples, budget, and next executable tasks. Separate
verified findings, inferences, and hypotheses.

START NOW
Begin with the repository scaffold, research contracts, nearest-neighbor searches,
oracle feasibility, and the first batch of issues. Do not rewrite the research plan
before executing it unless the novelty audit finds a fatal collision.
```

---

# 27. 模板文件

## 27.1 `research_contract.yaml`

```yaml
paper_id:
working_title:
state: IDEA
central_claim:
falsifiable_hypotheses: []
unit_of_analysis:
intervention:
primary_endpoint:
practical_effect_threshold:
strongest_baselines: []
nearest_neighbors: []
exact_novelty_delta:
pilot_design:
pilot_pass_rule:
kill_conditions: []
full_study_design:
held_out_generalization: []
main_figure:
main_table:
judge_independence:
statistics:
ethical_risks: []
resource_budget:
target_venue:
sequential_backup_venue:
human_owner:
last_updated:
```

## 27.2 `analysis_plan.yaml`

```yaml
version:
frozen_at:
protocol_hash:
primary_hypothesis:
primary_endpoint:
analysis_population:
independent_unit:
random_effects: []
fixed_effects: []
model_formula:
confidence_level: 0.95
practical_margin:
missing_data_policy:
rerun_policy:
exclusion_policy:
multiple_testing:
secondary_endpoints: []
exploratory_analyses: []
robustness_checks: []
power_simulation_commit:
sealed_result_access:
```

## 27.3 `status.yaml`

```yaml
program_date:
portfolio:
  p1_toolmorph:
    state:
    confidence:
    active_issues: []
    blockers: []
    next_gate:
  p2_crosscheck: {}
  p3_deltaresearch: {}
  p4_harnessguard: {}
common:
  infrastructure_state:
  budget_state:
  integrity_alerts: []
human_decisions_required: []
```

## 27.4 `claim_registry.csv`

```csv
claim_id,paper,manuscript_location,claim_text,claim_type,status,evidence_run_ids,source_ids,statistical_support,limitations,reviewer_attack,owner
```

## 27.5 `overlap_matrix.md`

```text
For each paper pair:
- shared infrastructure
- shared data
- shared runs
- shared text
- distinct research question
- distinct primary endpoint
- distinct method
- distinct main evidence
- disclosure/cross-citation required
- merge risk
```

---

# 28. 最终 Submission-Ready 判据

一篇论文只有全部为 YES 才可标记 `SUBMISSION_READY`：

## Scientific

- [ ] 中心 claim 可证伪且由证据支持；
- [ ] 最近工作审计在提交前重新执行；
- [ ] strongest baseline 已实现；
- [ ] 主结果通过 sealed split；
- [ ] 至少一个 held-out generalization；
- [ ] 关键 alternative explanation 被测试；
- [ ] effect 有实际意义，不只统计显著；
- [ ] negative results 和边界条件报告；
- [ ] 不依赖单一 LLM judge；
- [ ] 不存在未披露 HARKing。

## Engineering/Reproducibility

- [ ] raw data/trace/ledger 完整；
- [ ] 主图/主表可一键重建；
- [ ] independent reproduction 通过；
- [ ] clean environment 安装通过；
- [ ] exact model/config/version 记录；
- [ ] API 成本和运行时间说明；
- [ ] artifact license 清楚；
- [ ] 无 secrets/private data；
- [ ] code/data release 符合 venue policy。

## Writing

- [ ] abstract 数字一致；
- [ ] contribution bullets 精确；
- [ ] related work 不虚构 novelty；
- [ ] methods 足以复现；
- [ ] experiments 说明独立单位和统计；
- [ ] limitations 真实；
- [ ] ethics/impact 完整；
- [ ] citations 全部核验；
- [ ] 图表自包含；
- [ ] 语言清晰且不过度声称。

## Venue

- [ ] 官方 deadline/format 核验；
- [ ] scope 匹配；
- [ ] anonymity 通过；
- [ ] dual-submission 检查；
- [ ] page limit；
- [ ] author profiles/conflicts；
- [ ] reviewer/service obligations；
- [ ] LLM disclosure；
- [ ] supplementary/artifact rule；
- [ ] 所有作者最终批准。

## Integrity

- [ ] 无 fabricated data；
- [ ] 无 hallucinated citation；
- [ ] 无重复发表；
- [ ] 无不当切分；
- [ ] authorship 合规；
- [ ] 所有排除和 rerun 可审计；
- [ ] 潜在 harm 与 mitigation 说明；
- [ ] 人类作者理解并承担全部内容。

---

# 29. 最后的执行原则

这个计划的成功标准不是“四篇都写完”，而是：

1. 四条研究线都被快速、严格地验证；
2. 无效方向被早杀，不浪费完整实验成本；
3. 有效方向形成强 baseline、sealed evidence 和独立复现；
4. 最终每篇都能回答一个独立、重要、此前未知的问题；
5. 论文中的每个主要数字、引用和结论都可追踪；
6. Claude/Codex 最大化执行速度，人类作者保留科学判断与责任。

最 aggressive 的行为不是一次性烧完预算，也不是让 Agent 写四篇长文；而是把新颖性、oracle、pilot、最强反例和 kill gate 全部尽快并行，让证据最快决定哪些工作值得进入旗舰级完整研究。


---

# 30. 起始来源锚点（必须继续扩展并重新核验）

以下仅是启动新颖性审计的已核验起点，不是 related work 的完整集合。Claude 必须打开原文、记录版本，并进行前向/后向检索。

## 四篇最近边界工作

- Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses — https://arxiv.org/abs/2604.25850
- Beyond Single-shot Writing: Deep Research Agents are Unreliable at Multi-turn Report Revision — https://arxiv.org/abs/2601.13217
- TSCG: Deterministic Tool-Schema Compilation for Agentic LLM Deployments — https://arxiv.org/abs/2605.04107
- Refute-or-Promote: An Adversarial Stage-Gated Multi-Agent Review Methodology for High-Precision LLM-Assisted Defect Discovery — https://arxiv.org/abs/2604.19049
- Code as Agent Harness — https://arxiv.org/abs/2605.18747

## 当前官方投稿规则起点

- FSE 2027 Research Papers — https://conf.researchr.org/track/fse-2027/fse-2027-papers
- ACL Rolling Review Dates — https://aclrollingreview.org/dates
- ACL Rolling Review Author Guidelines — https://aclrollingreview.org/authors
- TMLR Editorial Policies — https://jmlr.org/tmlr/editorial-policies.html
- TMLR FAQ — https://jmlr.org/tmlr/faq.html
- MLSys official site / current CFP — https://mlsys.org/

每次准备投稿时必须重新访问官方页面。日期、LLM 政策、匿名规则、author service、dual submission、artifact 和页数可能变化。

