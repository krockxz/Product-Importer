import { Trash2 } from 'lucide-react';
import { Button } from './ui/button';
import { Dialog, DialogHeader, DialogTitle, DialogContent, DialogFooter } from './ui/dialog';

interface ProductDeleteAllProps {
    totalCount: number;
    showModal: boolean;
    onOpenModal: (open: boolean) => void;
    onConfirm: () => void;
    loading: boolean;
}

export function ProductDeleteAll({
    totalCount,
    showModal,
    onOpenModal,
    onConfirm,
    loading
}: ProductDeleteAllProps) {
    if (totalCount === 0) return null;

    return (
        <>
            <div className="mt-8 pt-6 border-t border-gray-200">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-red-900 mb-2">Danger Zone</h3>
                    <p className="text-sm text-red-700 mb-3">
                        Delete all {totalCount} products from the database. This action cannot be undone.
                    </p>
                    <Button
                        variant="destructive"
                        onClick={() => onOpenModal(true)}
                        className="text-sm"
                    >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete All Products
                    </Button>
                </div>
            </div>

            <Dialog open={showModal} onOpenChange={onOpenModal}>
                <DialogHeader>
                    <DialogTitle>Delete All Products?</DialogTitle>
                </DialogHeader>
                <DialogContent>
                    <div className="space-y-3">
                        <p className="text-red-800 font-semibold">⚠️ Warning: This action cannot be undone!</p>
                        <p>
                            You are about to delete <strong>all {totalCount} products</strong> from the database.
                            This will permanently remove all product data.
                        </p>
                        <p className="text-sm text-gray-600">
                            Are you absolutely sure you want to continue?
                        </p>
                    </div>
                </DialogContent>
                <DialogFooter>
                    <Button
                        variant="outline"
                        onClick={() => onOpenModal(false)}
                        disabled={loading}
                    >
                        Cancel
                    </Button>
                    <Button
                        variant="destructive"
                        onClick={onConfirm}
                        disabled={loading}
                    >
                        {loading ? 'Deleting...' : 'Yes, Delete All Products'}
                    </Button>
                </DialogFooter>
            </Dialog>
        </>
    );
}
