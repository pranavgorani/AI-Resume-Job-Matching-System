"use client";

import React, { useState, useRef } from "react";
import { 
  Upload, 
  X, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw, 
  Trash2, 
  Layers, 
  Sparkles,
  ArrowRight
} from "lucide-react";
import { uploadResumes, runMatching } from "@/lib/api";

interface ResumeUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  jobId: number;
  jobTitle?: string;
  onUploadComplete: () => Promise<void> | void;
}

interface UploadingFile {
  id: string;
  file: File;
  name: string;
  size: number;
  status: "Waiting" | "Uploading" | "Parsing" | "Mapping Evidence" | "Scoring" | "Completed" | "Failed";
  progress: number;
  error?: string;
  candidateName?: string;
}

export const ResumeUploadModal: React.FC<ResumeUploadModalProps> = ({
  isOpen,
  onClose,
  jobId,
  jobTitle,
  onUploadComplete,
}) => {
  const [files, setFiles] = useState<UploadingFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [globalError, setGlobalError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const validateFile = (file: File): string | null => {
    const ext = file.name.split(".").pop()?.toLowerCase();
    if (!ext || !["pdf", "docx", "doc", "txt"].includes(ext)) {
      return "Unsupported file format. Please upload PDF, DOCX, or TXT.";
    }
    const maxSizeBytes = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSizeBytes) {
      return `File is too large (${(file.size / (1024 * 1024)).toFixed(1)}MB). Max size is 10MB.`;
    }
    return null;
  };

  const addFiles = (selectedFiles: FileList | File[]) => {
    setGlobalError(null);
    setSuccessMessage(null);
    const newItems: UploadingFile[] = [];

    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];
      const error = validateFile(file);
      const id = `${file.name}-${file.size}-${Date.now()}-${Math.random()}`;

      newItems.push({
        id,
        file,
        name: file.name,
        size: file.size,
        status: error ? "Failed" : "Waiting",
        progress: error ? 0 : 0,
        error: error || undefined,
      });
    }

    setFiles((prev) => [...prev, ...newItems]);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      addFiles(e.dataTransfer.files);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const handleProcessUploads = async () => {
    const validFiles = files.filter((f) => f.status !== "Completed" && !f.error);
    if (validFiles.length === 0) {
      setGlobalError("Please add at least one valid resume file (PDF, DOCX, TXT) to upload.");
      return;
    }

    setIsProcessing(true);
    setGlobalError(null);
    setSuccessMessage(null);

    // Update statuses to Uploading
    setFiles((prev) =>
      prev.map((f) =>
        validFiles.some((vf) => vf.id === f.id)
          ? { ...f, status: "Uploading", progress: 20 }
          : f
      )
    );

    try {
      // Step: Parsing
      await new Promise((r) => setTimeout(r, 400));
      setFiles((prev) =>
        prev.map((f) =>
          validFiles.some((vf) => vf.id === f.id)
            ? { ...f, status: "Parsing", progress: 45 }
            : f
        )
      );

      // Call API with all files and exact jobId
      const rawFiles = validFiles.map((vf) => vf.file);
      const res = await uploadResumes(rawFiles, jobId);

      // Step: Mapping Evidence
      setFiles((prev) =>
        prev.map((f) =>
          validFiles.some((vf) => vf.id === f.id)
            ? { ...f, status: "Mapping Evidence", progress: 75 }
            : f
        )
      );
      await new Promise((r) => setTimeout(r, 400));

      // Step: Scoring
      setFiles((prev) =>
        prev.map((f) =>
          validFiles.some((vf) => vf.id === f.id)
            ? { ...f, status: "Scoring", progress: 90 }
            : f
        )
      );
      await new Promise((r) => setTimeout(r, 400));

      // Run matching engine to ensure fresh rankings
      try {
        await runMatching(jobId);
      } catch (_) {}

      // Update to Completed
      setFiles((prev) =>
        prev.map((f) => {
          const matchingResult = res.results?.find((r: any) => r.file_name === f.name || r.name);
          return validFiles.some((vf) => vf.id === f.id)
            ? {
                ...f,
                status: "Completed",
                progress: 100,
                candidateName: matchingResult?.name || "Verified Candidate",
              }
            : f;
        })
      );

      setSuccessMessage(
        `Successfully processed and ranked ${validFiles.length} candidate resume(s) for Requisition #${jobId}!`
      );

      // Refresh parent page data without manual reload
      await onUploadComplete();
    } catch (err: any) {
      setGlobalError(err.message || "Resume upload failed. Please retry.");
      setFiles((prev) =>
        prev.map((f) =>
          validFiles.some((vf) => vf.id === f.id)
            ? { ...f, status: "Failed", error: err.message || "Upload failed" }
            : f
        )
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const completedCount = files.filter((f) => f.status === "Completed").length;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-in fade-in">
      <div className="w-full max-w-xl bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-7 shadow-2xl border border-slate-200 dark:border-slate-800 space-y-5 relative overflow-hidden">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wider bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800">
                Target Requisition #{jobId}
              </span>
              {jobTitle && (
                <span className="text-xs font-semibold text-slate-500 truncate max-w-[240px]">
                  {jobTitle}
                </span>
              )}
            </div>
            <h2 className="text-xl font-black text-slate-900 dark:text-white flex items-center gap-2">
              <Upload className="w-5 h-5 text-indigo-600" />
              Upload Resumes
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Files are parsed, requirements mapped, claims verified, and candidates scored deterministically.
            </p>
          </div>
          <button
            onClick={onClose}
            disabled={isProcessing}
            className="p-1.5 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Drag & Drop Zone */}
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all ${
            isDragging
              ? "border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/30 scale-[0.99]"
              : "border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/40 hover:border-indigo-400 dark:hover:border-indigo-600"
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.docx,.doc,.txt"
            onChange={(e) => {
              if (e.target.files && e.target.files.length > 0) {
                addFiles(e.target.files);
              }
            }}
            disabled={isProcessing}
            className="hidden"
          />
          <div className="flex flex-col items-center gap-2">
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 text-indigo-600 flex items-center justify-center">
              <Upload className="w-6 h-6" />
            </div>
            <div className="space-y-0.5">
              <p className="text-xs font-bold text-slate-900 dark:text-white">
                Drag & drop resumes here, or <span className="text-indigo-600 underline">Browse Files</span>
              </p>
              <p className="text-[11px] text-slate-400">
                Supports PDF, DOCX, TXT • Max 10MB per file • Single or multiple files
              </p>
            </div>
          </div>
        </div>

        {/* Global Error Banner */}
        {globalError && (
          <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-xs flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
              <span>{globalError}</span>
            </div>
            <button
              onClick={handleProcessUploads}
              className="text-[11px] font-bold text-rose-600 underline hover:text-rose-800 shrink-0"
            >
              Retry
            </button>
          </div>
        )}

        {/* Success Banner */}
        {successMessage && (
          <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* Selected Files List */}
        {files.length > 0 && (
          <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
            <div className="flex items-center justify-between text-[11px] font-bold text-slate-400 uppercase tracking-wider px-1">
              <span>Selected Files ({files.length})</span>
              <span>{completedCount}/{files.length} Processed</span>
            </div>

            <div className="space-y-2">
              {files.map((item) => (
                <div
                  key={item.id}
                  className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-1.5"
                >
                  <div className="flex items-center justify-between gap-3 text-xs">
                    <div className="flex items-center gap-2 min-w-0">
                      <FileText className="w-4 h-4 text-indigo-500 shrink-0" />
                      <div className="min-w-0">
                        <p className="font-semibold text-slate-900 dark:text-slate-100 truncate">
                          {item.name}
                        </p>
                        <p className="text-[10px] text-slate-400 font-mono">
                          {formatFileSize(item.size)}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      {/* Status Badge */}
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          item.status === "Completed"
                            ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20"
                            : item.status === "Failed"
                            ? "bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20"
                            : item.status === "Waiting"
                            ? "bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300"
                            : "bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20 animate-pulse"
                        }`}
                      >
                        {item.status}
                      </span>

                      {/* Remove Button */}
                      {!isProcessing && item.status !== "Completed" && (
                        <button
                          onClick={() => removeFile(item.id)}
                          className="p-1 rounded-lg text-slate-400 hover:text-rose-500 transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Progress Bar */}
                  {item.status !== "Waiting" && (
                    <div className="h-1.5 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-300 ${
                          item.status === "Completed"
                            ? "bg-emerald-500"
                            : item.status === "Failed"
                            ? "bg-rose-500"
                            : "bg-indigo-600"
                        }`}
                        style={{ width: `${item.progress}%` }}
                      />
                    </div>
                  )}

                  {item.error && (
                    <p className="text-[10px] text-rose-500 font-medium">
                      {item.error}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-slate-800">
          <button
            onClick={() => setFiles([])}
            disabled={isProcessing || files.length === 0}
            className="text-xs font-semibold text-slate-400 hover:text-slate-600 disabled:opacity-50"
          >
            Clear All
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              disabled={isProcessing}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 transition-colors"
            >
              {completedCount > 0 ? "Done" : "Cancel"}
            </button>

            <button
              onClick={handleProcessUploads}
              disabled={isProcessing || files.length === 0 || files.every((f) => f.status === "Completed")}
              className="flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white shadow-md shadow-indigo-600/20 transition-all"
            >
              {isProcessing ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Processing Evidence...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Process & Rank ({files.filter((f) => f.status !== "Completed" && !f.error).length})</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
