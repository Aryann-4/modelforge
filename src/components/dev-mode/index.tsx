"use client";

import { useState } from "react";
import { ActivityBar } from "./activity-bar";
import { FileExplorer } from "./file-explorer";
import { EditorPanel } from "./editor-panel";
import { TerminalPanel } from "./terminal-panel";
import { StatusBar } from "./status-bar";

export function DevMode() {
  const [activeActivity, setActiveActivity] = useState("explorer");
  const [activeFile, setActiveFile] = useState("lora");

  return (
    <div className="mode-dev-view flex-1 flex flex-col h-full w-full overflow-hidden">
      <div className="flex flex-1 h-[calc(100%-26px)] w-full overflow-hidden">
        <ActivityBar activeActivity={activeActivity} onToggleActivity={setActiveActivity} />
        <FileExplorer activeFile={activeFile} onSelectFile={setActiveFile} />
        <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#121927]/80 backdrop-blur-xl relative">
          <EditorPanel activeFile={activeFile} />
          <TerminalPanel />
        </div>
      </div>
      <StatusBar />
    </div>
  );
}
