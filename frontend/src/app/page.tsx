"use client";

import { useEffect, useState } from "react";
import { 
  Play, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  Mail,
  RefreshCw,
  LayoutDashboard,
  ExternalLink,
  ChevronRight,
  ArrowRight
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8001";

interface Status {
  state: "idle" | "running" | "failed";
  last_run_timestamp: string | null;
  last_run_status: string | null;
  error: string | null;
}

interface Report {
  markdown: string;
  trends: Record<string, { current_pct: number; previous_pct: number; change: number; direction: string }>;
  impact: [string, number][];
  generated_at: string | null;
}

export default function Dashboard() {
  const [status, setStatus] = useState<Status | null>(null);
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [targetEmail, setTargetEmail] = useState("");
  const [triggering, setTriggering] = useState(false);
  const [sendingEmail, setSendingEmail] = useState(false);

  const fetchData = async () => {
    try {
      const [statusRes, reportRes] = await Promise.all([
        fetch(`${BACKEND_URL}/status`),
        fetch(`${BACKEND_URL}/report`)
      ]);
      if (statusRes.ok) setStatus(await statusRes.json());
      if (reportRes.ok) setReport(await reportRes.json());
    } catch (error) {
      console.error("Fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (status?.state === "running") {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`${BACKEND_URL}/status`);
          const data = await res.json();
          setStatus(data);
          if (data.state === "idle") {
            const rRes = await fetch(`${BACKEND_URL}/report`);
            if (rRes.ok) setReport(await rRes.json());
          }
        } catch (e) {}
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [status?.state]);

  const triggerPipeline = async () => {
    setTriggering(true);
    try {
      const res = await fetch(`${BACKEND_URL}/run`, { method: "POST" });
      if (res.ok) setStatus(prev => prev ? { ...prev, state: "running" } : null);
    } catch (e) {
      alert("Trigger failed.");
    } finally {
      setTriggering(false);
    }
  };

  const sendEmailToTarget = async () => {
    if (!targetEmail || !targetEmail.includes("@")) {
      alert("Please enter a valid email address.");
      return;
    }
    setSendingEmail(true);
    try {
      const res = await fetch(`${BACKEND_URL}/send-email`, { 
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ recipient: targetEmail })
      });
      if (res.ok) alert(`Report dispatched to ${targetEmail}`);
      else alert("Email delivery failed.");
    } catch (e) {
      alert("Communication error.");
    } finally {
      setSendingEmail(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-950">
        <Loader2 className="h-10 w-10 animate-spin text-indigo-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] text-zinc-200 font-sans">
      {/* Dynamic Header */}
      <header className="border-b border-white/5 bg-zinc-950/20 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
             <div className="w-10 h-10 bg-gradient-to-tr from-indigo-600 to-violet-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
                <LayoutDashboard className="h-5 w-5 text-white" />
             </div>
             <div>
               <h1 className="text-lg font-bold tracking-tight text-white">INDMoney Pulse</h1>
               <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-bold">Automated Weekly Intelligence</p>
             </div>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-900/50 border border-white/5">
              <div className={cn(
                "h-1.5 w-1.5 rounded-full",
                status?.state === "running" ? "bg-yellow-400 animate-pulse" : 
                status?.state === "failed" ? "bg-red-500" : "bg-emerald-500 shadow-[0_0_8px_#10b981]"
              )} />
              <span className="text-[11px] font-bold uppercase tracking-wider text-zinc-400">System {status?.state}</span>
            </div>
            
            <button
              onClick={triggerPipeline}
              disabled={status?.state === "running" || triggering}
              className="px-5 py-2.5 rounded-xl bg-white text-black font-bold text-sm transition-all hover:bg-zinc-200 active:scale-95 disabled:opacity-50 flex items-center gap-2 group"
            >
              {status?.state === "running" ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-3.5 w-3.5 fill-black group-hover:scale-110 transition-transform" />}
              {status?.state === "running" ? "Processing..." : "Run Analysis"}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          
          {/* Main Feed */}
          <div className="lg:col-span-8 space-y-12">
            
            {/* Top Critical Cards */}
            <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {report?.impact.slice(0, 3).map(([theme, score]) => (
                <div key={theme} className="p-5 rounded-2xl bg-zinc-900/30 border border-white/5 hover:border-indigo-500/20 transition-colors group">
                   <div className="flex justify-between items-start mb-4">
                      <span className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider">{theme}</span>
                      <div className="p-1 px-2 rounded bg-indigo-500/10 text-indigo-400 text-[10px] font-black italic">
                        IMPACT: {score}
                      </div>
                   </div>
                   <div className="flex items-end justify-between">
                     <span className="text-3xl font-bold text-white tabular-nums">{report.trends[theme]?.current_pct || 0}%</span>
                     <div className={cn(
                       "flex items-center text-xs font-bold",
                       report.trends[theme]?.direction === "up" ? "text-red-400" : "text-emerald-400"
                     )}>
                       {report.trends[theme]?.direction === "up" ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                       {Math.abs(report.trends[theme]?.change || 0)}%
                     </div>
                   </div>
                </div>
              ))}
            </section>

            {/* Markdown Viewer */}
            <article className="bg-[#0c0c0c] border border-white/5 rounded-3xl overflow-hidden shadow-2xl">
               <div className="px-8 py-6 border-b border-white/5 bg-zinc-900/10 flex items-center justify-between">
                 <h2 className="text-sm font-bold uppercase tracking-tighter flex items-center gap-3">
                   <div className="w-2 h-2 rounded-full bg-indigo-500" />
                   Latest Pulse Intelligence
                 </h2>
                 <span className="text-[10px] text-zinc-500 font-mono">ID: {report?.generated_at?.split('T')[1].slice(0,5) || '00:00'}</span>
               </div>
               <div className="p-10 prose prose-invert prose-p:text-zinc-400 prose-p:leading-relaxed prose-headings:text-white prose-strong:text-indigo-300 max-w-none">
                 {report ? (
                   <ReactMarkdown>{report.markdown}</ReactMarkdown>
                 ) : (
                   <div className="py-20 flex flex-col items-center justify-center opacity-30 select-none">
                     <Loader2 className="h-8 w-8 animate-spin mb-4" />
                     <p className="text-sm font-medium">Synchronizing with theme engine...</p>
                   </div>
                 )}
               </div>
            </article>
          </div>

          {/* Sidebar */}
          <aside className="lg:col-span-4 space-y-8">
            
            {/* Email Dispatcher */}
            <div className="p-8 rounded-3xl bg-zinc-900/40 border border-white/5 shadow-xl relative overflow-hidden group">
               <div className="absolute -right-4 -top-4 opacity-5 group-hover:rotate-12 transition-transform duration-700">
                  <Mail className="w-24 h-24" />
               </div>
               <h3 className="text-lg font-bold text-white mb-2">Share Analysis</h3>
               <p className="text-xs text-zinc-500 mb-6 leading-relaxed">Instantly deliver the full intelligence report to any executive email address.</p>
               
               <div className="space-y-3">
                 <div className="relative">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-600" />
                    <input 
                      type="email" 
                      placeholder="Enter recipeint email" 
                      value={targetEmail}
                      onChange={(e) => setTargetEmail(e.target.value)}
                      className="w-full bg-black border border-white/10 rounded-xl py-3 pl-11 pr-4 text-sm focus:border-indigo-500 outline-none transition-all placeholder:text-zinc-700"
                    />
                 </div>
                 <button 
                  onClick={sendEmailToTarget}
                  disabled={sendingEmail || !targetEmail}
                  className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-zinc-800 disabled:text-zinc-600 font-bold py-3 rounded-xl transition-all flex items-center justify-center gap-2 group"
                 >
                   {sendingEmail ? <RefreshCw className="h-4 w-4 animate-spin" /> : <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" /> }
                   {sendingEmail ? "Dispatching..." : "Send Intelligence"}
                 </button>
               </div>
            </div>

            {/* Trend Summary */}
            <div className="p-8 rounded-3xl border border-white/5 bg-zinc-950/40 space-y-6">
              <h3 className="text-[11px] font-black uppercase tracking-[0.2em] text-zinc-500">Longitudinal Trends</h3>
              <div className="space-y-4">
                {Object.entries(report?.trends || {}).map(([theme, info]) => (
                  <div key={theme} className="flex items-center justify-between group">
                    <div>
                      <div className="text-sm font-semibold text-zinc-300 group-hover:text-white transition-colors">{theme}</div>
                      <div className="text-[10px] text-zinc-600 font-medium">PREV: {info.previous_pct}%</div>
                    </div>
                    <div className={cn(
                      "flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[10px] font-black",
                      info.direction === "up" ? "bg-red-500/10 text-red-400" : 
                      info.direction === "down" ? "bg-emerald-500/10 text-emerald-400" : "bg-white/5 text-zinc-500"
                    )}>
                      {info.direction === "up" && <TrendingUp className="h-3 w-3" />}
                      {info.direction === "down" && <TrendingDown className="h-3 w-3" />}
                      {info.direction === "stable" && <Minus className="h-3 w-3" />}
                      {Math.abs(info.change)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Footer Meta */}
            <div className="flex items-center gap-4 text-zinc-600">
               <div className="flex-1 border-t border-white/5" />
               <a href="#" className="text-[10px] font-bold hover:text-indigo-400 transition-colors uppercase tracking-[0.1em]">Public API Docs</a>
               <div className="flex-1 border-t border-white/5" />
            </div>

          </aside>
        </div>
      </main>
    </div>
  );
}
