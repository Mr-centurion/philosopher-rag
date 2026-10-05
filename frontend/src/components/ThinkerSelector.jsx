import React from 'react';
import { Users, Check } from 'lucide-react';

const THINKER_EMBLEMS = {
  marcus_aurelius: '🏛️',
  friedrich_nietzsche: '⚡',
  immanuel_kant: '⚖️',
  aristotle: '📜',
  lao_tzu: '☯️',
};

export default function ThinkerSelector({ thinkers, selectedThinkers, onToggleThinker, onSelectAll }) {
  const isAllSelected = selectedThinkers.length === 0 || selectedThinkers.length === thinkers.length;

  return (
    <div className="w-full flex flex-col gap-2.5 py-1">
      <div className="flex items-center justify-between text-xs text-[#73624A] px-1 font-serif">
        <span className="flex items-center gap-1.5 font-medium">
          <Users className="w-3.5 h-3.5 text-[#B8995C]" />
          <span className="tracking-wide">Select Philosophical Traditions to Interrogate:</span>
        </span>
        <button
          onClick={onSelectAll}
          className="text-[#8B2E2E] hover:text-[#561A1A] font-serif text-[11.5px] font-semibold underline underline-offset-2 transition-colors"
        >
          {isAllSelected ? 'Custom Selection' : 'Compare All (5 Traditions)'}
        </button>
      </div>

      {/* Thinker Chips */}
      <div className="flex flex-wrap gap-2">
        {/* All/Auto Chip */}
        <button
          onClick={onSelectAll}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-serif transition-all border ${
            isAllSelected
              ? 'bg-[#FAF7F0] border-2 border-[#B8995C] text-[#2B2419] font-bold shadow-parchment-sm'
              : 'bg-[#F4EFE6]/80 border border-[#B8995C]/40 text-[#73624A] hover:border-[#B8995C] hover:text-[#2B2419]'
          }`}
        >
          {isAllSelected && <Check className="w-3 h-3 text-[#8B2E2E]" />}
          <span className="tracking-wide">All Traditions (Comparative Synthesis)</span>
        </button>

        {/* Per-thinker Chips with Ornate Emblems */}
        {thinkers.map((thinker) => {
          const isSelected = selectedThinkers.includes(thinker.id);
          const emblem = THINKER_EMBLEMS[thinker.id] || '🏛️';
          return (
            <button
              key={thinker.id}
              onClick={() => onToggleThinker(thinker.id)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-serif transition-all border ${
                isSelected
                  ? 'bg-[#FAF7F0] border-2 border-[#B8995C] text-[#2B2419] font-bold shadow-parchment-sm'
                  : 'bg-[#F4EFE6]/80 border border-[#B8995C]/40 text-[#73624A] hover:border-[#B8995C] hover:text-[#2B2419]'
              }`}
            >
              {/* Ornate Circular Emblem Seal */}
              <span className="w-5 h-5 rounded-full bg-[#FAF7F0] border border-[#B8995C]/60 flex items-center justify-center text-[11px] shadow-inner-gold shrink-0">
                {emblem}
              </span>
              <span className="tracking-wide">{thinker.name}</span>
              <span className="text-[10px] text-[#8C7D6B] font-serif italic hidden sm:inline">
                ({thinker.tradition.split(' ')[0]})
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
