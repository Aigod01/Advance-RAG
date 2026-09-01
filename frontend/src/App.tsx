import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { ChatView } from './components/ChatView';
import { StrategyDashboard } from './components/StrategyDashboard';
import { EvaluationView } from './components/EvaluationView';
import { DocumentUpload } from './components/DocumentUpload';
import { ChatMessage, TraceEvent, EvidenceItem } from './types';
import { checkHealth, sendChatMessage } from './api/client';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chat' | 'strategy' | 'evaluation' | 'documents'>('chat');
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentTrace, setCurrentTrace] = useState<TraceEvent[]>([]);
  const [currentEvidence, setCurrentEvidence] = useState<EvidenceItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const h = await checkHealth();
        setSystemHealth(h);
      } catch (e) {
        console.error('Health check error', e);
      }
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = async (queryText: string) => {
    const userMsgId = `user_${Date.now()}`;
    const assistantMsgId = `asst_${Date.now()}`;

    const userMessage: ChatMessage = {
      id: userMsgId,
      sender: 'user',
      content: queryText,
      timestamp: new Date().toLocaleTimeString(),
    };

    const pendingAssistantMessage: ChatMessage = {
      id: assistantMsgId,
      sender: 'assistant',
      content: 'Analyzing query and executing multi-agent orchestration...',
      timestamp: new Date().toLocaleTimeString(),
      loading: true,
    };

    setMessages((prev) => [...prev, userMessage, pendingAssistantMessage]);
    setCurrentTrace([]);
    setCurrentEvidence([]);
    setIsLoading(true);

    try {
      const result = await sendChatMessage(queryText, (traceEvt: TraceEvent) => {
        setCurrentTrace((prev) => {
          // Avoid duplicate event_ids
          if (prev.some((e) => e.event_id === traceEvt.event_id)) return prev;
          return [...prev, traceEvt];
        });
      });

      if (result) {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMsgId
              ? {
                  ...msg,
                  content: result.answer || 'Response generated successfully.',
                  run_id: result.run_id,
                  confidence: result.confidence,
                  citations: result.citations,
                  evidence: result.evidence,
                  execution_time_ms: result.execution_time_ms,
                  loading: false,
                }
              : msg
          )
        );
        if (result.evidence) {
          setCurrentEvidence(result.evidence);
        }
      }
    } catch (err: any) {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMsgId
            ? {
                ...msg,
                content: `Error executing multi-agent workflow: ${err.message}`,
                loading: false,
              }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        systemHealth={systemHealth}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'chat' && (
          <ChatView
            messages={messages}
            currentTrace={currentTrace}
            currentEvidence={currentEvidence}
            isLoading={isLoading}
            onSendMessage={handleSendMessage}
          />
        )}

        {activeTab === 'strategy' && <StrategyDashboard />}

        {activeTab === 'evaluation' && <EvaluationView />}

        {activeTab === 'documents' && <DocumentUpload />}
      </main>
    </div>
  );
};

export default App;
