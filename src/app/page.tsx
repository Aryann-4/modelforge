"use client";

import { useState } from "react";
import { TopNavBar } from "@/components/top-nav-bar";
import { GenMode } from "@/components/gen-mode";
import { DevMode } from "@/components/dev-mode";

export default function Home() {
  const [activeMode, setActiveMode] = useState<"gen" | "dev">("dev");

  return (
    <div className="bg-dusk-navy text-text-main font-body h-screen w-screen overflow-hidden flex flex-col selection:bg-dusk-peach selection:text-dusk-navy">
      {/* Atmospheric Wallpaper Layer */}
      <img
        alt="Atmospheric Background"
        className="fixed inset-0 w-full h-full object-cover opacity-30 pointer-events-none mix-blend-screen z-0"
        src="https://lh3.googleusercontent.com/aida/AEtjO1UzvihQc0I5wNdJhB0AjYxFrMxV6nEsHVrmxnUOfTtyPa3LYX7BQVegSSdUOG00gGHkTg4fiauVXSC7ZzgJ7z00mH0Aak5RNIentq0DaXGayvAXcK4py6yCXlSA-kDIM7ZLU2yUYRERSSRnSeX6UIOOjHgsGI1ldgqjD2K6EcPTxarSFQP-Fhd23ULHtaFaKNKT2ohQsLKjVDT5F5PkJTw0GuGCyJ35nnAlj139KI7uvl7s94FoDyBahjM"
      />

      {/* Ambient Gradient Lighting */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-dusk-peach/10 blur-[140px] rounded-full pointer-events-none z-0" />
      <div className="fixed -bottom-20 right-1/4 w-[500px] h-[300px] bg-dusk-crimson/15 blur-[120px] rounded-full pointer-events-none z-0" />
      <div className="fixed top-1/3 left-10 w-[350px] h-[300px] bg-dusk-plum/25 blur-[110px] rounded-full pointer-events-none z-0" />

      <TopNavBar activeMode={activeMode} onSwitchMode={setActiveMode} />

      <div className="flex flex-1 pt-16 h-full relative z-10 overflow-hidden">
        {activeMode === "gen" ? <GenMode /> : <DevMode />}
      </div>
    </div>
  );
}
