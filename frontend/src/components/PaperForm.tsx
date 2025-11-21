import { useEffect, useState } from 'react';
import { paperApi, rubricApi } from '../services/api';
import type { PaperCreate, Rubric } from '../services/api';

interface PaperFormProps {
  onSuccess?: () => void;
}

export default function PaperForm({ onSuccess }: PaperFormProps) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [rubricId, setRubricId] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [rubrics, setRubrics] = useState<Rubric[]>([]);
  const [rubricsError, setRubricsError] = useState('');
  const [rubricsLoading, setRubricsLoading] = useState(true);

  useEffect(() => {
    const loadRubrics = async () => {
      try {
        const data = await rubricApi.list();
        setRubrics(data);
      } catch (err) {
        setRubricsError(err instanceof Error ? err.message : 'Failed to load rubrics');
      } finally {
        setRubricsLoading(false);
      }
    };

    loadRubrics();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!title.trim()) {
      setError('Title is required');
      return;
    }
    if (!content.trim()) {
      setError('Content is required');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      const paperData: PaperCreate = {
        title: title.trim(),
        content: content.trim(),
        rubric_id: rubricId ? Number(rubricId) : null,
      };

      await paperApi.create(paperData);

      // Success!
      setSuccess(true);
      setTitle('');
      setContent('');
      setRubricId('');

      // Call the success callback if provided
      if (onSuccess) {
        onSuccess();
      }

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create paper');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Submit a Paper</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Title Input */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
            Paper Title
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter paper title..."
            disabled={loading}
          />
        </div>

        {/* Rubric Selector */}
        <div>
          <label htmlFor="rubric" className="block text-sm font-medium text-gray-700 mb-1">
            Rubric (optional)
          </label>
          <select
            id="rubric"
            value={rubricId}
            onChange={(e) => setRubricId(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading || rubricsLoading || !!rubricsError}
          >
            <option value="">No rubric selected</option>
            {rubrics.map((rubric) => (
              <option key={rubric.id} value={rubric.id}>
                {rubric.name}
              </option>
            ))}
          </select>
          {rubricsLoading && (
            <p className="text-sm text-gray-500 mt-1">Loading rubrics...</p>
          )}
          {rubricsError && (
            <p className="text-sm text-red-600 mt-1">Unable to load rubrics: {rubricsError}</p>
          )}
        </div>

        {/* Content Textarea */}
        <div>
          <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-1">
            Paper Content
          </label>
          <textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={10}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y"
            placeholder="Paste or type the paper content here..."
            disabled={loading}
          />
          <p className="text-sm text-gray-500 mt-1">
            {content.length} characters
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            {error}
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
            Paper submitted successfully!
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {loading ? 'Submitting...' : 'Submit Paper'}
        </button>
      </form>
    </div>
  );
}
