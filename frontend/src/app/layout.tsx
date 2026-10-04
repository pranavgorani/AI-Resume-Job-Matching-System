"use client";

import React, { useState, useEffect } from "react";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";
import { Navbar } from "@/components/Navbar";
import { CopilotDrawer } from "@/components/CopilotDrawer";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [copilotOpen, setCopilotOpen] = useState(false);

  // Restore sidebar collapse state from localStorage if present
  useEffect(() => {
    try {
      const saved = localStorage.getItem("talentproof_sidebar_collapsed");
      if (saved !== null) {
        setSidebarCollapsed(saved === "true");
      }
    } catch {
      // Ignore in SSR
    }
  }, []);

  const handleToggleCollapse = () => {
    setSidebarCollapsed((prev) => {
      const next = !prev;
      try {
        localStorage.setItem("talentproof_sidebar_collapsed", String(next));
      } catch {}
      return next;
    });
  };

  return (
    <html lang="en">
      <head>
        <title>TalentProof AI — Evidence-First Candidate Intelligence Platform</title>
        <meta
          name="description"
          content="Don't just rank resumes. Prove the match. TalentProof AI uses evidence graphs, contradiction detection, and explainable scoring for recruitment."
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100 flex font-sans antialiased overflow-x-hidden">
        {/* Left Permanent / Collapsible Sidebar */}
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggleCollapse={handleToggleCollapse}
          mobileOpen={mobileSidebarOpen}
          onCloseMobile={() => setMobileSidebarOpen(false)}
          onOpenCopilot={() => setCopilotOpen(true)}
        />

        {/* Main Content Area (resizes based on sidebar width) */}
        <div
          className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ease-in-out ${
            sidebarCollapsed ? "md:ml-[72px]" : "md:ml-[260px]"
          }`}
        >
          {/* Top Simplified Header */}
          <Navbar
            onToggleSidebar={() => {
              // On mobile toggle drawer, on desktop toggle collapse
              if (window.innerWidth < 768) {
                setMobileSidebarOpen((prev) => !prev);
              } else {
                handleToggleCollapse();
              }
            }}
            onOpenCopilot={() => setCopilotOpen(true)}
          />

          {/* Page Main Content */}
          <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
            {children}
          </main>
        </div>

        {/* Global AI Recruiter Copilot Drawer */}
        <CopilotDrawer
          isOpen={copilotOpen}
          onClose={() => setCopilotOpen(false)}
        />
      </body>
    </html>
  );
}
