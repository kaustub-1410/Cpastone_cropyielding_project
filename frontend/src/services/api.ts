import axios from 'axios';
import {
  PredictionInput,
  PredictionResponse,
  AnalyticsOverview,
  ModelComparisonReport,
  EvaluationReport,
  DatasetItem,
  AlertItem,
  FeatureImportanceItem,
  SystemHealth,
} from '../types';

const isLocal = typeof window !== 'undefined' && 
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (isLocal ? 'http://127.0.0.1:8000/api' : '/api');

export const apiClient = axios.create({
  baseURL: API_BASE_URL,

  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // System Health & Metadata
  getHealth: async (): Promise<SystemHealth> => {
    const res = await apiClient.get<SystemHealth>('/health');
    return res.data;
  },
  getMetadata: async () => {
    const res = await apiClient.get('/metadata');
    return res.data;
  },

  // Predictions
  predictYield: async (payload: PredictionInput): Promise<PredictionResponse> => {
    const res = await apiClient.post<PredictionResponse>('/predictions', payload);
    return res.data;
  },
  getPredictionHistory: async (params?: { page?: number; limit?: number; crop?: string; region?: string; search?: string }) => {
    const res = await apiClient.get('/predictions/history', { params });
    return res.data;
  },
  getPredictionDetail: async (id: string): Promise<PredictionResponse> => {
    const res = await apiClient.get<PredictionResponse>(`/predictions/${id}`);
    return res.data;
  },

  // Datasets
  getDatasets: async (): Promise<DatasetItem[]> => {
    const res = await apiClient.get<DatasetItem[]>('/datasets');
    return res.data;
  },
  getDatasetSummary: async () => {
    const res = await apiClient.get('/datasets/summary');
    return res.data;
  },
  getDatasetPreview: async (datasetId: string, limit: number = 25) => {
    const res = await apiClient.get(`/datasets/${datasetId}/preview`, { params: { limit } });
    return res.data;
  },
  uploadDataset: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post('/datasets/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
  generateSampleDataset: async (num_samples: number = 1200) => {
    const res = await apiClient.post('/datasets/generate-sample', { num_samples });
    return res.data;
  },

  // Models & Evaluation
  getModels: async (): Promise<ModelComparisonReport> => {
    const res = await apiClient.get<ModelComparisonReport>('/models');
    return res.data;
  },
  getModelEvaluation: async (): Promise<EvaluationReport> => {
    const res = await apiClient.get<EvaluationReport>('/models/evaluation');
    return res.data;
  },
  trainModel: async (datasetId?: string, algorithm?: string) => {
    const res = await apiClient.post('/models/train', {
      dataset_id: datasetId,
      selected_algorithm: algorithm || 'all',
    });
    return res.data;
  },
  getTrainingStatus: async () => {
    const res = await apiClient.get<{ training_in_progress: boolean }>('/models/status');
    return res.data;
  },

  // Alerts & Anomalies
  getAlerts: async (params?: { severity?: string; status?: string; crop?: string; region?: string; limit?: number }): Promise<AlertItem[]> => {
    const res = await apiClient.get<AlertItem[]>('/alerts', { params });
    return res.data;
  },
  updateAlertStatus: async (alertId: string, status: 'acknowledged' | 'resolved'): Promise<AlertItem> => {
    const res = await apiClient.patch<AlertItem>(`/alerts/${alertId}`, { status });
    return res.data;
  },

  // Analytics
  getAnalyticsOverview: async (): Promise<AnalyticsOverview> => {
    const res = await apiClient.get<AnalyticsOverview>('/analytics/overview');
    return res.data;
  },
  getYieldTrends: async (params?: { crop?: string; region?: string }) => {
    const res = await apiClient.get('/analytics/yield-trends', { params });
    return res.data;
  },
  getFeatureImportance: async (): Promise<FeatureImportanceItem[]> => {
    const res = await apiClient.get<FeatureImportanceItem[]>('/analytics/feature-importance');
    return res.data;
  },
  getCropAnalytics: async () => {
    const res = await apiClient.get('/analytics/crops');
    return res.data;
  },
};
