# ModelForge — Sovereign On-Premise Agentic AI Workbench

A self-routing, on-premise AI workbench built with **Next.js**, **Tailwind CSS**, and **shadcn/ui** components from [21st.dev](https://21st.dev).

## Features

- **Smart Model Router** — Classifies tasks and routes to the optimal model (Qwen2.5-Coder-32B, Llama-3.3-70B, Qwen2.5-VL-7B)
- **Seamless Model Handoff** — When context ceiling is reached, conversation state is preserved and transferred to another model automatically
- **Air-Gapped Sovereignty** — Zero external calls; all inference runs via local Ollama/vLLM endpoints
- **Agent Tooling** — OCR extraction, sandbox code execution, RAG search, document generation — all local
- **Live Network Monitor** — Proves zero data egress in real-time

## Tech Stack

- **Framework:** Next.js 16 (App Router)
- **Styling:** Tailwind CSS 4
- **Components:** shadcn/ui (base-nova style) + 21st.dev registry
- **Fonts:** Geist Sans + Geist Mono

## Demo Scenarios

1. **Scanned Inspection → Approval Note** — OCR a scanned PDF, extract findings, draft a Word document
2. **Code Task + Sandbox Verify** — Generate Python code and verify execution in a sandboxed environment
3. **Long Context → Model Switch** — Process 40+ pages, auto-switch when context limit hits, continue seamlessly
4. **Engineering Drawing Analysis** — Vision model parses P&IDs for valves, annotations, and anomalies

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## SIH 2024 — Problem Statement SIH26117 · MRPL
