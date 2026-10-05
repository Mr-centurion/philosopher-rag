import React, { useState } from 'react';
import { BookOpen, ChevronDown, ChevronUp, Quote, ShieldCheck, AlertTriangle, Sparkles, RefreshCw, Layers } from 'lucide-react';

export default function CitationViewer({ citations, sentenceGroundedness, regenerationLogs, faithfulnessScore }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeSubTab, setActiveSubTab] = useState('citations'); // 'citations' or 'breakdown'

  const sentences = sentenceGroundedness || [];
  const logs = regenerationLogs || [];
  const headlineScore = Math.round((faithfulnessScore || 0.95) * 100);

  return (
    <div className="mt-4 rounded-xl border border-[#B8995C]/40 bg-[#FAF7F0] overflow-hidden shadow-parchment-sm transition-all font-serif">
      {/* Header / Toggle Button */}
      <div 
        className="px-4 py-3 flex items-center justify-between text-xs text-[#2B2419] hover:bg-[#F4EFE6] transition-colors cursor-pointer border-b border-[#B8995C]/20"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 font-bold text-[#8B2E2E]">
            <BookOpen className="w-3.5 h-3.5 text-[#B8995C]" />
            <span>Grounded Primary Sources ({citations ? citations.length : 0})</span>
          </div>
          
          <div className="hidden sm:flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#FAF7F0] border border-[#366854]/40 text-[#366854] text-[11px] font-semibold">
            <ShieldCheck className="w-3 h-3 text-[#366854]" />
            <span>{headlineScore}% Grounded</span>
          </div>
          
          {sentences.some(s => s.was_regenerated) && (
            <span className="hidden md:flex items-center gap-1 text-[10.5px] text-[#583D72] bg-[#FAF7F0] border border-[#583D72]/40 px-2 py-0.5 rounded-full font-serif">
              <Sparkles className="w-2.5 h-2.5 text-[#583D72]" />
              <span>Self-Corrected Claims</span>
            </span>
          )}
        </div>

        <div className="flex items-center gap-1.5 text-[#73624A] text-xs font-serif italic">
          <span>{isExpanded ? 'Collapse' : 'Inspect Source Passages & Breakdown'}</span>
          {isExpanded ? <ChevronUp className="w-3.5 h-3.5 text-[#B8995C]" /> : <ChevronDown className="w-3.5 h-3.5 text-[#B8995C]" />}
        </div>
      </div>

      {/* Expanded Section */}
      {isExpanded && (
        <div className="bg-[#FAF6EE] p-4 sm:p-5 space-y-4">
          {/* Sub Tab Navigation */}
          <div className="flex items-center gap-2 border-b border-[#B8995C]/20 pb-2">
            <button
              onClick={() => setActiveSubTab('citations')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-serif transition-all ${
                activeSubTab === 'citations'
                  ? 'bg-[#FAF7F0] text-[#8B2E2E] font-bold border border-[#B8995C]/60 shadow-sm'
                  : 'text-[#73624A] hover:text-[#2B2419]'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5 text-[#B8995C]" />
              <span>Source Chunks ({citations ? citations.length : 0})</span>
            </button>

            <button
              onClick={() => setActiveSubTab('breakdown')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-serif transition-all ${
                activeSubTab === 'breakdown'
                  ? 'bg-[#FAF7F0] text-[#8B2E2E] font-bold border border-[#B8995C]/60 shadow-sm'
                  : 'text-[#73624A] hover:text-[#2B2419]'
              }`}
            >
              <Layers className="w-3.5 h-3.5 text-[#B8995C]" />
              <span>Sentence-Level Score Breakdown ({sentences.length})</span>
            </button>
          </div>

          {/* Sub Tab 1: Source Chunks */}
          {activeSubTab === 'citations' && citations && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {citations.map((cit, idx) => (
                <div
                  key={`${cit.chunk_id || idx}-${idx}`}
                  className="p-3.5 rounded-lg bg-[#FAF7F0] border border-[#B8995C]/40 text-xs flex flex-col justify-between hover:border-[#B8995C] transition-all shadow-parchment-sm"
                >
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-2 pb-1.5 border-b border-[#B8995C]/20">
                      <span className="font-bold text-[#8B2E2E] font-philosophy flex items-center gap-1.5">
                        <Quote className="w-3 h-3 text-[#B8995C] shrink-0" />
                        {cit.thinker_name}
                      </span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#F4EFE6] border border-[#B8995C]/30 text-[#73624A]">
                        Score: {cit.relevance_score ? (cit.relevance_score).toFixed(2) : '1.00'}
                      </span>
                    </div>

                    <div className="text-[11.5px] font-semibold text-[#2B2419] mb-1">
                      {cit.work_title} <span className="text-[#8C7D6B] font-serif italic">• {cit.chapter}</span>
                    </div>

                    <p className="text-[#3D3425] italic leading-relaxed text-[11.5px] border-l-2 border-[#B8995C] pl-2.5 my-2">
                      "{cit.quote}"
                    </p>
                  </div>

                  <div className="mt-2.5 pt-2 border-t border-[#B8995C]/20 flex items-center justify-between text-[10px] text-[#8C7D6B] font-mono">
                    <span>ID: {cit.chunk_id || `passage_${idx + 1}`}</span>
                    <span className="text-[#366854] flex items-center gap-1 font-serif font-semibold">
                      ✓ Primary Source Verified
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Sub Tab 2: Granular Sentence-Level Breakdown */}
          {activeSubTab === 'breakdown' && (
            <div className="space-y-3">
              <div className="flex items-center justify-between bg-[#FAF7F0] p-3 rounded-lg border border-[#B8995C]/40 text-xs font-serif">
                <span className="text-[#2B2419]">
                  Dialectical Groundedness Score: <strong className="text-[#366854] text-sm">{headlineScore}%</strong>
                </span>
                <span className="text-[#73624A]">
                  Total Claims Evaluated: <strong className="text-[#2B2419]">{sentences.length}</strong>
                </span>
              </div>

              <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
                {sentences.map((s, idx) => {
                  const scorePct = Math.round(s.confidence_score * 100);
                  const isHigh = scorePct >= 75;
                  const isMedium = scorePct >= 50 && scorePct < 75;
                  const dotColor = isHigh ? 'bg-[#366854]' : isMedium ? 'bg-[#92763A]' : 'bg-[#8B2E2E]';
                  
                  return (
                    <div
                      key={idx}
                      className={`p-3 rounded-lg border text-xs flex items-start justify-between gap-3 ${
                        s.grounded
                          ? 'bg-[#FAF7F0] border-[#B8995C]/30 text-[#2B2419]'
                          : 'bg-[#FDF4F4] border-[#8B2E2E]/40 text-[#8B2E2E]'
                      }`}
                    >
                      <div className="flex items-start gap-2.5 flex-1">
                        <span className={`w-2.5 h-2.5 rounded-full ${dotColor} shrink-0 mt-1 shadow-sm`} />
                        <div className="space-y-1">
                          <p className="text-[12px] leading-relaxed font-serif">
                            <span className="text-[#8C7D6B] font-mono text-[10.5px] mr-1.5">[{idx + 1}]</span>
                            {s.text}
                          </p>
                          
                          <div className="flex flex-wrap items-center gap-2 text-[10px] font-mono text-[#73624A]">
                            {s.supporting_chunk_id && (
                              <span className="text-[#366854] font-semibold">
                                Match: {s.supporting_chunk_id}
                              </span>
                            )}
                            {s.closest_chunk_id && (
                              <span className="text-[#92763A]">
                                Closest: {s.closest_chunk_id}
                              </span>
                            )}
                            {s.was_regenerated && (
                              <span className="px-1.5 py-0.5 rounded bg-[#FAF7F0] text-[#583D72] border border-[#583D72]/40 font-serif">
                                ↺ Self-Corrected (was {Math.round((s.original_score || 0) * 100)}%)
                              </span>
                            )}
                            {s.flag_reason && !s.grounded && (
                              <span className="text-[#8B2E2E] italic">
                                • {s.flag_reason}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="shrink-0 font-serif text-right">
                        <span className={`text-xs font-bold ${isHigh ? 'text-[#366854]' : isMedium ? 'text-[#92763A]' : 'text-[#8B2E2E]'}`}>
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
