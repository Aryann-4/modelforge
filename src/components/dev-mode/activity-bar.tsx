"use client";

import { MaterialIcon } from "@/components/ui/material-icon";

interface ActivityBarProps {
  activeActivity: string;
  onToggleActivity: (activity: string) => void;
}

const ACTIVITIES = [
  { id: "explorer", icon: "folder_open", filled: true, title: "Explorer (Ctrl+Shift+E)" },
  { id: "search", icon: "search", filled: false, title: "Search & Regex (Ctrl+Shift+F)" },
  { id: "git", icon: "commit", filled: false, title: "Source Control & Airgap PRs", badge: "2" },
  { id: "probes", icon: "psychology", filled: false, title: "Model Probes & Latent Visualizer" },
  { id: "ext", icon: "extension", filled: false, title: "Air-Gapped Toolchains & Linters" },
];

export function ActivityBar({ activeActivity, onToggleActivity }: ActivityBarProps) {
  return (
    <aside className="w-12 md:w-14 bg-[#101726]/95 border-r border-dusk-card-border/80 flex flex-col items-center py-3 justify-between z-30 flex-shrink-0 backdrop-blur-2xl">
      <div className="flex flex-col items-center gap-4 w-full">
        {ACTIVITIES.map((act) => {
          const isActive = activeActivity === act.id;
          return (
            <button
              key={act.id}
              onClick={() => onToggleActivity(act.id)}
              className={`relative w-9 h-9 rounded-xl flex items-center justify-center transition-all group cursor-pointer ${
                isActive
                  ? "text-dusk-peach bg-dusk-card/70 border border-dusk-peach/40 shadow-[0_0_12px_rgba(255,165,134,0.25)]"
                  : "text-text-muted hover:text-dusk-peach hover:bg-dusk-card/40"
              }`}
              title={act.title}
            >
              <MaterialIcon
                name={act.icon}
                className="text-[20px]"
                filled={act.filled}
              />
              {isActive && (
                <span className="absolute -left-1 top-2.5 bottom-2.5 w-1 rounded-r bg-dusk-peach" />
              )}
              {act.badge && (
                <span className="absolute -top-1 -right-1 bg-dusk-crimson text-white text-[9px] font-mono font-bold w-4 h-4 rounded-full flex items-center justify-center border border-dusk-navy shadow-[0_0_6px_#B51A28]">
                  {act.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>
      <div className="flex flex-col items-center gap-3 w-full">
        <button
          className="w-8 h-8 rounded-lg flex items-center justify-center text-emerald-400 hover:bg-dusk-card/40 transition-all"
          title="Enclave Status: Hardware Verified"
        >
          <MaterialIcon name="verified_user" className="text-[19px]" />
        </button>
        <button
          className="w-8 h-8 rounded-lg flex items-center justify-center text-text-muted hover:text-text-main hover:bg-dusk-card/40 transition-all"
          title="Preferences"
        >
          <MaterialIcon name="settings" className="text-[19px]" />
        </button>
      </div>
    </aside>
  );
}
