import { useState } from 'react';
import { FileUpload } from './components/FileUpload';
import { ProductList } from './components/ProductList';
import { WebhooksTab } from './components/WebhooksTab';
import { Package, Upload, Globe } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState<'upload' | 'products' | 'webhooks'>('upload');
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleUploadComplete = () => {
    // Trigger product list refresh
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <h1 className="text-xl font-bold text-gray-900">Product Importer</h1>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('upload')}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'upload'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Upload className="h-4 w-4" />
              <span>Upload</span>
            </button>
            <button
              onClick={() => setActiveTab('products')}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'products'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Package className="h-4 w-4" />
              <span>Products</span>
            </button>
            <button
              onClick={() => setActiveTab('webhooks')}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'webhooks'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Globe className="h-4 w-4" />
              <span>Webhooks</span>
            </button>
          </nav>
        </div>

        <div className="space-y-8">
          {activeTab === 'upload' && (
            <FileUpload onUploadComplete={handleUploadComplete} />
          )}
          {activeTab === 'products' && (
            <ProductList refreshTrigger={refreshTrigger} />
          )}
          {activeTab === 'webhooks' && (
            <WebhooksTab />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;