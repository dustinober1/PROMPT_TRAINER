import { useEffect, useState } from 'react';
import { rubricApi } from '../services/api';
import type { Rubric, ScoringType } from '../services/api';

export default function RubricsList() {
  const [rubrics, setRubrics] = useState<Rubric[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedRubric, setSelectedRubric] = useState<Rubric | null>(null);

  const fetchRubrics = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await rubricApi.list();
      setRubrics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load rubrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRubrics();

    // Listen for rubric creation events to auto-refresh
    const handleRubricCreated = () => {
      fetchRubrics();
    };

    window.addEventListener('rubricCreated', handleRubricCreated);

    return () => {
      window.removeEventListener('rubricCreated', handleRubricCreated);
    };
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this rubric?')) {
      return;
    }

    try {
      await rubricApi.delete(id);
      fetchRubrics();
      if (selectedRubric?.id === id) {
        setSelectedRubric(null);
      }
    } catch (err) {
      alert('Failed to delete rubric');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const scoringTypeLabels: Record<ScoringType, string> = {
    yes_no: 'Yes/No',
    meets: 'Meets/Not Meets',
    numerical: 'Numerical',
  };

  const scoringTypeBadgeColors: Record<ScoringType, string> = {
    yes_no: 'bg-blue-100 text-blue-800',
    meets: 'bg-green-100 text-green-800',
    numerical: 'bg-purple-100 text-purple-800',
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mx-auto mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto"></div>
        </div>
        <p className="text-gray-600 mt-4">Loading rubrics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">Error: {error}</p>
        <button
          onClick={fetchRubrics}
          className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
        >
          Try again
        </button>
      </div>
    );
  }

  if (rubrics.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <p className="text-gray-600 mb-2">No rubrics created yet.</p>
        <p className="text-sm text-gray-500">
          Use the form above to create your first rubric!
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">
          Rubrics ({rubrics.length})
        </h2>
        <button
          onClick={fetchRubrics}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          Refresh
        </button>
      </div>

      <div className="grid gap-4">
        {rubrics.map((rubric) => (
          <div
            key={rubric.id}
            className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition cursor-pointer"
            onClick={() => setSelectedRubric(rubric)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-lg font-semibold text-gray-800">
                    {rubric.name}
                  </h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${scoringTypeBadgeColors[rubric.scoring_type]}`}>
                    {scoringTypeLabels[rubric.scoring_type]}
                  </span>
                </div>
                <p className="text-sm text-gray-500 mb-2">
                  {rubric.criteria.length} {rubric.criteria.length === 1 ? 'criterion' : 'criteria'} •
                  Created {formatDate(rubric.created_at)}
                </p>
                <div className="flex flex-wrap gap-1">
                  {rubric.criteria.slice(0, 3).map((criterion) => (
                    <span
                      key={criterion.id}
                      className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                    >
                      {criterion.name}
                    </span>
                  ))}
                  {rubric.criteria.length > 3 && (
                    <span className="text-xs text-gray-500 px-2 py-1">
                      +{rubric.criteria.length - 3} more
                    </span>
                  )}
                </div>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(rubric.id);
                }}
                className="ml-4 text-red-600 hover:text-red-800 text-sm"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Rubric Detail Modal */}
      {selectedRubric && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedRubric(null)}
        >
          <div
            className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[80vh] overflow-y-auto p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">
                  {selectedRubric.name}
                </h2>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${scoringTypeBadgeColors[selectedRubric.scoring_type]}`}>
                  {scoringTypeLabels[selectedRubric.scoring_type]}
                </span>
              </div>
              <button
                onClick={() => setSelectedRubric(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="mb-4 text-sm text-gray-500 space-y-1">
              <p>Created: {formatDate(selectedRubric.created_at)}</p>
              <p>ID: {selectedRubric.id}</p>
            </div>

            <div className="border-t border-gray-200 pt-4">
              <h3 className="font-semibold text-gray-700 mb-3">
                Grading Criteria ({selectedRubric.criteria.length})
              </h3>
              <div className="space-y-3">
                {selectedRubric.criteria
                  .sort((a, b) => a.order - b.order)
                  .map((criterion, index) => (
                    <div
                      key={criterion.id}
                      className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                    >
                      <div className="flex items-start justify-between mb-1">
                        <span className="text-xs font-medium text-gray-500">
                          Criterion {index + 1}
                        </span>
                        <span className="text-xs text-gray-400">
                          Order: {criterion.order}
                        </span>
                      </div>
                      <h4 className="font-semibold text-gray-800 mb-1">
                        {criterion.name}
                      </h4>
                      {criterion.description && (
                        <p className="text-sm text-gray-600">
                          {criterion.description}
                        </p>
                      )}
                    </div>
                  ))}
              </div>
            </div>

            <div className="mt-6 flex justify-end space-x-3">
              <button
                onClick={() => setSelectedRubric(null)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md transition"
              >
                Close
              </button>
              <button
                onClick={() => {
                  handleDelete(selectedRubric.id);
                  setSelectedRubric(null);
                }}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition"
              >
                Delete Rubric
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
