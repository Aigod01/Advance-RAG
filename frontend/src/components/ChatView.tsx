import React, { useState } from 'react';
import {
  Send,
  Sparkles,
  Bot,
  User,
  ShieldCheck,
  ThumbsUp,
  ThumbsDown,
  Copy,
  Check,
  Layers,
  ArrowRight,
  Database,
  FileText,
  Globe
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ChatMessage, EvidenceItem, TraceEvent } from '../types';
import { AgentTimeline } from './AgentTimeline';
import { EvidenceViewer } from './EvidenceViewer';
import { CitationDetails } from './CitationDetails';
import { FeedbackModal } from './FeedbackModal';

interface ChatViewProps {
  messages: ChatMessage[];
  currentTrace: TraceEvent[];
  currentEvidence: EvidenceItem[];
  isLoading: boolean;
  onSendMessage: (query: string) => void;
}

const PRESET_QUERIES = [
  "Our laptop sales fell last quarter. Tell me how much they fell, identify reasons from internal reports, compare this with the current industry trend, and tell me whether it looks company-specific or market-wide.",
  "What is the total revenue and units sold for each product category in our database?",
  "What are the hardware specifications and volume tier discounts for the ApexBook Pro 16?",
  "What was the global PC market shipment decline percentage reported by IDC in Q3 2025?",
];

export const ChatView: React.FC<ChatViewProps> = ({
  messages,
  currentTrace,
  currentEvidence,
  isLoading,
  onSendMessage,
}) => {
  const [inputQuery, setInputQuery] = useState('');
  const [selectedCitation, setSelectedCitation] = useState<string | null>(null);
  const [feedbackRun, setFeedbackRun] = useState<{
    runId: string;
    query: string;
    answer: string;
    rating: number;
  } | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputQuery.trim() || isLoading) return;
    onSendMessage(inputQuery.trim());
    setInputQuery('');
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-6rem)]">
      {/* Left / Center Column: Chat Stream */}
      <div className="lg:col-span-7 flex flex-col bg-slate-900/90 rounded-2xl border border-slate-800 shadow-xl overflow-hidden">
        {/* Messages Scroll Area */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="py-12 px-4 text-center max-w-xl mx-auto space-y-4">
              <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
                <Sparkles className="w-8 h-8 text-slate-950" />
              </div>
              <h2 className="text-lg font-bold text-white">
                Multi-Agent Collaborative RAG Ready
              </h2>
              <p className="text-xs text-slate-400 leading-relaxed">
                Decomposes complex enterprise questions across Structured SQL Databases, Internal Documents (PDF/MD), and External Web Intelligence.
              </p>

              {/* Preset prompt pills */}
              <div className="pt-4 text-left space-y-2">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                  Recommended Benchmark Questions:
                </span>
                <div className="space-y-2">
                  {PRESET_QUERIES.map((preset, i) => (
                    <button
                      key={i}
                      onClick={() => onSendMessage(preset)}
                      className="w-full text-left p-3 rounded-xl bg-slate-950/80 hover:bg-slate-950 border border-slate-800 hover:border-emerald-500/50 text-xs text-slate-300 transition-all flex items-center justify-between group"
                    >
                      <span className="line-clamp-2 pr-2">{preset}</span>
                      <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-emerald-400 flex-shrink-0 transition-transform group-hover:translate-x-0.5" />
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex space-x-3.5 ${
                  msg.sender === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {msg.sender === 'assistant' && (
                  <div className="w-8 h-8 rounded-xl bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center flex-shrink-0 shadow">
                    <Bot className="w-4 h-4 text-emerald-400" />
                  </div>
                )}

                <div
                  className={`max-w-[85%] rounded-2xl p-4 text-xs leading-relaxed ${
                    msg.sender === 'user'
                      ? 'bg-emerald-600 text-white rounded-br-none shadow-md shadow-emerald-600/20'
                      : 'bg-slate-950/90 text-slate-200 border border-slate-800 rounded-bl-none shadow-lg'
                  }`}
                >
                  {/* Message body */}
                  <div className="prose prose-invert prose-xs max-w-none">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        table: ({ node, ...props }) => (
                          <div className="overflow-x-auto my-3">
                            <table className="min-w-full divide-y divide-slate-800 border border-slate-800 rounded-lg text-xs" {...props} />
                          </div>
                        ),
                        th: ({ node, ...props }) => (
                          <th className="bg-slate-900 px-2.5 py-1.5 font-semibold text-slate-300" {...props} />
                        ),
                        td: ({ node, ...props }) => (
                          <td className="px-2.5 py-1.5 border-t border-slate-800 text-slate-400" {...props} />
                        ),
                        p: ({ node, children, ...props }) => {
                          return <p className="mb-2 leading-relaxed" {...props}>{children}</p>;
                        }
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  </div>

                  {/* Assistant Footer metadata */}
                  {msg.sender === 'assistant' && !msg.loading && (
                    <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                      <div className="flex items-center space-x-3">
                        {msg.confidence !== undefined && (
                          <span
                            className="flex items-center space-x-1 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                            title="Calibrated Confidence Formula: 0.35*Relevance + 0.35*Critic + 0.20*Agreement + 0.10*Citations"
                          >
                            <ShieldCheck className="w-3.5 h-3.5" />
                            <span>Confidence: {(msg.confidence * 100).toFixed(0)}%</span>
                          </span>
                        )}

                        {msg.execution_time_ms && (
                          <span>{(msg.execution_time_ms / 1000).toFixed(2)}s</span>
                        )}
                      </div>

                      {/* Action buttons */}
                      <div className="flex items-center space-x-1 text-slate-400">
                        <button
                          onClick={() => handleCopy(msg.id, msg.content)}
                          className="p-1 hover:text-white rounded hover:bg-slate-800"
                          title="Copy answer"
                        >
                          {copiedId === msg.id ? (
                            <Check className="w-3.5 h-3.5 text-emerald-400" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                        </button>

                        <button
                          onClick={() =>
                            setFeedbackRun({
                              runId: msg.run_id || 'run_latest',
                              query: '',
                              answer: msg.content,
                              rating: 1,
                            })
                          }
                          className="p-1 hover:text-emerald-400 rounded hover:bg-slate-800"
                          title="Provide positive feedback (+1 reward)"
                        >
                          <ThumbsUp className="w-3.5 h-3.5" />
                        </button>

                        <button
                          onClick={() =>
                            setFeedbackRun({
                              runId: msg.run_id || 'run_latest',
                              query: '',
                              answer: msg.content,
                              rating: -1,
                            })
                          }
                          className="p-1 hover:text-rose-400 rounded hover:bg-slate-800"
                          title="Provide negative feedback (-1 reward)"
                        >
                          <ThumbsDown className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                {msg.sender === 'user' && (
                  <div className="w-8 h-8 rounded-xl bg-slate-800 flex items-center justify-center flex-shrink-0 shadow">
                    <User className="w-4 h-4 text-slate-300" />
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSubmit} className="p-3 bg-slate-950/80 border-t border-slate-800">
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              placeholder="Ask a multi-source question spanning DB, Internal Documents, and Web..."
              disabled={isLoading}
              className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition"
            />
            <button
              type="submit"
              disabled={!inputQuery.trim() || isLoading}
              className="p-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl shadow-lg shadow-emerald-600/30 transition disabled:opacity-40"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>

      {/* Right Column: Live Agent Timeline & Evidence Drawer */}
      <div className="lg:col-span-5 flex flex-col space-y-6 overflow-y-auto max-h-[calc(100vh-6rem)] pr-1">
        <AgentTimeline traceEvents={currentTrace} isLoading={isLoading} />
        <EvidenceViewer
          evidence={currentEvidence}
          onSelectCitation={(c) => setSelectedCitation(c)}
        />
      </div>

      {/* Citation details modal */}
      {selectedCitation && (
        <CitationDetails
          citationText={selectedCitation}
          evidenceList={currentEvidence}
          onClose={() => setSelectedCitation(null)}
        />
      )}

      {/* User Feedback Modal */}
      {feedbackRun && (
        <FeedbackModal
          isOpen={true}
          onClose={() => setFeedbackRun(null)}
          runId={feedbackRun.runId}
          query={feedbackRun.query}
          finalAnswer={feedbackRun.answer}
          initialRating={feedbackRun.rating}
        />
      )}
    </div>
  );
};
