import { useState, useEffect } from 'react';
import { Plus, Trash2, TestTube, ExternalLink, Check, X, Power } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Dialog, DialogHeader, DialogTitle, DialogContent, DialogFooter } from './ui/dialog';
import { webhooksApi } from '@/services/api';
import type { Webhook } from '@/services/api';

const EVENT_TYPES = [
  { id: 'product.created', label: 'Product Created' },
  { id: 'product.updated', label: 'Product Updated' },
  { id: 'product.deleted', label: 'Product Deleted' },
  { id: 'bulk_import.completed', label: 'Bulk Import Completed' },
];

export function WebhooksTab() {
  const [webhooks, setWebhooks] = useState<Webhook[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createLoading, setCreateLoading] = useState(false);
  const [testResults, setTestResults] = useState<{ [key: number]: 'testing' | 'success' | 'error' | null }>({});
  const [newWebhook, setNewWebhook] = useState({
    url: '',
    event_types: [] as string[],
  });

  const fetchWebhooks = async () => {
    try {
      setLoading(true);
      const response = await webhooksApi.list();
      setWebhooks((response as any).data || response);
    } catch (error) {
      console.error('Failed to fetch webhooks:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWebhooks();
  }, []);

  const [createError, setCreateError] = useState<string | null>(null);

  const handleCreate = async () => {
    if (!newWebhook.url || newWebhook.event_types.length === 0) return;

    try {
      setCreateLoading(true);
      setCreateError(null);
      await webhooksApi.create(newWebhook);
      setNewWebhook({ url: '', event_types: [] });
      setShowCreateModal(false);
      fetchWebhooks();
    } catch (error: any) {
      console.error('Failed to create webhook:', error);
      const msg = error.response?.data?.non_field_errors?.[0]
        || error.response?.data?.url?.[0]
        || error.response?.data?.event_type?.[0]
        || 'Failed to create webhook';
      setCreateError(msg);
    } finally {
      setCreateLoading(false);
    }
  };

  // ... (inside DialogContent)

  {
    createError && (
      <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md border border-red-200">
        {createError}
      </div>
    )
  }

  <div>
    <label className="block text-sm font-medium mb-2">URL</label>
    {/* ... */}

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this webhook?')) return;

    try {
      await webhooksApi.delete(id);
    fetchWebhooks();
    } catch (error) {
      console.error('Failed to delete webhook:', error);
    }
  };

  const handleTest = async (id: number) => {
    try {
      setTestResults(prev => ({ ...prev, [id]: 'testing' }));
    await webhooksApi.test(id);
      setTestResults(prev => ({...prev, [id]: 'success' }));
      setTimeout(() => {
      setTestResults(prev => ({ ...prev, [id]: null }));
      }, 3000);
    } catch (error) {
      setTestResults(prev => ({ ...prev, [id]: 'error' }));
      setTimeout(() => {
      setTestResults(prev => ({ ...prev, [id]: null }));
      }, 3000);
    console.error('Failed to test webhook:', error);
    }
  };

  const handleToggleActive = async (id: number, currentState: boolean) => {
    try {
      await webhooksApi.update(id, { is_active: !currentState });
    fetchWebhooks();
    } catch (error) {
      console.error('Failed to toggle webhook:', error);
    }
  };

  const toggleEventType = (eventType: string) => {
      setNewWebhook(prev => ({
        ...prev,
        event_types: prev.event_types.includes(eventType)
          ? prev.event_types.filter(t => t !== eventType)
          : [...prev.event_types, eventType],
      }));
  };

    return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Webhooks</h2>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Webhook
        </Button>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      ) : (
        <>
          {webhooks.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p className="text-lg mb-2">No webhooks configured</p>
              <p className="text-sm">Add a webhook to receive real-time notifications</p>
            </div>
          ) : (
            <div className="space-y-4">
              {Array.isArray(webhooks) && webhooks.map((webhook) => (
                <div key={webhook.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="font-medium">{webhook.url}</h3>
                        <button
                          onClick={() => handleToggleActive(webhook.id, webhook.is_active)}
                          className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium cursor-pointer transition-colors ${webhook.is_active
                            ? 'bg-green-100 text-green-800 hover:bg-green-200'
                            : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                            }`}
                          title="Click to toggle"
                        >
                          <Power className="h-3 w-3 mr-1" />
                          {webhook.is_active ? 'Active' : 'Inactive'}
                        </button>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {webhook.event_types.map(eventType => (
                          <span
                            key={eventType}
                            className="inline-flex items-center px-2 py-1 rounded bg-gray-100 text-xs text-gray-700"
                          >
                            {EVENT_TYPES.find(t => t.id === eventType)?.label || eventType}
                          </span>
                        ))}
                      </div>
                      <p className="text-sm text-gray-500 mt-2">
                        Created {new Date(webhook.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleTest(webhook.id)}
                        disabled={testResults[webhook.id] === 'testing'}
                      >
                        {testResults[webhook.id] === 'testing' && (
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2" />
                        )}
                        {testResults[webhook.id] === 'success' && (
                          <Check className="h-4 w-4 text-green-600 mr-2" />
                        )}
                        {testResults[webhook.id] === 'error' && (
                          <X className="h-4 w-4 text-red-600 mr-2" />
                        )}
                        <TestTube className="h-4 w-4 mr-2" />
                        Test
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        asChild
                      >
                        <a href={webhook.url} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(webhook.id)}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogHeader>
          <DialogTitle>Add New Webhook</DialogTitle>
        </DialogHeader>
        <DialogContent>
          <div className="space-y-4">
            {createError && (
              <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md border border-red-200">
                {createError}
              </div>
            )}
            <div>
              <label className="block text-sm font-medium mb-2">URL</label>
              <Input
                placeholder="https://example.com/webhook"
                value={newWebhook.url}
                onChange={(e) => setNewWebhook(prev => ({ ...prev, url: e.target.value }))}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Events</label>
              <div className="space-y-2">
                {EVENT_TYPES.map(eventType => (
                  <label key={eventType.id} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={newWebhook.event_types.includes(eventType.id)}
                      onChange={() => toggleEventType(eventType.id)}
                      className="rounded border-gray-300"
                    />
                    <span className="text-sm">{eventType.label}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </DialogContent>
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => setShowCreateModal(false)}
            disabled={createLoading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleCreate}
            disabled={createLoading || !newWebhook.url || newWebhook.event_types.length === 0}
          >
            {createLoading ? 'Creating...' : 'Create'}
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
    );
}