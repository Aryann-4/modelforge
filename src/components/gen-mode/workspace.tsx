"use client";

import { MaterialIcon } from "@/components/ui/material-icon";

interface WorkspaceProps {
  prompt: string;
  onPromptChange: (value: string) => void;
}

export function Workspace({ prompt, onPromptChange }: WorkspaceProps) {
  return (
    <main className="flex-1 flex flex-col h-full overflow-hidden relative">
      {/* Top bar */}
      <div className="h-12 border-b border-dusk-card-border/70 px-6 flex items-center justify-between bg-dusk-navy/60 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono text-text-muted">Scenario:</span>
          <span className="text-xs font-semibold text-text-main">
            Defect Inspection Log — Session #204
          </span>
          <span className="text-[10px] font-mono bg-dusk-plum/50 border border-dusk-peach/30 text-dusk-peach px-2 py-0.5 rounded-full">
            vLLM Engine Active
          </span>
        </div>
        <div className="flex items-center gap-3 text-xs font-mono text-text-muted">
          <span>
            Latency: <span className="text-text-main font-semibold">18ms</span>
          </span>
          <span className="w-1 h-1 rounded-full bg-dusk-card-border" />
          <span>
            Speed: <span className="text-dusk-peach font-semibold">86.4 tok/s</span>
          </span>
          <span className="w-1 h-1 rounded-full bg-dusk-card-border" />
          <span>
            Egress: <span className="text-emerald-400 font-semibold">0.00 kB</span>
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
                  Zero Latency Spill
                </span>
              </div>
              <p className="text-[11px] text-text-muted">
                Routing text query through local embedder & specialized vision-quantized weights.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1.5 font-mono text-xs">
            <span className="px-2.5 py-1 rounded-lg bg-[#1a2336] text-text-muted border border-dusk-card-border text-[11px]">
              Vision-OCR
            </span>
            <span className="text-dusk-peach">→</span>
            <span className="px-2.5 py-1 rounded-lg bg-dusk-plum/60 text-dusk-peach border border-dusk-peach/40 font-semibold text-[11px]">
              Qwen2.5-Coder-32B
            </span>
          </div>
        </div>

        {/* User message */}
        <div className="flex items-start gap-3.5 max-w-3xl">
          <div className="w-8 h-8 rounded-full bg-dusk-card border border-dusk-card-border flex items-center justify-center text-text-muted flex-shrink-0 text-xs font-mono font-bold">
            US
          </div>
          <div className="glass-panel rounded-2xl p-4 text-xs md:text-sm text-text-secondary leading-relaxed border border-dusk-card-border">
            Extract non-conforming weld bead anomalies from the internal airframe thermal inspection
            scan and format the output as a classified engineering sign-off table.
            <div className="mt-2.5 flex items-center gap-2 text-[10px] font-mono text-text-muted">
              <MaterialIcon name="attach_file" className="text-xs text-dusk-peach" />
              <span>airframe_scan_layer7_pass3.raw</span>
              <span className="text-dusk-peach font-semibold">12.4 MB (Encrypted RAM)</span>
            </div>
          </div>
        </div>

        {/* AI response */}
        <div className="flex items-start gap-3.5 max-w-3xl ml-auto">
          <div className="glass-panel-deep rounded-2xl p-5 text-xs md:text-sm text-text-main leading-relaxed border border-dusk-peach/40 shadow-[0_4px_30px_rgba(255,165,134,0.06)] flex-1">
            <div className="flex items-center justify-between border-b border-dusk-card-border/60 pb-2.5 mb-3 text-xs font-mono">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-dusk-peach shadow-[0_0_6px_#FFA586]" />
                <span className="text-dusk-peach font-semibold">ModelForge Synthesis Result</span>
              </div>
              <div className="flex items-center gap-2 text-text-muted text-[11px]">
                <span>1.42s total</span>
                <span className="text-emerald-400 font-mono">99.2% confidence</span>
              </div>
            </div>
            <p className="text-xs text-text-secondary mb-3">
              Scan analysis complete across 18,400 thermal slice frames. Two deviations exceed
              tolerance specifications under ISO-5817 Level B:
            </p>

            {/* Results table */}
            <div className="overflow-x-auto rounded-xl border border-dusk-card-border/80 bg-[#121927]/90 p-2.5 font-mono text-[11px] mb-3">
              <table className="w-full text-left">
                <thead>
                  <tr className="text-text-muted border-b border-dusk-card-border/60">
                    <th className="pb-1.5 font-semibold">Ref ID</th>
                    <th className="pb-1.5 font-semibold">Location</th>
                    <th className="pb-1.5 font-semibold">Anomaly Type</th>
                    <th className="pb-1.5 font-semibold">Severity</th>
                    <th className="pb-1.5 font-semibold">Recommendation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-dusk-card-border/30 text-text-secondary">
                  <tr>
                    <td className="py-1.5 text-dusk-peach">ANOM-048</td>
                    <td className="py-1.5">Rib 14 / Lower Cap</td>
                    <td className="py-1.5">Micro-porosity cluster (&gt;0.4mm)</td>
                    <td className="py-1.5">
                      <span className="text-dusk-crimson font-bold">CRITICAL</span>
                    </td>
                    <td className="py-1.5">Ultrasonic NDT re-test</td>
                  </tr>
                  <tr>
                    <td className="py-1.5 text-dusk-peach">ANOM-051</td>
                    <td className="py-1.5">Stringer 28 Flange</td>
                    <td className="py-1.5">Undercut 0.12mm (within limit)</td>
                    <td className="py-1.5">
                      <span className="text-amber-400 font-bold">MARGINAL</span>
                    </td>
                    <td className="py-1.5">Surface blend polish</td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Action buttons */}
            <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-dusk-card-border/60 text-xs font-mono">
              <div className="flex items-center gap-2">
                <button className="px-2.5 py-1 rounded-lg bg-dusk-card hover:bg-dusk-peach/20 hover:text-dusk-peach border border-dusk-card-border transition-all flex items-center gap-1 text-[11px]">
                  <MaterialIcon name="content_copy" className="text-xs" />
                  Copy Table
                </button>
                <button className="px-2.5 py-1 rounded-lg bg-dusk-card hover:bg-dusk-peach/20 hover:text-dusk-peach border border-dusk-card-border transition-all flex items-center gap-1 text-[11px]">
                  <MaterialIcon name="picture_as_pdf" className="text-xs" />
                  Export Signed PDF
                </button>
              </div>
              <span className="text-[10px] text-text-muted">
                Checksum:{" "}
                <span className="text-text-main font-mono">sha256-8a9d...43f2</span>
              </span>
            </div>
          </div>
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-dusk-plum to-dusk-crimson border border-dusk-peach/50 flex items-center justify-center text-dusk-peach flex-shrink-0 text-xs shadow-[0_0_10px_rgba(255,165,134,0.3)]">
            <MaterialIcon name="auto_awesome" className="text-sm" />
          </div>
        </div>
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
            onChange={(e) => onPromptChange(e.target.value)}
            className="flex-1 bg-transparent border-none text-text-main font-body placeholder:text-text-muted/60 focus:ring-0 px-2 text-xs md:text-sm"
            placeholder="Ask anything — prompts never cross the air-gap boundary..."
          />
          <button className="bg-dusk-peach hover:bg-[#ffb59c] text-dusk-navy hover:shadow-[0_0_18px_rgba(255,165,134,0.45)] rounded-full px-4 md:px-5 py-2 font-mono font-bold text-xs transition-all duration-200 flex items-center gap-1.5 flex-shrink-0 cursor-pointer">
            <span>Generate</span>
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
          <span className="w-1 h-1 rounded-full bg-dusk-card-border hidden sm:inline-block" />
          <span className="text-text-muted hidden sm:inline-block">
            Offline Context Window: 32,768 tok
          </span>
        </div>
      </div>
    </main>
  );
}
