import { useState } from 'react';
import { rubricApi } from '../services/api';
import type { RubricCreate, ScoringType, CriterionCreate } from '../services/api';

interface RubricFormProps {
  onSuccess?: () => void;
}

export default function RubricForm({ onSuccess }: RubricFormProps) {
  const [name, setName] = useState('');
  const [scoringType, setScoringType] = useState<ScoringType>('yes_no');
  const [criteria, setCriteria] = useState<CriterionCreate[]>([
    { name: '', description: '', order: 0 }
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const addCriterion = () => {
    setCriteria([
      ...criteria,
      { name: '', description: '', order: criteria.length }
    ]);
  };

  const removeCriterion = (index: number) => {
    if (criteria.length <= 1) {
      setError('Rubric must have at least one criterion');
      return;
    }
    const newCriteria = criteria.filter((_, i) => i !== index);
    // Reorder the remaining criteria
    newCriteria.forEach((criterion, i) => {
      criterion.order = i;
    });
    setCriteria(newCriteria);
    setError('');
  };

  const updateCriterion = (index: number, field: keyof CriterionCreate, value: string | number) => {
    const newCriteria = [...criteria];
    newCriteria[index] = { ...newCriteria[index], [field]: value };
    setCriteria(newCriteria);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!name.trim()) {
      setError('Rubric name is required');
      return;
    }

    // Check all criteria have names
    const emptyCriteria = criteria.filter(c => !c.name.trim());
    if (emptyCriteria.length > 0) {
      setError('All criteria must have a name');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      const rubricData: RubricCreate = {
        name: name.trim(),
        scoring_type: scoringType,
        criteria: criteria.map((c, index) => ({
          name: c.name.trim(),
          description: c.description?.trim() || undefined,
          order: index,
        })),
      };

      await rubricApi.create(rubricData);

      // Success!
      setSuccess(true);
      setName('');
      setScoringType('yes_no');
      setCriteria([{ name: '', description: '', order: 0 }]);

      if (onSuccess) {
        onSuccess();
      }

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create rubric');
    } finally {
      setLoading(false);
    }
  };

  const scoringTypeLabels: Record<ScoringType, string> = {
    yes_no: 'Yes / No',
    meets: 'Meets / Does Not Meet',
    numerical: 'Numerical Score',
  };

  const scoringTypeDescriptions: Record<ScoringType, string> = {
    yes_no: 'Binary evaluation (Yes or No)',
    meets: 'Standards-based (Meets expectations or not)',
    numerical: 'Numeric scores (e.g., 0-10)',
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Create Rubric</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Rubric Name */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            Rubric Name
          </label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="e.g., Essay Evaluation Rubric"
            disabled={loading}
          />
        </div>

        {/* Scoring Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Scoring Type
          </label>
          <div className="space-y-2">
            {(Object.keys(scoringTypeLabels) as ScoringType[]).map((type) => (
              <label key={type} className="flex items-start cursor-pointer">
                <input
                  type="radio"
                  name="scoringType"
                  value={type}
                  checked={scoringType === type}
                  onChange={(e) => setScoringType(e.target.value as ScoringType)}
                  className="mt-1 mr-3"
                  disabled={loading}
                />
                <div>
                  <div className="font-medium text-gray-800">{scoringTypeLabels[type]}</div>
                  <div className="text-sm text-gray-500">{scoringTypeDescriptions[type]}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Criteria Section */}
        <div className="border-t pt-4">
          <div className="flex items-center justify-between mb-3">
            <label className="block text-sm font-medium text-gray-700">
              Grading Criteria ({criteria.length})
            </label>
            <button
              type="button"
              onClick={addCriterion}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              disabled={loading}
            >
              + Add Criterion
            </button>
          </div>

          <div className="space-y-3">
            {criteria.map((criterion, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                <div className="flex items-start justify-between mb-2">
                  <span className="text-sm font-medium text-gray-600">Criterion {index + 1}</span>
                  {criteria.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeCriterion(index)}
                      className="text-red-600 hover:text-red-800 text-sm"
                      disabled={loading}
                    >
                      Remove
                    </button>
                  )}
                </div>

                <div className="space-y-2">
                  <input
                    type="text"
                    value={criterion.name}
                    onChange={(e) => updateCriterion(index, 'name', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                    placeholder="Criterion name (required)"
                    disabled={loading}
                  />
                  <textarea
                    value={criterion.description || ''}
                    onChange={(e) => updateCriterion(index, 'description', e.target.value)}
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm resize-none"
                    placeholder="Description (optional)"
                    disabled={loading}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
            {error}
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md text-sm">
            Rubric created successfully!
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {loading ? 'Creating Rubric...' : 'Create Rubric'}
        </button>
      </form>
    </div>
  );
}
