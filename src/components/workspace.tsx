"use client";

import { useState, useRef, useEffect } from "react";
import type { ChatMessage } from "@/hooks/use-modelforge";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";

interface WorkspaceProps {
  messages: ChatMessage[];
  routerStatus: string;
  onSend: (text: string) => void;
  onAttach: () => void;
  isRunning: boolean;
}

export function Workspace({ messages, routerStatus, onSend, onAttach, isRunning }: WorkspaceProps) {
  const [input, setInput] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function handleSend() {
    if (!input.trim()) return;
    onSend(input);
    setInput("");
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="flex flex-col flex-1 overflow-hidden bg-[#0c0e12]">
      {/* Router Banner */}
      <div className="bg-gradient-to-r from-[rgba(59,130,246,0.12)] to-[rgba(139,92,246,0.08)] border-b border-[#222833] px-5 py-2 text-[12px] flex items-center gap-2.5 text-[#9aa3b2] min-h-[36px]">
        <span className="font-semibold text-[#3b82f6] uppercase text-[10px] tracking-[0.06em]">
          Router
        </span>
        <span>{routerStatus}</span>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 px-6 py-5">
        {messages.length === 0 ? (
          <WelcomeScreen onDemo={onAttach} />
        ) : (
          <div className="flex flex-col gap-4 max-w-[780px]">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} msg={msg} />
            ))}
          </div>
        )}
        <div ref={endRef} />
      </ScrollArea>

      {/* Input */}
      <div className="border-t border-[#2a3140] bg-[#13161c] px-5 pt-3.5 pb-4">
        <div className="flex gap-2.5 items-end bg-[#181c24] border border-[#2a3140] rounded-xl px-3 py-2.5 focus-within:border-[#3b82f6] transition-colors">
          <Button
            variant="ghost"
            size="icon"
            className="shrink-0 text-base text-[#9aa3b2] hover:text-[#e8eaed]"
            onClick={onAttach}
          >
            📎
          </Button>
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything — confidential industrial work stays local..."
            rows={1}
            className="flex-1 bg-transparent border-none outline-none resize-none max-h-[120px] text-[14px] text-[#e8eaed] placeholder:text-[#6b7385] min-h-0 shadow-none focus-visible:ring-0"
          />
          <Button
            onClick={handleSend}
            disabled={isRunning || !input.trim()}
            className="shrink-0 bg-[#3b82f6] text-white hover:bg-[#3b82f6]/90 h-9 px-5 font-semibold text-[13px] rounded-lg"
          >
            Send
          </Button>
        </div>
        <div className="text-[11px] text-[#6b7385] mt-2 text-center">
          Models auto-routed · Air-gapped · No data leaves this machine
        </div>
      </div>
    </div>
  );
}

function WelcomeScreen({ onDemo }: { onDemo: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-20 text-[#9aa3b2]">
      <h1 className="text-[28px] font-bold text-[#e8eaed] mb-2 tracking-tight">ModelForge</h1>
      <p className="max-w-[420px] text-[14px] leading-relaxed mb-7">
        Self-routing, on-premise AI workbench. Automatically selects the right open-weight model and
        switches mid-task when limits are hit — all data stays on premises.
      </p>
      <div className="grid grid-cols-2 gap-2.5 max-w-[520px] w-full">
        {[
          { icon: "📄", title: "Inspection Report", desc: "OCR → Agent drafts Word approval note" },
          { icon: "💻", title: "Coding Task", desc: "Routed to coder · sandbox verified" },
          { icon: "🔄", title: "Limit Switch", desc: "Context ceiling → seamless handoff" },
          { icon: "🖼️", title: "Drawing Analysis", desc: "Vision model on engineering PDF" },
        ].map((d) => (
          <div
            key={d.title}
            onClick={onDemo}
            className="bg-[#181c24] border border-[#2a3140] rounded-[10px] p-3.5 text-left cursor-pointer transition-all hover:border-[#3b82f6] hover:bg-[#1e2430] hover:-translate-y-px"
          >
            <div className="text-xl mb-1.5">{d.icon}</div>
            <strong className="block text-[13px] text-[#e8eaed] mb-0.5">{d.title}</strong>
            <span className="text-[11px] text-[#6b7385]">{d.desc}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function MessageBubble({ msg }: { msg: ChatMessage }) {
  if (msg.role === "user") {
    const isAttachment = msg.content.startsWith("attachment:");
    return (
      <div className="self-end max-w-[780px] bg-[rgba(59,130,246,0.15)] border border-[rgba(59,130,246,0.3)] rounded-[14px_14px_4px_14px] px-4 py-3 text-[14px] leading-relaxed animate-fade-in-up whitespace-pre-wrap">
        {isAttachment && (
          <div className="text-[#3b82f6] text-[12px] font-medium mb-1">
            📎 {msg.content.split("\n")[0].replace("attachment:", "")}
          </div>
        )}
        {isAttachment ? msg.content.split("\n").slice(1).join("\n") : msg.content}
      </div>
    );
  }

  // assistant
  const hasDeliverable = msg.content.includes("deliverable:");
  const hasTool = msg.content.includes("tool:");
  const hasCode = msg.content.includes("```");

  const parts = msg.content.split("\n");

  return (
    <div className="self-start w-full max-w-[780px] animate-fade-in-up">
      <div className="flex items-center gap-2 mb-2 text-[12px] text-[#6b7385]">
        {msg.model && (
          <span className="bg-[#181c24] border border-[#2a3140] px-2 py-0.5 rounded-full font-mono text-[11px] text-[#22d3ee]">
            {msg.model}
          </span>
        )}
        <span>local · on-premise</span>
      </div>
      <div className="bg-[#181c24] border border-[#222833] rounded-xl px-4 py-4 text-[14px] leading-[1.6]">
        {parts.map((line, i) => {
          if (line.startsWith("tool:")) {
            return (
              <div key={i} className="bg-[#0c0e12] border border-[#2a3140] rounded-lg px-3 py-2.5 my-2 text-[12px] font-mono text-[#9aa3b2]">
                🔧 <span className="text-[#a78bfa] font-medium">{line.replace("tool:", "").split("(")[0]}</span>
                ({line.split("(").slice(1).join("(")}
              </div>
            );
          }
          if (line.startsWith("deliverable:")) {
            const parts = line.replace("deliverable:", "").split("|");
            return (
              <div key={i} className="bg-gradient-to-br from-[rgba(34,197,94,0.08)] to-[rgba(59,130,246,0.06)] border border-[rgba(34,197,94,0.35)] rounded-[10px] px-4 py-3.5 my-3 flex items-center gap-3">
                <div className="w-10 h-10 bg-[rgba(34,197,94,0.12)] rounded-lg grid place-items-center text-lg">
                  📄
                </div>
                <div className="flex-1">
                  <strong className="block text-[13px]">{parts[0]}</strong>
                  <span className="text-[11px] text-[#6b7385]">{parts[1]}</span>
                </div>
                <button className="bg-[#22c55e] text-[#0c0e12] border-none px-3.5 py-1.5 rounded-md text-[12px] font-semibold cursor-pointer hover:brightness-110">
                  Download
                </button>
              </div>
            );
          }
          if (line.startsWith("```")) {
            return null; // handled by code block below
          }
          if (line.trim() === "") {
            return <br key={i} />;
          }

          // Bold
          let rendered: React.ReactNode = line;
          if (line.includes("**")) {
            const segments = line.split(/(\*\*.*?\*\*)/g);
            rendered = segments.map((seg, j) =>
              seg.startsWith("**") && seg.endsWith("**") ? (
                <strong key={j} className="text-[#e8eaed] font-semibold">
                  {seg.slice(2, -2)}
                </strong>
              ) : (
                <span key={j}>{seg}</span>
              )
            );
          }

          // Inline code
          if (typeof rendered === "string" && rendered.includes("`")) {
            const segments = rendered.split(/(`[^`]+`)/g);
            rendered = segments.map((seg, j) =>
              seg.startsWith("`") && seg.endsWith("`") ? (
                <code key={j} className="font-mono bg-[#0c0e12] px-1.5 py-[2px] rounded text-[13px]">
                  {seg.slice(1, -1)}
                </code>
              ) : (
                <span key={j}>{seg}</span>
              )
            );
          }

          // List items
          if (line.startsWith("- ") || line.startsWith("  - ")) {
            return (
              <li key={i} className="ml-4 my-1">
                {rendered}
              </li>
            );
          }

          return <p key={i} className="mb-2.5 last:mb-0">{rendered}</p>;
        })}

        {/* Code blocks */}
        {(() => {
          const codeBlocks: React.ReactNode[] = [];
          let inCode = false;
          let codeLines: string[] = [];
          let lang = "";
          parts.forEach((line, i) => {
            if (line.startsWith("```") && !inCode) {
              inCode = true;
              lang = line.replace("```", "").trim();
              codeLines = [];
            } else if (line.startsWith("```") && inCode) {
              inCode = false;
              codeBlocks.push(
                <pre
                  key={`code-${i}`}
                  className="bg-[#0c0e12] border border-[#2a3140] rounded-lg px-3 py-3 overflow-x-auto font-mono text-[12px] my-2.5 leading-[1.5]"
                >
                  {codeLines.join("\n")}
                </pre>
              );
            } else if (inCode) {
              codeLines.push(line);
            }
          });
          return codeBlocks;
        })()}
      </div>
    </div>
  );
}
