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

  const handleMark = async (id: number, isCorrect: boolean) => {
    try {
      await evaluationApi.markCorrect(id, isCorrect);
      onToast?.('success', isCorrect ? 'Marked correct' : 'Marked incorrect');
      fetchEvaluations();
    } catch (err) {
      onToast?.('error', err instanceof Error ? err.message : 'Failed to update feedback');
    }
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
                • Paper {ev.paper_title ? `${ev.paper_title} (ID ${ev.paper_id})` : ev.paper_id}{' '}
                • Rubric {ev.rubric_name ? `${ev.rubric_name} (ID ${ev.rubric_id})` : ev.rubric_id}{' '}
                • Prompt {ev.prompt_id}
              </div>
              <span className="text-xs text-gray-500">{formatDate(ev.created_at)}</span>
            </div>
            {ev.model_response && Array.isArray(ev.model_response.evaluations) ? (
              <div className="space-y-2">
                {ev.model_response.evaluations.map((entry: any, idx: number) => (
                  <div key={idx} className="bg-gray-50 rounded-md p-3 text-sm text-gray-800 border border-gray-100">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold">{entry.criterion_name || `Criterion ${entry.criterion_id}`}</span>
                      <span className="text-blue-700 font-medium">{entry.score}</span>
                    </div>
                    {entry.reasoning && (
                      <p className="text-gray-600 text-sm">{entry.reasoning}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-gray-50 rounded-md p-3 text-sm text-gray-800 whitespace-pre-wrap">
                {typeof ev.model_response === 'string'
                  ? ev.model_response
                : ev.model_response
                  ? JSON.stringify(ev.model_response, null, 2)
                  : 'No evaluation detail returned (check adapter).'}
              </div>
            )}
            <div className="mt-3 flex gap-2">
              <button
                onClick={() => handleMark(ev.id, true)}
                className="px-3 py-1 rounded-md bg-green-100 text-green-800 text-xs hover:bg-green-200"
              >
                Mark Correct
              </button>
              <button
                onClick={() => handleMark(ev.id, false)}
                className="px-3 py-1 rounded-md bg-red-100 text-red-800 text-xs hover:bg-red-200"
              >
                Mark Incorrect
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
