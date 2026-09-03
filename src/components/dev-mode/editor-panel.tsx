"use client";

import { MaterialIcon } from "@/components/ui/material-icon";

interface EditorPanelProps {
  activeFile: string;
}

const FILES_DATA: Record<string, { name: string; icon: string; iconColor: string; code: string }> = {
  lora: {
    name: "lora_kernel.cu",
    icon: "memory",
    iconColor: "text-emerald-400",
    code: `// ModelForge Enclave Runtime: Air-Gapped FP8 GEMM LoRA Fusion
#include <cuda_fp8.h>
#include <mma.h>
#include "modelforge_security_enclave.h"

// Zero-egress hardware isolation verification
__device__ void assert_isolated_ram_bounds(const void* ptr) {
    ENCLAVE_CUDA_ASSERT((uintptr_t)ptr >= 0x7F0000000000ULL);
}

__global__ void fuse_lora_gemm_fp8(
    const __nv_fp8_e4m3* __restrict__ A_base,      // Base model quantized weights
    const __nv_fp8_e4m3* __restrict__ B_lora_a,    // Down-projection rank 16
    const __nv_fp8_e4m3* __restrict__ B_lora_b,    // Up-projection rank 32
    half* __restrict__ C_out,                       // FP16 fused accumulation
    const float lora_scale,
    int M, int N, int K, int rank
) {
    // Warp tile dimensions: 16x16x32 with Tensor Core WMMA
    int warp_id = threadIdx.x / 32;
    int lane_id = threadIdx.x % 32;

    // Local shared memory cache for double-buffering
    __shared__ __nv_fp8_e4m3 smem_base[32][64];
    __shared__ half smem_adapter[32][32];

    assert_isolated_ram_bounds(A_base);
    assert_isolated_ram_bounds(C_out);

    // Compute Base GEMM + Scaled LoRA in single memory pass
    half acc = 0.0f;
    #pragma unroll
    for (int k_step = 0; k_step < K; k_step += 32) {
        smem_base[warp_id][lane_id] = A_base[k_step + lane_id];
        __syncwarp();
    }
}`,
  },
  policy: {
    name: "airgap_policy.yaml",
    icon: "shield_lock",
    iconColor: "text-dusk-crimson",
    code: `# ModelForge Air-Gap Zero-Trust Security Specification
version: "2.4-enclave"
enclave_id: "node-ada-rtx-classified-01"

network_rules:
  drop_all_egress: true
  allow_unix_sockets:
    - "/var/run/vllm.sock"
    - "/tmp/modelforge_lora.ipc"
  drop_icmp: true

model_constraints:
  max_vram_gb: 24.0
  kv_cache_type: "FP8_E4M3"
  disallow_remote_checkpoints: true
  sha256_audit: "0x89fd10b3e5a74"`,
  },
  infer: {
    name: "infer_engine.rs",
    icon: "construction",
    iconColor: "text-orange-400",
    code: `// High-concurrency Rust inference daemon wrapper
use std::sync::Arc;
use tokio::sync::mpsc;

pub struct InferenceRunner {
    model_id: String,
    max_context_tokens: usize,
    hardware_enclave_locked: bool,
}

impl InferenceRunner {
    pub fn new(model_id: &str) -> Self {
        InferenceRunner {
            model_id: model_id.to_string(),
            max_context_tokens: 32768,
            hardware_enclave_locked: true,
        }
    }
}`,
  },
};

const TABS = ["lora", "policy", "infer"];

function highlightCode(code: string): string {
  return code
    .replace(/\/\/.*$/gm, '<span class="syn-comm">$&</span>')
    .replace(/#include\s*<([^>]+)>/g, '<span class="syn-macro">#include</span> <span class="syn-str">&lt;$1&gt;</span>')
    .replace(/#include\s*"([^"]+)"/g, '<span class="syn-macro">#include</span> <span class="syn-str">"$1"</span>')
    .replace(/\b(__global__|__device__|__shared__|__restrict__|__syncwarp|__nv_fp8_e4m3|pragma\s+unroll)\b/g, '<span class="syn-kw">$1</span>')
    .replace(/\b(void|int|float|half|const|uint32_t|uintptr_t|usize)\b/g, '<span class="syn-type">$1</span>')
    .replace(/\b(fuse_lora_gemm_fp8|assert_isolated_ram_bounds|ENCLAVE_CUDA_ASSERT)\b/g, '<span class="syn-fn">$1</span>')
    .replace(/\b(\d+\.?\d*f?)\b/g, '<span class="syn-num">$1</span>')
    .replace(/\b(threadIdx\.x|blockDim\.x|warp_id|lane_id|smem_base|smem_adapter|A_base|B_lora_a|B_lora_b|C_out|lora_scale|M|N|K|rank|acc|k_step|ptr)\b/g, '<span class="syn-var">$1</span>');
}

function SyntaxHighlight({ code }: { code: string }) {
  const lines = code.split("\n");
  return (
    <div className="outline-none min-h-[360px] text-text-secondary whitespace-pre font-mono" contentEditable suppressContentEditableWarning spellCheck={false}>
      {lines.map((line, i) => {
        const lineNum = i + 36;
        const isAdded = line.startsWith("+");
        const hasBreakpoint = lineNum === 43;
        
        return (
          <div key={i} className="flex">
            <span className={`w-14 flex-shrink-0 text-right pr-3 select-none text-[11px] font-mono leading-6 ${
              hasBreakpoint
                ? "bg-dusk-plum/40 text-dusk-peach font-bold border-r-2 border-dusk-peach"
                : isAdded
                ? "bg-emerald-950/40 text-emerald-400 font-bold border-r-2 border-emerald-400"
                : "text-text-muted/60"
            }`}>
              {hasBreakpoint && (
                <span className="w-2 h-2 rounded-full bg-dusk-crimson inline-block mr-0.5 shadow-[0_0_6px_#B51A28]" title="Breakpoint Active: Line 43" />
              )}
              {lineNum}
            </span>
            <span className="flex-1 leading-6 px-2">
              {line.includes("//") && !line.trimStart().startsWith("//") ? (
                <>
                  {highlightCode(line.split("//")[0])}
                  <span className="syn-comm">{"//" + line.split("//").slice(1).join("//")}</span>
                </>
              ) : (
                <span dangerouslySetInnerHTML={{ __html: highlightCode(line) }} />
              )}
            </span>
          </div>
        );
      })}
    </div>
  );
}

export function EditorPanel({ activeFile }: EditorPanelProps) {
  const file = FILES_DATA[activeFile] || FILES_DATA.lora;

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden">
      {/* Tabs */}
      <div className="h-10 bg-dusk-navy/95 border-b border-dusk-card-border/80 flex items-center justify-between px-2 select-none">
        <div className="flex items-center h-full overflow-x-auto gap-1">
          {TABS.map((key) => {
            const f = FILES_DATA[key];
            if (!f) return null;
            const isActive = activeFile === key;
            return (
              <div
                key={key}
                className={`h-full flex items-center gap-2 px-3.5 cursor-pointer transition-colors group ${
                  isActive
                    ? "bg-dusk-card/80 border-t-2 border-dusk-peach border-r border-l border-dusk-card-border/60 text-xs font-mono font-semibold text-text-main shadow-[0_-2px_8px_rgba(255,165,134,0.15)]"
                    : "bg-transparent border-r border-dusk-card-border/40 text-xs font-mono text-text-muted hover:text-text-main hover:bg-dusk-card/40"
                }`}
              >
                <MaterialIcon name={f.icon} className={`text-sm ${f.iconColor}`} />
                <span>{f.name}</span>
                {isActive && <span className="w-1.5 h-1.5 rounded-full bg-dusk-peach ml-0.5" />}
                <button className="hover:bg-white/10 rounded p-0.5 ml-1 text-text-muted hover:text-text-main">
                  <MaterialIcon name="close" className="text-[13px]" />
                </button>
              </div>
            );
          })}
        </div>

        <div className="flex items-center gap-1.5 text-xs font-mono">
          <div className="hidden xl:flex items-center gap-2 px-2.5 py-1 rounded-lg bg-dusk-plum/40 border border-dusk-peach/30 text-dusk-peach text-[11px]">
            <span className="w-1.5 h-1.5 rounded-full bg-dusk-peach animate-pulse" />
            <span>2 staged reviews • Reviewing Commit #a8f19c</span>
          </div>
          <button className="px-3 py-1 rounded-lg bg-dusk-peach hover:bg-[#ffb59c] text-dusk-navy font-bold text-xs flex items-center gap-1.5 shadow-[0_0_14px_rgba(255,165,134,0.3)] transition-all active:scale-95 cursor-pointer">
            <MaterialIcon name="play_arrow" className="text-sm" filled />
            <span>Run Kernel</span>
          </button>
          <button className="p-1.5 text-text-muted hover:text-dusk-peach hover:bg-dusk-card/70 rounded-lg transition-colors">
            <MaterialIcon name="save" className="text-[18px]" />
          </button>
          <button className="p-1.5 text-text-muted hover:text-dusk-peach hover:bg-dusk-card/70 rounded-lg transition-colors">
            <MaterialIcon name="vertical_split" className="text-[18px]" />
          </button>
          <button className="p-1.5 text-text-muted hover:text-dusk-peach hover:bg-dusk-card/70 rounded-lg transition-colors">
            <MaterialIcon name="difference" className="text-[18px]" />
          </button>
          <button className="p-1.5 text-text-muted hover:text-dusk-peach hover:bg-dusk-card/70 rounded-lg transition-colors">
            <MaterialIcon name="more_vert" className="text-[18px]" />
          </button>
        </div>
      </div>

      {/* Breadcrumb */}
      <div className="h-7 px-4 bg-[#141d2e]/80 border-b border-dusk-card-border/50 flex items-center gap-2 text-[11px] font-mono text-text-muted select-none">
        <span className="text-text-muted hover:text-text-main cursor-pointer">modelforge-airgap-pipeline</span>
        <span className="text-dusk-card-border">&gt;</span>
        <span className="text-text-muted hover:text-text-main cursor-pointer">src</span>
        <span className="text-dusk-card-border">&gt;</span>
        <span className="text-dusk-peach font-semibold flex items-center gap-1">
          <MaterialIcon name={file.icon} className={`text-[13px] ${file.iconColor}`} />
          {file.name}
        </span>
        <span className="text-dusk-card-border">&gt;</span>
        <span className="text-text-secondary">fuse_lora_gemm_fp8()</span>
      </div>

      {/* Code surface */}
      <div className="flex-1 flex overflow-hidden relative">
        <div className="overflow-y-auto overflow-x-auto p-3 text-xs font-mono leading-6 code-editor relative flex-1">
          <SyntaxHighlight code={file.code} />

          {/* Review card */}
          {activeFile === "lora" && <ReviewCard />}
        </div>
      </div>
    </div>
  );
}

function ReviewCard() {
  return (
    <div className="my-4 mr-6 rounded-2xl bg-[#1e273d]/95 border border-dusk-peach/50 p-4 shadow-[0_8px_30px_rgba(0,0,0,0.6)] backdrop-blur-2xl">
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-lg bg-dusk-plum/70 border border-dusk-peach/40 flex items-center justify-center text-dusk-peach shadow-[0_0_8px_rgba(255,165,134,0.3)]">
            <MaterialIcon name="smart_toy" className="text-xs" />
          </div>
          <div>
            <span className="text-xs font-semibold text-text-main">
              AI Enclave Security & Performance Reviewer
            </span>
            <span className="text-[10px] text-text-muted font-mono ml-2">
              2 minutes ago • staged against master
            </span>
          </div>
        </div>
        <span className="text-[9px] font-mono text-dusk-peach bg-dusk-peach/10 border border-dusk-peach/30 px-2 py-0.5 rounded font-semibold">
          SUGGESTION APPLIED
        </span>
      </div>
      <div className="text-xs text-text-secondary pl-8 leading-relaxed">
        <p className="mb-2">
          <span className="text-dusk-peach font-mono font-semibold">Optimization Notice:</span>{" "}
          Memory coalescing can be improved in{" "}
          <code className="bg-[#121927] px-1.5 py-0.5 rounded text-text-main font-mono border border-dusk-card-border">
            blockDim.x = 256
          </code>{" "}
          by packing two FP8 elements into a 16-bit register prior to WMMA load. Verified 0
          outbound network requests.
        </p>
        <div className="bg-[#101624] border border-dusk-card-border/80 rounded-xl p-2.5 font-mono text-[11px] mb-3">
          <div className="text-dusk-crimson flex items-center gap-1.5">
            <span className="w-3">-</span>
            smem_base[warp_id][lane_id] = A_base[k_step + lane_id];
          </div>
          <div className="text-emerald-400 flex items-center gap-1.5">
            <span className="w-3">+</span>
            uint32_t packed_fp8 = *reinterpret_cast&lt;const uint32_t*&gt;(&amp;A_base[k_step + lane_id * 4]);
          </div>
        </div>
        <div className="flex items-center gap-2 font-mono text-[11px]">
          <button className="px-3 py-1 rounded-lg bg-dusk-peach hover:bg-[#ffb59c] text-dusk-navy font-bold flex items-center gap-1 cursor-pointer transition-all shadow-[0_0_12px_rgba(255,165,134,0.3)]">
            <MaterialIcon name="check" className="text-xs" />
            Accept & Merge Commit
          </button>
          <button className="px-3 py-1 rounded-lg bg-dusk-card hover:bg-white/[0.08] text-text-secondary border border-dusk-card-border transition-all">
            Reply inline...
          </button>
          <span className="text-[10px] text-text-muted ml-auto">
            Verified Air-gapped Hash:{" "}
            <span className="text-text-main font-mono">0x4a91...bc</span>
          </span>
        </div>
      </div>
    </div>
  );
}
