"use client";

import { TopBar } from "@/components/top-bar";
import { Sidebar } from "@/components/sidebar";
import { Workspace } from "@/components/workspace";
import { RightPanel } from "@/components/right-panel";
import { useModelforge } from "@/hooks/use-modelforge";

export default function Home() {
  const state = useModelforge();

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <TopBar gpuUsage={state.gpuUsage} vramUsage={state.vramUsage} />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          activeModel={state.activeModel}
          models={state.models}
          onRunDemo={state.runDemo}
          isRunning={state.isRunning}
        />
        <Workspace
          messages={state.messages}
          routerStatus={state.routerStatus}
          onSend={state.sendMessage}
          onAttach={state.simulateAttach}
          isRunning={state.isRunning}
        />
        <RightPanel
          logs={state.logs}
          agentSteps={state.agentSteps}
        />
      </div>
    </div>
  );
}
