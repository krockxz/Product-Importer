import React, { useState } from 'react';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { productsApi } from '@/services/api';

interface ProductFormData {
    sku: string;
    name: string;
    description: string;
    active: boolean;
}

interface ProductFormDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSuccess: () => void;
    productId?: number;
    initialData?: ProductFormData;
    mode: 'create' | 'edit';
}

export function ProductFormDialog({
    open,
    onOpenChange,
    onSuccess,
    productId,
    initialData,
    mode
}: ProductFormDialogProps) {
    const [formData, setFormData] = useState<ProductFormData>(
        initialData || {
            sku: '',
            name: '',
            description: '',
            active: true,
        }
    );
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    React.useEffect(() => {
        if (initialData) {
            setFormData(initialData);
        }
    }, [initialData]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        try {
            setLoading(true);

            if (mode === 'create') {
                await productsApi.createProduct(formData);
            } else if (productId) {
                await productsApi.updateProduct(productId, formData);
            }

            onSuccess();
            onOpenChange(false);

            // Reset form
            setFormData({
                sku: '',
                name: '',
                description: '',
                active: true,
            });
        } catch (err: any) {
            setError(err.response?.data?.error?.message || 'Failed to save product');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (field: keyof ProductFormData, value: string | boolean) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogHeader>
                <DialogTitle>{mode === 'create' ? 'Create Product' : 'Edit Product'}</DialogTitle>
            </DialogHeader>
            <DialogContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium mb-2">
                            SKU <span className="text-red-600">*</span>
                        </label>
                        <Input
                            value={formData.sku}
                            onChange={(e) => handleChange('sku', e.target.value)}
                            placeholder="e.g., PROD-001"
                            required
                            disabled={mode === 'edit'}
                        />
                        {mode === 'edit' && (
                            <p className="text-xs text-gray-500 mt-1">SKU cannot be changed</p>
                        )}
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">
                            Name <span className="text-red-600">*</span>
                        </label>
                        <Input
                            value={formData.name}
                            onChange={(e) => handleChange('name', e.target.value)}
                            placeholder="Product name"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Description</label>
                        <textarea
                            value={formData.description}
                            onChange={(e) => handleChange('description', e.target.value)}
                            placeholder="Product description (optional)"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            rows={3}
                        />
                    </div>

                    <div className="flex items-center space-x-2">
                        <input
                            type="checkbox"
                            id="active"
                            checked={formData.active}
                            onChange={(e) => handleChange('active', e.target.checked)}
                            className="rounded border-gray-300"
                        />
                        <label htmlFor="active" className="text-sm font-medium">
                            Active
                        </label>
                    </div>

                    {error && (
                        <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                            <p className="text-sm text-red-800">{error}</p>
                        </div>
                    )}
                </form>
            </DialogContent>
            <DialogFooter>
                <Button
                    type="button"
                    variant="outline"
                    onClick={() => onOpenChange(false)}
                    disabled={loading}
                >
                    Cancel
                </Button>
                <Button onClick={handleSubmit} disabled={loading}>
                    {loading ? 'Saving...' : mode === 'create' ? 'Create' : 'Save Changes'}
                </Button>
            </DialogFooter>
        </Dialog>
    );
}
