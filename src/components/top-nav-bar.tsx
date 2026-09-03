"use client";

import { useState, useRef, useEffect } from "react";
import { MaterialIcon } from "@/components/ui/material-icon";

interface TopNavBarProps {
  activeMode: "gen" | "dev";
  onSwitchMode: (mode: "gen" | "dev") => void;
}

export function TopNavBar({ activeMode, onSwitchMode }: TopNavBarProps) {
  const [telemetryOpen, setTelemetryOpen] = useState(false);
  const popupRef = useRef<HTMLDivElement>(null);
  const btnRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (
        telemetryOpen &&
        popupRef.current &&
        btnRef.current &&
        !popupRef.current.contains(e.target as Node) &&
        !btnRef.current.contains(e.target as Node)
      ) {
        setTelemetryOpen(false);
      }
    }
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, [telemetryOpen]);

  return (
    <>
      <nav className="fixed top-0 w-full z-50 flex justify-between items-center px-4 md:px-7 h-16 bg-dusk-navy/90 backdrop-blur-xl border-b border-dusk-card-border/70 shadow-[0_4px_30px_rgba(0,0,0,0.5)]">
        {/* Brand & Context */}
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2.5 cursor-pointer">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-dusk-plum to-dusk-crimson border border-dusk-peach/40 flex items-center justify-center shadow-[0_0_12px_rgba(255,165,134,0.3)]">
              <MaterialIcon name="deployed_code" className="text-dusk-peach text-base" filled />
            </div>
            <span className="text-lg md:text-xl font-bold tracking-tight text-text-main flex items-center gap-1.5">
              ModelForge{" "}
              <span className="inline-block w-2 h-2 rounded-full bg-dusk-peach shadow-[0_0_8px_#FFA586]" />
            </span>
          </div>

          {/* Security & Air-gapped Pills */}
          <div className="hidden xl:flex items-center gap-2">
            <div className="flex items-center gap-2 bg-dusk-plum/50 border border-dusk-plum rounded-full px-2.5 py-0.5 shadow-[0_0_12px_rgba(84,26,46,0.4)]">
              <div className="w-1.5 h-1.5 rounded-full bg-dusk-peach animate-pulse shadow-[0_0_6px_#FFA586]" />
              <span className="text-dusk-peach font-mono text-[10px] font-semibold tracking-wider uppercase">
                Air-Gapped
              </span>
              <span className="w-[1px] h-2.5 bg-white/20" />
              <span className="text-dusk-crimson font-mono text-[9px] uppercase font-bold tracking-tight">
                Zero Exfil
              </span>
            </div>
            <div className="flex items-center gap-1.5 bg-dusk-card/70 border border-dusk-card-border/70 rounded-full px-2.5 py-0.5 font-mono text-[10px] text-text-muted">
              <span className="text-text-muted">RTX 6000 Ada</span>
              <span className="text-dusk-peach font-semibold">18.7/24GB</span>
            </div>
          </div>
        </div>

        {/* Center: Mode Switcher */}
        <div className="flex items-center">
          <div className="relative bg-[#101726]/90 border border-dusk-card-border/90 p-1 rounded-full shadow-[0_4px_20px_rgba(0,0,0,0.4)] flex items-center gap-1">
            <button
              onClick={() => onSwitchMode("gen")}
              className={`relative flex items-center gap-2 px-4 md:px-5 py-1.5 rounded-full font-mono text-xs font-semibold transition-all duration-200 cursor-pointer ${
                activeMode === "gen"
                  ? "text-dusk-navy bg-dusk-peach shadow-[0_0_18px_rgba(255,165,134,0.4)]"
                  : "text-text-muted hover:text-text-main hover:bg-white/[0.04]"
              }`}
            >
              <MaterialIcon name="auto_awesome" className="text-[15px]" />
              <span>Gen Mode</span>
              <span className="hidden sm:inline text-[9px] opacity-80 font-normal px-1.5 py-0.2 bg-white/10 rounded-md">
                Playground
              </span>
            </button>
            <button
              onClick={() => onSwitchMode("dev")}
              className={`relative flex items-center gap-2 px-4 md:px-5 py-1.5 rounded-full font-mono text-xs font-semibold transition-all duration-200 cursor-pointer ${
                activeMode === "dev"
                  ? "text-dusk-navy bg-dusk-peach shadow-[0_0_18px_rgba(255,165,134,0.4)]"
                  : "text-text-muted hover:text-text-main hover:bg-white/[0.04]"
              }`}
            >
              <MaterialIcon name="terminal" className="text-[15px]" filled />
              <span>Developer Mode</span>
              <span className="hidden sm:inline text-[9px] opacity-80 font-normal px-1.5 py-0.2 bg-dusk-navy/20 rounded-md">
                IDE & Workbench
              </span>
            </button>
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-2 md:gap-3">
          {/* Active Model Indicator */}
          <div className="hidden md:flex items-center gap-2 bg-dusk-card/80 border border-dusk-card-border px-3 py-1 rounded-lg text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.6)]" />
            <span className="text-text-secondary text-[11px]">Qwen2.5-Coder-32B</span>
            <span className="text-dusk-peach text-[10px] bg-dusk-peach/10 px-1 rounded">4-bit</span>
          </div>
          <div className="flex items-center gap-1 border-l border-dusk-card-border/80 pl-3">
            <button
              ref={btnRef}
              onClick={() => setTelemetryOpen((v) => !v)}
              className={`p-2 rounded-lg transition-colors group relative ${
                telemetryOpen
                  ? "text-dusk-peach bg-dusk-card"
                  : "text-text-muted hover:text-dusk-peach hover:bg-dusk-card/60"
              }`}
              title="Hardware Telemetry"
            >
              <MaterialIcon
                name="memory"
                className="text-[19px] group-hover:drop-shadow-[0_0_8px_rgba(255,165,134,0.6)]"
              />
            </button>
            <button
              className="p-2 text-text-muted hover:text-dusk-peach hover:bg-dusk-card/60 rounded-lg transition-colors"
              title="Settings"
            >
              <MaterialIcon name="tune" className="text-[19px]" />
            </button>
          </div>
        </div>
      </nav>

      {/* Telemetry Popup */}
      <div
        ref={popupRef}
        className={`absolute top-20 right-6 w-84 bg-[#1e273d]/95 backdrop-blur-2xl border border-dusk-card-border rounded-2xl z-50 p-5 shadow-[0_15px_40px_rgba(0,0,0,0.7)] origin-top-right transition-all duration-200 ${
          telemetryOpen
            ? "opacity-100 scale-100"
            : "opacity-0 scale-95 pointer-events-none"
        }`}
      >
        <div className="flex items-center justify-between mb-4 border-b border-dusk-card-border pb-3">
          <div className="flex items-center gap-2">
            <MaterialIcon name="speed" className="text-dusk-peach text-sm" />
            <h3 className="font-mono text-text-main tracking-wider text-[11px] font-semibold uppercase">
              Hardware Telemetry
            </h3>
          </div>
          <span className="text-white text-[10px] font-mono border border-dusk-crimson/50 bg-dusk-crimson/30 px-2 py-0.5 rounded font-semibold">
            SECURE NODE
          </span>
        </div>
        <div className="space-y-3.5 font-mono text-sm">
          <div className="flex justify-between items-center text-xs">
            <span className="text-text-muted font-medium">GPU Compute Load</span>
            <span className="text-dusk-peach font-bold">42.4%</span>
          </div>
          <div className="w-full bg-black/40 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-dusk-plum via-dusk-crimson to-dusk-peach h-1.5 rounded-full shadow-[0_0_8px_#FFA586]"
              style={{ width: "42.4%" }}
            />
          </div>
          <div className="flex justify-between items-center text-xs pt-1">
            <span className="text-text-muted font-medium">VRAM Allocation</span>
            <div className="text-right">
              <span className="text-dusk-peach font-bold">18.7</span>{" "}
              <span className="text-text-muted/60">/ 24.0 GB</span>
            </div>
          </div>
          <div className="w-full bg-black/40 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-dusk-plum via-dusk-crimson to-dusk-peach h-1.5 rounded-full shadow-[0_0_8px_#FFA586]"
              style={{ width: "78%" }}
            />
          </div>
          <div className="pt-3 border-t border-dusk-card-border space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-text-muted text-[11px]">Local Engine Stack</span>
              <span className="text-dusk-peach text-[10px] font-mono border border-dusk-peach/40 bg-dusk-peach/10 px-2 py-0.5 rounded shadow-[0_0_6px_rgba(255,165,134,0.2)]">
                ONLINE
              </span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-text-muted">Ollama API</span>
              <span className="text-text-secondary font-mono">127.0.0.1:11434</span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-text-muted">vLLM Inference</span>
              <span className="text-text-secondary font-mono">127.0.0.1:8000</span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-text-muted">NIC Egress Filters</span>
              <span className="text-emerald-400 font-mono">0 bytes/sec (DROP_ALL)</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
