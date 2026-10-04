"use client";

import React, { useState } from "react";
import { X, Sparkles, Send, Bot, User, ArrowRight, CornerDownLeft } from "lucide-react";
import { askCopilot } from "@/lib/api";
import Link from "next/link";

interface CopilotDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  jobId?: number;
  candidateId?: number;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  actions?: string[];
  highlightIds?: number[];
}

export const CopilotDrawer: React.FC<CopilotDrawerProps> = ({
  isOpen,
  onClose,
  jobId,
  candidateId,
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello! I am your **TalentProof AI Recruiter Copilot**. I analyze real candidate evidence, trace claims to verified chronology, and uncover hidden risks. How can I assist your hiring decision today?",
      actions: [
        "Why is the top candidate ranked #1?",
        "Which candidates have AWS experience?",
        "Who has the strongest project evidence?",
        "Show candidates with weak evidence",
        "Summarize all candidates in 30 seconds",
      ],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || input;
    if (!textToSend.trim() || loading) return;

    const userMsg: Message = { role: "user", content: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await askCopilot(textToSend, jobId, candidateId);
      const botMsg: Message = {
        role: "assistant",
        content: res.answer,
        actions: res.suggested_actions,
        highlightIds: res.candidate_highlight_ids,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Error retrieving recruiter intelligence: ${err.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-lg bg-white dark:bg-slate-900 shadow-2xl h-full flex flex-col border-l border-slate-200 dark:border-slate-800">
        {/* Drawer Header */}
        <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50 dark:bg-slate-950">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center shadow-md shadow-indigo-600/20">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-slate-900 dark:text-white">TalentProof AI Copilot</h3>
              <p className="text-[11px] text-slate-500">Evidence-grounded hiring intelligence</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-200/50"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Messages Scroll Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 text-sm">
          {messages.map((m, idx) => (
            <div key={idx} className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              {m.role === "assistant" && (
                <div className="w-7 h-7 rounded-full bg-indigo-100 dark:bg-indigo-950/80 text-indigo-600 flex items-center justify-center shrink-0 mt-0.5">
                  <Bot className="w-4 h-4" />
                </div>
              )}
              <div
                className={`rounded-xl px-4 py-3 max-w-[85%] leading-relaxed ${
                  m.role === "user"
                    ? "bg-indigo-600 text-white shadow-sm"
                    : "bg-slate-100 dark:bg-slate-800/80 text-slate-900 dark:text-slate-100 border border-slate-200/60 dark:border-slate-700/60"
                }`}
              >
                <div className="whitespace-pre-line text-[13px]">{m.content}</div>

                {/* Candidate Highlight Links if returned */}
                {m.highlightIds && m.highlightIds.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-slate-200 dark:border-slate-700 flex flex-wrap gap-1.5">
                    {m.highlightIds.map((cid) => (
                      <Link
                        key={cid}
                        href={`/candidates/${cid}${jobId ? `?job_id=${jobId}` : ""}`}
                        className="inline-flex items-center gap-1 px-2 py-1 rounded bg-white dark:bg-slate-900 text-xs font-semibold text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800 hover:bg-indigo-50"
                      >
                        Inspect Candidate #{cid} <ArrowRight className="w-3 h-3" />
                      </Link>
                    ))}
                  </div>
                )}

                {/* Suggested actions chips */}
                {m.actions && m.actions.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-slate-200 dark:border-slate-700 space-y-1.5">
                    <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Suggested Queries</p>
                    <div className="flex flex-wrap gap-1.5">
                      {m.actions.map((act, i) => (
                        <button
                          key={i}
                          onClick={() => handleSend(act)}
                          className="text-left text-xs px-2.5 py-1 rounded-full bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-slate-700 hover:border-indigo-500 hover:text-indigo-600 transition-colors"
                        >
                          {act}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              {m.role === "user" && (
                <div className="w-7 h-7 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-600 flex items-center justify-center shrink-0 mt-0.5">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex items-center gap-2 text-xs text-slate-500 pl-10">
              <div className="w-2 h-2 rounded-full bg-indigo-600 animate-ping" />
              Reasoning over candidate evidence...
            </div>
          )}
        </div>

        {/* Input area */}
        <div className="p-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Copilot (e.g. Why is Rahul ranked #1?)..."
              className="flex-1 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg px-3.5 py-2 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="p-2 rounded-lg bg-indigo-600 text-white disabled:opacity-40 hover:bg-indigo-700 transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
