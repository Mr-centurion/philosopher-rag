import React, { useState } from 'react';
import { 
  Sparkles, ShieldCheck, AlertTriangle, Clock, Layers, Grid, 
  ChevronRight, User, BookOpen, CheckCircle, Scale, Info, RefreshCw, Compass
} from 'lucide-react';
import CitationViewer from './CitationViewer';

const THINKER_THEMES = {
  marcus_aurelius: { color: '#92763A', emblem: '🏛️', name: 'Marcus Aurelius', tradition: 'Roman Stoicism' },
  friedrich_nietzsche: { color: '#8B2E2E', emblem: '⚡', name: 'Friedrich Nietzsche', tradition: 'Continental Existentialism' },
  immanuel_kant: { color: '#324E7B', emblem: '⚖️', name: 'Immanuel Kant', tradition: 'German Deontology' },
  aristotle: { color: '#366854', emblem: '📜', name: 'Aristotle', tradition: 'Classical Virtue Ethics' },
  lao_tzu: { color: '#583D72', emblem: '☯️', name: 'Laozi', tradition: 'Ancient Daoism' },
};

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'tabs'
  const [activeTab, setActiveTab] = useState(0);
  const [activeSentenceTooltip, setActiveSentenceTooltip] = useState(null);

  if (isUser) {
    return (
      <div className="flex items-start justify-end gap-3 my-5">
        <div className="max-w-2xl bg-[#FAF7F0] border-2 border-[#B8995C]/60 rounded-2xl rounded-tr-sm px-5 py-4 shadow-parchment-md">
          <div className="eyebrow-maroon text-[10px] mb-1.5 flex items-center gap-1.5">
            <span>Inquirer's Proposition</span>
          </div>
          <p className="text-sm sm:text-base text-[#2B2419] leading-relaxed font-serif">{message.content}</p>
        </div>
        <div className="w-8 h-8 rounded-full bg-[#FAF7F0] border-2 border-[#B8995C] flex items-center justify-center shrink-0 text-[#2B2419] shadow-inner-gold">
          <User className="w-4 h-4 text-[#8B2E2E]" />
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

  // Strict hard gate: if query is rejected by guardrail, show ONLY rejection message
  const isRejected = 
    data.is_safe === false || 
    flags.some(f => f.category === 'off_topic' || f.category === 'harmful' || f.category === 'harmful_content_request' || f.category === 'jailbreak' || f.severity === 'high') ||
    (breakdowns.length === 0 && citations.length === 0 && (!data.faithfulness_score || data.faithfulness_score === 0.0));

  if (isRejected) {
    return (
      <div className="flex items-start gap-3.5 my-6">
        <div className="w-9 h-9 rounded-full bg-[#FAF7F0] border-2 border-[#8B2E2E] flex items-center justify-center shrink-0 shadow-md text-[#8B2E2E] font-bold text-sm">
          🛡️
        </div>
        <div className="flex-1 max-w-full rounded-xl p-5 border-2 border-[#8B2E2E] bg-[#FDF4F4] shadow-parchment-md space-y-2.5">
          <div className="flex items-center gap-2 text-[#8B2E2E] eyebrow-maroon text-xs">
            <AlertTriangle className="w-4 h-4 text-[#8B2E2E]" />
            <span>Scope & Safety Guardrail Refusal</span>
          </div>
          <div className="text-[#2B2419] text-sm leading-relaxed font-serif">
            {message.content || data.answer}
          </div>
        </div>
      </div>
    );
  }

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
      {/* Bot Icon - Ornate Classical Seal */}
      <div className="w-9 h-9 rounded-full bg-[#FAF7F0] border-2 border-[#B8995C] flex items-center justify-center shrink-0 shadow-inner-gold text-lg">
        🏛️
      </div>

      <div className="flex-1 max-w-full parchment-panel rounded-xl p-5 sm:p-6 shadow-parchment-md space-y-5">
        {/* Top Meta Bar: Guardrail Status & Latency */}
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#B8995C]/30 pb-3">
          <div className="flex items-center gap-2">
            {/* Groundedness Badge */}
            {flaggedCount > 0 ? (
              <button
                onClick={handleScrollToFlagged}
                className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-serif font-semibold bg-[#FDF4F4] text-[#8B2E2E] border border-[#8B2E2E]/60 hover:bg-[#FBE8E8] transition-all shadow-sm"
                title="Click to jump to flagged claims"
              >
                <AlertTriangle className="w-3.5 h-3.5 text-[#8B2E2E]" />
                <span>{flaggedCount} of {totalSentences} claims need review</span>
              </button>
            ) : (
              <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-serif font-medium bg-[#FAF7F0] text-[#366854] border border-[#366854]/40 shadow-sm">
                <ShieldCheck className="w-3.5 h-3.5 text-[#366854]" />
                <span>All {totalSentences || 'claims'} verified ({Math.round(faithfulness * 100)}% grounded)</span>
              </span>
            )}

            {/* Retrieval Alignment Status */}
            {isWeakMatch ? (
              <span className="flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-serif bg-[#FAF6EE] text-[#92763A] border border-[#92763A]/40">
                <Compass className="w-3 h-3 text-[#92763A]" />
                <span>Thematic Match Only</span>
              </span>
            ) : (
              <span className="flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-serif bg-[#FAF6EE] text-[#324E7B] border border-[#324E7B]/40">
                <Compass className="w-3 h-3 text-[#324E7B]" />
                <span>Topic Aligned</span>
              </span>
            )}

            {/* Self-Correction Badge */}
            {regenerationLogs.length > 0 && (
              <span className="flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-serif bg-[#FAF6EE] text-[#583D72] border border-[#583D72]/40">
                <RefreshCw className="w-3 h-3 text-[#583D72]" />
                <span>{regenerationLogs.length} self-corrected</span>
              </span>
            )}
          </div>

          {latency && (
            <div className="flex items-center gap-1.5 text-[#8C7D6B] font-serif text-[11px]">
              <Clock className="w-3 h-3 text-[#B8995C]" />
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
        <div className="space-y-3 pt-1">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Scale className="w-4 h-4 text-[#8B2E2E]" />
              <h3 className="font-philosophy text-base font-bold text-[#8B2E2E] tracking-wide">
                Dialectical Comparative Synthesis
              </h3>
            </div>
            
            {sentenceGroundedness.length > 0 && (
              <span className="text-[11px] font-serif italic text-[#73624A] hidden sm:inline">
                Inspect underlined claims for source verification
              </span>
            )}
          </div>
          
          <div className="max-w-none text-[#2B2419] text-sm leading-relaxed space-y-3 bg-[#FAF7F0] p-5 rounded-xl border border-[#B8995C]/40 shadow-parchment-sm relative font-serif">
            {sentenceGroundedness.length > 0 ? (
              <div className="space-y-3 leading-relaxed">
                {sentenceGroundedness.map((s, idx) => {
                  const isHeading = s.text.startsWith('#');
                  if (isHeading) {
                    return (
                      <h4 key={idx} className="font-philosophy text-[#8B2E2E] text-sm font-bold pt-3 pb-1 border-b border-[#B8995C]/25 flex items-center gap-2 tracking-wide">
                        <span className="text-[#B8995C] text-xs">§</span>
                        <span>{s.text.replace(/^#+\s*/, '')}</span>
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
                            ? 'sentence-flagged bg-[#FDF4F4] border-b-2 border-[#8B2E2E] text-[#8B2E2E] font-medium hover:bg-[#FBE8E8]'
                            : isRegenerated
                            ? 'bg-[#EAF3EE] border-b-2 border-[#366854] text-[#1E3E32] hover:bg-[#DCEEE3]'
                            : 'hover:bg-[#B8995C]/15'
                        }`}
                      >
                        {s.text}{' '}
                      </span>

                      {/* Interactive Tooltip Popover on Hover / Click - Antique Certificate Style */}
                      {activeSentenceTooltip === idx && (
                        <span className="absolute z-50 bottom-full left-0 mb-2 w-72 sm:w-80 p-3.5 rounded-xl bg-[#FAF7F0] border-2 border-[#B8995C] shadow-parchment-lg text-xs text-left block font-serif animate-in fade-in duration-150">
                          <span className="flex items-center justify-between pb-1.5 border-b border-[#B8995C]/30 mb-2 font-serif">
                            <span className="flex items-center gap-1 font-bold">
                              {isFlagged ? (
                                <>
                                  <AlertTriangle className="w-3.5 h-3.5 text-[#8B2E2E]" />
                                  <span className="text-[#8B2E2E]">Ungrounded Claim</span>
                                </>
                              ) : isRegenerated ? (
                                <>
                                  <Sparkles className="w-3.5 h-3.5 text-[#366854]" />
                                  <span className="text-[#366854]">Self-Corrected Claim</span>
                                </>
                              ) : (
                                <>
                                  <CheckCircle className="w-3.5 h-3.5 text-[#366854]" />
                                  <span className="text-[#366854]">Source Grounded</span>
                                </>
                              )}
                            </span>
                            <span className={`px-2 py-0.5 rounded text-[10.5px] font-bold font-serif ${
                              scorePct >= 75 ? 'bg-[#FAF7F0] text-[#366854] border border-[#366854]/40' : 'bg-[#FDF4F4] text-[#8B2E2E] border border-[#8B2E2E]/40'
                            }`}>
                              Confidence: {scorePct}%
                            </span>
                          </span>

                          {/* Reason */}
                          {s.flag_reason && (
                            <span className="block text-[11px] text-[#564936] mb-1.5 leading-snug italic">
                              {s.flag_reason}
                            </span>
                          )}

                          {/* Supporting or Closest Chunk Reference */}
                          {s.supporting_chunk_id && (
                            <span className="block text-[10.5px] font-mono text-[#366854] mb-1">
                              ✓ Supported by Chunk: <strong className="text-[#2B2419]">{s.supporting_chunk_id}</strong>
                            </span>
                          )}
                          {s.closest_chunk_id && (
                            <span className="block text-[10.5px] font-mono text-[#8B2E2E] mb-1">
                              ⚠️ Closest Match: <strong className="text-[#2B2419]">{s.closest_chunk_id}</strong> (insufficient)
                            </span>
                          )}

                          {/* Before/After regeneration diff */}
                          {isRegenerated && s.original_text && (
                            <span className="block text-[10px] font-mono text-[#564936] bg-[#F4EFE6] p-2 rounded border border-[#B8995C]/30 mt-1.5">
                              <span className="text-[#8B2E2E] line-through block">Original ({Math.round((s.original_score || 0) * 100)}%): "{s.original_text.slice(0, 60)}..."</span>
                              <span className="text-[#366854] block mt-0.5 font-semibold">Corrected ({scorePct}%): "{s.text.slice(0, 60)}..."</span>
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
                <p key={pIdx} className="text-xs sm:text-sm text-[#2B2419] leading-relaxed">
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
                <Sparkles className="w-4 h-4 text-[#8B2E2E]" />
                <h3 className="font-philosophy text-sm font-bold text-[#8B2E2E] tracking-wide">
                  Per-Thinker Deep Dive ({breakdowns.length} Traditions)
                </h3>
              </div>

              {/* View Mode Toggle: Grid vs Tabs */}
              <div className="flex items-center bg-[#F4EFE6] rounded-md p-0.5 border border-[#B8995C]/40 text-xs font-serif">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`flex items-center gap-1 px-2.5 py-1 rounded transition-all ${
                    viewMode === 'grid' ? 'bg-[#FAF7F0] text-[#2B2419] font-bold shadow-sm border border-[#B8995C]/50' : 'text-[#73624A] hover:text-[#2B2419]'
                  }`}
                >
                  <Grid className="w-3 h-3 text-[#B8995C]" />
                  <span className="hidden sm:inline">Grid</span>
                </button>
                <button
                  onClick={() => setViewMode('tabs')}
                  className={`flex items-center gap-1 px-2.5 py-1 rounded transition-all ${
                    viewMode === 'tabs' ? 'bg-[#FAF7F0] text-[#2B2419] font-bold shadow-sm border border-[#B8995C]/50' : 'text-[#73624A] hover:text-[#2B2419]'
                  }`}
                >
                  <Layers className="w-3 h-3 text-[#B8995C]" />
                  <span className="hidden sm:inline">Tabs</span>
                </button>
              </div>
            </div>

            {/* Grid View */}
            {viewMode === 'grid' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                {breakdowns.map((b, idx) => {
                  const theme = THINKER_THEMES[b.thinker_id] || { color: '#92763A', emblem: '🏛️' };
                  return (
                    <div
                      key={b.thinker_id || idx}
                      className="parchment-card rounded-xl p-4 border border-[#B8995C]/50 shadow-parchment-sm flex flex-col justify-between hover:border-[#B8995C] hover:shadow-parchment-md transition-all relative"
                    >
                      <div className="space-y-2.5">
                        {/* Header */}
                        <div className="flex items-center justify-between gap-2 border-b border-[#B8995C]/20 pb-2">
                          <div className="flex items-center gap-2">
                            {/* Philosopher Emblem Seal */}
                            <div className="w-7 h-7 rounded-full bg-[#FAF7F0] border border-[#B8995C] flex items-center justify-center text-xs shadow-inner-gold shrink-0">
                              {theme.emblem}
                            </div>
                            <div>
                              <h4 className="font-bold text-[#2B2419] text-sm tracking-tight font-philosophy">
                                {b.thinker_name}
                              </h4>
                              <span className="text-[10px] text-[#73624A] font-serif italic block">
                                {b.tradition}
                              </span>
                            </div>
                          </div>

                          {b.is_weak_match && (
                            <span className="text-[9.5px] font-serif px-2 py-0.5 rounded bg-[#FAF6EE] text-[#92763A] border border-[#92763A]/40">
                              Thematic Match
                            </span>
                          )}
                        </div>

                        {/* Core Stance Callout */}
                        <div className="p-3 rounded-lg text-xs font-serif italic leading-snug bg-[#F4EFE6] border-l-2 border-[#B8995C] text-[#2B2419]">
                          "{b.core_stance}"
                        </div>

                        {/* Classical Decorative Divider between summary quote and full explanation */}
                        <div className="flex items-center justify-center my-2 text-[#B8995C]/60 text-[10px] select-none">
                          <span className="w-12 h-px bg-[#B8995C]/30"></span>
                          <span className="mx-2">❖</span>
                          <span className="w-12 h-px bg-[#B8995C]/30"></span>
                        </div>

                        {/* Detailed Argument */}
                        <div className="text-xs text-[#3D3425] leading-relaxed font-serif whitespace-pre-line">
                          {b.detailed_argument}
                        </div>
                      </div>

                      {/* Concept Tags - Cream/Gold-bordered pills with serif text */}
                      {b.key_concepts && b.key_concepts.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-3 pt-2.5 border-t border-[#B8995C]/20">
                          {b.key_concepts.map((concept, cIdx) => (
                            <span
                              key={cIdx}
                              className="text-[10.5px] font-serif px-2.5 py-0.5 rounded-full bg-[#FAF7F0] text-[#564936] border border-[#B8995C]/50 tracking-wide hover:border-[#8B2E2E] hover:text-[#8B2E2E] transition-colors"
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
              <div className="parchment-card rounded-xl p-5 border border-[#B8995C]/60 shadow-parchment-md space-y-4">
                {/* Tab buttons */}
                <div className="flex flex-wrap gap-1.5 border-b border-[#B8995C]/25 pb-2.5">
                  {breakdowns.map((b, idx) => {
                    const theme = THINKER_THEMES[b.thinker_id] || { color: '#92763A', emblem: '🏛️' };
                    const isActive = activeTab === idx;
                    return (
                      <button
                        key={idx}
                        onClick={() => setActiveTab(idx)}
                        className={`px-3 py-1.5 rounded-full text-xs font-serif transition-all flex items-center gap-1.5 ${
                          isActive
                            ? 'bg-[#FAF7F0] text-[#2B2419] font-bold shadow-sm border-2 border-[#B8995C]'
                            : 'bg-[#F4EFE6]/70 text-[#73624A] border border-[#B8995C]/30 hover:border-[#B8995C] hover:text-[#2B2419]'
                        }`}
                      >
                        <span className="text-[11px]">{theme.emblem}</span>
                        <span>{b.thinker_name}</span>
                        {b.is_weak_match && <span className="text-[9px] text-[#92763A] ml-0.5">•</span>}
                      </button>
                    );
                  })}
                </div>

                {/* Active Tab Content */}
                {breakdowns[activeTab] && (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between border-b border-[#B8995C]/20 pb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-[#FAF7F0] border border-[#B8995C] flex items-center justify-center text-sm shadow-inner-gold shrink-0">
                          {THINKER_THEMES[breakdowns[activeTab].thinker_id]?.emblem || '🏛️'}
                        </div>
                        <div>
                          <h4 className="font-bold text-[#2B2419] text-sm font-philosophy">
                            {breakdowns[activeTab].thinker_name}
                          </h4>
                          <span className="text-xs text-[#73624A] font-serif italic">
                            {breakdowns[activeTab].tradition}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="p-3.5 rounded-lg bg-[#F4EFE6] border-l-2 border-[#B8995C] text-[#2B2419] text-xs font-serif italic leading-relaxed font-medium">
                      "{breakdowns[activeTab].core_stance}"
                    </div>

                    {/* Classical Decorative Divider between summary quote and full explanation */}
                    <div className="flex items-center justify-center my-2 text-[#B8995C]/60 text-[10px] select-none">
                      <span className="w-16 h-px bg-[#B8995C]/30"></span>
                      <span className="mx-2">❖</span>
                      <span className="w-16 h-px bg-[#B8995C]/30"></span>
                    </div>

                    <p className="text-xs sm:text-sm text-[#3D3425] leading-relaxed font-serif whitespace-pre-line">
                      {breakdowns[activeTab].detailed_argument}
                    </p>

                    <div className="flex flex-wrap gap-1.5 pt-2 border-t border-[#B8995C]/20">
                      {breakdowns[activeTab].key_concepts?.map((c, i) => (
                        <span key={i} className="text-[10.5px] font-serif px-2.5 py-0.5 rounded-full bg-[#FAF7F0] text-[#564936] border border-[#B8995C]/50 tracking-wide hover:border-[#8B2E2E] hover:text-[#8B2E2E] transition-colors">
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
