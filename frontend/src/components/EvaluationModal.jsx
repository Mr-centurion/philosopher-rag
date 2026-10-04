import React, { useState } from 'react';
import { X, Play, Activity, CheckCircle, AlertTriangle, Clock, RefreshCw, BarChart2, ShieldCheck, Sparkles, Layers, Compass } from 'lucide-react';
import { runEvaluation } from '../services/api';

export default function EvaluationModal({ isOpen, onClose }) {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleRunEval = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await runEvaluation();
      setResults(data);
    } catch (err) {
      setError(err.message || 'Failed to complete evaluation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md">
      <div className="w-full max-w-4xl bg-[#11131c] border border-white/10 rounded-2xl p-6 shadow-2xl space-y-6 max-h-[90vh] flex flex-col justify-between overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-philosophy text-lg font-bold text-white">
                RAG Benchmark Evaluation Suite
              </h3>
              <p className="text-xs text-slate-400">
                Ground Truth Dialectic Evaluation: Retrieval Mismatch vs. Generation Faithfulness & Self-Correction
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Trigger Button / Status */}
        <div className="flex items-center justify-between bg-slate-950/60 p-4 rounded-xl border border-white/5">
          <div className="text-xs text-slate-300">
            <span className="font-semibold text-white">Automated Golden Test Suite:</span> 6 multi-thinker philosophical dilemmas evaluated for query-topic alignment, sentence groundedness, and self-correction.
          </div>
          <button
            onClick={handleRunEval}
            disabled={loading}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all shrink-0 ${
              loading
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/30'
            }`}
          >
            {loading ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Evaluating...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Run Benchmark</span>
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="p-3 bg-rose-950/40 border border-rose-500/30 rounded-xl text-rose-300 text-xs">
            {error}
          </div>
        )}

        {/* Results Cards */}
        {results && (
          <div className="space-y-5">
            {/* Top Level Metric Score Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-6 gap-3">
              <div className="p-3 rounded-xl bg-slate-900/80 border border-emerald-500/30">
                <div className="text-[10px] font-mono text-slate-400 uppercase">Faithfulness</div>
                <div className="text-lg font-bold text-emerald-400 mt-1">
                  {(results.mean_faithfulness * 100).toFixed(1)}%
                </div>
                <div className="text-[9px] text-slate-500 mt-0.5">Mean Grounding</div>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/80 border border-purple-500/30">
                <div className="text-[10px] font-mono text-slate-400 uppercase">Voice Distinct</div>
                <div className="text-lg font-bold text-purple-400 mt-1">
                  {(results.mean_voice_distinctiveness_score * 100).toFixed(1)}%
                </div>
                <div className="text-[9px] text-slate-500 mt-0.5">Anti-Template Score</div>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/80 border border-amber-500/30">
                <div className="text-[10px] font-mono text-slate-400 uppercase">Context Recall</div>
                <div className="text-lg font-bold text-amber-400 mt-1">
                  {(results.mean_context_recall * 100).toFixed(1)}%
                </div>
                <div className="text-[9px] text-slate-500 mt-0.5">Concept hit rate</div>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/80 border border-rose-500/30">
                <div className="text-[10px] font-mono text-slate-400 uppercase">Retrieval Mismatch</div>
                <div className="text-lg font-bold text-rose-400 mt-1">
                  {results.retrieval_mismatch_rate_pct}%
                </div>
                <div className="text-[9px] text-slate-500 mt-0.5">Topic mismatch</div>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/80 border border-indigo-500/30">
                <div className="text-[10px] font-mono text-slate-400 uppercase">Comp. Balance</div>
                <div className="text-lg font-bold text-indigo-400 mt-1">
                  {(results.mean_comparative_balance * 100).toFixed(1)}%
                </div>
                <div className="text-[9px] text-slate-500 mt-0.5">Tradition equity</div>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/80 border border-sky-500/30">
                <div className="text-[10px] font-mono text-slate-400 uppercase">Mean Latency</div>
                <div className="text-lg font-bold text-sky-400 mt-1">
                  {results.mean_latency_ms.toFixed(0)} ms
                </div>
                <div className="text-[9px] text-slate-500 mt-0.5">Graph latency</div>
              </div>
            </div>

            {/* Sentence-Level Faithfulness & Self-Correction Distribution */}
            <div className="p-4 rounded-xl bg-slate-950/70 border border-white/10 space-y-3">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="font-bold text-white flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Sentence-Level Faithfulness Distribution ({results.total_sentences_evaluated} claims evaluated)</span>
                </span>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="p-3 rounded-lg bg-slate-900/80 border border-emerald-500/30 flex flex-col justify-between">
                  <span className="text-[11px] font-mono text-slate-400">Directly Grounded</span>
                  <span className="text-lg font-bold text-emerald-400 mt-1">
                    {results.grounded_sentences_pct}%
                  </span>
                  <span className="text-[10px] text-slate-500">Verified on first pass</span>
                </div>

                <div className="p-3 rounded-lg bg-slate-900/80 border border-cyan-500/30 flex flex-col justify-between">
                  <span className="text-[11px] font-mono text-slate-400">Self-Corrected</span>
                  <span className="text-lg font-bold text-cyan-400 mt-1">
                    {results.regenerated_sentences_pct}%
                  </span>
                  <span className="text-[10px] text-slate-500">Resolved via 1-retry regeneration</span>
                </div>

                <div className="p-3 rounded-lg bg-slate-900/80 border border-amber-500/30 flex flex-col justify-between">
                  <span className="text-[11px] font-mono text-slate-400">Unresolved / Flagged</span>
                  <span className="text-lg font-bold text-amber-400 mt-1">
                    {results.unresolved_flagged_pct}%
                  </span>
                  <span className="text-[10px] text-slate-500">Marked as low-confidence</span>
                </div>
              </div>
            </div>

            {/* Test Case Breakdown Table */}
            <div className="space-y-2">
              <div className="text-xs font-mono text-slate-400 uppercase font-semibold">
                Benchmark Query Results
              </div>
              <div className="border border-white/10 rounded-xl overflow-hidden bg-slate-950/40 text-xs">
                <table className="w-full text-left">
                  <thead className="bg-slate-900/90 text-slate-400 font-mono text-[11px] border-b border-white/5">
                    <tr>
                      <th className="p-2.5 pl-3">Query</th>
                      <th className="p-2.5">Topic Match</th>
                      <th className="p-2.5">Voice Distinct</th>
                      <th className="p-2.5">Faithfulness</th>
                      <th className="p-2.5">Claims (G/R/U)</th>
                      <th className="p-2.5">Recall</th>
                      <th className="p-2.5">Latency</th>
                      <th className="p-2.5 pr-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {results.details.map((item, idx) => (
                      <tr key={idx} className="hover:bg-white/5 transition-colors">
                        <td className="p-2.5 pl-3 text-slate-200 font-medium max-w-xs truncate" title={item.question}>
                          {item.question}
                        </td>
                        <td className="p-2.5 font-mono">
                          {item.is_retrieval_mismatch ? (
                            <span className="text-rose-400 font-bold">Weak Match</span>
                          ) : (
                            <span className="text-emerald-400">Aligned ({Math.round(item.retrieval_topic_alignment * 100)}%)</span>
                          )}
                        </td>
                        <td className="p-2.5 font-mono">
                          {item.template_collision ? (
                            <span className="text-rose-400 font-bold">Collision</span>
                          ) : (
                            <span className="text-purple-400">{(item.voice_distinctiveness_score * 100).toFixed(0)}%</span>
                          )}
                        </td>
                        <td className="p-2.5 font-mono text-emerald-400">
                          {(item.faithfulness * 100).toFixed(0)}%
                        </td>
                        <td className="p-2.5 font-mono text-slate-300">
                          <span className="text-emerald-400">{item.grounded_sentences}</span> / <span className="text-cyan-400">{item.regenerated_sentences}</span> / <span className="text-amber-400">{item.unresolved_sentences}</span>
                        </td>
                        <td className="p-2.5 font-mono text-amber-400">
                          {(item.context_recall * 100).toFixed(0)}%
                        </td>
                        <td className="p-2.5 font-mono text-slate-400">
                          {item.latency_ms.toFixed(0)}ms
                        </td>
                        <td className="p-2.5 pr-3">
                          <span
                            className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-medium ${
                              item.status === 'PASS'
                                ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-500/30'
                                : 'bg-amber-950/60 text-amber-400 border border-amber-500/30'
                            }`}
                          >
                            {item.status === 'PASS' ? <CheckCircle className="w-3 h-3" /> : <AlertTriangle className="w-3 h-3" />}
                            <span>{item.status}</span>
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        <div className="text-right pt-4 border-t border-white/10">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
