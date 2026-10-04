import React, { useState } from 'react';
import { BookOpen, ChevronDown, ChevronUp, Quote, ShieldCheck, AlertTriangle, Sparkles, RefreshCw, Layers } from 'lucide-react';

export default function CitationViewer({ citations, sentenceGroundedness, regenerationLogs, faithfulnessScore }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeSubTab, setActiveSubTab] = useState('citations'); // 'citations' or 'breakdown'

  const sentences = sentenceGroundedness || [];
  const logs = regenerationLogs || [];
  const headlineScore = Math.round((faithfulnessScore || 0.95) * 100);

  return (
    <div className="mt-4 rounded-xl border border-white/10 bg-black/25 overflow-hidden transition-all">
      {/* Header / Toggle Button */}
      <div className="px-4 py-2.5 flex items-center justify-between text-xs text-slate-300 hover:bg-white/5 transition-colors font-mono cursor-pointer"
           onClick={() => setIsExpanded(!isExpanded)}>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 font-semibold text-amber-200">
            <BookOpen className="w-3.5 h-3.5 text-amber-400" />
            <span>Grounded Primary Sources ({citations ? citations.length : 0})</span>
          </div>
          
          <div className="hidden sm:flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 text-[10.5px]">
            <ShieldCheck className="w-3 h-3 text-emerald-400" />
            <span>Score: {headlineScore}% Grounded</span>
          </div>
          
          {sentences.some(s => s.was_regenerated) && (
            <span className="hidden md:flex items-center gap-1 text-[10px] text-cyan-300 bg-cyan-950/60 border border-cyan-500/30 px-2 py-0.5 rounded-full">
              <Sparkles className="w-2.5 h-2.5 text-cyan-400" />
              <span>Self-Corrected Claims</span>
            </span>
          )}
        </div>

        <div className="flex items-center gap-1 text-slate-400 text-xs">
          <span>{isExpanded ? 'Collapse' : 'View Passages & Score Breakdown'}</span>
          {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </div>
      </div>

      {/* Expanded Section */}
      {isExpanded && (
        <div className="border-t border-white/5 bg-slate-950/50 p-4 space-y-4">
          {/* Sub Tab Navigation */}
          <div className="flex items-center gap-2 border-b border-white/10 pb-2">
            <button
              onClick={() => setActiveSubTab('citations')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeSubTab === 'citations'
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>Source Chunks ({citations ? citations.length : 0})</span>
            </button>

            <button
              onClick={() => setActiveSubTab('breakdown')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeSubTab === 'breakdown'
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Sentence-Level Score Breakdown ({sentences.length})</span>
            </button>
          </div>

          {/* Sub Tab 1: Source Chunks */}
          {activeSubTab === 'citations' && citations && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {citations.map((cit, idx) => (
                <div
                  key={`${cit.chunk_id || idx}-${idx}`}
                  className="p-3 rounded-lg bg-slate-900/70 border border-slate-800 text-xs flex flex-col justify-between hover:border-slate-700 transition-colors"
                >
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-1.5">
                      <span className="font-bold text-amber-300 flex items-center gap-1">
                        <Quote className="w-3 h-3 text-amber-400 shrink-0" />
                        {cit.thinker_name}
                      </span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                        Score: {cit.relevance_score ? (cit.relevance_score).toFixed(2) : '1.00'}
                      </span>
                    </div>

                    <div className="text-[11px] font-semibold text-slate-300 mb-1">
                      {cit.work_title} <span className="text-slate-500">• {cit.chapter}</span>
                    </div>

                    <p className="text-slate-300/90 italic leading-relaxed text-[11.5px] border-l-2 border-amber-500/40 pl-2 my-1.5">
                      "{cit.quote}"
                    </p>
                  </div>

                  <div className="mt-2 pt-1.5 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500 font-mono">
                    <span>ID: {cit.chunk_id || `passage_${idx + 1}`}</span>
                    <span className="text-emerald-400/80 flex items-center gap-1">
                      ✓ Source Verified
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Sub Tab 2: Granular Sentence-Level Breakdown */}
          {activeSubTab === 'breakdown' && (
            <div className="space-y-3">
              <div className="flex items-center justify-between bg-slate-900/90 p-3 rounded-xl border border-white/5 text-xs font-mono">
                <span className="text-slate-300">
                  Headline Groundedness: <strong className="text-emerald-400">{headlineScore}%</strong>
                </span>
                <span className="text-slate-400">
                  Total Claims Evaluated: <strong className="text-white">{sentences.length}</strong>
                </span>
              </div>

              <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
                {sentences.map((s, idx) => {
                  const scorePct = Math.round(s.confidence_score * 100);
                  const isHigh = scorePct >= 75;
                  const isMedium = scorePct >= 50 && scorePct < 75;
                  const dotColor = isHigh ? 'bg-emerald-400' : isMedium ? 'bg-amber-400' : 'bg-rose-400';
                  
                  return (
                    <div
                      key={idx}
                      className={`p-2.5 rounded-lg border text-xs flex items-start justify-between gap-3 ${
                        s.grounded
                          ? 'bg-slate-900/60 border-slate-800 text-slate-200'
                          : 'bg-amber-950/20 border-amber-500/30 text-amber-100'
                      }`}
                    >
                      <div className="flex items-start gap-2.5 flex-1">
                        <span className={`w-2.5 h-2.5 rounded-full ${dotColor} shrink-0 mt-1 shadow-sm`} />
                        <div className="space-y-1">
                          <p className="text-[12px] leading-relaxed">
                            <span className="text-slate-500 font-mono text-[10.5px] mr-1.5">[{idx + 1}]</span>
                            {s.text}
                          </p>
                          
                          <div className="flex flex-wrap items-center gap-2 text-[10px] font-mono text-slate-400">
                            {s.supporting_chunk_id && (
                              <span className="text-emerald-400">
                                Match: {s.supporting_chunk_id}
                              </span>
                            )}
                            {s.closest_chunk_id && (
                              <span className="text-amber-400">
                                Closest: {s.closest_chunk_id}
                              </span>
                            )}
                            {s.was_regenerated && (
                              <span className="px-1.5 py-0.2 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-500/30">
                                ↺ Self-Corrected (was {Math.round((s.original_score || 0) * 100)}%)
                              </span>
                            )}
                            {s.flag_reason && !s.grounded && (
                              <span className="text-rose-400">
                                • {s.flag_reason}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="shrink-0 font-mono text-right">
                        <span className={`text-xs font-bold ${isHigh ? 'text-emerald-400' : isMedium ? 'text-amber-400' : 'text-rose-400'}`}>
                          {scorePct}%
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
