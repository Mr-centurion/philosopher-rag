import React from 'react';
import { BookOpen, Activity, PlusCircle, Sparkles, Moon, Sun } from 'lucide-react';

export default function Header({ isOnline, onOpenEval, onToggleSidebar, onNewChat, isDarkMode, onToggleTheme }) {
  return (
    <header className="sticky top-0 z-30 w-full bg-[#FAF7F0] border-b border-[#B8995C]/40 px-4 lg:px-8 py-3 flex items-center justify-between shadow-parchment-sm">
      {/* Left: Brand / Title */}
      <div className="flex items-center gap-3.5">
        {/* Classical Philosopher Emblem / Seal */}
        <div className="w-10 h-10 rounded-full bg-[#F4EFE6] border-2 border-[#B8995C] flex items-center justify-center shadow-inner-gold text-lg shrink-0">
          <span className="transform -translate-y-0.5">🏛️</span>
        </div>
        <div>
          <h1 className="text-lg lg:text-xl font-bold tracking-tight text-[#2B2419] flex items-center gap-2 font-philosophy">
            <span className="tracking-wide">PHILOSOPHERMIND</span>
            <span className="eyebrow-maroon text-[9.5px] px-2 py-0.5 rounded-full border border-[#B8995C]/50 bg-[#F4EFE6]">
              Classic RAG
            </span>
          </h1>
          <p className="text-[11.5px] text-[#73624A] font-serif italic hidden sm:block">
            Dialectical Multi-Thinker Engine • Primary Sources • Citation Guardrails
          </p>
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2 sm:gap-2.5">
        {/* System Health Status */}
        <div className="hidden md:flex items-center gap-2 px-2.5 py-1.5 rounded-md bg-[#F4EFE6] border border-[#B8995C]/30 text-xs">
          <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-600 animate-pulse' : 'bg-rose-600'}`} />
          <span className="text-[#564936] font-serif text-[11px] font-medium">
            {isOnline ? 'Corpus Online' : 'Backend Offline'}
          </span>
        </div>

        {/* Evaluation Benchmark Modal Trigger */}
        <button
          onClick={onOpenEval}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-[#FAF7F0] hover:bg-[#EFE8DD] border border-[#B8995C]/60 text-[#8B2E2E] text-xs font-serif font-semibold tracking-wide transition-all shadow-sm"
          title="Run automated benchmark evaluation suite"
        >
          <Activity className="w-3.5 h-3.5 text-[#8B2E2E]" />
          <span>Eval Suite</span>
        </button>

        {/* Thinker Sidebar Toggle */}
        <button
          onClick={onToggleSidebar}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-[#FAF7F0] hover:bg-[#EFE8DD] border border-[#B8995C]/60 text-[#564936] text-xs font-serif font-semibold tracking-wide transition-all shadow-sm"
          title="View available philosophers and corpus statistics"
        >
          <BookOpen className="w-3.5 h-3.5 text-[#92763A]" />
          <span className="hidden sm:inline">Corpus Stats</span>
        </button>

        {/* New Session Button - Classic Deep Brown with Gold Border */}
        <button
          onClick={onNewChat}
          className="btn-ink flex items-center gap-1.5 px-3.5 py-1.5 rounded-md text-xs font-serif font-semibold tracking-wide shadow-sm"
        >
          <PlusCircle className="w-3.5 h-3.5 text-[#DEC695]" />
          <span>New Query</span>
        </button>

        {/* Theme Toggle (Parchment vs Dark) */}
        {onToggleTheme && (
          <button
            onClick={onToggleTheme}
            className="p-1.5 rounded-md border border-[#B8995C]/40 text-[#564936] hover:bg-[#EFE8DD] transition-all"
            title={isDarkMode ? 'Switch to Vintage Parchment Theme' : 'Switch to Dark Mode'}
          >
            {isDarkMode ? <Sun className="w-3.5 h-3.5 text-[#B8995C]" /> : <Moon className="w-3.5 h-3.5 text-[#73624A]" />}
          </button>
        )}
      </div>
    </header>
  );
}
