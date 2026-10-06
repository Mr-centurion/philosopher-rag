import React from 'react';
import { Users, Check } from 'lucide-react';

const THINKER_EMBLEMS = {
  marcus_aurelius: '🏛️',
  friedrich_nietzsche: '⚡',
  immanuel_kant: '⚖️',
  aristotle: '📜',
  lao_tzu: '☯️',
  seneca: '🏺',
  epictetus: '⛓️',
  plato: '🏛️',
  voltaire: '🕯️',
  leo_tolstoy: '🌾',
  franz_kafka: '🪲',
  bhagavad_gita: '🏹',
  chanakya: '👑',
  sun_tzu: '⚔️',
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
          {isAllSelected ? 'Custom Selection' : `Compare All (${thinkers.length} Traditions)`}
        </button>
      </div>

      {/* Thinker Chips */}
      <div className="flex flex-wrap gap-2">
        {/* All/Auto Chip */}
        <button
          onClick={onSelectAll}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-serif transition-all border ${
            isAllSelected
              ? 'bg-[#FDF4F4] border-2 border-[#8B2E2E] text-[#561A1A] font-semibold shadow-sm'
              : 'bg-[#FAF6EE] border border-[#B8995C]/40 text-[#73624A] hover:border-[#8B2E2E]/70 hover:text-[#8B2E2E]'
          }`}
        >
          {isAllSelected && <Check className="w-3.5 h-3.5 text-[#8B2E2E]" />}
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
                  ? 'bg-[#FDF4F4] border-2 border-[#8B2E2E] text-[#561A1A] font-semibold shadow-sm'
                  : 'bg-[#FAF6EE] border border-[#B8995C]/40 text-[#73624A] hover:border-[#8B2E2E]/70 hover:text-[#8B2E2E]'
              }`}
            >
              {/* Ornate Circular Emblem Seal */}
              <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[11px] shrink-0 border ${
                isSelected ? 'bg-[#FAF7F0] border-[#8B2E2E]/60 text-[#8B2E2E]' : 'bg-[#FAF7F0] border-[#B8995C]/60 shadow-inner-gold'
              }`}>
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
