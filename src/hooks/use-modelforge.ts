"use client";

import { useCallback, useEffect, useState } from "react";

export interface ModelInfo {
  name: string;
  tag: string;
  ctx: number;
  max: number;
  status: "idle" | "active" | "switching";
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  model?: string;
}

export interface AgentStep {
  title: string;
  detail?: string;
  status: "pending" | "active" | "done";
}

export interface LogEntry {
  time: string;
  msg: string;
  type: "ok" | "info" | "warn";
}

const MODELS: Record<string, ModelInfo> = {
  coder: { name: "Qwen2.5-Coder-32B", tag: "Code", ctx: 0, max: 32, status: "idle" },
  reason: { name: "Llama-3.3-70B", tag: "Reason", ctx: 0, max: 128, status: "idle" },
  vision: { name: "Qwen2.5-VL-7B", tag: "Vision", ctx: 0, max: 32, status: "idle" },
};

function genId() {
  return Math.random().toString(36).slice(2, 10);
}

function now() {
  return new Date().toLocaleTimeString("en-IN", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

export function useModelforge() {
  const [models, setModels] = useState<Record<string, ModelInfo>>(MODELS);
  const [activeModel, setActiveModel] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [routerStatus, setRouterStatus] = useState(
    "Idle — waiting for request. Task classification + limit monitoring active."
  );
  const [logs, setLogs] = useState<LogEntry[]>([
    { time: "09:10:01", msg: "Network monitor started — all interfaces sealed", type: "ok" },
    { time: "09:10:02", msg: "Loaded Qwen2.5-Coder-32B via Ollama", type: "info" },
    { time: "09:10:03", msg: "Loaded Llama-3.3-70B via vLLM", type: "info" },
    { time: "09:10:04", msg: "Loaded Qwen2.5-VL-7B (vision)", type: "info" },
    { time: "09:10:05", msg: "Router online · task classifier ready", type: "ok" },
    { time: "09:10:05", msg: "Sovereignty check passed · 0 outbound", type: "ok" },
  ]);
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [gpuUsage, setGpuUsage] = useState("42%");
  const [vramUsage, setVramUsage] = useState("18.4 / 24 GB");

  const addLog = useCallback((msg: string, type: LogEntry["type"] = "info") => {
    setLogs((prev) => [{ time: now(), msg, type }, ...prev]);
  }, []);

  const activateModel = useCallback((key: string | null) => {
    setModels((prev) => {
      const next = { ...prev };
      for (const k of Object.keys(next)) {
        next[k] = { ...next[k], status: "idle" };
      }
      if (key && next[key]) {
        next[key] = { ...next[key], status: "active" };
      }
      return next;
    });
    setActiveModel(key);
  }, []);

  const setCtx = useCallback((key: string, pct: number) => {
    setModels((prev) => ({
      ...prev,
      [key]: { ...prev[key], ctx: pct },
    }));
  }, []);

  const flashSwitch = useCallback((key: string) => {
    setModels((prev) => ({
      ...prev,
      [key]: { ...prev[key], status: "switching" },
    }));
    setTimeout(() => {
      setModels((prev) => ({
        ...prev,
        [key]: { ...prev[key], status: "idle" },
      }));
    }, 700);
  }, []);

  // GPU simulation
  useEffect(() => {
    const iv = setInterval(() => {
      setGpuUsage(35 + Math.floor(Math.random() * 25) + "%");
      setVramUsage(`${(16 + Math.random() * 4).toFixed(1)} / 24 GB`);
    }, 3000);
    return () => clearInterval(iv);
  }, []);

  // Heartbeat
  useEffect(() => {
    const iv = setInterval(() => {
      if (Math.random() > 0.7) {
        addLog("Sovereignty heartbeat: 0 outbound connections", "ok");
      }
    }, 15000);
    return () => clearInterval(iv);
  }, [addLog]);

  // --- DEMOS ---
  async function demoInspection() {
    setMessages((prev) => [
      ...prev,
      {
        id: genId(),
        role: "user",
        content:
          "attachment:inspection_report_unit3_scanned.pdf\n\nProcess this scanned inspection report. Extract key findings and draft an approval note as a Word document for the Maintenance Head.",
      },
    ]);
    addLog("File received: inspection_report_unit3_scanned.pdf (local only)", "info");
    setRouterStatus("Classifying task… multimodal document + generation → routing to Vision + Reasoner");

    setAgentSteps([
      { title: "OCR / Vision extraction", detail: "Reading scanned PDF pages", status: "active" },
      { title: "Key findings extraction", detail: "Structure findings from OCR text", status: "pending" },
      { title: "Draft approval note", detail: "Generate formal note for Maintenance Head", status: "pending" },
      { title: "Export deliverable", detail: "Write .docx via local file I/O", status: "pending" },
    ]);

    await sleep(800);
    activateModel("vision");
    setCtx("vision", 28);
    addLog("Router → Qwen2.5-VL-7B (vision/OCR)", "info");

    setMessages((prev) => [
      ...prev,
      {
        id: genId(),
        role: "assistant",
        model: "Qwen2.5-VL-7B",
        content:
          'tool:ocr.extract(file="inspection_report_unit3_scanned.pdf")\n\nOCR complete. 4 pages processed. Extracting structured findings…',
      },
    ]);
    setAgentSteps((s) => s.map((x, i) => (i === 0 ? { ...x, status: "done" } : i === 1 ? { ...x, status: "active" } : x)));
    await sleep(1000);

    activateModel("reason");
    setCtx("reason", 12);
    setRouterStatus("Handoff: Vision → Llama-3.3-70B for reasoning & document generation (state preserved)");
    addLog("Model handoff: vision → reason · conversation state transferred", "warn");
    flashSwitch("reason");

    setMessages((prev) => [
      ...prev,
      {
        id: genId(),
        role: "assistant",
        model: "Llama-3.3-70B",
        content:
          "**Key findings extracted:**\n\n- Unit-3 Heat Exchanger E-301: minor scale deposit on tube side (within tolerance)\n- Relief valve PSV-412: set pressure verified at 12.5 barg — OK\n- Flange leak indication at nozzle N-2 — recommend re-torque during next shutdown\n- Insulation damage on 15 m of 6\" line — safety & efficiency concern\n\nDrafting formal approval note…\n\ntool:docx.create(template=\"approval_note\", recipient=\"Maintenance Head\")",
      },
    ]);
    setAgentSteps((s) => s.map((x, i) => (i === 1 ? { ...x, status: "done" } : i === 2 ? { ...x, status: "active" } : x)));
    setCtx("reason", 35);
    await sleep(1500);

    setMessages((prev) => [
      ...prev,
      {
        id: genId(),
        role: "assistant",
        model: "Llama-3.3-70B",
        content:
          "deliverable:Approval_Note_Unit3_Inspection.docx|Generated locally · 2 pages · ready for review\n\nNote recommends: (1) schedule re-torque of N-2 at next opportunity shutdown, (2) insulation repair under work order, (3) continue normal operation. No immediate safety hold.",
      },
    ]);
    setAgentSteps((s) => s.map((x, i) => (i === 2 || i === 3 ? { ...x, status: "done" } : x)));
    setCtx("reason", 42);
    setRouterStatus("Task complete · deliverable written to local workspace · 0 external calls");
    addLog("Deliverable written: Approval_Note_Unit3_Inspection.docx", "ok");
    addLog("Sovereignty check: 0 outbound packets during task", "ok");
  }

  async function demoCoding() {
    setMessages((prev) => [
      ...prev,
      {
        id: genId(),
        role: "user",
        content:
          "Write a Python function to calculate pressure drop across a pipe using Darcy-Weisbach, with input validation. Then run a test with: L=50m, D=0.1m, v=2.5 m/s, f=0.02, rho=850 kg/m³.",
      },
    ]);
    setRouterStatus("Classifying… coding + execution → routing to Qwen2.5-Coder-32B");
    addLog("Router → Qwen2.5-Coder-32B (code specialist)", "info");

    setAgentSteps([
      { title: "Generate code", detail: "Darcy-Weisbach implementation", status: "active" },
      { title: "Sandbox execution", detail: "Run test case in isolated env", status: "pending" },
      { title: "Verify result", detail: "Check output against expected range", status: "pending" },
    ]);

    await sleep(600);
    activateModel("coder");
    setCtx("coder", 18);

    setMessages((prev) => [
      ...prev,
      {
        id: genId(),
        role: "assistant",
        model: "Qwen2.5-Coder-32B",
        content:
          "Here's a validated Darcy-Weisbach pressure-drop function:\n\n```python\nimport math\n\ndef pressure_drop(L, D, v, f, rho):\n    \"\"\"Darcy-Weisbach ΔP = f * (L/D) * (ρ v² / 2)\"\"\"\n    if any(x <= 0 for x in (L, D, v, f, rho)):\n        raise ValueError(\"All inputs must be positive\")\n    return f * (L / D) * (rho * v**2 / 2)\n\n# Test\ndp = pressure_drop(L=50, D=0.1, v=2.5, f=0.02, rho=850)\nprint(f\"ΔP = {dp:.1f} Pa ({dp/1e5:.4f} bar)\")\n```\n\ntool:sandbox.exec(lang=\"python\", timeout=5s)",
      },
    ]);
    setAgentSteps((s) => s.map((x, i) => (i === 0 ? { ...x, status: "done" } : i === 1 ? { ...x, status: "active" } : x)));
    setCtx("coder", 32);
    await sleep(1300);

    setMessages((prev) => [
      ...prev,
      {
        id: genId(),
        role: "assistant",
        model: "Qwen2.5-Coder-32B",
        content:
          "**Sandbox output:**\n\n```\nΔP = 53125.0 Pa (0.5313 bar)\n```\n\nResult is within expected engineering range for the given parameters. Function is ready for use in internal calculation tools.",
      },
    ]);
    setAgentSteps((s) => s.map((x) => ({ ...x, status: "done" })));
    setCtx("coder", 38);
    setRouterStatus("Code task verified in sandbox · 0 external calls");
    addLog("Sandbox run OK · ΔP = 53125 Pa", "ok");
  }

  async function demoHandoff() {
    setMessages((prev) => [
      ...prev,
      {
        id: genId(),
        role: "user",
        content:
          "Summarize the last 40 pages of the Unit-4 turnaround planning pack, cross-reference with SOP-MNT-017, and produce a risk register for the next shutdown. Include all vendor dependencies.",
      },
    ]);
    setRouterStatus("Classifying… long multi-document reasoning → Llama-3.3-70B");
    addLog("Router → Llama-3.3-70B (long-context reasoner)", "info");

    setAgentSteps([
      { title: "Load documents", detail: "Turnaround pack + SOP-MNT-017", status: "active" },
      { title: "Summarize & extract", detail: "40-page synthesis", status: "pending" },
      { title: "Context limit reached", detail: "Auto-switch to secondary model", status: "pending" },
      { title: "Continue + risk register", detail: "State preserved across models", status: "pending" },
    ]);

    await sleep(700);
    activateModel("reason");
    setCtx("reason", 45);

    setMessages((prev) => [
      ...prev,
      {
        id: genId(),
        role: "assistant",
        model: "Llama-3.3-70B",
        content:
          'tool:rag.search(corpus="turnaround_U4", query="planning pack")\ntool:rag.search(corpus="SOPs", doc="SOP-MNT-017")\n\nLoaded 40-page turnaround pack and SOP-MNT-017 from local knowledge base. Synthesizing summary…',
      },
    ]);
    setAgentSteps((s) => s.map((x, i) => (i === 0 ? { ...x, status: "done" } : i === 1 ? { ...x, status: "active" } : x)));
    setCtx("reason", 72);
    await sleep(1400);

    setCtx("reason", 94);
    setMessages((prev) => [
      ...prev,
      {
        id: genId(),
        role: "assistant",
        model: "Llama-3.3-70B",
        content:
          "Partial summary complete (sections 1–28). Context window approaching limit…",
      },
    ]);
    setAgentSteps((s) => s.map((x, i) => (i === 1 ? { ...x, status: "done" } : i === 2 ? { ...x, status: "active" } : x)));
    setRouterStatus("⚠ Context ceiling at 94% on Llama-3.3-70B — initiating seamless model switch");
    addLog("Context limit threshold hit (94%) — preparing handoff", "warn");
    await sleep(900);

    flashSwitch("coder");
    activateModel("coder");
    setCtx("coder", 15);
    setRouterStatus("Model switch complete: Llama-3.3-70B → Qwen2.5-Coder-32B · full conversation state transferred");
    addLog("Handoff complete · state preserved · continuing on Qwen2.5-Coder", "warn");

    setMessages((prev) => [
      ...prev,
      {
        id: genId(),
        role: "assistant",
        model: "Qwen2.5-Coder-32B",
        content:
          "Continuing from transferred state. Risk register for next Unit-4 shutdown:\n\n- **R-01** Vendor delay on replacement tube bundle (E-402) — mitigate: expedite PO, parallel temporary repair plan\n- **R-02** Scaffolding capacity shortage during peak — mitigate: pre-book third contractor\n- **R-03** SOP-MNT-017 requires double isolation; current P&ID shows single valve at V-881 — mitigate: engineering change request before shutdown\n- **R-04** Catalyst handling window weather-dependent — mitigate: flexible 48h buffer in schedule\n\ndeliverable:Risk_Register_U4_Shutdown.xlsx|Generated locally · 4 risks with mitigations",
      },
    ]);
    setAgentSteps((s) => s.map((x, i) => (i === 2 || i === 3 ? { ...x, status: "done" } : x)));
    setCtx("coder", 48);
    setRouterStatus("Long-context task completed via automatic model switch · 0 external calls");
    addLog("Risk register deliverable written locally", "ok");
  }

  async function demoMultimodal() {
    setMessages((prev) => [
      ...prev,
      {
        id: genId(),
        role: "user",
        content:
          "attachment:P&ID_Unit2_RevD_scan.png\n\nAnalyze this engineering drawing. List all pressure safety valves and their set pressures if annotated. Flag any symbols that look non-standard.",
      },
    ]);
    setRouterStatus("Classifying… image / engineering drawing → Qwen2.5-VL-7B");
    addLog("Router → Qwen2.5-VL-7B (vision)", "info");

    setAgentSteps([
      { title: "Vision analysis", detail: "Parse P&ID symbols & annotations", status: "active" },
      { title: "Extract PSV list", detail: "Identify valves and set pressures", status: "pending" },
      { title: "Non-standard check", detail: "Flag unusual symbols", status: "pending" },
    ]);

    await sleep(600);
    activateModel("vision");
    setCtx("vision", 40);

    setMessages((prev) => [
      ...prev,
      {
        id: genId(),
        role: "assistant",
        model: "Qwen2.5-VL-7B",
        content:
          'tool:vision.analyze(image="P&ID_Unit2_RevD_scan.png")\n\n**Pressure Safety Valves identified:**\n\n- `PSV-201` — set pressure annotated **18.5 barg** (on vessel V-201)\n- `PSV-205` — set pressure annotated **12.0 barg** (on column C-205 overhead)\n- `PSV-210` — set pressure **not legible** on scan (recommend re-scan or check isometric)',
      },
    ]);
    setAgentSteps((s) => s.map((x, i) => (i === 0 || i === 1 ? { ...x, status: "done" } : i === 2 ? { ...x, status: "active" } : x)));
    setCtx("vision", 55);
    await sleep(900);

    setMessages((prev) => [
      ...prev,
      {
        id: genId(),
        role: "assistant",
        model: "Qwen2.5-VL-7B",
        content:
          '**Non-standard / flagged symbols:**\n\n- Symbol near nozzle N-14 resembles a control valve but lacks actuator annotation — possible drafting omission\n- Line number on 4" line from P-203 discharge partially obscured by stamp; cross-check with line list recommended\n\nAnalysis performed entirely on-device. Drawing never left the premises.',
      },
    ]);
    setAgentSteps((s) => s.map((x) => ({ ...x, status: "done" })));
    setCtx("vision", 62);
    setRouterStatus("Multimodal task complete · 0 external calls");
    addLog("Vision analysis complete · 3 PSVs extracted, 2 flags raised", "ok");
  }

  const runDemo = useCallback(
    async (type: "inspection" | "coding" | "handoff" | "multimodal") => {
      if (isRunning) return;
      setIsRunning(true);

      if (type === "inspection") await demoInspection();
      else if (type === "coding") await demoCoding();
      else if (type === "handoff") await demoHandoff();
      else if (type === "multimodal") await demoMultimodal();

      setIsRunning(false);
    },
    [isRunning, addLog, activateModel, setCtx, flashSwitch]
  );

  // --- FREEFORM ---
  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim() || isRunning) return;
      setIsRunning(true);

      setMessages((prev) => [...prev, { id: genId(), role: "user", content: text }]);

      const lower = text.toLowerCase();
      let modelKey = "reason";
      if (/\b(code|python|function|script|debug|compile)\b/.test(lower)) modelKey = "coder";
      if (/\b(image|scan|drawing|pdf|photo|ocr|diagram|p&id)\b/.test(lower)) modelKey = "vision";

      setRouterStatus(`Classifying… routing to ${models[modelKey].name}`);
      addLog(`Router → ${models[modelKey].name}`, "info");
      activateModel(modelKey);
      setCtx(modelKey, Math.min(models[modelKey].ctx + 15, 90));

      await sleep(900 + Math.random() * 600);

      setMessages((prev) => [
        ...prev,
        {
          id: genId(),
          role: "assistant",
          model: models[modelKey].name,
          content:
            `This is a simulated response from the local **${models[modelKey].name}** model.\n\nIn a full deployment, your query would be processed entirely on-premise via Ollama/vLLM with the router selecting and, if needed, switching models automatically. Agent tools (file I/O, sandbox, RAG) would execute against local resources only.\n\nTry the demo scenarios on the left for full multi-step agent + handoff flows.`,
        },
      ]);
      setRouterStatus("Response complete · 0 external calls");
      addLog("Freeform response served locally", "ok");
      setIsRunning(false);
    },
    [isRunning, models, addLog, activateModel, setCtx]
  );

  const simulateAttach = useCallback(() => {
    // placeholder
  }, []);

  return {
    models,
    activeModel,
    messages,
    routerStatus,
    logs,
    agentSteps,
    isRunning,
    gpuUsage,
    vramUsage,
    runDemo,
    sendMessage,
    simulateAttach,
  };
}
