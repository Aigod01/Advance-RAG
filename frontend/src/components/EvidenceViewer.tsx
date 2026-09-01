import React, { useState } from 'react';
import {
  Layers,
  Database,
  FileText,
  Globe,
  ExternalLink,
  ShieldCheck,
  Tag,
  AlertCircle
} from 'lucide-react';
import { EvidenceItem } from '../types';

interface EvidenceViewerProps {
  evidence: EvidenceItem[];
  onSelectCitation?: (citation: string) => void;
}

export const EvidenceViewer: React.FC<EvidenceViewerProps> = ({
  evidence,
  onSelectCitation,
}) => {
  const [activeFilter, setActiveFilter] = useState<'all' | 'database' | 'document' | 'web'>('all');

  const filteredEvidence = evidence.filter((e) => {
    if (activeFilter === 'all') return true;
    return e.source_type.toLowerCase() === activeFilter;
  });

  const getSourceIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'database':
        return <Database className="w-3.5 h-3.5 text-blue-400" />;
      case 'document':
        return <FileText className="w-3.5 h-3.5 text-emerald-400" />;
      case 'web':
        return <Globe className="w-3.5 h-3.5 text-amber-400" />;
      default:
        return <Layers className="w-3.5 h-3.5 text-slate-400" />;
    }
  };

  const getSourceBadgeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'database':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      case 'document':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      case 'web':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      default:
        return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
    }
  };

  return (
    <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-5 shadow-xl flex flex-col h-full">
      <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Layers className="w-5 h-5 text-emerald-400" />
          <h3 className="font-semibold text-sm text-slate-200">
            Unified Normalized Evidence
          </h3>
          <span className="text-xs font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded-full">
            {evidence.length}
          </span>
        </div>

        {/* Source Filter Tabs */}
        <div className="flex space-x-1 bg-slate-950 p-1 rounded-lg border border-slate-800 text-[11px]">
          {(['all', 'database', 'document', 'web'] as const).map((filter) => (
            <button
              key={filter}
              onClick={() => setActiveFilter(filter)}
              className={`px-2.5 py-1 rounded capitalize transition-all ${
                activeFilter === filter
                  ? 'bg-emerald-600 text-white font-medium shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {filter}
            </button>
          ))}
        </div>
      </div>

      {filteredEvidence.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-slate-500 text-xs text-center py-10">
          No evidence items available for this filter.
        </div>
      ) : (
        <div className="space-y-3 overflow-y-auto max-h-[600px] pr-1">
          {filteredEvidence.map((item, idx) => (
            <div
              key={item.evidence_id || idx}
              className="bg-slate-950/80 rounded-xl p-3.5 border border-slate-800/80 hover:border-slate-700 transition-all group"
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span
                    className={`flex items-center space-x-1 text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full border ${getSourceBadgeColor(
                      item.source_type
                    )}`}
                  >
                    {getSourceIcon(item.source_type)}
                    <span>{item.source_type}</span>
                  </span>
                  <span className="text-xs font-mono text-slate-300 truncate max-w-[200px]" title={item.citation}>
                    {item.citation}
                  </span>
                </div>

                <div className="flex items-center space-x-2 text-[10px] font-mono">
                  <span className="text-slate-400">
                    Rel: <span className="text-emerald-400 font-bold">{(item.relevance_score * 100).toFixed(0)}%</span>
                  </span>
                  <span className="text-slate-500">•</span>
                  <span className="text-slate-400">
                    Trust: <span className="text-blue-400 font-bold">{(item.source_quality * 100).toFixed(0)}%</span>
                  </span>
                </div>
              </div>

              {/* Body Content */}
              <div className="text-xs text-slate-300 font-sans leading-relaxed bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/50">
                <pre className="whitespace-pre-wrap font-sans text-xs break-words">
                  {item.content}
                </pre>
              </div>

              {/* Footer / Metadata tag */}
              {item.metadata && Object.keys(item.metadata).length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1.5 text-[10px] font-mono text-slate-500">
                  {item.metadata.filename && (
                    <span className="bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                      File: {item.metadata.filename}
                    </span>
                  )}
                  {item.metadata.page && (
                    <span className="bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                      Page: {item.metadata.page}
                    </span>
                  )}
                  {item.metadata.domain && (
                    <span className="bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                      Domain: {item.metadata.domain}
                    </span>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
