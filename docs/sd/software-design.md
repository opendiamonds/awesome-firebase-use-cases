# Cloud-360 Software Design

> 本文件必須同時包含中文版與英文版。
> This document must include both Chinese and English versions.

## 中文版

## 1. 目的

本 SD（Software Design）文件把 SA 的架構決策轉成可開發的模組設計、目錄結構、介面契約、資料模型與 MVP 實作順序。本文用於引導 dev-agent 建立 Cloud-360 第一版 single repo / modular folders skeleton。

## 2. Single repo / modular folders 目錄設計

```text
cloud-360/
  web/                    # Nuxt / Vue frontend
  api/                    # FastAPI backend
  worker/                 # background workers
  mcp-gateway/            # MCP registry / proxy / tool gateway
  infra/
    docker/               # local dev containers
    opentofu/             # IaC modules and examples
  docs/
    srs/
    sa/
    sd/
    architecture/
    adr/
    user-stories/
  scripts/
    validate_repo_contract.py
```

## 3. Backend 模組設計

建議 FastAPI backend 目錄：

```text
api/app/
  main.py
  api/
    health.py
    chat.py
    agents.py
    approvals.py
    diagrams.py
    mcp.py
    skills.py
  agents/
    contracts.py
    router.py
    runtime.py
    runtimes/
      native.py
      langgraph_runtime.py
      openai_agents_runtime.py
      n8n_runtime.py
      google_adk_runtime.py
  llm/
    contracts.py
    providers/
      openai_oauth.py
      anthropic_oauth.py
      nvidia_nim.py
  tools/
    registry.py
    executor.py
    permissions.py
  policies/
    permission_engine.py
    risk_classifier.py
  audit/
    logger.py
  db/
    models.py
    session.py
    migrations/
```

## 4. Frontend 模組設計

建議 Nuxt frontend 目錄：

```text
web/
  app.vue
  pages/
    index.vue
    chat.vue
    diagrams.vue
    approvals.vue
    settings/
      mcp.vue
      skills.vue
  components/
    chat/
    diagram/
    approvals/
    cloud/
  composables/
    useChat.ts
    useDiagrams.ts
    useApprovals.ts
  stores/
    chat.ts
    project.ts
  types/
    api.ts
```

第一階段 UI：

- 首頁 / project workspace。
- AI Chat panel。
- Mermaid preview。
- draw.io canvas placeholder / embed boundary。
- Approval list。
- MCP / Skill management placeholder。

## 5. Core contracts

### AgentRouteRequest

```python
class AgentRouteRequest(BaseModel):
    project_id: str
    user_id: str
    message: str
    diagram_id: str | None = None
    cloud_account_ids: list[str] = []
    requested_action: str | None = None
```

### AgentRouteDecision

```python
class AgentRouteDecision(BaseModel):
    intent: str
    target_runtime: str
    target_agent: str
    model_provider: str
    required_tools: list[str]
    risk_level: str
    requires_approval: bool
    reason: str
```

### AgentRunResult

```python
class AgentRunResult(BaseModel):
    run_id: str
    status: str
    message: str
    artifacts: list[str] = []
    findings: list[dict] = []
    approval_request_id: str | None = None
```

## 6. Runtime selection rule

```text
simple_chat_or_qna
  -> NativeRuntime + Anthropic / OpenAI / NVIDIA

complex_multi_step_workflow
  -> LangGraphRuntime + Anthropic / OpenAI / NVIDIA

external_notification_or_approval_workflow
  -> N8NRuntime + OpenRouter

openai_handoff_or_tracing_demo
  -> OpenAIAgentsRuntime + OpenAI OAuth

gcp_gemini_specialist_future
  -> GoogleADKRuntime，MVP 暫緩
```

## 7. Provider adapter design

每個模型 provider 必須實作共同介面：

```python
class LLMProvider(Protocol):
    name: str

    async def complete(self, request: LLMRequest) -> LLMResponse:
        ...

    async def stream(self, request: LLMRequest) -> AsyncIterator[LLMChunk]:
        ...
```

第一階段 provider：

- `NvidiaNimProvider`：支援 NVIDIA Developer / NIM OpenAI-compatible endpoint。
- `AnthropicOAuthProvider`：支援 Anthropic OAuth 可用情境；production 使用前需確認授權與 token lifecycle。
- `OpenAIOAuthProvider`：支援 OpenAI OAuth 與 OpenAI Agents SDK adapter。
- `OpenRouter`：不放在 backend primary provider，主要由 n8n 使用。

## 8. Data model 初稿

```text
projects
conversations
messages
agent_runs
tool_calls
approval_requests
diagrams
artifacts
mcp_servers
skills
audit_logs
cloud_accounts
security_findings
cost_estimates
```

關鍵設計：

- `agent_runs` 記錄 runtime、provider、intent、risk level、status。
- `tool_calls` 記錄 tool name、input hash、result summary、risk level、approval status。
- `approval_requests` 記錄 high-risk action、requested by、approved by、decision、timestamp。
- `mcp_servers` 與 `skills` 記錄 registry metadata、version、enabled state、health status、risk classification。

## 9. MVP 實作順序

1. 建立 single repo / modular folders skeleton：`web`、`api`、`worker`、`mcp-gateway`、`infra/docker`。
2. 建立 FastAPI `/health` 與 `/chat` endpoint。
3. 建立 Custom Router contracts 與 mock routing。
4. 建立 Nuxt Chat UI 與 Mermaid preview。
5. 建立 provider adapter interface 與 placeholder providers。
6. 建立 n8n webhook adapter contract。
7. 建立 PostgreSQL / Redis Docker Compose。
8. 更新 README 開發指令與 repo validator。

## 10. 測試策略

- Backend：pytest、ruff、API contract tests。
- Frontend：Vitest、Playwright smoke test。
- Repo contract：`python scripts/validate_repo_contract.py`。
- Docs：所有 `docs/**/*.md` 必須包含 `## 中文版` 與 `## English Version`。
- Safety：高風險 tool execution 必須測試 approval gate。

## English Version

## 1. Purpose

This SD (Software Design) document turns the SA decisions into implementable module design, directory structure, interface contracts, data models, and MVP implementation order. It guides dev-agent when creating the first Cloud-360 single repo / modular folders skeleton.

## 2. Single Repo / Modular Folders Directory Design

```text
cloud-360/
  web/                    # Nuxt / Vue frontend
  api/                    # FastAPI backend
  worker/                 # background workers
  mcp-gateway/            # MCP registry / proxy / tool gateway
  infra/
    docker/               # local dev containers
    opentofu/             # IaC modules and examples
  docs/
    srs/
    sa/
    sd/
    architecture/
    adr/
    user-stories/
  scripts/
    validate_repo_contract.py
```

## 3. Backend Module Design

Recommended FastAPI backend layout:

```text
api/app/
  main.py
  api/
    health.py
    chat.py
    agents.py
    approvals.py
    diagrams.py
    mcp.py
    skills.py
  agents/
    contracts.py
    router.py
    runtime.py
    runtimes/
      native.py
      langgraph_runtime.py
      openai_agents_runtime.py
      n8n_runtime.py
      google_adk_runtime.py
  llm/
    contracts.py
    providers/
      openai_oauth.py
      anthropic_oauth.py
      nvidia_nim.py
  tools/
    registry.py
    executor.py
    permissions.py
  policies/
    permission_engine.py
    risk_classifier.py
  audit/
    logger.py
  db/
    models.py
    session.py
    migrations/
```

## 4. Frontend Module Design

Recommended Nuxt frontend layout:

```text
web/
  app.vue
  pages/
    index.vue
    chat.vue
    diagrams.vue
    approvals.vue
    settings/
      mcp.vue
      skills.vue
  components/
    chat/
    diagram/
    approvals/
    cloud/
  composables/
    useChat.ts
    useDiagrams.ts
    useApprovals.ts
  stores/
    chat.ts
    project.ts
  types/
    api.ts
```

First-stage UI:

- Home / project workspace.
- AI Chat panel.
- Mermaid preview.
- draw.io canvas placeholder / embed boundary.
- Approval list.
- MCP / Skill management placeholder.

## 5. Core Contracts

### AgentRouteRequest

```python
class AgentRouteRequest(BaseModel):
    project_id: str
    user_id: str
    message: str
    diagram_id: str | None = None
    cloud_account_ids: list[str] = []
    requested_action: str | None = None
```

### AgentRouteDecision

```python
class AgentRouteDecision(BaseModel):
    intent: str
    target_runtime: str
    target_agent: str
    model_provider: str
    required_tools: list[str]
    risk_level: str
    requires_approval: bool
    reason: str
```

### AgentRunResult

```python
class AgentRunResult(BaseModel):
    run_id: str
    status: str
    message: str
    artifacts: list[str] = []
    findings: list[dict] = []
    approval_request_id: str | None = None
```

## 6. Runtime Selection Rule

```text
simple_chat_or_qna
  -> NativeRuntime + Anthropic / OpenAI / NVIDIA

complex_multi_step_workflow
  -> LangGraphRuntime + Anthropic / OpenAI / NVIDIA

external_notification_or_approval_workflow
  -> N8NRuntime + OpenRouter

openai_handoff_or_tracing_demo
  -> OpenAIAgentsRuntime + OpenAI OAuth

gcp_gemini_specialist_future
  -> GoogleADKRuntime, deferred for MVP
```

## 7. Provider Adapter Design

Every model provider must implement the shared interface:

```python
class LLMProvider(Protocol):
    name: str

    async def complete(self, request: LLMRequest) -> LLMResponse:
        ...

    async def stream(self, request: LLMRequest) -> AsyncIterator[LLMChunk]:
        ...
```

First-stage providers:

- `NvidiaNimProvider`: supports NVIDIA Developer / NIM OpenAI-compatible endpoints.
- `AnthropicOAuthProvider`: supports available Anthropic OAuth flows; production usage requires authorization and token-lifecycle review.
- `OpenAIOAuthProvider`: supports OpenAI OAuth and the OpenAI Agents SDK adapter.
- `OpenRouter`: not a primary backend provider; primarily used by n8n.

## 8. Initial Data Model

```text
projects
conversations
messages
agent_runs
tool_calls
approval_requests
diagrams
artifacts
mcp_servers
skills
audit_logs
cloud_accounts
security_findings
cost_estimates
```

Key design:

- `agent_runs` records runtime, provider, intent, risk level, and status.
- `tool_calls` records tool name, input hash, result summary, risk level, and approval status.
- `approval_requests` records high-risk action, requester, approver, decision, and timestamp.
- `mcp_servers` and `skills` record registry metadata, version, enabled state, health status, and risk classification.

## 9. MVP Implementation Order

1. Create the single repo / modular folders skeleton: `web`, `api`, `worker`, `mcp-gateway`, `infra/docker`.
2. Create FastAPI `/health` and `/chat` endpoints.
3. Create Custom Router contracts and mock routing.
4. Create Nuxt Chat UI and Mermaid preview.
5. Create provider adapter interface and placeholder providers.
6. Create n8n webhook adapter contract.
7. Create PostgreSQL / Redis Docker Compose.
8. Update README development commands and repo validator.

## 10. Test Strategy

- Backend: pytest, ruff, API contract tests.
- Frontend: Vitest, Playwright smoke test.
- Repo contract: `python scripts/validate_repo_contract.py`.
- Docs: all `docs/**/*.md` must include `## 中文版` and `## English Version`.
- Safety: high-risk tool execution must test the approval gate.
