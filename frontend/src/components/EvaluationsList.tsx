import { useCallback, useEffect, useMemo, useState } from 'react';
import { evaluationApi } from '../services/api';
import type { Criterion, Evaluation, FeedbackEntry, ModelResponse } from '../services/api';

interface Props {
  onToast?: (type: 'success' | 'error' | 'info', message: string) => void;
}

type FeedbackDrafts = Record<number, { corrected: string; note: string }>;
type EvaluationEntry = {
  criterion_id?: number;
  criterion_name?: string;
  score?: string;
  reasoning?: string;
};

function StatusBadge({ isCorrect }: { isCorrect?: boolean | null }) {
  const label = isCorrect === true ? 'Correct' : isCorrect === false ? 'Incorrect' : 'Not reviewed';
  const styles =
    isCorrect === true
      ? 'bg-green-100 text-green-800'
      : isCorrect === false
        ? 'bg-red-100 text-red-800'
        : 'bg-gray-100 text-gray-700';
  return <span className={`px-2 py-1 rounded-full text-xs font-semibold ${styles}`}>{label}</span>;
}

export default function EvaluationsList({ onToast }: Props) {
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [selectedEvaluation, setSelectedEvaluation] = useState<Evaluation | null>(null);
  const [feedbackDrafts, setFeedbackDrafts] = useState<FeedbackDrafts>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [savingFeedbackFor, setSavingFeedbackFor] = useState<number | null>(null);
  const [marking, setMarking] = useState(false);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const applySelection = useCallback(
    (data: Evaluation[], targetId?: number) => {
      if (data.length === 0) {
        setSelectedId(null);
        setSelectedEvaluation(null);
        return;
      }
      const desiredId = targetId ?? selectedId ?? data[0].id;
      const found = data.find((ev) => ev.id === desiredId) || data[0];
      setSelectedId(found.id);
      setSelectedEvaluation(found);
    },
    [selectedId]
  );

  const fetchEvaluations = useCallback(
    async (targetId?: number) => {
      setLoading(true);
      setError('');
      try {
        const data = await evaluationApi.list();
        setEvaluations(data);
        applySelection(data, targetId);
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Failed to load evaluations';
        setError(msg);
        onToast?.('error', msg);
      } finally {
        setLoading(false);
      }
    },
    [applySelection, onToast]
  );

  useEffect(() => {
    fetchEvaluations();
    const handleEvalCreated = () => fetchEvaluations();
    window.addEventListener('evaluationCreated', handleEvalCreated);
    return () => window.removeEventListener('evaluationCreated', handleEvalCreated);
  }, [fetchEvaluations]);

  // When selection changes, prefill drafts from saved feedback
  useEffect(() => {
    if (!selectedEvaluation) {
      setFeedbackDrafts({});
      return;
    }
    const drafts: FeedbackDrafts = {};
    (selectedEvaluation.feedback || []).forEach((fb: FeedbackEntry) => {
      if (fb.criterion_id !== null && fb.criterion_id !== undefined) {
        drafts[fb.criterion_id] = {
          corrected: fb.user_corrected_score,
          note: fb.user_explanation || '',
        };
      }
    });
    setFeedbackDrafts(drafts);
  }, [selectedEvaluation]);

  const evaluationEntries = useMemo<EvaluationEntry[]>(() => {
    if (!selectedEvaluation || !selectedEvaluation.model_response) return [];
    const response = selectedEvaluation.model_response as ModelResponse | string;
    if (typeof response === 'string') return [];
    const evaluations = response.evaluations;
    return Array.isArray(evaluations) ? (evaluations as EvaluationEntry[]) : [];
  }, [selectedEvaluation]);

  const results = useMemo(() => {
    if (!selectedEvaluation) return [];
    const criteria: Criterion[] =
      selectedEvaluation.rubric_criteria && selectedEvaluation.rubric_criteria.length > 0
        ? selectedEvaluation.rubric_criteria
        : evaluationEntries.map((entry, idx) => ({
            id: entry.criterion_id ?? idx,
            rubric_id: selectedEvaluation.rubric_id,
            name: entry.criterion_name || `Criterion ${idx + 1}`,
            description: entry.reasoning,
            order: idx,
        }));

    return criteria.map((criterion, idx) => {
      const entry =
        evaluationEntries.find((ev) => ev.criterion_id === criterion.id) || evaluationEntries[idx];
      return {
        criterion,
        modelScore: entry?.score ?? '',
        reasoning: entry?.reasoning ?? '',
      };
    });
  }, [selectedEvaluation, evaluationEntries]);

  const savedFeedbackByCriterion = useMemo(() => {
    const map: Record<number, FeedbackEntry> = {};
    (selectedEvaluation?.feedback || []).forEach((fb) => {
      if (fb.criterion_id !== null && fb.criterion_id !== undefined) {
        map[fb.criterion_id] = fb;
      }
    });
    return map;
  }, [selectedEvaluation?.feedback]);

  const handleSelect = (id: number) => {
    const found = evaluations.find((ev) => ev.id === id);
    if (found) {
      setSelectedId(found.id);
      setSelectedEvaluation(found);
    }
  };

  const handleMark = async (isCorrect: boolean) => {
    if (!selectedEvaluation) return;
    setMarking(true);
    try {
      await evaluationApi.markCorrect(selectedEvaluation.id, isCorrect);
      onToast?.('success', isCorrect ? 'Marked correct' : 'Marked incorrect');
      await fetchEvaluations(selectedEvaluation.id);
      window.dispatchEvent(new Event('evaluationUpdated'));
    } catch (err) {
      onToast?.('error', err instanceof Error ? err.message : 'Failed to update feedback');
    } finally {
      setMarking(false);
    }
  };

  const handleDraftChange = (criterionId: number, field: 'corrected' | 'note', value: string) => {
    setFeedbackDrafts((prev) => ({
      ...prev,
      [criterionId]: {
        corrected: field === 'corrected' ? value : prev[criterionId]?.corrected || '',
        note: field === 'note' ? value : prev[criterionId]?.note || '',
      },
    }));
  };

  const handleSaveFeedback = async (criterionId: number, modelScore: string) => {
    if (!selectedEvaluation) return;
    const draft = feedbackDrafts[criterionId];
    if (!draft || !draft.corrected) {
      onToast?.('error', 'Select a corrected score before saving.');
      return;
    }

    setSavingFeedbackFor(criterionId);
    try {
      await evaluationApi.saveFeedback(selectedEvaluation.id, {
        criterion_id: criterionId,
        model_score: modelScore || 'yes',
        user_corrected_score: draft.corrected,
        user_explanation: draft.note || undefined,
      });
      onToast?.('success', 'Feedback saved');
      await fetchEvaluations(selectedEvaluation.id);
      window.dispatchEvent(new Event('evaluationUpdated'));
    } catch (err) {
      onToast?.('error', err instanceof Error ? err.message : 'Failed to save feedback');
    } finally {
      setSavingFeedbackFor(null);
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
          onClick={() => fetchEvaluations(selectedId ?? undefined)}
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

  const scoringType = selectedEvaluation?.rubric_scoring_type || 'yes_no';

  // Format score display based on scoring type
  const formatScore = (score: string | number, criterion?: Criterion): string => {
    if (!score && score !== 0) return 'n/a';

    if (scoringType === 'yes_no') {
      return String(score).toLowerCase() === 'yes' ? 'Yes' : 'No';
    } else if (scoringType === 'meets_not_meets') {
      return String(score).toLowerCase() === 'meets' ? 'Meets Standard' : 'Does Not Meet';
    } else if (scoringType === 'numerical' && criterion) {
      return `${score} / ${criterion.max_score || '?'} points`;
    }
    return String(score);
  };

  // Get score badge color based on scoring type and value
  const getScoreBadgeClass = (score: string | number): string => {
    if (!score && score !== 0) return 'bg-gray-100 text-gray-700';

    if (scoringType === 'yes_no') {
      return String(score).toLowerCase() === 'yes'
        ? 'bg-green-100 text-green-800'
        : 'bg-red-100 text-red-800';
    } else if (scoringType === 'meets_not_meets') {
      return String(score).toLowerCase() === 'meets'
        ? 'bg-green-100 text-green-800'
        : 'bg-red-100 text-red-800';
    } else if (scoringType === 'numerical') {
      // For numerical, use green for high scores, yellow for mid, red for low
      const numScore = Number(score);
      if (numScore >= 7) return 'bg-green-100 text-green-800';
      if (numScore >= 4) return 'bg-yellow-100 text-yellow-800';
      return 'bg-red-100 text-red-800';
    }
    return 'bg-blue-100 text-blue-800';
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">Evaluations ({evaluations.length})</h2>
        <button
          onClick={() => fetchEvaluations(selectedId ?? undefined)}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="space-y-3">
          {evaluations.map((ev) => (
            <button
              key={ev.id}
              onClick={() => handleSelect(ev.id)}
              className={`w-full text-left bg-white rounded-lg border p-4 shadow-sm transition hover:shadow-md ${
                selectedId === ev.id ? 'border-blue-500 ring-1 ring-blue-100' : 'border-gray-200'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <div className="text-sm font-semibold text-gray-800">Eval #{ev.id}</div>
                <StatusBadge isCorrect={ev.is_correct} />
              </div>
              <div className="text-xs text-gray-600">
                Paper: {ev.paper_title ? `${ev.paper_title} (ID ${ev.paper_id})` : ev.paper_id}
              </div>
              <div className="text-xs text-gray-600">
                Rubric: {ev.rubric_name ? `${ev.rubric_name} (ID ${ev.rubric_id})` : ev.rubric_id}
              </div>
              <div className="text-xs text-gray-500 mt-1">Created {formatDate(ev.created_at)}</div>
              <div className="text-xs text-gray-500 mt-1">
                Feedback: {ev.feedback ? ev.feedback.length : 0} item(s)
              </div>
            </button>
          ))}
        </div>

        <div className="lg:col-span-2">
          {!selectedEvaluation ? (
            <div className="bg-white rounded-lg shadow-md p-6 text-center text-gray-600">
              Select an evaluation to view details and leave feedback.
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-md border border-gray-100 p-6 space-y-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-xl font-bold text-gray-900">Evaluation #{selectedEvaluation.id}</h3>
                    <StatusBadge isCorrect={selectedEvaluation.is_correct} />
                  </div>
                  <p className="text-sm text-gray-700 mt-1">
                    Paper: {selectedEvaluation.paper_title || `ID ${selectedEvaluation.paper_id}`} • Rubric:{' '}
                    {selectedEvaluation.rubric_name || `ID ${selectedEvaluation.rubric_id}`} • Prompt{' '}
                    {selectedEvaluation.prompt_id}
                  </p>
                  <p className="text-xs text-gray-500">
                    Created {formatDate(selectedEvaluation.created_at)} • Scoring: {scoringType.replace('_', '/')}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleMark(true)}
                    disabled={marking}
                    className="px-3 py-1 rounded-md bg-green-100 text-green-800 text-xs hover:bg-green-200 disabled:opacity-60"
                  >
                    Mark Correct
                  </button>
                  <button
                    onClick={() => handleMark(false)}
                    disabled={marking}
                    className="px-3 py-1 rounded-md bg-red-100 text-red-800 text-xs hover:bg-red-200 disabled:opacity-60"
                  >
                    Mark Incorrect
                  </button>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-lg font-semibold text-gray-800">Model Results</h4>
                  {!evaluationEntries.length && (
                    <span className="text-sm text-gray-500">No model response returned</span>
                  )}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {results.map(({ criterion, modelScore, reasoning }) => (
                    <div key={criterion.id} className="border border-gray-200 rounded-md p-3 bg-gray-50">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-gray-800">{criterion.name}</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getScoreBadgeClass(modelScore)}`}>
                          {formatScore(modelScore, criterion)}
                        </span>
                      </div>
                      {criterion.description && (
                        <p className="text-xs text-gray-600 mt-1">{criterion.description}</p>
                      )}
                      {scoringType === 'numerical' && criterion.min_score !== undefined && (
                        <p className="text-xs text-gray-500 mt-1">
                          Range: {criterion.min_score} - {criterion.max_score} points
                        </p>
                      )}
                      {reasoning && (
                        <p className="text-sm text-gray-700 mt-2">Reasoning: {reasoning}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="border-t border-gray-200 pt-4 space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-lg font-semibold text-gray-800">Feedback & Corrections</h4>
                  <p className="text-sm text-gray-500">Mark incorrect and supply corrected scores.</p>
                </div>

                {results.map(({ criterion, modelScore }) => {
                  const draft = feedbackDrafts[criterion.id] || { corrected: '', note: '' };
                  const saved = savedFeedbackByCriterion[criterion.id];
                  const isSaving = savingFeedbackFor === criterion.id;

                  return (
                    <div key={criterion.id} className="border border-gray-200 rounded-md p-4">
                      <div className="flex items-center justify-between mb-1">
                        <div>
                          <p className="text-sm font-semibold text-gray-800">{criterion.name}</p>
                          <p className="text-xs text-gray-500">
                            Model score: <span className={`font-semibold ${getScoreBadgeClass(modelScore)}`}>
                              {formatScore(modelScore, criterion)}
                            </span>
                          </p>
                        </div>
                        {saved && (
                          <span className="text-xs text-green-700 bg-green-50 border border-green-200 px-2 py-1 rounded">
                            Saved
                          </span>
                        )}
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {/* Corrected Score Input - varies by scoring type */}
                        {scoringType === 'yes_no' ? (
                          <div>
                            <label className="text-xs font-medium text-gray-700">Corrected score</label>
                            <select
                              value={draft.corrected}
                              onChange={(e) => handleDraftChange(criterion.id, 'corrected', e.target.value)}
                              className="mt-1 w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm"
                            >
                              <option value="">Select</option>
                              <option value="yes">Yes</option>
                              <option value="no">No</option>
                            </select>
                          </div>
                        ) : scoringType === 'meets_not_meets' ? (
                          <div>
                            <label className="text-xs font-medium text-gray-700">Corrected score</label>
                            <select
                              value={draft.corrected}
                              onChange={(e) => handleDraftChange(criterion.id, 'corrected', e.target.value)}
                              className="mt-1 w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm"
                            >
                              <option value="">Select</option>
                              <option value="meets">Meets Standard</option>
                              <option value="does_not_meet">Does Not Meet</option>
                            </select>
                          </div>
                        ) : (
                          <div>
                            <label className="text-xs font-medium text-gray-700">
                              Corrected score
                              {criterion.min_score !== undefined && (
                                <span className="text-gray-500 ml-1">
                                  ({criterion.min_score}-{criterion.max_score})
                                </span>
                              )}
                            </label>
                            <input
                              type="number"
                              value={draft.corrected}
                              onChange={(e) => handleDraftChange(criterion.id, 'corrected', e.target.value)}
                              className="mt-1 w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm"
                              placeholder={`Enter score (${criterion.min_score}-${criterion.max_score})`}
                              min={criterion.min_score ?? undefined}
                              max={criterion.max_score ?? undefined}
                            />
                          </div>
                        )}

                        {/* Explanation textarea with character counter */}
                        <div>
                          <label className="text-xs font-medium text-gray-700">
                            Explanation (optional)
                          </label>
                          <textarea
                            value={draft.note}
                            onChange={(e) => handleDraftChange(criterion.id, 'note', e.target.value)}
                            rows={2}
                            maxLength={1000}
                            className="mt-1 w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm resize-none"
                            placeholder="Explain why the model was wrong (optional)"
                          />
                          <div className="text-xs text-gray-500 mt-1 text-right">
                            {draft.note.length}/1000 characters
                          </div>
                        </div>
                      </div>
                      <div className="mt-3 flex items-center gap-3">
                        <button
                          onClick={() => handleSaveFeedback(criterion.id, modelScore)}
                          disabled={isSaving}
                          className="px-3 py-1.5 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 disabled:opacity-60"
                        >
                          {isSaving ? 'Saving...' : saved ? 'Update Feedback' : 'Save Feedback'}
                        </button>
                        {saved && (
                          <div className="text-xs text-gray-600">
                            <p>
                              Corrected to: <span className="font-semibold">{formatScore(saved.user_corrected_score, criterion)}</span>
                            </p>
                            {saved.user_explanation && (
                              <p className="text-gray-500 mt-1 italic">"{saved.user_explanation}"</p>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
