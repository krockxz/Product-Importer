import React, { useState, useCallback } from 'react';
import { Upload, File, X, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { productsApi } from '@/services/api';
import type { UploadResponse, TaskStatus } from '@/services/api';

export function FileUpload({ onUploadComplete }: { onUploadComplete?: () => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<TaskStatus | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    try {
      setUploading(true);
      const response: any = await productsApi.upload(file);
      const data = response.data || response;
      setTaskId(data.task_id);
      pollStatus(data.task_id);
    } catch (error) {
      console.error('Upload failed:', error);
      setUploading(false);
    }
  };

  const pollStatus = async (taskId: string) => {
    try {
      const response: any = await productsApi.getTaskStatus(taskId);
      const taskStatus: TaskStatus = response.data || response;
      setStatus(taskStatus);

      if (taskStatus.status === 'pending' || taskStatus.status === 'processing') {
        setTimeout(() => pollStatus(taskId), 1000);
      } else {
        setUploading(false);
        if (taskStatus.status === 'completed' && onUploadComplete) {
          onUploadComplete();
        }
      }
    } catch (error) {
      console.error('Failed to get status:', error);
      setTimeout(() => pollStatus(taskId), 1000);
    }
  };

  const reset = () => {
    setFile(null);
    setTaskId(null);
    setStatus(null);
    setUploading(false);
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6">Upload Products</h2>

      {!file ? (
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${dragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
            }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <p className="text-lg text-gray-600 mb-2">
            Drag and drop your CSV file here, or
          </p>
          <label className="cursor-pointer">
            <span className="text-blue-600 hover:text-blue-700">browse</span>
            <input
              type="file"
              className="hidden"
              accept=".csv"
              onChange={handleFileChange}
            />
          </label>
          <p className="text-sm text-gray-500 mt-2">CSV files only</p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <File className="h-8 w-8 text-blue-600" />
              <div>
                <p className="font-medium">{file.name}</p>
                <p className="text-sm text-gray-500">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            {!uploading && (
              <Button
                variant="ghost"
                size="icon"
                onClick={reset}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>

          {!uploading && !taskId && (
            <div className="flex space-x-3">
              <Button onClick={handleUpload} className="flex-1">
                Upload File
              </Button>
              <Button variant="outline" onClick={reset}>
                Cancel
              </Button>
            </div>
          )}

          {taskId && status && (
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                {status.status === 'completed' ? (
                  <CheckCircle className="h-5 w-5 text-green-600" />
                ) : status.status === 'failed' ? (
                  <AlertCircle className="h-5 w-5 text-red-600" />
                ) : (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600" />
                )}
                <span className="font-medium capitalize">{status.status}</span>
                {status.progress > 0 && (
                  <span className="text-gray-500">({status.progress}%)</span>
                )}
              </div>

              <Progress value={status.progress} />

              <p className="text-sm text-gray-600">{status.message}</p>

              {status.processed_count !== undefined && status.total_count && (
                <p className="text-sm text-gray-500">
                  Processed: {status.processed_count} of {status.total_count} products
                </p>
              )}

              {status.errors && status.errors.length > 0 && (
                <div className="p-3 bg-red-50 rounded-lg">
                  <p className="text-sm font-medium text-red-800 mb-1">Errors:</p>
                  <ul className="text-sm text-red-700 space-y-1">
                    {status.errors.slice(0, 5).map((error, idx) => (
                      <li key={idx}>• {error}</li>
                    ))}
                    {status.errors.length > 5 && (
                      <li>• ... and {status.errors.length - 5} more</li>
                    )}
                  </ul>
                </div>
              )}

              {(status.status === 'completed' || status.status === 'failed') && (
                <Button variant="outline" onClick={reset} className="w-full">
                  Upload Another File
                </Button>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}