# LightRAG 工程实践说明

> 本仓库是基于 [HKUDS/LightRAG](https://github.com/HKUDS/LightRAG) 的学习与二次开发分支，保留上游 MIT 许可证和提交历史。本文明确区分上游能力与本次工程改动。

## 项目定位

LightRAG 是一个图增强的 RAG 完整应用。它从文档中抽取实体和关系，同时维护 KV、向量、知识图谱和文档状态四类存储，再按问题选择实体邻域、关系主题或原文片段进行组合检索。

本次实践重点是复杂文档入库、图与向量的混合检索、Rerank、引用返回、处理中断恢复和 RAGAS 评测。它与普通“切块后只查向量库”的知识库项目相比，更适合学习知识工程与检索可靠性。

## 核心技术栈

| 层次 | 技术与用途 |
|---|---|
| RAG 核心 | Python 3.10+、异步文档流水线、实体/关系抽取、多模式检索、Rerank |
| 服务端 | FastAPI、Uvicorn、REST、流式响应、Ollama 兼容 API |
| 默认本地存储 | JsonKVStorage、JsonDocStatusStorage、NetworkX、NanoVectorDB |
| 可替换存储 | PostgreSQL、Neo4j、MongoDB、Redis、Milvus、Qdrant、Faiss、OpenSearch 等 |
| 文档与分块 | legacy/native/MinerU/Docling 路由，固定、递归、向量语义、段落语义分块 |
| 前端 | React 19、TypeScript、Vite、Bun、Tailwind、Sigma 图可视化 |
| 评测与部署 | RAGAS、pytest、Bun test、Docker Compose |

## 核心思路

```text
文档上传/目录扫描
  → 解析和分块
  → LLM 抽取实体与关系
  → 写入 KV + Graph + Vector + DocStatus
  → local/global/hybrid/mix/naive 检索
  → Rerank 与上下文预算
  → 带引用的回答
```

`local` 聚焦实体邻域，`global` 聚焦关系主题，`hybrid` 合并两者，`mix` 再加入原文向量片段，`naive` 只使用 chunk 向量；`bypass` 直接调用模型，不属于 RAG。入库流水线用 workspace 级状态、锁和 ingress mailbox 协调上传、扫描、删除和恢复，文档状态是调度事实来源。

## 本次自主改进

1. **Windows 启动与状态契约**：修复跨平台启动问题和 tracking 状态行为，并以定向 Python 回归覆盖。
2. **前端测试可移植性**：隔离 WebUI 测试环境，使 TypeScript、lint、production build 和 Bun 测试可以稳定重复执行。
3. **RAGAS 兼容接口**：让评测层支持 OpenAI-compatible 的独立 LLM 与 Embedding 端点，而不是隐含绑定单一供应商。
4. **真实提供商组合验证**：使用 DeepSeek 完成生成，使用阿里 1024 维 Embedding 与 Rerank，验证多供应商配置闭环。

## 验证结果

- 5 篇基线文档均完成入库；local/global/hybrid/mix/naive 均走真实检索，mix 返回引用。
- 图谱基线为 58 个节点、74 条边；临时文档删除后，其图、向量、KV 和状态贡献均清除。
- 目录扫描、直接文本、去重、更新、删除、取消、显式重试和硬重启恢复均有端到端样本。
- RAGAS 固定 6 问样本全部成功：Faithfulness 0.9641、Answer Relevance 0.9683、Context Recall 1.0000、Context Precision 1.0000。该小样本用于回归，不外推为通用准确率。
- 前端 **613 tests passed**，TypeScript、lint、production build 通过；Python 定向回归 **6 tests passed**。

## 适合作为项目经历的价值

这个项目覆盖文档状态机、图谱构建、混合检索、Rerank、引用溯源、数据生命周期和检索评测。面试时可以从一次文档入库追到四类存储，再解释不同 query mode 的召回对象和 RAGAS 指标，形成完整的知识工程叙事。

## 已知边界

- 当前真实验收使用本地 JSON/NetworkX/NanoVectorDB 组合，没有把外部数据库或多 worker 场景描述为已验证。
- MinerU、Docling、VLM 和其他模型绑定保留为可选能力，本次没有具备条件的真实验收。
- RAGAS 数值来自小型受控数据集，主要用于发现回归，不能代表公开基准或生产效果。

## 上游与许可证

- 上游仓库：<https://github.com/HKUDS/LightRAG>
- 论文：<https://arxiv.org/abs/2410.05779>
- 许可证：MIT License
