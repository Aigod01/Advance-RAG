import React, { useEffect, useState } from 'react';
import {
  Sparkles,
  Zap,
  TrendingUp,
  Award,
  Clock,
  RefreshCw,
  Database,
  Cpu,
  Sliders,
  CheckCircle2,
  ThumbsUp,
  ThumbsDown
} from 'lucide-react';
import { StrategySummary } from '../types';
import { getStrategySummary } from '../api/client';

export const StrategyDashboard: React.FC = () => {
  const [summary, setSummary] = useState<StrategySummary | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const data = await getStrategySummary();
      setSummary(data);
    } catch (e) {
      console.error('Failed to fetch strategy summary', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto py-2">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2.5">
            <Sparkles className="w-6 h-6 text-emerald-400" />
            <span>Collaborative Retrieval Learning & Strategy Memory</span>
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Contextual-Bandit policy learning that optimizes retriever type, top-k candidates, and neural reranking from measured critic outcomes.
          </p>
        </div>
        <button
          onClick={fetchSummary}
          disabled={loading}
          className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium border border-slate-700 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Memory</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Total Episodes</span>
            <Database className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">
            {summary?.total_episodes ?? 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Experience episodes logged</p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Avg Critic Quality</span>
            <Award className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400 font-mono">
            {summary?.avg_critic_score ? (summary.avg_critic_score * 100).toFixed(1) + '%' : '0%'}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Critic verification reward</p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Success Rate</span>
            <TrendingUp className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-blue-400 font-mono">
            {summary?.success_rate ? (summary.success_rate * 100).toFixed(1) + '%' : '0%'}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Queries verified sufficient</p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Avg Latency</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400 font-mono">
            {summary?.avg_latency_ms ? summary.avg_latency_ms.toFixed(0) + 'ms' : '0ms'}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Retrieval & reranking time</p>
        </div>
      </div>

      {/* Blueprint Formula Card */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-950 border border-emerald-500/20 rounded-2xl p-5 shadow-xl">
        <div className="flex items-center space-x-2 mb-3">
          <Cpu className="w-5 h-5 text-emerald-400" />
          <h3 className="font-semibold text-sm text-slate-200">
            Learned Strategy Selection Formula
          </h3>
        </div>
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs text-emerald-300 overflow-x-auto">
          strategy_score = historical_success × domain_similarity × question_type_similarity × source_reliability
        </div>
        <p className="text-xs text-slate-400 mt-3 leading-relaxed">
          The system balances exploitation (selecting the highest scoring retrieval strategy from memory) with exploration (ε = 0.15) to discover superior retrieval configurations for new query domains.
        </p>
      </div>

      {/* Episode Log Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl">
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <Sliders className="w-5 h-5 text-purple-400" />
            <h3 className="font-semibold text-sm text-slate-200">
              Recent Learned Retrieval Episodes
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            Last {summary?.recent_episodes?.length ?? 0} runs
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 font-mono uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Domain</th>
                <th className="py-2.5 px-3">Type</th>
                <th className="py-2.5 px-3">Query</th>
                <th className="py-2.5 px-3">Chosen Strategy</th>
                <th className="py-2.5 px-3">Critic Score</th>
                <th className="py-2.5 px-3">Feedback</th>
                <th className="py-2.5 px-3">Latency</th>
                <th className="py-2.5 px-3">Outcome</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {summary?.recent_episodes?.map((ep, idx) => (
                <tr key={ep.episode_id || idx} className="hover:bg-slate-800/30 transition">
                  <td className="py-3 px-3 font-semibold text-emerald-400 capitalize">
                    {ep.domain}
                  </td>
                  <td className="py-3 px-3 text-slate-300 capitalize">
                    {ep.question_type}
                  </td>
                  <td className="py-3 px-3 text-slate-300 max-w-[200px] truncate" title={ep.original_query}>
                    {ep.original_query}
                  </td>
                  <td className="py-3 px-3 font-mono text-[11px] text-purple-300">
                    {ep.strategy.retriever} (k={ep.strategy.top_k}, {ep.strategy.reranker})
                  </td>
                  <td className="py-3 px-3 font-mono font-bold text-slate-200">
                    {(ep.critic_score * 100).toFixed(0)}%
                  </td>
                  <td className="py-3 px-3">
                    {ep.user_feedback === 1 ? (
                      <span className="flex items-center space-x-1 text-emerald-400">
                        <ThumbsUp className="w-3.5 h-3.5" />
                        <span>+1</span>
                      </span>
                    ) : ep.user_feedback === -1 ? (
                      <span className="flex items-center space-x-1 text-rose-400">
                        <ThumbsDown className="w-3.5 h-3.5" />
                        <span>-1</span>
                      </span>
                    ) : (
                      <span className="text-slate-500">-</span>
                    )}
                  </td>
                  <td className="py-3 px-3 font-mono text-slate-400">
                    {ep.latency_ms.toFixed(0)}ms
                  </td>
                  <td className="py-3 px-3">
                    {ep.success ? (
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-semibold">
                        Sufficient
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 text-[10px] font-semibold">
                        Retried
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
