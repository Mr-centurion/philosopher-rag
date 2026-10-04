import React from 'react';
import { BookOpen, Activity, PlayCircle, PlusCircle, Sparkles } from 'lucide-react';

export default function Header({ isOnline, onOpenEval, onToggleSidebar, onNewChat }) {
  return (
    <header className="sticky top-0 z-30 w-full glass-panel border-b border-white/10 px-4 lg:px-8 py-3.5 flex items-center justify-between">
      {/* Left: Brand / Title */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-rose-500 flex items-center justify-center shadow-lg shadow-amber-500/20 text-white font-bold text-xl">
          🏛️
        </div>
        <div>
          <h1 className="text-lg lg:text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <span className="gradient-gold font-philosophy font-bold">PHILOSOPHY RAG</span>
            <span className="text-[10px] uppercase px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-mono tracking-wider font-semibold border border-amber-500/30">
              Multi-Thinker v1.0
            </span>
          </h1>
          <p className="text-xs text-slate-400 hidden sm:block">
            LangGraph Dialectical Engine • Hybrid BM25 & Vector Retrieval • Citation Guardrails
          </p>
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2.5">
        {/* System Health Status */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/60 border border-slate-800 text-xs">
          <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-400 animate-pulse shadow-emerald-400/50' : 'bg-rose-400'}`} />
          <span className="text-slate-300 font-mono text-[11px]">
            {isOnline ? 'System Healthy' : 'Backend Offline'}
          </span>
        </div>

        {/* Evaluation Benchmark Modal Trigger */}
        <button
          onClick={onOpenEval}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-950/60 hover:bg-indigo-900/80 border border-indigo-500/30 text-indigo-300 text-xs font-medium transition-all shadow-sm"
          title="Run automated benchmark evaluation suite"
        >
          <Activity className="w-3.5 h-3.5 text-indigo-400" />
          <span>Eval Suite</span>
        </button>

        {/* Thinker Sidebar Toggle */}
        <button
          onClick={onToggleSidebar}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/60 hover:bg-slate-700/80 border border-slate-700 text-slate-200 text-xs font-medium transition-all"
          title="View available philosophers and corpus statistics"
        >
          <BookOpen className="w-3.5 h-3.5 text-amber-400" />
          <span className="hidden sm:inline">Corpus Stats</span>
        </button>

        {/* New Session */}
        <button
          onClick={onNewChat}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 text-xs font-medium transition-all"
        >
          <PlusCircle className="w-3.5 h-3.5 text-amber-400" />
          <span>New Query</span>
        </button>
      </div>
    </header>
  );
}
