---
$schema: ".aegis/schemas/frontmatter.schema.json"
doc_type: "architecture_doc"
id: "ASDLC-CHANGE-001-IMPLEMENTATION"
title: "ASDLC SDK 実装設計書"
version: "1.0.0"
status: "active"
language: "ja"
canonical_ref: ".devs/changes/2026-09-19_initial-asdlc-sdk/implementation.md"
compatibility:
  tools: ["google-antigravity", "claude-code", "github-copilot", "gemini-cli"]
  min_asdlc_version: "0.2.0"
tags: ["implementation", "antigravity", "classes", "modules", "asdlc"]
author: "@sun-flat-yamada"
last_reviewed: "2026-09-19"
---

# ASDLC SDK 実装設計書

## 1. モジュール構成図

```mermaid
classDiagram
    class SDLCOrchestrator {
        +SDLCState state
        +ProceduralAgent procedural
        +QAAgent qa
        +CodingAgent coding
        +IssueAutoTriageEngine triage_engine
        +triage_issue(title, body) IssueTriageResult
        +register_artifact(name, content) SDLCArtifact
        +review_artifact(name) MeisterEvaluation
        +advance_phase() Dict
    }

    class ProceduralAgent {
        +get_phase_info(phase) Dict
        +check_guardrails(state, phase) Dict
    }

    class QAAgent {
        +evaluate_document(name, content, phase) MeisterEvaluation
    }

    class CodingAgent {
        +search_reusable_components(intent) List
        +synthesize_code_context(intent) Dict
    }

    class IssueAutoTriageEngine {
        +sanitize(text) Tuple
        +triage(title, body) IssueTriageResult
    }

    SDLCOrchestrator --> ProceduralAgent
    SDLCOrchestrator --> QAAgent
    SDLCOrchestrator --> CodingAgent
    SDLCOrchestrator --> IssueAutoTriageEngine
```

---

## 2. ディレクトリ配置

```text
v:/repos/sun.flat.yamada/ai-sdlc/
├── docs/charter/MEISTERS_CHARTER.md
├── AI_SDLC_SDK_SPECIFICATION.md
├── README.ja.md / README.md / LICENSE / Makefile / CONTRIBUTING.md
├── CLAUDE.md / .github/ / .gemini/ / .agents/
├── .devs/changes/2026-09-19_initial-asdlc-sdk/
│   ├── blueprint.md
│   ├── spec.md
│   ├── plan.md
│   ├── implementation.md
│   └── walkthrough.md
├── asdlc/
│   ├── models.py
│   ├── orchestrator.py
│   ├── triage/engine.py
│   ├── agents/ (procedural.py, qa.py, coding.py)
│   └── cli/main.py
└── tests/test_asdlc.py
```
