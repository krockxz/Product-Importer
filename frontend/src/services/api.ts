import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Product {
  id: number;
  sku: string;
  name: string;
  description?: string;
  price?: string;
  stock?: number;
  active?: boolean;
  created_at: string;
  updated_at: string;
}

export interface UploadResponse {
  task_id: string;
  message: string;
}

export interface TaskStatus {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  processed_count?: number;
  total_count?: number;
  errors?: string[];
}

export interface PaginatedProducts {
  count: number;
  next: string | null;
  previous: string | null;
  results: Product[];
}

export interface Webhook {
  id: number;
  url: string;
  event_types: string[];
  is_active: boolean;
  created_at: string;
}

export const productsApi = {
  upload: (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    return api.post('/products/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }).then(res => res.data);
  },

  getTaskStatus: (taskId: string): Promise<TaskStatus> => {
    return api.get(`/products/upload/status/${taskId}/`).then(res => res.data);
  },

  getProducts: (params?: {
    page?: number;
    page_size?: number;
    search?: string;
    sku?: string;
    name?: string;
  }): Promise<PaginatedProducts> => {
    return api.get('/products/', { params }).then(res => res.data);
  },

  createProduct: (data: {
    sku: string;
    name: string;
    description?: string;
    active?: boolean;
  }): Promise<Product> => {
    return api.post('/products/', data).then(res => res.data);
  },

  updateProduct: (id: number, data: Partial<Product>): Promise<Product> => {
    return api.patch(`/products/${id}/`, data).then(res => res.data);
  },

  deleteProduct: (id: number): Promise<void> => {
    return api.delete(`/products/${id}/`).then(() => { });
  },

  bulkDelete: (ids: number[]): Promise<void> => {
    return api.post('/products/bulk-delete/', { ids }).then(() => { });
  },

  deleteAll: (): Promise<{ deleted_count: number }> => {
    return api.delete('/products/delete_all/', {
      data: { confirmed: true }
    }).then(res => res.data.data);
  },
};

export const webhooksApi = {
  list: (): Promise<Webhook[]> => {
    return api.get('/products/webhooks/').then(res => res.data);
  },

  create: (data: {
    url: string;
    event_types: string[];
  }): Promise<Webhook> => {
    return api.post('/products/webhooks/', data).then(res => res.data);
  },

  update: (id: number, data: Partial<Webhook>): Promise<Webhook> => {
    return api.patch(`/products/webhooks/${id}/`, data).then(res => res.data);
  },

  delete: (id: number): Promise<void> => {
    return api.delete(`/products/webhooks/${id}/`).then(() => { });
  },

  test: (id: number): Promise<void> => {
    return api.post(`/products/webhooks/${id}/test/`).then(() => { });
  },
};