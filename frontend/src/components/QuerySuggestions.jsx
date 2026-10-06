import React from 'react';
import { Compass, ArrowRight } from 'lucide-react';

const SUGGESTIONS = [
  {
    title: 'Suffering & Meaning',
    query: 'What is the meaning and purpose of suffering in human life?',
    thinkers: ['friedrich_nietzsche', 'marcus_aurelius', 'lao_tzu'],
  },
  {
    title: 'Duty vs. Desire',
    query: 'How should one resolve the conflict between personal desire and universal moral duty?',
    thinkers: ['immanuel_kant', 'aristotle', 'marcus_aurelius'],
  },
  {
    title: 'Active Striving vs. Wu Wei',
    query: 'Is happiness achieved through active striving or effortless yielding (Wu Wei)?',
    thinkers: ['lao_tzu', 'aristotle', 'friedrich_nietzsche'],
  },
  {
    title: 'The Inner Citadel & Harm',
    query: 'Can external events, public opinion, or insults truly harm the self?',
    thinkers: ['marcus_aurelius', 'immanuel_kant', 'lao_tzu'],
  },
];

export default function QuerySuggestions({ onSelectQuery }) {
  return (
    <div className="w-full space-y-2.5 py-4">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-[#8B2E2E] font-philosophy tracking-wide">
        <Compass className="w-4 h-4 text-[#8B2E2E]" />
        <span>Dialectical Dilemma Prompts</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {SUGGESTIONS.map((item, idx) => (
          <button
            key={idx}
            onClick={() => onSelectQuery(item.query, item.thinkers)}
            className="text-left p-3.5 rounded-lg parchment-card parchment-card-hover border-l-4 border-l-[#8B2E2E] flex flex-col justify-between group transition-all"
          >
            <div>
              <div className="flex items-center justify-between text-xs font-bold text-[#8B2E2E] group-hover:text-[#561A1A] font-philosophy tracking-wide">
                <span>{item.title}</span>
                <ArrowRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all text-[#8B2E2E]" />
              </div>
              <p className="text-[12px] text-[#564936] mt-1.5 leading-relaxed font-serif italic line-clamp-2">
                "{item.query}"
              </p>
            </div>
            <div className="mt-2.5 pt-2 border-t border-[#B8995C]/20 text-[11px] font-serif italic text-[#8B2E2E]/85">
              {item.thinkers.length} traditions compared
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
