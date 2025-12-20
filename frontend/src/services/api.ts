import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

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

  deleteProduct: (id: number): Promise<void> => {
    return api.delete(`/products/${id}/`).then(() => { });
  },

  bulkDelete: (ids: number[]): Promise<void> => {
    return api.post('/products/bulk-delete/', { ids }).then(() => { });
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

  delete: (id: number): Promise<void> => {
    return api.delete(`/products/webhooks/${id}/`).then(() => { });
  },

  test: (id: number): Promise<void> => {
    return api.post(`/products/webhooks/${id}/test/`).then(() => { });
  },
};