import React, { useState, useEffect, useRef } from 'react';
import { Send, Sparkles, RefreshCw, AlertCircle, BookOpen, Layers } from 'lucide-react';
import Header from './components/Header';
import ThinkerSelector from './components/ThinkerSelector';
import ThinkerSidebar from './components/ThinkerSidebar';
import ChatMessage from './components/ChatMessage';
import QuerySuggestions from './components/QuerySuggestions';
import EvaluationModal from './components/EvaluationModal';
import { fetchThinkers, sendQuery, checkHealth } from './services/api';

export default function App() {
  const [thinkers, setThinkers] = useState([]);
  const [selectedThinkers, setSelectedThinkers] = useState([]);
  const [messages, setMessages] = useState([]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isEvalOpen, setIsEvalOpen] = useState(false);
  const [sessionId, setSessionId] = useState(() => `session_${Date.now()}`);
  const [error, setError] = useState(null);

  const messagesEndRef = useRef(null);

  // Initialize Thinkers & Health
  useEffect(() => {
    async function init() {
      try {
        const health = await checkHealth();
        setIsOnline(health.status === 'healthy');

        const data = await fetchThinkers();
        setThinkers(data);
      } catch (err) {
        console.error('Init error:', err);
        setIsOnline(false);
      }
    }
    init();
  }, []);

  // Auto scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleToggleThinker = (id) => {
    setSelectedThinkers((prev) =>
      prev.includes(id) ? prev.filter((t) => t !== id) : [...prev, id]
    );
  };

  const handleSelectAllThinkers = () => {
    if (selectedThinkers.length === 0 || selectedThinkers.length === thinkers.length) {
      // Clear to allow custom picking
      setSelectedThinkers([]);
    } else {
      setSelectedThinkers(thinkers.map((t) => t.id));
    }
  };

  const handleSend = async (queryText = inputQuery, overrideThinkers = null) => {
    const q = (queryText || '').trim();
    if (!q || loading) return;

    setError(null);
    setInputQuery('');
    setLoading(true);

    const activeThinkers = overrideThinkers || (selectedThinkers.length > 0 ? selectedThinkers : null);

    // Append user message immediately
    const userMsg = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: q,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const response = await sendQuery({
        question: q,
        thinkers: activeThinkers,
        sessionId: sessionId,
      });

      const assistantMsg = {
        id: `assistant_${Date.now()}`,
        role: 'assistant',
        content: response.answer,
        data: response,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error('Query error:', err);
      setError(err.message || 'Failed to generate philosophical response.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setError(null);
    setSessionId(`session_${Date.now()}`);
  };

  return (
    <div className="min-h-screen flex flex-col justify-between text-slate-100">
      {/* Top Header */}
      <Header
        isOnline={isOnline}
        onOpenEval={() => setIsEvalOpen(true)}
        onToggleSidebar={() => setIsSidebarOpen(true)}
        onNewChat={handleNewChat}
      />

      {/* Main Container */}
      <main className="flex-1 w-full max-w-5xl mx-auto px-4 sm:px-6 py-6 flex flex-col justify-between">
        {/* Messages or Welcome Hero */}
        {messages.length === 0 ? (
          <div className="my-auto py-8 space-y-8 text-center max-w-2xl mx-auto">
            <div className="space-y-3">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-mono">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Multi-Thinker Dialectical Engine</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold font-philosophy tracking-tight text-white">
                Interrogate the Great Minds
              </h2>
              <p className="text-sm text-slate-400 leading-relaxed font-sans">
                Pose foundational ethical, existential, and metaphysical questions. Our LangGraph pipeline simultaneously consults the primary source works of Marcus Aurelius, Nietzsche, Kant, Aristotle, and Laozi.
              </p>
            </div>

            {/* Thinker Chips */}
            <div className="glass-panel p-4 rounded-2xl border border-white/10 text-left">
              <ThinkerSelector
                thinkers={thinkers}
                selectedThinkers={selectedThinkers}
                onToggleThinker={handleToggleThinker}
                onSelectAll={handleSelectAllThinkers}
              />
            </div>

            {/* Prompt Suggestion Cards */}
            <QuerySuggestions
              onSelectQuery={(q, th) => {
                setSelectedThinkers(th);
                handleSend(q, th);
              }}
            />
          </div>
        ) : (
          <div className="space-y-6 pb-20">
            {/* Thinker Selector Bar while chatting */}
            <div className="glass-panel p-3.5 rounded-xl border border-white/10">
              <ThinkerSelector
                thinkers={thinkers}
                selectedThinkers={selectedThinkers}
                onToggleThinker={handleToggleThinker}
                onSelectAll={handleSelectAllThinkers}
              />
            </div>

            {/* Message Thread */}
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}

            {/* Skeleton Loader during generation */}
            {loading && (
              <div className="flex items-start gap-3.5 my-6 animate-pulse">
                <div className="w-9 h-9 rounded-xl bg-slate-800 flex items-center justify-center text-slate-600 font-bold">
                  🏛️
                </div>
                <div className="flex-1 glass-panel rounded-2xl p-6 border border-white/10 space-y-4">
                  <div className="flex items-center gap-2">
                    <RefreshCw className="w-4 h-4 text-amber-400 animate-spin" />
                    <span className="text-xs font-mono text-amber-300">
                      LangGraph synthesizing parallel thinker retrievals & verifying citations...
                    </span>
                  </div>
                  <div className="h-4 bg-slate-800 rounded w-3/4"></div>
                  <div className="h-4 bg-slate-800 rounded w-5/6"></div>
                  <div className="h-4 bg-slate-800 rounded w-2/3"></div>
                  <div className="grid grid-cols-2 gap-3 pt-2">
                    <div className="h-24 bg-slate-900/60 rounded-xl border border-slate-800"></div>
                    <div className="h-24 bg-slate-900/60 rounded-xl border border-slate-800"></div>
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="flex items-center gap-2.5 p-4 rounded-xl bg-rose-950/50 border border-rose-500/40 text-rose-300 text-xs">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
                <span>{error}</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Input Bar */}
        <div className="sticky bottom-4 z-20 w-full glass-panel rounded-2xl border border-white/15 p-2 shadow-2xl mt-4">
          <div className="relative flex items-center">
            <textarea
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a philosophical inquiry (e.g. 'What is the nature of suffering and free will?')..."
              rows={1}
              className="w-full bg-transparent px-4 py-3 text-sm sm:text-base text-white placeholder:text-slate-500 focus:outline-none resize-none font-sans"
            />
            <button
              onClick={() => handleSend()}
              disabled={loading || !inputQuery.trim()}
              className={`p-3 rounded-xl transition-all shrink-0 flex items-center justify-center ${
                inputQuery.trim() && !loading
                  ? 'bg-gradient-to-r from-amber-500 to-rose-500 hover:from-amber-400 hover:to-rose-400 text-white shadow-lg shadow-amber-500/20'
                  : 'bg-slate-800 text-slate-600 cursor-not-allowed'
              }`}
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </main>

      {/* Thinker Stats Sidebar Drawer */}
      <ThinkerSidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        thinkers={thinkers}
      />

      {/* Evaluation Dashboard Modal */}
      <EvaluationModal
        isOpen={isEvalOpen}
        onClose={() => setIsEvalOpen(false)}
      />
    </div>
  );
}
