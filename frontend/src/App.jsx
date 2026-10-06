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
  const [isDarkMode, setIsDarkMode] = useState(false);

  const messagesEndRef = useRef(null);

  // Sync dark class on document element
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

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
    <div className="min-h-screen flex flex-col justify-between text-[#2B2419]">
      {/* Top Header */}
      <Header
        isOnline={isOnline}
        onOpenEval={() => setIsEvalOpen(true)}
        onToggleSidebar={() => setIsSidebarOpen(true)}
        onNewChat={handleNewChat}
        isDarkMode={isDarkMode}
        onToggleTheme={() => setIsDarkMode(!isDarkMode)}
      />

      {/* Main Container */}
      <main className="flex-1 w-full max-w-5xl mx-auto px-4 sm:px-6 py-8 flex flex-col justify-between">
        {/* Messages or Welcome Hero */}
        {messages.length === 0 ? (
          <div className="my-auto py-8 space-y-8 text-center max-w-2xl mx-auto">
            <div className="space-y-4">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#FDF4F4] border border-[#8B2E2E]/40 shadow-sm">
                <span className="w-2 h-2 rounded-full bg-[#8B2E2E]" />
                <span className="text-[11.5px] font-philosophy font-semibold text-[#8B2E2E]">Comparative Philosophical Dialectic</span>
              </div>
              
              {/* Large Editorial Headline */}
              <h2 className="text-3xl sm:text-5xl font-bold font-editorial-heading tracking-tight text-[#2B2419] leading-tight">
                Study the past. <br className="hidden sm:inline" />
                <span className="italic font-serif text-[#8B2E2E]">Interrogate the great minds.</span>
              </h2>

              <p className="text-sm sm:text-base text-[#564936] leading-relaxed font-serif italic max-w-xl mx-auto">
                Pose foundational inquiries into ethics, virtue, suffering, and human purpose. Our LangGraph council consults primary texts from Marcus Aurelius, Nietzsche, Kant, Aristotle, and Laozi.
              </p>
            </div>

            {/* Thinker Chips Selector Panel */}
            <div className="parchment-panel p-4 rounded-xl border border-[#B8995C]/50 border-l-4 border-l-[#8B2E2E] text-left shadow-parchment-sm">
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
            <div className="parchment-panel p-3.5 rounded-xl border border-[#B8995C]/50 border-l-4 border-l-[#8B2E2E] shadow-parchment-sm">
              <ThinkerSelector
                thinkers={thinkers}
                selectedThinkers={selectedThinkers}
                onToggleThinker={handleToggleThinker}
                onSelectAll={handleSelectAllThinkers}
              />
            </div>

            {/* Message Thread */}
            {messages.map((msg) => (
              <ChatMessage 
                key={msg.id} 
                message={msg} 
                onSelectQuery={(q) => handleSend(q)}
              />
            ))}

            {/* Skeleton Loader during generation */}
            {loading && (
              <div className="flex items-start gap-3.5 my-6 animate-pulse">
                <div className="w-9 h-9 rounded-full bg-[#FAF7F0] border-2 border-[#B8995C] flex items-center justify-center text-base shadow-inner-gold shrink-0">
                  🏛️
                </div>
                <div className="flex-1 parchment-panel rounded-xl p-6 border border-[#B8995C]/50 shadow-parchment-sm space-y-4">
                  <div className="flex items-center gap-2">
                    <RefreshCw className="w-4 h-4 text-[#8B2E2E] animate-spin" />
                    <span className="text-xs font-serif italic text-[#8B2E2E] font-medium">
                      LangGraph council synthesizing parallel primary texts & verifying citations...
                    </span>
                  </div>
                  <div className="h-4 bg-[#EFE8DD] rounded w-3/4"></div>
                  <div className="h-4 bg-[#EFE8DD] rounded w-5/6"></div>
                  <div className="h-4 bg-[#EFE8DD] rounded w-2/3"></div>
                  <div className="grid grid-cols-2 gap-3 pt-2">
                    <div className="h-24 bg-[#F4EFE6] rounded-xl border border-[#B8995C]/30"></div>
                    <div className="h-24 bg-[#F4EFE6] rounded-xl border border-[#B8995C]/30"></div>
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="flex items-center gap-2.5 p-4 rounded-xl bg-[#FDF4F4] border border-[#8B2E2E]/60 text-[#8B2E2E] text-xs font-serif font-semibold">
                <AlertCircle className="w-4 h-4 shrink-0 text-[#8B2E2E]" />
                <span>{error}</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Input Bar - Classic Writing Desk / Console with Gold Border & Ink Button */}
        <div className="sticky bottom-4 z-20 w-full parchment-panel rounded-xl border-2 border-[#B8995C] p-2 shadow-parchment-md mt-4 bg-[#FAF7F0]">
          <div className="relative flex items-center">
            <textarea
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Inquire of the traditions (e.g. 'What is the nature of suffering and free will?')..."
              rows={1}
              className="w-full bg-transparent px-4 py-3 text-sm sm:text-base text-[#2B2419] placeholder:text-[#8C7D6B] placeholder:italic focus:outline-none resize-none font-serif leading-relaxed"
            />
            {/* Rich Burgundy Send Button with Gold Linework Accent */}
            <button
              onClick={() => handleSend()}
              disabled={loading || !inputQuery.trim()}
              className={`p-3 rounded-lg transition-all shrink-0 flex items-center justify-center border font-serif ${
                inputQuery.trim() && !loading
                  ? 'btn-burgundy shadow-sm'
                  : 'bg-[#EFE8DD] text-[#AD997B] border-[#DACDB8] cursor-not-allowed'
              }`}
              title="Submit Inquiry"
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
