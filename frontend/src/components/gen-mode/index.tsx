"use client";

import { useModelforge } from "@/hooks/use-modelforge";
import { ScenarioSidebar } from "./scenario-sidebar";
import { Workspace } from "./workspace";

export function GenMode() {
  const { messages, routerStatus, isRunning, sendMessage } = useModelforge();

  return (
    <div className="mode-gen-view flex-1 flex flex-col md:flex-row h-full w-full overflow-hidden">
      <ScenarioSidebar />
      <Workspace
        messages={messages}
        routerStatus={routerStatus}
        isRunning={isRunning}
        onSend={sendMessage}
      />
    </div>
  );
}
