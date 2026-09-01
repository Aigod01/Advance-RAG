import React, { useEffect, useState } from 'react';
import {
  BarChart3,
  Play,
  CheckCircle2,
  TrendingUp,
  Layers,
  FlaskConical,
  Award,
  Zap,
  Info
} from 'lucide-react';
import { EvaluationResults } from '../types';
import { getEvaluationResults, runBenchmarkEvaluation, getRetrievalAblations } from '../api/client';

export const EvaluationView: React.FC = () => {
  const [results, setResults] = useState<EvaluationResults | null>(null);
  const [ablations, setAblations] = useState<any | null>(null);
  const [running, setRunning] = useState(false);

  const fetchResults = async () => {
    try {
      const data = await getEvaluationResults();
      setResults(data);
      const abl = await getRetrievalAblations();
      setAblations(abl);
    } catch (e) {
      console.error('Failed to load evaluation data', e);
    }
  };

  const handleRunEvaluation = async () => {
    setRunning(true);
    try {
      const data = await runBenchmarkEvaluation(5);
      setResults(data);
    } catch (e) {
      console.error('Benchmark execution error', e);
    } finally {
      setRunning(false);
    }
  };

  useEffect(() => {
    fetchResults();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto py-2">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2.5">
            <FlaskConical className="w-6 h-6 text-purple-400" />
            <span>Research & Comparative Benchmark Suite</span>
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Empirical evaluation proving adaptive multi-agent collaboration improvements across 4 RAG architectures.
          </p>
        </div>

        <button
          onClick={handleRunEvaluation}
          disabled={running}
          className="flex items-center space-x-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-emerald-600/30 transition disabled:opacity-60"
        >
          <Play className={`w-3.5 h-3.5 ${running ? 'animate-spin' : ''}`} />
          <span>{running ? 'Running Benchmark...' : 'Run Benchmark (5 Tests)'}</span>
        </button>
      </div>

      {/* 4 Systems Definition Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
        <div className="bg-slate-900/80 p-3.5 rounded-xl border border-slate-800">
          <div className="font-semibold text-slate-300 mb-1">1. Baseline RAG</div>
          <p className="text-slate-400 text-[11px]">Single document retriever (BM25) + single direct LLM call.</p>
        </div>
        <div className="bg-slate-900/80 p-3.5 rounded-xl border border-slate-800">
          <div className="font-semibold text-blue-300 mb-1">2. Agentic RAG</div>
          <p className="text-slate-400 text-[11px]">Single agent with query rewriting and retrieval retries.</p>
        </div>
        <div className="bg-slate-900/80 p-3.5 rounded-xl border border-slate-800">
          <div className="font-semibold text-purple-300 mb-1">3. Multi-Agent RAG</div>
          <p className="text-slate-400 text-[11px]">Specialized DB + Document + Web agents with Critic verification.</p>
        </div>
        <div className="bg-slate-900/80 p-3.5 rounded-xl border border-emerald-500/30 bg-emerald-950/10">
          <div className="font-semibold text-emerald-400 mb-1">4. Adaptive Collaborative</div>
          <p className="text-slate-400 text-[11px]">Multi-Agent + shared Strategy Memory policy learning.</p>
        </div>
      </div>

      {/* Comparison Results Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl">
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <Award className="w-5 h-5 text-emerald-400" />
            <h3 className="font-semibold text-sm text-slate-200">
              Benchmark Metrics Comparison Matrix
            </h3>
          </div>
          <span className="text-xs font-mono text-slate-400">
            N = {results?.benchmark_size ?? 0} benchmark queries
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 font-mono uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-3 px-3">System Architecture</th>
                <th className="py-3 px-3">Recall</th>
                <th className="py-3 px-3">Hit Rate</th>
                <th className="py-3 px-3">MRR</th>
                <th className="py-3 px-3">Groundedness</th>
                <th className="py-3 px-3">Citation Coverage</th>
                <th className="py-3 px-3">Avg Latency</th>
                <th className="py-3 px-3">Avg Retries</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {results?.summary?.map((row, idx) => {
                const isAdaptive = row.system.includes('Adaptive');
                return (
                  <tr
                    key={row.system || idx}
                    className={`transition ${
                      isAdaptive ? 'bg-emerald-950/20 font-semibold' : 'hover:bg-slate-800/30'
                    }`}
                  >
                    <td className="py-3.5 px-3 flex items-center space-x-2">
                      {isAdaptive && <Zap className="w-4 h-4 text-emerald-400" />}
                      <span className={isAdaptive ? 'text-emerald-300 font-bold' : 'text-slate-200'}>
                        {row.system}
                      </span>
                    </td>
                    <td className="py-3.5 px-3 font-mono">
                      <div className="flex items-center space-x-2">
                        <span>{(row.recall * 100).toFixed(1)}%</span>
                        <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${isAdaptive ? 'bg-emerald-400' : 'bg-blue-400'}`}
                            style={{ width: `${row.recall * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-3 font-mono text-slate-300">
                      {(row.hit_rate * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-3 font-mono text-slate-300">
                      {row.mrr.toFixed(3)}
                    </td>
                    <td className="py-3.5 px-3 font-mono">
                      <span className={row.groundedness > 0.8 ? 'text-emerald-400' : 'text-slate-300'}>
                        {(row.groundedness * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="py-3.5 px-3 font-mono text-slate-300">
                      {(row.citation_coverage * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-3 font-mono text-slate-400">
                      {row.avg_latency_ms.toFixed(0)}ms
                    </td>
                    <td className="py-3.5 px-3 font-mono text-slate-400">
                      {row.avg_retries.toFixed(1)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Retrieval Ablation Studies Card */}
      {ablations?.ablation_results && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl">
          <div className="flex items-center space-x-2 mb-4 pb-3 border-b border-slate-800">
            <Layers className="w-5 h-5 text-blue-400" />
            <h3 className="font-semibold text-sm text-slate-200">
              Retrieval Strategy Ablation Studies
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
            {ablations.ablation_results.map((abl: any, i: number) => (
              <div key={i} className="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800">
                <div className="text-[11px] font-semibold text-slate-300 truncate" title={abl.configuration}>
                  {abl.configuration}
                </div>
                <div className="mt-2 space-y-1 text-xs font-mono">
                  <div className="flex justify-between text-slate-400">
                    <span>Recall:</span>
                    <span className="text-emerald-400 font-bold">{(abl.avg_recall * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Hit Rate:</span>
                    <span className="text-blue-400">{(abl.avg_hit_rate * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>MRR:</span>
                    <span className="text-purple-400">{abl.avg_mrr.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
