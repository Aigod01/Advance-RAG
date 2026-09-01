import React, { useState } from 'react';
import { X, ThumbsUp, ThumbsDown, Send, CheckCircle2 } from 'lucide-react';
import { submitUserFeedback } from '../api/client';

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  runId: string;
  query: string;
  finalAnswer: string;
  initialRating?: number;
}

export const FeedbackModal: React.FC<FeedbackModalProps> = ({
  isOpen,
  onClose,
  runId,
  query,
  finalAnswer,
  initialRating = 1,
}) => {
  const [rating, setRating] = useState<number>(initialRating);
  const [comments, setComments] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await submitUserFeedback(runId, rating, comments, query, finalAnswer);
      setSubmitted(true);
      setTimeout(() => {
        setSubmitted(false);
        onClose();
      }, 1500);
    } catch (e) {
      console.error('Error submitting feedback', e);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-5 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
        >
          <X className="w-4 h-4" />
        </button>

        <h3 className="text-base font-bold text-white mb-1">Provide Retrieval Feedback</h3>
        <p className="text-xs text-slate-400 mb-4">
          Your rating updates the Strategy Memory bandit weights to improve future strategy selection.
        </p>

        {submitted ? (
          <div className="py-8 text-center space-y-2">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
            <p className="text-sm font-semibold text-white">Feedback Logged!</p>
            <p className="text-xs text-slate-400">Strategy Memory rewards updated successfully.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex justify-center space-x-4 py-2">
              <button
                type="button"
                onClick={() => setRating(1)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${
                  rating === 1
                    ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500 shadow-md shadow-emerald-500/20'
                    : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700'
                }`}
              >
                <ThumbsUp className="w-4 h-4" />
                <span>Helpful / Accurate (+1)</span>
              </button>

              <button
                type="button"
                onClick={() => setRating(-1)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${
                  rating === -1
                    ? 'bg-rose-500/20 text-rose-300 border-rose-500 shadow-md shadow-rose-500/20'
                    : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700'
                }`}
              >
                <ThumbsDown className="w-4 h-4" />
                <span>Inaccurate / Missing (-1)</span>
              </button>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Qualitative Notes or Corrections (Optional)
              </label>
              <textarea
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                placeholder="e.g. Highlighted root cause accurately, but query could retrieve faster top-k..."
                rows={3}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div className="flex justify-end space-x-2 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-medium"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="flex items-center space-x-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold shadow-md shadow-emerald-600/30"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{submitting ? 'Updating...' : 'Submit Reward'}</span>
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
