import React from 'react';
import { X, BookOpen, Scroll, Hash, Quote } from 'lucide-react';

const THINKER_EMBLEMS = {
  marcus_aurelius: '🏛️',
  friedrich_nietzsche: '⚡',
  immanuel_kant: '⚖️',
  aristotle: '📜',
  lao_tzu: '☯️',
};

export default function ThinkerSidebar({ isOpen, onClose, thinkers }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-xs transition-opacity">
      <div className="w-full max-w-md h-full bg-[#FAF7F0] border-l-2 border-[#B8995C] p-6 flex flex-col justify-between overflow-y-auto shadow-2xl font-serif">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-[#B8995C]/30">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-[#FAF7F0] border border-[#B8995C] flex items-center justify-center text-sm shadow-inner-gold">
                🏛️
              </div>
              <div>
                <h3 className="font-philosophy text-base font-bold text-[#8B2E2E]">
                  Philosophical Corpus
                </h3>
                <p className="text-xs text-[#73624A] italic">Primary texts & indexed lexicon</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-md text-[#73624A] hover:text-[#2B2419] hover:bg-[#F4EFE6] transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Thinker List */}
          <div className="space-y-4">
            {thinkers.map((thinker) => {
              const emblem = THINKER_EMBLEMS[thinker.id] || '🏛️';
              return (
                <div
                  key={thinker.id}
                  className="parchment-card rounded-xl p-4 border border-[#B8995C]/50 hover:border-[#B8995C] transition-all space-y-3 shadow-parchment-sm"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-full bg-[#FAF7F0] border border-[#B8995C] flex items-center justify-center text-xs shadow-inner-gold shrink-0">
                        {emblem}
                      </div>
                      <div>
                        <h4 className="font-bold text-[#2B2419] text-sm font-philosophy">
                          {thinker.name}
                        </h4>
                        <span className="text-xs text-[#73624A] italic">
                          {thinker.tradition} • {thinker.period}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Quote */}
                  <div className="text-xs text-[#3D3425] italic bg-[#F4EFE6] p-3 rounded-lg border-l-2 border-[#B8995C] flex gap-2">
                    <Quote className="w-3.5 h-3.5 text-[#B8995C] shrink-0 mt-0.5" />
                    <span>"{thinker.sample_quote}"</span>
                  </div>

                  {/* Key themes */}
                  <div className="flex flex-wrap gap-1.5">
                    {thinker.key_themes.map((theme, tIdx) => (
                      <span
                        key={tIdx}
                        className="text-[10px] font-serif px-2 py-0.5 rounded-full bg-[#FAF7F0] text-[#564936] border border-[#B8995C]/40"
                      >
                        {theme}
                      </span>
                    ))}
                  </div>

                  {/* Corpus Stats */}
                  <div className="flex items-center justify-between text-[11px] font-serif text-[#73624A] pt-2 border-t border-[#B8995C]/20">
                    <span className="flex items-center gap-1.5">
                      <Scroll className="w-3 h-3 text-[#B8995C]" />
                      <span>{thinker.chunk_count} Passages</span>
                    </span>
                    <span className="flex items-center gap-1.5">
                      <Hash className="w-3 h-3 text-[#B8995C]" />
                      <span>{thinker.word_count.toLocaleString()} Words</span>
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="pt-6 border-t border-[#B8995C]/30 text-center text-xs text-[#8C7D6B] font-serif italic">
          BM25 + ChromaDB Vector Corpus • FlashRank Reranked
        </div>
      </div>
    </div>
  );
}
