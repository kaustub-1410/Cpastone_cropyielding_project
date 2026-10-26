export interface PredictionInput {
  field_id: string;
  crop: string;
  season: string;
  region: string;
  latitude?: number;
  longitude?: number;
  rainfall_mm: number;
  temperature_min_c: number;
  temperature_max_c: number;
  humidity: number;
  soil_ph: number;
  soil_nitrogen: number;
  soil_phosphorus: number;
  soil_potassium: number;
  soil_moisture: number;
  irrigation: string;
  fertilizer_usage: number;
  vegetation_index_ndvi?: number;
  previous_season_yield?: number;
  actual_yield_t_ha?: number;
}

export interface FeatureDriver {
  feature: string;
  feature_name: string;
  impact: number;
  direction: 'positive' | 'negative' | 'neutral';
  description: string;
}

export interface AnomalyItem {
  type: string;
  severity: 'Info' | 'Warning' | 'High' | 'Critical';
  affected_field: string;
  triggering_value: number;
  reference_range: string;
  explanation: string;
  suggested_action: string;
}

export interface AlertItem {
  alert_id: string;
  field_id: string;
  crop: string;
  region: string;
  severity: 'Info' | 'Warning' | 'High' | 'Critical';
  rule_name: string;
  reason: string;
  predicted_yield?: number;
  threshold_value?: number;
  suggested_action: string;
  status: 'active' | 'acknowledged' | 'resolved';
  created_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
}

export interface PredictionResponse {
  prediction_id: string;
  field_id: string;
  crop: string;
  season: string;
  region: string;
  predicted_yield_t_ha: number;
  lower_bound_t_ha?: number;
  upper_bound_t_ha?: number;
  prediction_interval_calibrated: boolean;
  confidence_level: number;
  forecast_date: string;
  model_name: string;
  model_version: string;
  input_summary: Record<string, any>;
  top_drivers: FeatureDriver[];
  anomalies: AnomalyItem[];
  alerts: AlertItem[];
  data_quality_warnings: string[];
  disclaimer: string;
}

export interface AnalyticsOverview {
  total_fields: number;
  total_predictions: number;
  average_predicted_yield: number;
  active_alerts_count: number;
  critical_alerts_count: number;
  active_model_name: string;
  active_model_version: string;
  active_model_r2?: number;
  active_model_rmse?: number;
  is_synthetic_data: boolean;
  top_crops: Array<{ crop: string; prediction_count: number; avg_yield: number }>;
  recent_predictions: Array<{
    prediction_id: string;
    field_id: string;
    crop: string;
    region: string;
    predicted_yield_t_ha: number;
    lower_bound_t_ha?: number;
    upper_bound_t_ha?: number;
    created_at?: string;
  }>;
  recent_alerts: AlertItem[];
}

export interface ModelMetrics {
  rmse?: number;
  mae?: number;
  r2?: number;
  mape?: number;
  bias?: number;
  coverage_90?: number;
}

export interface ModelEvaluationSummary {
  model_id: string;
  name: string;
  algorithm: string;
  version: string;
  is_active: boolean;
  is_synthetic_trained: boolean;
  validation_metrics: ModelMetrics;
  test_metrics: ModelMetrics;
  train_size: number;
  val_size: number;
  test_size: number;
  created_at: string;
}

export interface ModelComparisonReport {
  models: ModelEvaluationSummary[];
  selected_model_id?: string;
  evaluation_dataset: string;
  split_strategy: string;
  target_unit: string;
}

export interface EvaluationReport {
  model_key: string;
  model_name: string;
  algorithm: string;
  version: string;
  test_sample_size: number;
  overall_metrics: ModelMetrics;
  calibration_quantile_90: number;
  is_synthetic_evaluation: boolean;
  provenance: string;
  scatter_points: Array<{
    actual: number;
    predicted: number;
    lower: number;
    upper: number;
    crop: string;
    region: string;
    field_id: string;
  }>;
  residual_distribution: Array<{
    bin: string;
    count: number;
    midpoint: number;
  }>;
  per_crop_metrics: Record<string, {
    sample_count: number;
    rmse: number;
    mae: number;
    r2: number;
    mape: number;
  }>;
  per_region_metrics: Record<string, {
    sample_count: number;
    rmse: number;
    mae: number;
    r2: number;
  }>;
}

export interface DatasetItem {
  dataset_id: string;
  filename: string;
  row_count: number;
  column_count: number;
  is_synthetic: boolean;
  provenance: string;
  is_training_eligible: boolean;
  created_at: string;
}

export interface FeatureImportanceItem {
  feature: string;
  label: string;
  importance: number;
  category: string;
}

export interface SystemHealth {
  status: string;
  project_id: string;
  project_title: string;
  team_members: string;
  supervisor: string;
  backend_version: string;
  active_model?: string;
  model_version?: string;
  model_trained: boolean;
  database_connected: boolean;
  xgboost_available: boolean;
  shap_available: boolean;
  timestamp: string;
}
