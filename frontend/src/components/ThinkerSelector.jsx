import React from 'react';
import { Users, Check } from 'lucide-react';

export default function ThinkerSelector({ thinkers, selectedThinkers, onToggleThinker, onSelectAll }) {
  const isAllSelected = selectedThinkers.length === 0 || selectedThinkers.length === thinkers.length;

  return (
    <div className="w-full flex flex-col gap-2 py-2">
      <div className="flex items-center justify-between text-xs text-slate-400 px-1">
        <span className="flex items-center gap-1.5 font-medium">
          <Users className="w-3.5 h-3.5 text-amber-400" />
          <span>Select Philosophical Perspectives to Query:</span>
        </span>
        <button
          onClick={onSelectAll}
          className="text-amber-400/90 hover:text-amber-300 font-mono text-[11px] underline underline-offset-2 transition-colors"
        >
          {isAllSelected ? 'Custom Selection' : 'Compare All (5)'}
        </button>
      </div>

      {/* Thinker Chips */}
      <div className="flex flex-wrap gap-2">
        {/* All/Auto Chip */}
        <button
          onClick={onSelectAll}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all border ${
            isAllSelected
              ? 'bg-amber-500/20 border-amber-500/60 text-amber-300 shadow-sm shadow-amber-500/10'
              : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
          }`}
        >
          {isAllSelected && <Check className="w-3 h-3 text-amber-400" />}
          <span>All Traditions (Comparative)</span>
        </button>

        {/* Per-thinker Chips */}
        {thinkers.map((thinker) => {
          const isSelected = selectedThinkers.includes(thinker.id);
          return (
            <button
              key={thinker.id}
              onClick={() => onToggleThinker(thinker.id)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all border ${
                isSelected
                  ? 'bg-slate-800/90 border-slate-600 text-white shadow-md'
                  : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-300'
              }`}
              style={{
                borderColor: isSelected ? thinker.color : undefined,
                boxShadow: isSelected ? `0 0 12px ${thinker.color}25` : undefined,
              }}
            >
              <span
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: thinker.color }}
              />
              <span>{thinker.name}</span>
              <span className="text-[10px] text-slate-400 font-mono opacity-80 hidden sm:inline">
                ({thinker.tradition.split(' ')[0]})
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
