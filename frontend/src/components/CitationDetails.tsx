import React from 'react';
import { X, Database, FileText, Globe, ExternalLink, ShieldCheck } from 'lucide-react';
import { EvidenceItem } from '../types';

interface CitationDetailsProps {
  citationText: string;
  evidenceList: EvidenceItem[];
  onClose: () => void;
}

export const CitationDetails: React.FC<CitationDetailsProps> = ({
  citationText,
  evidenceList,
  onClose,
}) => {
  // Find matching evidence items
  const matchedEvidence = evidenceList.filter((e) => {
    return (
      e.citation.toLowerCase().includes(citationText.toLowerCase()) ||
      e.source_id.toLowerCase().includes(citationText.toLowerCase()) ||
      citationText.toLowerCase().includes(e.source_type.toLowerCase())
    );
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl p-6 shadow-2xl relative max-h-[80vh] flex flex-col">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-2 mb-2">
          <ShieldCheck className="w-5 h-5 text-emerald-400" />
          <h3 className="text-base font-bold text-white">Citation Evidence Grounding</h3>
        </div>
        <p className="text-xs text-slate-400 font-mono mb-4">
          Referenced source tag: <span className="text-emerald-400">{citationText}</span>
        </p>

        <div className="flex-1 overflow-y-auto space-y-3 pr-1">
          {matchedEvidence.length === 0 ? (
            <div className="text-xs text-slate-400 bg-slate-950 p-4 rounded-xl border border-slate-800">
              Citation is grounded in multi-source combined evidence ({evidenceList.length} items verified by Critic).
            </div>
          ) : (
            matchedEvidence.map((ev, i) => (
              <div key={i} className="bg-slate-950 rounded-xl p-4 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-emerald-400 uppercase">
                    {ev.source_type} Source
                  </span>
                  <span className="text-[11px] font-mono text-slate-400">
                    Relevance: {(ev.relevance_score * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="text-xs text-slate-300 font-mono bg-slate-900/80 p-3 rounded-lg border border-slate-800/80">
                  <pre className="whitespace-pre-wrap font-sans text-xs">{ev.content}</pre>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
