"use client";

import { useEffect, useRef, useState } from "react";
import { MaterialIcon } from "@/components/ui/material-icon";
import type { ChatMessage } from "@/hooks/use-modelforge";

interface WorkspaceProps {
  messages: ChatMessage[];
  routerStatus: string;
  isRunning: boolean;
  onSend: (text: string) => void;
}

export function Workspace({ messages, routerStatus, isRunning, onSend }: WorkspaceProps) {
  const [prompt, setPrompt] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const lastAssistant = [...messages].reverse().find((m) => m.role === "assistant");

  function handleSend() {
    if (!prompt.trim() || isRunning) return;
    onSend(prompt);
    setPrompt("");
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <main className="flex-1 flex flex-col h-full overflow-hidden relative">
      {/* Top bar */}
      <div className="h-12 border-b border-dusk-card-border/70 px-6 flex items-center justify-between bg-dusk-navy/60 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono text-text-muted">Router:</span>
          <span className="text-xs font-semibold text-text-main truncate max-w-[420px]">
            {routerStatus}
          </span>
        </div>
        <div className="flex items-center gap-3 text-xs font-mono text-text-muted">
          <span className="flex items-center gap-1.5">
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                isRunning ? "bg-amber-400 animate-pulse" : "bg-emerald-400"
              }`}
            />
            {isRunning ? "Routing…" : "Idle"}
          </span>
        </div>
      </div>

      {/* Chat content */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 flex flex-col gap-4 max-w-5xl mx-auto w-full">
        {/* Intent Router Card */}
        <div className="glass-panel rounded-2xl p-4 flex flex-wrap items-center justify-between gap-3 border border-dusk-card-border/80">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-dusk-peach/15 border border-dusk-peach/30 flex items-center justify-center text-dusk-peach">
              <MaterialIcon name="alt_route" className="text-lg" />
            </div>
            <div>
              <div className="text-xs font-semibold text-text-main flex items-center gap-2">
                Automated Intent Router
                <span className="text-[10px] font-mono bg-emerald-950/60 text-emerald-400 border border-emerald-800/60 px-1.5 py-0.2 rounded">
                  ModelForge Backend
                </span>
              </div>
              <p className="text-[11px] text-text-muted">
                Prompts are routed through the live ModelForge policy/routing engine — no hard-coded model choice.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1.5 font-mono text-xs">
            <span className="px-2.5 py-1 rounded-lg bg-[#1a2336] text-text-muted border border-dusk-card-border text-[11px]">
              Auto-classify
            </span>
            <span className="text-dusk-peach">→</span>
            <span className="px-2.5 py-1 rounded-lg bg-dusk-plum/60 text-dusk-peach border border-dusk-peach/40 font-semibold text-[11px]">
              {lastAssistant?.model ?? "Awaiting request"}
            </span>
          </div>
        </div>

        {messages.length === 0 && (
          <div className="glass-panel rounded-2xl p-6 border border-dusk-card-border/60 text-xs text-text-muted text-center">
            No requests yet. Ask something below to route it through the live ModelForge backend.
          </div>
        )}

        {messages.map((m) =>
          m.role === "user" ? (
            <div key={m.id} className="flex items-start gap-3.5 max-w-3xl">
              <div className="w-8 h-8 rounded-full bg-dusk-card border border-dusk-card-border flex items-center justify-center text-text-muted flex-shrink-0 text-xs font-mono font-bold">
                US
              </div>
              <div className="glass-panel rounded-2xl p-4 text-xs md:text-sm text-text-secondary leading-relaxed border border-dusk-card-border whitespace-pre-wrap">
                {m.content}
              </div>
            </div>
          ) : (
            <div key={m.id} className="flex items-start gap-3.5 max-w-3xl ml-auto">
              <div className="glass-panel-deep rounded-2xl p-5 text-xs md:text-sm text-text-main leading-relaxed border border-dusk-peach/40 shadow-[0_4px_30px_rgba(255,165,134,0.06)] flex-1">
                <div className="flex items-center justify-between border-b border-dusk-card-border/60 pb-2.5 mb-3 text-xs font-mono">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-dusk-peach shadow-[0_0_6px_#FFA586]" />
                    <span className="text-dusk-peach font-semibold">ModelForge Synthesis Result</span>
                  </div>
                  {m.model && (
                    <span className="text-text-muted text-[11px] font-mono">{m.model}</span>
                  )}
                </div>
                <p className="text-xs text-text-secondary whitespace-pre-wrap">{m.content}</p>
              </div>
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-dusk-plum to-dusk-crimson border border-dusk-peach/50 flex items-center justify-center text-dusk-peach flex-shrink-0 text-xs shadow-[0_0_10px_rgba(255,165,134,0.3)]">
                <MaterialIcon name="auto_awesome" className="text-sm" />
              </div>
            </div>
          )
        )}
        <div ref={endRef} />
      </div>

      {/* Input bar */}
      <div className="w-full max-w-4xl mx-auto px-4 md:px-8 pb-5 pt-2 relative z-20">
        <div className="glass-panel rounded-full p-1.5 pl-4 flex items-center gap-2 input-glow transition-all duration-300 relative bg-[#1c253b]/90 border border-dusk-card-border group">
          <button
            className="p-1.5 text-text-muted hover:text-dusk-peach hover:bg-white/[0.05] rounded-full transition-colors"
            title="Attach file or dataset sample"
          >
            <MaterialIcon name="attach_file" className="text-[19px]" />
          </button>
          <button
            className="p-1.5 text-text-muted hover:text-dusk-peach hover:bg-white/[0.05] rounded-full transition-colors hidden sm:block"
            title="Voice dictation (local whisper)"
          >
            <MaterialIcon name="mic" className="text-[19px]" />
          </button>
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isRunning}
            className="flex-1 bg-transparent border-none text-text-main font-body placeholder:text-text-muted/60 focus:ring-0 px-2 text-xs md:text-sm disabled:opacity-60"
            placeholder="Ask anything — prompts never cross the air-gap boundary..."
          />
          <button
            onClick={handleSend}
            disabled={isRunning || !prompt.trim()}
            className="bg-dusk-peach hover:bg-[#ffb59c] text-dusk-navy hover:shadow-[0_0_18px_rgba(255,165,134,0.45)] rounded-full px-4 md:px-5 py-2 font-mono font-bold text-xs transition-all duration-200 flex items-center gap-1.5 flex-shrink-0 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span>{isRunning ? "Routing…" : "Generate"}</span>
            <MaterialIcon name="arrow_upward" className="text-[15px] font-bold" />
          </button>
        </div>
        <div className="text-center mt-2 flex items-center justify-center gap-3 font-mono text-[10px] md:text-[11px] text-text-muted">
          <span className="flex items-center gap-1 text-text-secondary">
            <span className="w-1.5 h-1.5 rounded-full bg-dusk-peach shadow-[0_0_6px_#FFA586]" />
            Auto-routing Enabled
          </span>
          <span className="w-1 h-1 rounded-full bg-dusk-card-border" />
          <span className="text-dusk-crimson font-semibold flex items-center gap-1">
            <span className="w-1 h-1 rounded-full bg-dusk-crimson" />
            Zero Egress Enforced
          </span>
        </div>
      </div>
    </main>
  );
}
