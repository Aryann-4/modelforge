"use client";

import { useState } from "react";
import type { LogEntry, AgentStep } from "@/hooks/use-modelforge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

interface RightPanelProps {
  logs: LogEntry[];
  agentSteps: AgentStep[];
}

export function RightPanel({ logs, agentSteps }: RightPanelProps) {
  return (
    <aside className="w-[300px] bg-[#13161c] border-l border-[#2a3140] flex flex-col overflow-hidden shrink-0">
      <Tabs defaultValue="network" className="flex flex-col h-full">
        <TabsList className="flex border-b border-[#2a3140] rounded-none bg-transparent h-auto p-0 shrink-0">
          <TabsTrigger
            value="network"
            className="flex-1 py-3 text-center text-[11px] font-semibold uppercase tracking-[0.04em] text-[#6b7385] data-[state=active]:text-[#3b82f6] border-b-2 border-transparent data-[state=active]:border-[#3b82f6] rounded-none bg-transparent hover:text-[#9aa3b2]"
          >
            Network
          </TabsTrigger>
          <TabsTrigger
            value="agent"
            className="flex-1 py-3 text-center text-[11px] font-semibold uppercase tracking-[0.04em] text-[#6b7385] data-[state=active]:text-[#3b82f6] border-b-2 border-transparent data-[state=active]:border-[#3b82f6] rounded-none bg-transparent hover:text-[#9aa3b2]"
          >
            Agent
          </TabsTrigger>
          <TabsTrigger
            value="logs"
            className="flex-1 py-3 text-center text-[11px] font-semibold uppercase tracking-[0.04em] text-[#6b7385] data-[state=active]:text-[#3b82f6] border-b-2 border-transparent data-[state=active]:border-[#3b82f6] rounded-none bg-transparent hover:text-[#9aa3b2]"
          >
            Logs
          </TabsTrigger>
        </TabsList>

        <ScrollArea className="flex-1 p-3">
          <TabsContent value="network" className="mt-0">
            <NetworkPanel />
          </TabsContent>
          <TabsContent value="agent" className="mt-0">
            <AgentPanel steps={agentSteps} />
          </TabsContent>
          <TabsContent value="logs" className="mt-0">
            <LogsPanel logs={logs} />
          </TabsContent>
        </ScrollArea>
      </Tabs>
    </aside>
  );
}

function NetworkPanel() {
  return (
    <>
      <StatBlock
        rows={[
          { label: "Outbound connections", value: "0" },
          { label: "External DNS queries", value: "0" },
          { label: "Cloud API calls", value: "0" },
          { label: "Data egress", value: "0 bytes" },
        ]}
      />
      <StatBlock
        rows={[
          { label: "Local inference", value: "ACTIVE", color: "text-[#22d3ee]" },
          { label: "Ollama endpoint", value: "127.0.0.1:11434", color: "text-[#9aa3b2]" },
          { label: "vLLM endpoint", value: "127.0.0.1:8000", color: "text-[#9aa3b2]" },
        ]}
      />
      <div className="text-[11px] text-[#6b7385] p-2 leading-relaxed">
        Live network monitor proves sovereignty. All inference stays on-loopback. No packet leaves the host.
      </div>
    </>
  );
}

function StatBlock({ rows }: { rows: { label: string; value: string; color?: string }[] }) {
  return (
    <div className="bg-[#181c24] border border-[#222833] rounded-lg p-3 mb-2.5">
      {rows.map((r, i) => (
        <div key={i} className="flex justify-between text-[12px] mb-1.5 last:mb-0">
          <span className="text-[#6b7385]">{r.label}</span>
          <strong className={cn("font-mono", r.color || "text-[#22c55e]")}>{r.value}</strong>
        </div>
      ))}
    </div>
  );
}

function AgentPanel({ steps }: { steps: AgentStep[] }) {
  if (steps.length === 0) {
    return (
      <div className="text-[12px] text-[#6b7385] p-3 text-center">
        Agent plan will appear here when a multi-step task runs.
      </div>
    );
  }

  return (
    <div className="flex flex-col">
      {steps.map((s, i) => (
        <div key={i} className="flex gap-2.5 py-2 border-b border-[#222833] last:border-b-0">
          <div
            className={cn(
              "w-[22px] h-[22px] rounded-full border grid place-items-center text-[10px] font-semibold shrink-0",
              s.status === "done"
                ? "bg-[rgba(34,197,94,0.12)] border-[#22c55e] text-[#22c55e]"
                : s.status === "active"
                ? "bg-[rgba(59,130,246,0.15)] border-[#3b82f6] text-[#3b82f6] animate-pulse-glow"
                : "bg-[#181c24] border-[#2a3140] text-[#6b7385]"
            )}
          >
            {s.status === "done" ? "✓" : i + 1}
          </div>
          <div className="text-[12px] text-[#9aa3b2] leading-snug">
            <strong className="block text-[12px] text-[#e8eaed]">{s.title}</strong>
            {s.detail}
          </div>
        </div>
      ))}
    </div>
  );
}

function LogsPanel({ logs }: { logs: LogEntry[] }) {
  return (
    <div>
      {logs.map((l, i) => (
        <div
          key={i}
          className={cn(
            "font-mono text-[11px] px-2 py-1.5 rounded mb-1 leading-snug",
            l.type === "ok" ? "text-[#22c55e]" : l.type === "warn" ? "text-[#f59e0b]" : "text-[#22d3ee]"
          )}
        >
          <span className="text-[#6b7385] mr-1.5">{l.time}</span>
          {l.msg}
        </div>
      ))}
    </div>
  );
}
