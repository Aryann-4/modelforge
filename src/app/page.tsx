"use client";

import { useState, useCallback } from "react";
import { TopBar } from "@/components/top-bar";
import { Sidebar } from "@/components/sidebar";
import { Workspace } from "@/components/workspace";
import { RightPanel } from "@/components/right-panel";
import { useModelforge } from "@/hooks/use-modelforge";

export default function Home() {
  const state = useModelforge();
  const [mobileSidebar, setMobileSidebar] = useState(false);
  const [mobilePanel, setMobilePanel] = useState(false);

  const closeMobileSidebar = useCallback(() => setMobileSidebar(false), []);
  const closeMobilePanel = useCallback(() => setMobilePanel(false), []);

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <TopBar
        gpuUsage={state.gpuUsage}
        vramUsage={state.vramUsage}
        onToggleSidebar={() => setMobileSidebar((v) => !v)}
        onTogglePanel={() => setMobilePanel((v) => !v)}
      />
      <div className="flex flex-1 overflow-hidden relative">
        {/* Sidebar — always visible on lg+, overlay on mobile */}
        <div className="hidden lg:flex lg:flex-col lg:w-[260px] lg:shrink-0">
          <Sidebar
            activeModel={state.activeModel}
            models={state.models}
            onRunDemo={state.runDemo}
            isRunning={state.isRunning}
          />
        </div>

        {/* Mobile sidebar overlay */}
        {mobileSidebar && (
          <>
            <div
              className="fixed inset-0 bg-black/50 z-40 lg:hidden"
              onClick={closeMobileSidebar}
            />
            <div className="fixed inset-y-0 left-0 z-50 w-[260px] lg:hidden flex flex-col">
              <Sidebar
                activeModel={state.activeModel}
                models={state.models}
                onRunDemo={(type) => {
                  state.runDemo(type);
                  closeMobileSidebar();
                }}
                isRunning={state.isRunning}
              />
            </div>
          </>
        )}

        <Workspace
          messages={state.messages}
          routerStatus={state.routerStatus}
          onSend={state.sendMessage}
          onAttach={state.simulateAttach}
          isRunning={state.isRunning}
        />

        {/* Right panel — always visible on xl+, overlay on mobile */}
        <div className="hidden xl:flex xl:flex-col xl:w-[300px] xl:shrink-0">
          <RightPanel logs={state.logs} agentSteps={state.agentSteps} />
        </div>

        {/* Mobile right panel overlay */}
        {mobilePanel && (
          <>
            <div
              className="fixed inset-0 bg-black/50 z-40 xl:hidden"
              onClick={closeMobilePanel}
            />
            <div className="fixed inset-y-0 right-0 z-50 w-[300px] max-w-[85vw] xl:hidden flex flex-col">
              <RightPanel logs={state.logs} agentSteps={state.agentSteps} />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
