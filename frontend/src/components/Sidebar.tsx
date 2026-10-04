"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { getCandidates } from "@/lib/api";
import {
  ShieldCheck,
  Plus,
  LayoutDashboard,
  Briefcase,
  Users,
  Layers,
  BarChart3,
  Sparkles,
  Settings,
  PanelLeftClose,
  PanelLeftOpen,
  CheckCircle2,
  User,
  LogOut,
  ChevronRight
} from "lucide-react";

interface SidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
  mobileOpen: boolean;
  onCloseMobile: () => void;
  onOpenCopilot: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  collapsed,
  onToggleCollapse,
  mobileOpen,
  onCloseMobile,
  onOpenCopilot,
}) => {
  const pathname = usePathname();
  const [candidateCount, setCandidateCount] = useState<number | null>(null);

  useEffect(() => {
    getCandidates()
      .then((cands) => setCandidateCount(Array.isArray(cands) ? cands.length : 0))
      .catch(() => setCandidateCount(null));
  }, [pathname]);

  const navItems = [
    { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard, badge: null },
    { label: "Jobs", href: "/jobs", icon: Briefcase, badge: null },
    { 
      label: "Candidates", 
      href: "/candidates", 
      icon: Users, 
      badge: candidateCount !== null ? String(candidateCount) : null 
    },
    { label: "Compare", href: "/compare", icon: Layers, badge: null },
    { label: "Analytics", href: "/analytics", icon: BarChart3, badge: "Real-time" },
  ];

  const secondaryItems = [
    { label: "Settings", href: "/settings", icon: Settings },
  ];

  const isItemActive = (href: string) => {
    if (href === "/dashboard") {
      return pathname === "/" || pathname === "/dashboard";
    }
    return pathname.startsWith(href);
  };

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {mobileOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden transition-opacity"
        />
      )}

      {/* Main Sidebar Element */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 flex flex-col bg-slate-950 text-slate-100 border-r border-slate-800/80 transition-all duration-300 ease-in-out ${
          collapsed ? "w-[72px]" : "w-[260px]"
        } ${
          mobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
      >
        {/* Top Header / Branding */}
        <div className="h-16 flex items-center justify-between px-3.5 border-b border-slate-800/80">
          <Link
            href="/dashboard"
            onClick={onCloseMobile}
            className="flex items-center gap-2.5 overflow-hidden group"
          >
            <div className="w-9 h-9 min-w-[36px] rounded-lg bg-gradient-to-tr from-indigo-600 to-emerald-500 flex items-center justify-center text-white shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform">
              <ShieldCheck className="w-5 h-5" />
            </div>
            {!collapsed && (
              <div className="flex flex-col min-w-0">
                <div className="flex items-center gap-1.5">
                  <span className="font-extrabold text-white text-base tracking-tight truncate">
                    TalentProof<span className="text-indigo-400"> AI</span>
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="text-[9px] font-bold uppercase tracking-wider text-emerald-400 bg-emerald-950/60 border border-emerald-500/30 px-1 py-0.2 rounded">
                    Fair Match
                  </span>
                  <span className="text-[10px] text-slate-400 truncate">v1.0</span>
                </div>
              </div>
            )}
          </Link>

          {/* Desktop Collapse Toggle */}
          <button
            onClick={onToggleCollapse}
            title={collapsed ? "Expand sidebar (260px)" : "Collapse sidebar (72px)"}
            className="hidden md:flex p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors"
          >
            {collapsed ? (
              <PanelLeftOpen className="w-4 h-4" />
            ) : (
              <PanelLeftClose className="w-4 h-4" />
            )}
          </button>
        </div>

        {/* Action: + New Job Button */}
        <div className="p-3">
          <Link
            href="/jobs/new"
            onClick={onCloseMobile}
            className={`w-full flex items-center justify-center gap-2 py-2.5 rounded-xl font-bold text-xs bg-gradient-to-r from-indigo-600 via-indigo-500 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white shadow-lg shadow-indigo-600/25 transition-all transform active:scale-98 ${
              collapsed ? "px-0" : "px-4"
            }`}
            title="Create New Job Requisition"
          >
            <Plus className="w-4 h-4" />
            {!collapsed && <span>New Job</span>}
          </Link>
        </div>

        {/* Primary Navigation Items */}
        <div className="flex-1 overflow-y-auto px-2 space-y-1 py-1">
          <div className="space-y-0.5">
            {!collapsed && (
              <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1">
                Main Menu
              </p>
            )}
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isItemActive(item.href);

              return (
                <div key={item.href} className="relative group">
                  <Link
                    href={item.href}
                    onClick={onCloseMobile}
                    className={`flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
                      active
                        ? "bg-indigo-600/20 text-indigo-300 border-l-4 border-indigo-500 shadow-sm"
                        : "text-slate-400 hover:bg-slate-900 hover:text-slate-100"
                    } ${collapsed ? "justify-center px-0" : ""}`}
                  >
                    <Icon className={`w-4 h-4 ${active ? "text-indigo-400" : "text-slate-400 group-hover:text-slate-200"}`} />
                    {!collapsed && (
                      <span className="flex-1 truncate">{item.label}</span>
                    )}
                    {!collapsed && item.badge && (
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-indigo-950 text-indigo-400 border border-indigo-800/60">
                        {item.badge}
                      </span>
                    )}
                  </Link>

                  {/* Tooltip when collapsed */}
                  {collapsed && (
                    <div className="absolute left-full ml-3 top-1/2 -translate-y-1/2 hidden group-hover:flex items-center z-50">
                      <div className="bg-slate-900 text-white text-xs font-semibold px-2.5 py-1 rounded-md shadow-lg border border-slate-700 whitespace-nowrap">
                        {item.label}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Divider */}
          <div className="my-3 border-t border-slate-800/80" />

          {/* AI Tools & Utilities */}
          <div className="space-y-0.5">
            {!collapsed && (
              <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1">
                AI Intelligence
              </p>
            )}

            {/* AI Copilot Trigger */}
            <div className="relative group">
              <button
                onClick={() => {
                  onCloseMobile();
                  onOpenCopilot();
                }}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold text-amber-300 hover:bg-amber-500/10 hover:text-amber-200 transition-all ${
                  collapsed ? "justify-center px-0" : ""
                }`}
              >
                <Sparkles className="w-4 h-4 text-amber-400" />
                {!collapsed && <span className="flex-1 text-left">AI Copilot</span>}
                {!collapsed && (
                  <span className="text-[9px] font-black uppercase tracking-wider px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                    Live
                  </span>
                )}
              </button>
              {collapsed && (
                <div className="absolute left-full ml-3 top-1/2 -translate-y-1/2 hidden group-hover:flex items-center z-50">
                  <div className="bg-slate-900 text-white text-xs font-semibold px-2.5 py-1 rounded-md shadow-lg border border-slate-700 whitespace-nowrap">
                    AI Recruiter Copilot
                  </div>
                </div>
              )}
            </div>

            {/* Secondary links (Settings) */}
            {secondaryItems.map((item) => {
              const Icon = item.icon;
              const active = isItemActive(item.href);

              return (
                <div key={item.href} className="relative group">
                  <Link
                    href={item.href}
                    onClick={onCloseMobile}
                    className={`flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
                      active
                        ? "bg-indigo-600/20 text-indigo-300 border-l-4 border-indigo-500 shadow-sm"
                        : "text-slate-400 hover:bg-slate-900 hover:text-slate-100"
                    } ${collapsed ? "justify-center px-0" : ""}`}
                  >
                    <Icon className={`w-4 h-4 ${active ? "text-indigo-400" : "text-slate-400 group-hover:text-slate-200"}`} />
                    {!collapsed && <span className="flex-1 truncate">{item.label}</span>}
                  </Link>

                  {collapsed && (
                    <div className="absolute left-full ml-3 top-1/2 -translate-y-1/2 hidden group-hover:flex items-center z-50">
                      <div className="bg-slate-900 text-white text-xs font-semibold px-2.5 py-1 rounded-md shadow-lg border border-slate-700 whitespace-nowrap">
                        {item.label}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Bottom User Profile Section */}
        <div className="p-3 border-t border-slate-800/80 bg-slate-950/60">
          <div
            className={`flex items-center gap-2.5 rounded-xl p-1.5 transition-colors ${
              collapsed ? "justify-center" : "hover:bg-slate-900"
            }`}
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-600 flex items-center justify-center text-white font-bold text-xs ring-2 ring-indigo-500/20">
              PR
            </div>
            {!collapsed && (
              <div className="flex-1 min-w-0">
                <p className="text-xs font-bold text-white truncate">Pranav</p>
                <p className="text-[10px] text-slate-400 truncate">Lead Technical Recruiter</p>
              </div>
            )}
          </div>
        </div>
      </aside>
    </>
  );
};
