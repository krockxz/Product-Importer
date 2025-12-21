import React, { useState, useEffect } from 'react';
import { Trash2, Search, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Dialog, DialogHeader, DialogTitle, DialogContent, DialogFooter } from './ui/dialog';
import { productsApi } from '@/services/api';
import type { Product } from '@/services/api';

export function ProductList({ refreshTrigger }: { refreshTrigger?: number }) {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [filters, setFilters] = useState({
    sku: '',
    name: '',
  });
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const pageSize = 20;
      const response: any = await productsApi.getProducts({
        page,
        page_size: pageSize,
        sku: filters.sku || undefined,
        name: filters.name || undefined,
      });

      const data = response.data || response;
      setProducts(data.results);
      setTotalCount(data.count);
      setTotalPages(Math.ceil(data.count / pageSize));
    } catch (error) {
      console.error('Failed to fetch products:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [page, filters, refreshTrigger]);

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedIds(products.map(p => p.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleSelectOne = (id: number, checked: boolean) => {
    if (checked) {
      setSelectedIds([...selectedIds, id]);
    } else {
      setSelectedIds(selectedIds.filter(selectedId => selectedId !== id));
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await productsApi.deleteProduct(id);
      fetchProducts();
    } catch (error) {
      console.error('Failed to delete product:', error);
    }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) return;

    try {
      setDeleteLoading(true);
      await productsApi.bulkDelete(selectedIds);
      setSelectedIds([]);
      setShowDeleteModal(false);
      fetchProducts();
    } catch (error) {
      console.error('Failed to bulk delete products:', error);
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPage(1);
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Products</h2>
        {selectedIds.length > 0 && (
          <Button
            variant="destructive"
            onClick={() => setShowDeleteModal(true)}
            className="flex items-center space-x-2"
          >
            <Trash2 className="h-4 w-4" />
            <span>Delete Selected ({selectedIds.length})</span>
          </Button>
        )}
      </div>

      <div className="flex space-x-4 mb-6">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Filter by SKU..."
            value={filters.sku}
            onChange={(e) => handleFilterChange('sku', e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Filter by Name..."
            value={filters.name}
            onChange={(e) => handleFilterChange('name', e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4">
                    <input
                      type="checkbox"
                      checked={selectedIds.length === products.length && products.length > 0}
                      onChange={(e) => handleSelectAll(e.target.checked)}
                      className="rounded border-gray-300"
                    />
                  </th>
                  <th className="text-left py-3 px-4">SKU</th>
                  <th className="text-left py-3 px-4">Name</th>
                  <th className="text-left py-3 px-4">Price</th>
                  <th className="text-left py-3 px-4">Stock</th>
                  <th className="text-left py-3 px-4">Created</th>
                  <th className="text-left py-3 px-4"></th>
                </tr>
              </thead>
              <tbody>
                {products.map((product) => (
                  <tr key={`${product.id}-${product.sku}`} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(product.id)}
                        onChange={(e) => handleSelectOne(product.id, e.target.checked)}
                        className="rounded border-gray-300"
                      />
                    </td>
                    <td className="py-3 px-4 font-mono text-sm">{product.sku}</td>
                    <td className="py-3 px-4">{product.name}</td>
                    <td className="py-3 px-4">{product.price || '-'}</td>
                    <td className="py-3 px-4">{product.stock ?? '-'}</td>
                    <td className="py-3 px-4 text-sm text-gray-500">
                      {new Date(product.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(product.id)}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {products.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No products found
              </div>
            )}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-6">
              <p className="text-sm text-gray-600">
                Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, totalCount)} of {totalCount} results
              </p>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className="px-3 py-1 text-sm">
                  Page {page} of {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setPage(page + 1)}
                  disabled={page === totalPages}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </>
      )}

      <Dialog open={showDeleteModal} onOpenChange={setShowDeleteModal}>
        <DialogHeader>
          <DialogTitle>Confirm Bulk Delete</DialogTitle>
        </DialogHeader>
        <DialogContent>
          <p>
            Are you sure you want to delete {selectedIds.length} selected product(s)?
            This action cannot be undone.
          </p>
        </DialogContent>
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => setShowDeleteModal(false)}
            disabled={deleteLoading}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleBulkDelete}
            disabled={deleteLoading}
          >
            {deleteLoading ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
  );
}