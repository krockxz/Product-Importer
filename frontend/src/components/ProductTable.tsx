import { Trash2, Edit } from 'lucide-react';
import { Button } from './ui/button';
import type { Product } from '@/services/api';

interface ProductTableProps {
    products: Product[];
    selectedIds: number[];
    onSelectAll: (checked: boolean) => void;
    onSelectOne: (id: number, checked: boolean) => void;
    onEdit: (product: Product) => void;
    onDelete: (id: number) => void;
    isEmpty: boolean;
}

export function ProductTable({
    products,
    selectedIds,
    onSelectAll,
    onSelectOne,
    onEdit,
    onDelete,
    isEmpty
}: ProductTableProps) {
    if (isEmpty) {
        return (
            <div className="text-center py-8 text-gray-500">
                No products found
            </div>
        );
    }

    return (
        <div className="overflow-x-auto">
            <table className="w-full">
                <thead>
                    <tr className="border-b">
                        <th className="text-left py-3 px-4">
                            <input
                                type="checkbox"
                                checked={products.length > 0 && selectedIds.length === products.length}
                                onChange={(e) => onSelectAll(e.target.checked)}
                                className="rounded border-gray-300"
                            />
                        </th>
                        <th className="text-left py-3 px-4">SKU</th>
                        <th className="text-left py-3 px-4">Name</th>
                        <th className="text-left py-3 px-4">Created</th>
                        <th className="text-left py-3 px-4">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {products.map((product) => (
                        <tr key={`${product.id}-${product.sku}`} className="border-b hover:bg-gray-50">
                            <td className="py-3 px-4">
                                <input
                                    type="checkbox"
                                    checked={selectedIds.includes(product.id)}
                                    onChange={(e) => onSelectOne(product.id, e.target.checked)}
                                    className="rounded border-gray-300"
                                />
                            </td>
                            <td className="py-3 px-4 font-mono text-sm">{product.sku}</td>
                            <td className="py-3 px-4">{product.name}</td>
                            <td className="py-3 px-4 text-sm text-gray-500">
                                {new Date(product.created_at).toLocaleDateString()}
                            </td>
                            <td className="py-3 px-4">
                                <div className="flex items-center space-x-2">
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        onClick={() => onEdit(product)}
                                        className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                                    >
                                        <Edit className="h-4 w-4" />
                                    </Button>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        onClick={() => onDelete(product.id)}
                                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                </div>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
