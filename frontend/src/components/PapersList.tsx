import { useEffect, useState } from 'react';
import { paperApi } from '../services/api';
import type { Paper } from '../services/api';

export default function PapersList() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);

  const fetchPapers = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await paperApi.list();
      setPapers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load papers');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPapers();

    // Listen for paper submission events to auto-refresh
    const handlePaperSubmitted = () => {
      fetchPapers();
    };

    window.addEventListener('paperSubmitted', handlePaperSubmitted);

    return () => {
      window.removeEventListener('paperSubmitted', handlePaperSubmitted);
    };
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this paper?')) {
      return;
    }

    try {
      await paperApi.delete(id);
      // Refresh the list
      fetchPapers();
      // Close detail view if deleted paper was selected
      if (selectedPaper?.id === id) {
        setSelectedPaper(null);
      }
    } catch (err) {
      alert('Failed to delete paper');
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
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
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mx-auto mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto"></div>
        </div>
        <p className="text-gray-600 mt-4">Loading papers...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">Error: {error}</p>
        <button
          onClick={fetchPapers}
          className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
        >
          Try again
        </button>
      </div>
    );
  }

  if (papers.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <p className="text-gray-600 mb-2">No papers submitted yet.</p>
        <p className="text-sm text-gray-500">
          Use the form above to submit your first paper!
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">
          Submitted Papers ({papers.length})
        </h2>
        <button
          onClick={fetchPapers}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          Refresh
        </button>
      </div>

      <div className="grid gap-4">
        {papers.map((paper) => (
          <div
            key={paper.id}
            className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition cursor-pointer"
            onClick={() => setSelectedPaper(paper)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-800 mb-1">
                  {paper.title}
                </h3>
                <div className="flex items-center gap-2 text-sm text-gray-500 mb-2 flex-wrap">
                  <span>Created: {formatDate(paper.created_at)}</span>
                  {paper.submission_date && (
                    <span className="text-gray-400">•</span>
                  )}
                  {paper.submission_date && (
                    <span>Submitted: {formatDate(paper.submission_date)}</span>
                  )}
                  {paper.rubric_name && (
                    <>
                      <span className="text-gray-400">•</span>
                      <span className="text-blue-700 font-medium">Rubric: {paper.rubric_name}</span>
                    </>
                  )}
                </div>
                <p className="text-gray-600 line-clamp-2">
                  {paper.content.substring(0, 200)}
                  {paper.content.length > 200 && '...'}
                </p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(paper.id);
                }}
                className="ml-4 text-red-600 hover:text-red-800 text-sm"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Paper Detail Modal */}
      {selectedPaper && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedPaper(null)}
        >
          <div
            className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[80vh] overflow-y-auto p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between mb-4">
              <h2 className="text-2xl font-bold text-gray-800">
                {selectedPaper.title}
              </h2>
              <button
                onClick={() => setSelectedPaper(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="mb-4 text-sm text-gray-500 space-y-1">
              <p>Created: {formatDate(selectedPaper.created_at)}</p>
              <p>Submitted: {formatDate(selectedPaper.submission_date)}</p>
              {selectedPaper.rubric_name && (
                <p>Rubric: {selectedPaper.rubric_name}</p>
              )}
              <p>ID: {selectedPaper.id}</p>
            </div>

            <div className="border-t border-gray-200 pt-4">
              <h3 className="font-semibold text-gray-700 mb-2">Content:</h3>
              <div className="whitespace-pre-wrap text-gray-700 bg-gray-50 p-4 rounded-md">
                {selectedPaper.content}
              </div>
            </div>

            <div className="mt-6 flex justify-end space-x-3">
              <button
                onClick={() => setSelectedPaper(null)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md transition"
              >
                Close
              </button>
              <button
                onClick={() => {
                  handleDelete(selectedPaper.id);
                  setSelectedPaper(null);
                }}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition"
              >
                Delete Paper
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
