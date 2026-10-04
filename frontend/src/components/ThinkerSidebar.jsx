import React from 'react';
import { X, BookOpen, Scroll, Hash, Quote } from 'lucide-react';

export default function ThinkerSidebar({ isOpen, onClose, thinkers }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm transition-opacity">
      <div className="w-full max-w-md h-full bg-[#11131c] border-l border-white/10 p-6 flex flex-col justify-between overflow-y-auto shadow-2xl">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-white/10">
            <div className="flex items-center gap-2.5">
              <BookOpen className="w-5 h-5 text-amber-400" />
              <div>
                <h3 className="font-philosophy text-base font-bold text-white">
                  Philosophical Corpus
                </h3>
                <p className="text-xs text-slate-400">Available thinkers & knowledge stats</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Thinker List */}
          <div className="space-y-4">
            {thinkers.map((thinker) => (
              <div
                key={thinker.id}
                className="glass-card rounded-xl p-4 border border-white/5 hover:border-slate-700 transition-all space-y-3"
                style={{ borderLeft: `3px solid ${thinker.color}` }}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-bold text-white text-sm flex items-center gap-1.5">
                      {thinker.name}
                    </h4>
                    <span className="text-xs text-amber-400/90 font-mono">
                      {thinker.tradition} • {thinker.period}
                    </span>
                  </div>
                </div>

                {/* Quote */}
                <div className="text-xs text-slate-300/80 italic bg-black/20 p-2.5 rounded-lg border border-white/5 flex gap-2">
                  <Quote className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                  <span>"{thinker.sample_quote}"</span>
                </div>

                {/* Key themes */}
                <div className="flex flex-wrap gap-1">
                  {thinker.key_themes.map((theme, tIdx) => (
                    <span
                      key={tIdx}
                      className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-900 text-slate-300 border border-slate-800"
                    >
                      {theme}
                    </span>
                  ))}
                </div>

                {/* Corpus Stats */}
                <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-2 border-t border-white/5">
                  <span className="flex items-center gap-1">
                    <Scroll className="w-3 h-3 text-slate-500" />
                    <span>{thinker.chunk_count} Indexed Chunks</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <Hash className="w-3 h-3 text-slate-500" />
                    <span>{thinker.word_count} Words</span>
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="pt-6 border-t border-white/10 text-center text-xs text-slate-500 font-mono">
          BM25 + ChromaDB Vector Corpus • FlashRank Reranked
        </div>
      </div>
    </div>
  );
}
