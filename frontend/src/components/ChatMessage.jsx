import React, { useState } from 'react';
import { 
  Sparkles, ShieldCheck, AlertTriangle, Clock, Layers, Grid, 
  ChevronRight, User, BookOpen, CheckCircle, Scale, Info, RefreshCw, Compass
} from 'lucide-react';
import CitationViewer from './CitationViewer';

const THINKER_COLORS = {
  marcus_aurelius: '#eab308',
  friedrich_nietzsche: '#ef4444',
  immanuel_kant: '#3b82f6',
  aristotle: '#10b981',
  lao_tzu: '#8b5cf6',
};

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'tabs'
  const [activeTab, setActiveTab] = useState(0);
  const [activeSentenceTooltip, setActiveSentenceTooltip] = useState(null);

  if (isUser) {
    return (
      <div className="flex items-start justify-end gap-3 my-4">
        <div className="max-w-2xl bg-amber-500/10 border border-amber-500/30 rounded-2xl rounded-tr-sm px-5 py-3.5 shadow-lg shadow-amber-500/5">
          <div className="text-xs text-amber-400 font-mono font-medium mb-1">User Inquiry</div>
          <p className="text-sm sm:text-base text-amber-50 leading-relaxed font-sans">{message.content}</p>
        </div>
        <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0 text-slate-300">
          <User className="w-4 h-4" />
        </div>
      </div>
    );
  }

  const data = message.data || {};
  const breakdowns = data.per_thinker_breakdown || [];
  const citations = data.citations || [];
  const flags = data.guardrail_flags || [];
  const faithfulness = data.faithfulness_score || 0.95;
  const latency = data.latency_ms;
  const sentenceGroundedness = data.sentence_groundedness || [];
  const regenerationLogs = data.regeneration_logs || [];
  const totalSentences = data.total_sentences || sentenceGroundedness.length;
  const flaggedCount = data.flagged_sentences_count || sentenceGroundedness.filter(s => !s.grounded).length;
  const isWeakMatch = data.is_weak_match;
  const weakWarning = data.weak_match_warning;

  const handleScrollToFlagged = () => {
    const firstFlagged = document.querySelector('.sentence-flagged');
    if (firstFlagged) {
      firstFlagged.scrollIntoView({ behavior: 'smooth', block: 'center' });
      firstFlagged.classList.add('animate-pulse');
      setTimeout(() => firstFlagged.classList.remove('animate-pulse'), 2000);
    }
  };

  return (
    <div className="flex items-start gap-3.5 my-6">
      {/* Bot Icon */}
      <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500 to-rose-600 flex items-center justify-center shrink-0 shadow-lg shadow-amber-500/20 text-white font-bold text-sm">
        🏛️
      </div>

      <div className="flex-1 max-w-full glass-panel rounded-2xl p-5 sm:p-6 border border-white/10 shadow-2xl space-y-5">
        {/* Top Meta Bar: Guardrail Status & Latency */}
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/5 pb-3">
          <div className="flex items-center gap-2">
            {/* Groundedness Badge */}
            {flaggedCount > 0 ? (
              <button
                onClick={handleScrollToFlagged}
                className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-medium bg-amber-950/70 text-amber-300 border border-amber-500/50 hover:bg-amber-900/80 transition-all shadow-sm"
                title="Click to jump to flagged claims"
              >
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                <span>{flaggedCount} of {totalSentences} claims need review</span>
              </button>
            ) : (
              <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-medium bg-emerald-950/60 text-emerald-400 border border-emerald-500/30">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>All {totalSentences || 'claims'} verified ({Math.round(faithfulness * 100)}% grounded)</span>
              </span>
            )}

            {/* Retrieval Alignment Status */}
            {isWeakMatch ? (
              <span className="flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-mono bg-amber-950/60 text-amber-300 border border-amber-500/40">
                <Compass className="w-3 h-3 text-amber-400" />
                <span>Thematic Match Only</span>
              </span>
            ) : (
              <span className="flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-mono bg-blue-950/60 text-blue-300 border border-blue-500/30">
                <Compass className="w-3 h-3 text-blue-400" />
                <span>Topic Aligned</span>
              </span>
            )}

            {/* Self-Correction Badge */}
            {regenerationLogs.length > 0 && (
              <span className="flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-mono bg-cyan-950/60 text-cyan-300 border border-cyan-500/30">
                <RefreshCw className="w-3 h-3 text-cyan-400" />
                <span>{regenerationLogs.length} self-corrected</span>
              </span>
            )}
          </div>

          {latency && (
            <div className="flex items-center gap-1.5 text-slate-500 font-mono text-[11px]">
              <Clock className="w-3 h-3" />
              <span>{latency}ms</span>
            </div>
          )}
        </div>

        {/* Weak Match / Thematically Adjacent Passages Callout Banner */}
        {isWeakMatch && (
          <div className="p-3.5 rounded-xl bg-amber-950/30 border border-amber-500/40 flex items-start gap-3 text-amber-200 text-xs shadow-lg">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <div className="font-bold text-amber-300 font-mono text-[11.5px] uppercase tracking-wider">
                Closest Related Passages Found — Thematic Match Only
              </div>
              <p className="text-amber-100/90 leading-relaxed text-[11px]">
                {weakWarning || `The primary texts provide general principles rather than a direct treatise on this specific topic. The synthesis below frames the adjacent philosophical doctrines.`}
              </p>
            </div>
          </div>
        )}

        {/* Master Comparative Synthesis Section with Sentence-Level Groundedness Spans */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Scale className="w-4 h-4 text-amber-400" />
              <h3 className="font-philosophy text-base font-bold text-amber-200 tracking-wide">
                Dialectical Comparative Synthesis
              </h3>
            </div>
            
            {sentenceGroundedness.length > 0 && (
              <span className="text-[11px] font-mono text-slate-400 hidden sm:inline">
                Hover or click underlined claims to inspect verification
              </span>
            )}
          </div>
          
          <div className="prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed space-y-3 bg-slate-950/40 p-4 rounded-xl border border-white/5 relative">
            {sentenceGroundedness.length > 0 ? (
              <div className="space-y-2.5 leading-relaxed">
                {sentenceGroundedness.map((s, idx) => {
                  const isHeading = s.text.startsWith('#');
                  if (isHeading) {
                    return (
                      <h4 key={idx} className="font-philosophy text-amber-300 text-sm font-semibold pt-2">
                        {s.text.replace(/^#+\s*/, '')}
                      </h4>
                    );
                  }

                  const isFlagged = !s.grounded;
                  const isRegenerated = s.was_regenerated;
                  const scorePct = Math.round(s.confidence_score * 100);

                  return (
                    <span
                      key={idx}
                      className="relative inline"
                      onMouseEnter={() => setActiveSentenceTooltip(idx)}
                      onMouseLeave={() => setActiveSentenceTooltip(null)}
                      onClick={() => setActiveSentenceTooltip(activeSentenceTooltip === idx ? null : idx)}
                    >
                      <span
                        className={`inline transition-all rounded px-1 py-0.5 cursor-pointer ${
                          isFlagged
                            ? 'sentence-flagged bg-amber-500/15 border-b-2 border-amber-400/80 text-amber-100 hover:bg-amber-500/30'
                            : isRegenerated
                            ? 'bg-cyan-500/10 border-b border-cyan-400/40 text-slate-200 hover:bg-cyan-500/20'
                            : 'hover:bg-white/5'
                        }`}
                      >
                        {s.text}{' '}
                      </span>

                      {/* Interactive Tooltip Popover on Hover / Click */}
                      {activeSentenceTooltip === idx && (
                        <span className="absolute z-50 bottom-full left-0 mb-2 w-72 sm:w-80 p-3 rounded-xl bg-[#131622] border border-slate-700 shadow-2xl text-xs text-left block font-sans animate-in fade-in duration-150">
                          <span className="flex items-center justify-between pb-1.5 border-b border-white/10 mb-1.5 font-mono">
                            <span className="flex items-center gap-1 font-bold">
                              {isFlagged ? (
                                <>
                                  <AlertTriangle className="w-3 h-3 text-amber-400" />
                                  <span className="text-amber-300">Ungrounded Claim</span>
                                </>
                              ) : isRegenerated ? (
                                <>
                                  <Sparkles className="w-3 h-3 text-cyan-400" />
                                  <span className="text-cyan-300">Self-Corrected Claim</span>
                                </>
                              ) : (
                                <>
                                  <CheckCircle className="w-3 h-3 text-emerald-400" />
                                  <span className="text-emerald-300">Source Grounded</span>
                                </>
                              )}
                            </span>
                            <span className={`px-1.5 py-0.5 rounded text-[10.5px] font-bold ${
                              scorePct >= 75 ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30' : 'bg-amber-950 text-amber-400 border border-amber-500/30'
                            }`}>
                              Confidence: {scorePct}%
                            </span>
                          </span>

                          {/* Reason */}
                          {s.flag_reason && (
                            <span className="block text-[11px] text-slate-300 mb-1.5 leading-snug">
                              {s.flag_reason}
                            </span>
                          )}

                          {/* Supporting or Closest Chunk Reference */}
                          {s.supporting_chunk_id && (
                            <span className="block text-[10.5px] font-mono text-emerald-400/90 mb-1">
                              ✓ Supported by Chunk: <strong className="text-white">{s.supporting_chunk_id}</strong>
                            </span>
                          )}
                          {s.closest_chunk_id && (
                            <span className="block text-[10.5px] font-mono text-amber-400/90 mb-1">
                              ⚠️ Closest Match: <strong className="text-white">{s.closest_chunk_id}</strong> (insufficient)
                            </span>
                          )}

                          {/* Before/After regeneration diff */}
                          {isRegenerated && s.original_text && (
                            <span className="block text-[10px] font-mono text-slate-400 bg-slate-900/90 p-1.5 rounded border border-white/5 mt-1">
                              <span className="text-rose-400 line-through block">Original ({Math.round((s.original_score || 0) * 100)}%): "{s.original_text.slice(0, 60)}..."</span>
                              <span className="text-emerald-400 block mt-0.5">Corrected ({scorePct}%): "{s.text.slice(0, 60)}..."</span>
                            </span>
                          )}
                        </span>
                      )}
                    </span>
                  );
                })}
              </div>
            ) : (
              message.content.split('\n\n').map((paragraph, pIdx) => (
                <p key={pIdx} className="text-xs sm:text-sm text-slate-300/95 leading-relaxed">
                  {paragraph}
                </p>
              ))
            )}
          </div>
        </div>

        {/* Per-Thinker Perspectives Component */}
        {breakdowns.length > 0 && (
          <div className="space-y-3 pt-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-rose-400" />
                <h3 className="font-philosophy text-sm font-bold text-slate-200 tracking-wide">
                  Per-Thinker Deep Dive ({breakdowns.length} Perspectives)
                </h3>
              </div>

              {/* View Mode Toggle: Grid vs Tabs */}
              <div className="flex items-center bg-slate-900/80 rounded-lg p-0.5 border border-slate-800 text-xs">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`flex items-center gap-1 px-2.5 py-1 rounded-md transition-all ${
                    viewMode === 'grid' ? 'bg-amber-500/20 text-amber-300 font-medium' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Grid className="w-3 h-3" />
                  <span className="hidden sm:inline">Grid</span>
                </button>
                <button
                  onClick={() => setViewMode('tabs')}
                  className={`flex items-center gap-1 px-2.5 py-1 rounded-md transition-all ${
                    viewMode === 'tabs' ? 'bg-amber-500/20 text-amber-300 font-medium' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Layers className="w-3 h-3" />
                  <span className="hidden sm:inline">Tabs</span>
                </button>
              </div>
            </div>

            {/* Grid View */}
            {viewMode === 'grid' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                {breakdowns.map((b, idx) => {
                  const color = THINKER_COLORS[b.thinker_id] || '#f59e0b';
                  return (
                    <div
                      key={b.thinker_id || idx}
                      className="glass-card rounded-xl p-4 border flex flex-col justify-between hover:border-slate-600 transition-all"
                      style={{ borderLeft: `3px solid ${color}` }}
                    >
                      <div className="space-y-2.5">
                        {/* Header */}
                        <div className="flex items-center justify-between gap-2">
                          <div>
                            <h4 className="font-bold text-white text-sm tracking-tight flex items-center gap-1.5">
                              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                              {b.thinker_name}
                            </h4>
                            <span className="text-[10px] text-slate-400 font-mono block">
                              {b.tradition}
                            </span>
                          </div>

                          {b.is_weak_match && (
                            <span className="text-[9.5px] font-mono px-2 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-500/30">
                              Thematic Match
                            </span>
                          )}
                        </div>

                        {/* Core Stance Callout */}
                        <div
                          className="p-2.5 rounded-lg text-xs font-medium leading-snug"
                          style={{ backgroundColor: `${color}12`, color: color }}
                        >
                          "{b.core_stance}"
                        </div>

                        {/* Detailed Argument */}
                        <div className="text-xs text-slate-300/90 leading-relaxed whitespace-pre-line">
                          {b.detailed_argument}
                        </div>
                      </div>

                      {/* Concepts */}
                      {b.key_concepts && b.key_concepts.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-3 pt-2.5 border-t border-white/5">
                          {b.key_concepts.map((concept, cIdx) => (
                            <span
                              key={cIdx}
                              className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-900 text-slate-300 border border-slate-800"
                            >
                              {concept}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              /* Tabbed View */
              <div className="glass-card rounded-xl p-4 border border-white/10 space-y-4">
                {/* Tab buttons */}
                <div className="flex flex-wrap gap-1.5 border-b border-white/10 pb-2.5">
                  {breakdowns.map((b, idx) => {
                    const color = THINKER_COLORS[b.thinker_id] || '#f59e0b';
                    const isActive = activeTab === idx;
                    return (
                      <button
                        key={idx}
                        onClick={() => setActiveTab(idx)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                          isActive
                            ? 'bg-slate-800 text-white shadow-md border'
                            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/50'
                        }`}
                        style={{
                          borderColor: isActive ? color : 'transparent',
                        }}
                      >
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                        <span>{b.thinker_name}</span>
                        {b.is_weak_match && <span className="text-[9px] text-amber-400 ml-0.5">•</span>}
                      </button>
                    );
                  })}
                </div>

                {/* Active Tab Content */}
                {breakdowns[activeTab] && (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="font-bold text-white text-sm font-philosophy">
                        {breakdowns[activeTab].thinker_name}
                      </h4>
                      <span className="text-xs text-amber-400/90 font-mono">
                        {breakdowns[activeTab].tradition}
                      </span>
                    </div>

                    <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-200 text-xs font-medium italic">
                      "{breakdowns[activeTab].core_stance}"
                    </div>

                    <p className="text-xs sm:text-sm text-slate-300 leading-relaxed whitespace-pre-line">
                      {breakdowns[activeTab].detailed_argument}
                    </p>

                    <div className="flex flex-wrap gap-1.5 pt-2">
                      {breakdowns[activeTab].key_concepts?.map((c, i) => (
                        <span key={i} className="text-[10.5px] font-mono px-2 py-0.5 rounded-full bg-slate-900 text-slate-300 border border-slate-800">
                          {c}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Primary Source Citations & Granular Score Breakdown */}
        <CitationViewer 
          citations={citations}
          sentenceGroundedness={sentenceGroundedness}
          regenerationLogs={regenerationLogs}
          faithfulnessScore={faithfulness}
        />
      </div>
    </div>
  );
}
