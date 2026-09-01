import React from 'react';
import {
  BrainCircuit,
  MessageSquare,
  Sparkles,
  BarChart3,
  FileText,
  Activity,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

interface HeaderProps {
  activeTab: 'chat' | 'strategy' | 'evaluation' | 'documents';
  setActiveTab: (tab: 'chat' | 'strategy' | 'evaluation' | 'documents') => void;
  systemHealth: {
    status?: string;
    llm_provider?: string;
    database_connected?: boolean;
    qdrant_points?: number;
    bm25_chunks?: number;
  } | null;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  systemHealth,
}) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <BrainCircuit className="w-6 h-6 text-slate-950 font-bold" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-tight text-white">
                Multi-Agent Collaborative RAG
              </span>
              <span className="text-[10px] font-semibold tracking-wide uppercase px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                Adaptive v1.0
              </span>
            </div>
            <p className="text-xs text-slate-400">
              LangGraph Orchestration • Hybrid RAG • Contextual Bandit Learning
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 bg-slate-950/60 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'chat'
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Chat & Orchestration</span>
          </button>

          <button
            onClick={() => setActiveTab('strategy')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'strategy'
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Strategy Memory</span>
          </button>

          <button
            onClick={() => setActiveTab('evaluation')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'evaluation'
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Research Benchmark</span>
          </button>

          <button
            onClick={() => setActiveTab('documents')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'documents'
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Documents Corpus</span>
          </button>
        </nav>

        {/* Health status */}
        <div className="hidden lg:flex items-center space-x-4 text-xs">
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-800/60 border border-slate-700/60">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-slate-300 font-mono">
              {systemHealth?.database_connected ? 'DB: Postgres/SQLite' : 'DB: Offline'}
            </span>
          </div>

          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-800/60 border border-slate-700/60">
            <span className="text-slate-400">RAG Chunks:</span>
            <span className="text-emerald-400 font-mono font-semibold">
              {systemHealth?.qdrant_points ?? 0}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
