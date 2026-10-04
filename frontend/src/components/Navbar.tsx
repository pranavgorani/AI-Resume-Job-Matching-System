"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { 
  Menu, 
  Search, 
  Bell, 
  PlayCircle, 
  Sparkles, 
  ShieldCheck,
  CheckCircle2
} from "lucide-react";
import { seedDemoData } from "@/lib/api";

interface NavbarProps {
  onToggleSidebar?: () => void;
  onOpenCopilot?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleSidebar, onOpenCopilot }) => {
  const router = useRouter();
  const [seeding, setSeeding] = useState(false);
  const [seededMsg, setSeededMsg] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const handleSeedDemo = async () => {
    try {
      setSeeding(true);
      const res = await seedDemoData();
      setSeededMsg(true);
      setTimeout(() => setSeededMsg(false), 3000);
      router.push(`/jobs/${res.job_id}`);
    } catch (err: any) {
      alert(`Demo Seed failed: ${err.message}`);
    } finally {
      setSeeding(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/candidates?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="sticky top-0 z-30 h-16 w-full border-b border-slate-200 dark:border-slate-800/80 bg-white/95 dark:bg-slate-950/90 backdrop-blur-md px-4 sm:px-6 flex items-center justify-between gap-4">
      {/* Left side: Hamburger toggle & Quick search */}
      <div className="flex items-center gap-3 flex-1 max-w-xl">
        {onToggleSidebar && (
          <button
            onClick={onToggleSidebar}
            title="Toggle Sidebar Menu"
            className="p-2 rounded-lg text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        {/* Global Search Bar */}
        <form onSubmit={handleSearchSubmit} className="relative flex-1 hidden sm:block">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search candidates, evidence, or job skills..."
            className="w-full bg-slate-100 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 rounded-xl pl-9 pr-8 py-1.5 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
          />
          <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] font-mono text-slate-400 border border-slate-300 dark:border-slate-700 px-1.5 py-0.5 rounded">
            ↵
          </span>
        </form>
      </div>

      {/* Right side: Action Controls & User Avatar */}
      <div className="flex items-center gap-3">
        {/* 1-Click Demo Seed Button */}
        <button
          onClick={handleSeedDemo}
          disabled={seeding}
          id="try-demo-btn"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 hover:bg-indigo-100 dark:hover:bg-indigo-900/40 transition-all shadow-sm active:scale-95"
        >
          <PlayCircle className={`w-3.5 h-3.5 ${seeding ? "animate-spin text-indigo-600" : "text-indigo-600"}`} />
          <span className="hidden sm:inline">
            {seeding ? "Loading..." : seededMsg ? "✓ Loaded" : "Try Live Demo"}
          </span>
        </button>

        {/* AI Copilot Trigger */}
        {onOpenCopilot && (
          <button
            onClick={onOpenCopilot}
            id="copilot-open-btn"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white shadow-md shadow-indigo-600/20 transition-all active:scale-95"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            <span>AI Copilot</span>
          </button>
        )}

        {/* Notifications Icon */}
        <button
          title="Notifications"
          className="relative p-2 rounded-lg text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-emerald-500 ring-2 ring-white dark:ring-slate-950" />
        </button>

        {/* User Profile Avatar */}
        <div className="flex items-center gap-2 pl-2 border-l border-slate-200 dark:border-slate-800">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-emerald-500 flex items-center justify-center text-white font-bold text-xs shadow-sm">
            PR
          </div>
        </div>
      </div>
    </header>
  );
};
