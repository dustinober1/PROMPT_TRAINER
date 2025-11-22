import { useCallback, useEffect, useMemo, useState } from 'react';
import { promptApi } from '../services/api';
import type { Prompt } from '../services/api';

interface Props {
  onToast?: (type: 'success' | 'error' | 'info', message: string) => void;
}

const REQUIRED_PLACEHOLDERS = ['{{paper_content}}', '{{rubric}}'];

export default function PromptManager({ onToast }: Props) {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [templateDraft, setTemplateDraft] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [creating, setCreating] = useState(false);

  const selectedPrompt = useMemo(
    () => prompts.find((p) => p.id === selectedId) || prompts.find((p) => p.is_active) || prompts[0],
    [prompts, selectedId],
  );

  const placeholdersMissing = useMemo(
    () => REQUIRED_PLACEHOLDERS.filter((p) => !templateDraft.includes(p)),
    [templateDraft],
  );

  const fetchPrompts = useCallback(async () => {
    setLoading(true);
    try {
      const data = await promptApi.list();
      setPrompts(data);
      const active = data.find((p) => p.is_active);
      const chosen = data.find((p) => p.id === selectedId) || active || data[0];
      if (chosen) {
        setSelectedId(chosen.id);
        setTemplateDraft(chosen.template_text);
      }
    } catch (err) {
      onToast?.('error', err instanceof Error ? err.message : 'Failed to load prompts');
    } finally {
      setLoading(false);
    }
  }, [onToast, selectedId]);

  useEffect(() => {
    fetchPrompts();
  }, [fetchPrompts]);

  useEffect(() => {
    if (selectedPrompt) {
      setTemplateDraft(selectedPrompt.template_text);
    }
  }, [selectedPrompt]);

  const handleSave = async () => {
    if (!selectedPrompt) return;
    if (placeholdersMissing.length > 0) {
      onToast?.('error', `Missing placeholders: ${placeholdersMissing.join(', ')}`);
      return;
    }
    setSaving(true);
    try {
      await promptApi.update(selectedPrompt.id, { template_text: templateDraft });
      onToast?.('success', 'Prompt updated');
      await fetchPrompts();
    } catch (err) {
      onToast?.('error', err instanceof Error ? err.message : 'Failed to save prompt');
    } finally {
      setSaving(false);
    }
  };

  const handleActivate = async (id: number) => {
    setSaving(true);
    try {
      await promptApi.activate(id);
      onToast?.('success', 'Prompt activated');
      await fetchPrompts();
    } catch (err) {
      onToast?.('error', err instanceof Error ? err.message : 'Failed to activate prompt');
    } finally {
      setSaving(false);
    }
  };

  const handleCreateNew = async () => {
    if (placeholdersMissing.length > 0) {
      onToast?.('error', `Missing placeholders: ${placeholdersMissing.join(', ')}`);
      return;
    }
    setCreating(true);
    try {
      const parentId = selectedPrompt?.id;
      await promptApi.create({
        template_text: templateDraft,
        parent_version_id: parentId,
        is_active: true,
      });
      onToast?.('success', 'New prompt version created and activated');
      await fetchPrompts();
    } catch (err) {
      onToast?.('error', err instanceof Error ? err.message : 'Failed to create prompt');
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 text-center">
        <p className="text-gray-600">Loading prompts...</p>
      </div>
    );
  }

  if (prompts.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
        <div>
          <h3 className="text-xl font-bold text-gray-800">Create your first prompt</h3>
          <p className="text-sm text-gray-600">
            Include placeholders {REQUIRED_PLACEHOLDERS.join(' & ')} so the evaluator can inject paper content and rubric details.
          </p>
        </div>
        <textarea
          value={templateDraft}
          onChange={(e) => setTemplateDraft(e.target.value)}
          rows={8}
          className="w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm"
          placeholder="e.g., Evaluate {{paper_content}} using rubric {{rubric}}"
        />
        <button
          onClick={handleCreateNew}
          disabled={creating}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-60 text-sm"
        >
          {creating ? 'Saving...' : 'Create Prompt'}
        </button>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-800">Versions</h3>
          <span className="text-xs text-gray-500">{prompts.length} total</span>
        </div>
        <div className="space-y-2">
          {prompts.map((p) => (
            <button
              key={p.id}
              onClick={() => setSelectedId(p.id)}
              className={`w-full text-left border rounded-md p-3 transition ${
                selectedPrompt?.id === p.id ? 'border-blue-500 ring-1 ring-blue-100 bg-blue-50' : 'border-gray-200 bg-white'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-gray-800">
                    v{p.version} {p.is_active && <span className="text-green-700 text-xs ml-2">(active)</span>}
                  </p>
                  <p className="text-xs text-gray-500">
                    Created {new Date(p.created_at).toLocaleString()}
                    {p.parent_version_id && ` • Parent v${p.parent_version_id}`}
                  </p>
                </div>
                {!p.is_active && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleActivate(p.id);
                    }}
                    className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 disabled:opacity-60"
                    disabled={saving}
                  >
                    Activate
                  </button>
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="lg:col-span-2 bg-white rounded-lg shadow-md p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-gray-900">Edit Prompt</h3>
            <p className="text-sm text-gray-600">
              Placeholders required: {REQUIRED_PLACEHOLDERS.join(', ')}. Include criteria text if needed.
            </p>
          </div>
          <div className="text-xs text-gray-500">
            Editing v{selectedPrompt?.version} {selectedPrompt?.is_active ? '(active)' : ''}
          </div>
        </div>

        <textarea
          value={templateDraft}
          onChange={(e) => setTemplateDraft(e.target.value)}
          rows={12}
          className="w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm"
        />

        {placeholdersMissing.length > 0 && (
          <div className="text-sm text-red-700 bg-red-50 border border-red-200 rounded-md p-3">
            Missing placeholders: {placeholdersMissing.join(', ')}
          </div>
        )}

        <div className="flex flex-wrap gap-3">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-60 text-sm"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
          <button
            onClick={() => selectedPrompt && handleActivate(selectedPrompt.id)}
            disabled={saving || !selectedPrompt}
            className="px-4 py-2 bg-green-100 text-green-800 rounded-md hover:bg-green-200 disabled:opacity-60 text-sm"
          >
            Set Active
          </button>
          <button
            onClick={handleCreateNew}
            disabled={creating}
            className="px-4 py-2 bg-purple-100 text-purple-800 rounded-md hover:bg-purple-200 disabled:opacity-60 text-sm"
          >
            {creating ? 'Creating...' : 'Create New Version'}
          </button>
        </div>
      </div>
    </div>
  );
}
