import { useEffect, useState } from 'react';
import { evaluationApi } from '../services/api';
import type { Evaluation } from '../services/api';

interface Props {
  onToast?: (type: 'success' | 'error' | 'info', message: string) => void;
}

export default function EvaluationsList({ onToast }: Props) {
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchEvaluations = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await evaluationApi.list();
      setEvaluations(data);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to load evaluations';
      setError(msg);
      onToast?.('error', msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvaluations();
    const handleEvalCreated = () => fetchEvaluations();
    window.addEventListener('evaluationCreated', handleEvalCreated);
    return () => window.removeEventListener('evaluationCreated', handleEvalCreated);
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <p className="text-gray-600">Loading evaluations...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">Error: {error}</p>
        <button
          onClick={fetchEvaluations}
          className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
        >
          Try again
        </button>
      </div>
    );
  }

  if (evaluations.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <p className="text-gray-600">No evaluations yet. Submit a paper with a rubric, then click Evaluate.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">
          Evaluations ({evaluations.length})
        </h2>
        <button
          onClick={fetchEvaluations}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          Refresh
        </button>
      </div>

      <div className="grid gap-4">
        {evaluations.map((ev) => (
          <div key={ev.id} className="bg-white rounded-lg shadow-md p-4 border border-gray-100">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm text-gray-600">
                <span className="font-semibold text-gray-800">Eval #{ev.id}</span>{' '}
                • Paper {ev.paper_id} • Rubric {ev.rubric_id} • Prompt {ev.prompt_id}
              </div>
              <span className="text-xs text-gray-500">{formatDate(ev.created_at)}</span>
            </div>
            <div className="bg-gray-50 rounded-md p-3 text-sm text-gray-800 whitespace-pre-wrap">
              {typeof ev.model_response === 'string'
                ? ev.model_response
                : JSON.stringify(ev.model_response, null, 2)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
