import React, { useState } from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Clock,
  ChevronDown,
  ChevronRight,
  Database,
  FileSearch,
  Globe,
  ShieldCheck,
  Sparkles,
  GitBranch
} from 'lucide-react';
import { TraceEvent } from '../types';

interface AgentTimelineProps {
  traceEvents: TraceEvent[];
  isLoading?: boolean;
}

export const AgentTimeline: React.FC<AgentTimelineProps> = ({
  traceEvents,
  isLoading,
}) => {
  const [expandedEvents, setExpandedEvents] = useState<Record<string, boolean>>({});

  const toggleExpand = (id: string) => {
    setExpandedEvents((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const getAgentIcon = (agent: string) => {
    switch (agent.toLowerCase()) {
      case 'planner':
        return <GitBranch className="w-4 h-4 text-purple-400" />;
      case 'database_agent':
        return <Database className="w-4 h-4 text-blue-400" />;
      case 'document_agent':
        return <FileSearch className="w-4 h-4 text-emerald-400" />;
      case 'web_agent':
        return <Globe className="w-4 h-4 text-amber-400" />;
      case 'critic':
        return <ShieldCheck className="w-4 h-4 text-rose-400" />;
      case 'retry_router':
        return <RotateCcw className="w-4 h-4 text-orange-400" />;
      case 'synthesizer':
        return <Sparkles className="w-4 h-4 text-teal-400" />;
      default:
        return <Clock className="w-4 h-4 text-slate-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      case 'retrying':
        return <RotateCcw className="w-4 h-4 text-orange-400 animate-spin" />;
      case 'started':
        return <span className="w-3.5 h-3.5 rounded-full border-2 border-emerald-400 border-t-transparent animate-spin" />;
      default:
        return <CheckCircle2 className="w-4 h-4 text-slate-500" />;
    }
  };

  return (
    <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-5 shadow-xl">
      <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <GitBranch className="w-5 h-5 text-emerald-400" />
          <h3 className="font-semibold text-sm text-slate-200">
            Multi-Agent LangGraph Timeline
          </h3>
        </div>
        {isLoading && (
          <span className="flex items-center space-x-1.5 text-xs text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20 animate-pulse">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            <span>Executing Workflow...</span>
          </span>
        )}
      </div>

      {traceEvents.length === 0 ? (
        <div className="py-8 text-center text-slate-500 text-xs">
          No active execution traces. Submit a query to observe multi-agent orchestration.
        </div>
      ) : (
        <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
          {traceEvents.map((evt, idx) => {
            const hasDetails = evt.details && Object.keys(evt.details).length > 0;
            const isExpanded = !!expandedEvents[evt.event_id];

            return (
              <div key={evt.event_id || idx} className="relative group">
                {/* Node icon anchor on timeline line */}
                <div className="absolute -left-6 top-0.5 w-5 h-5 rounded-full bg-slate-950 border border-slate-700 flex items-center justify-center shadow">
                  {getStatusBadge(evt.status)}
                </div>

                <div className="bg-slate-950/70 hover:bg-slate-950 rounded-xl p-3 border border-slate-800/80 transition-all">
                  <div
                    className="flex items-center justify-between cursor-pointer select-none"
                    onClick={() => hasDetails && toggleExpand(evt.event_id)}
                  >
                    <div className="flex items-center space-x-2.5">
                      <div className="p-1 rounded bg-slate-900 border border-slate-800">
                        {getAgentIcon(evt.agent)}
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-semibold text-slate-200 capitalize">
                            {evt.agent.replace('_', ' ')}
                          </span>
                          <span className="text-[10px] text-slate-500 font-mono">
                            {evt.step}
                          </span>
                        </div>
                        <p className="text-xs text-slate-300 mt-0.5 font-sans">
                          {evt.message}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <span className="text-[10px] font-mono text-slate-500">
                        {evt.timestamp}
                      </span>
                      {hasDetails && (
                        <button className="text-slate-400 hover:text-slate-200 p-0.5">
                          {isExpanded ? (
                            <ChevronDown className="w-3.5 h-3.5" />
                          ) : (
                            <ChevronRight className="w-3.5 h-3.5" />
                          )}
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Expanded metadata drawer */}
                  {isExpanded && hasDetails && (
                    <div className="mt-3 pt-2.5 border-t border-slate-800/60 text-xs">
                      <pre className="p-2.5 rounded-lg bg-slate-900/90 text-slate-300 font-mono text-[11px] overflow-x-auto max-h-48">
                        {JSON.stringify(evt.details, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
