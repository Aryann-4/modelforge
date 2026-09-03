"use client";

import { useState } from "react";
import { ScenarioSidebar } from "./scenario-sidebar";
import { Workspace } from "./workspace";

export function GenMode() {
  const [prompt, setPrompt] = useState(
    "Run parametric verification on the thermal report against ASTM E1444"
  );

  return (
    <div className="mode-gen-view flex-1 flex flex-col md:flex-row h-full w-full overflow-hidden">
      <ScenarioSidebar />
      <Workspace prompt={prompt} onPromptChange={setPrompt} />
    </div>
  );
}
