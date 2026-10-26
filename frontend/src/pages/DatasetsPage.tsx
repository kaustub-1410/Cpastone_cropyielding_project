import React, { useState, useEffect } from 'react';
import {
  Database,
  Upload,
  Sparkles,
  FileText,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Table,
  Eye,
  Info,
} from 'lucide-react';
import { api } from '../services/api';
import { DatasetItem } from '../types';

export const DatasetsPage: React.FC = () => {
  const [datasets, setDatasets] = useState<DatasetItem[]>([]);
  const [activeSummary, setActiveSummary] = useState<any>(null);
  const [preview, setPreview] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const fetchDatasetList = async () => {
    setLoading(true);
    try {
      const [list, summary] = await Promise.all([
        api.getDatasets(),
        api.getDatasetSummary(),
      ]);
      setDatasets(list);
      setActiveSummary(summary);
      if (list.length > 0) {
        loadPreview(list[0].dataset_id);
      }
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadPreview = async (datasetId: string) => {
    try {
      const p = await api.getDatasetPreview(datasetId, 15);
      setPreview(p);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchDatasetList();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadMessage(null);
    setUploadError(null);
    try {
      const res = await api.uploadDataset(file);
      setUploadMessage(`Successfully validated and uploaded ${res.row_count} records from ${file.name}!`);
      fetchDatasetList();
    } catch (err: any) {
      setUploadError(err?.response?.data?.detail || err?.message || 'CSV upload failed.');
    } finally {
      setUploading(false);
    }
  };

  const handleGenerateSample = async () => {
    setGenerating(true);
    setUploadMessage(null);
    try {
      const res = await api.generateSampleDataset(1200);
      setUploadMessage(res.message);
      fetchDatasetList();
    } catch (err: any) {
      setUploadError('Failed to generate synthetic dataset.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            Dataset & Feature Store Management
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Import agricultural field observations, view schema validation, and inspect training provenance.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleGenerateSample}
            disabled={generating}
            className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 rounded-lg text-xs font-medium border border-slate-700 flex items-center gap-2 transition"
          >
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            {generating ? 'Generating 1,200 Rows...' : 'Generate Synthetic Benchmark Data'}
          </button>
        </div>
      </div>

      {/* Upload & Summary Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Upload Dropzone */}
        <div className="lg:col-span-5 glass-card p-6 rounded-xl border border-slate-800 space-y-4">
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
            <Upload className="w-4 h-4 text-emerald-400" /> Upload CSV Dataset
          </h2>
          <p className="text-xs text-slate-400">
            Files must contain agricultural records (crop, season, region, rainfall, temperature, soil pH, NPK, and actual yield).
          </p>

          <label className="border-2 border-dashed border-slate-700 hover:border-emerald-500/60 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer bg-slate-900/40 transition">
            <Upload className="w-8 h-8 text-slate-400 mb-2" />
            <span className="text-xs font-semibold text-slate-200">
              {uploading ? 'Validating CSV...' : 'Click to select CSV file'}
            </span>
            <span className="text-[11px] text-slate-500 mt-1">Max upload limit: 25MB</span>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
            />
          </label>

          {uploadMessage && (
            <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{uploadMessage}</span>
            </div>
          )}

          {uploadError && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}

          <div className="text-[11px] text-slate-500 pt-2 border-t border-slate-800 flex items-start gap-1.5">
            <Info className="w-3.5 h-3.5 shrink-0 text-slate-400 mt-0.5" />
            <span>
              Synthetic records generated for development and demonstration are explicitly tagged to prevent misleading production claims.
            </span>
          </div>
        </div>

        {/* Active Dataset Summary Card */}
        <div className="lg:col-span-7 glass-card p-6 rounded-xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center gap-2">
              <Database className="w-4 h-4 text-emerald-400" /> Active Dataset Diagnostics
            </h2>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
              {activeSummary?.filename || 'crop_yield_sample_dataset.csv'}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
              <div className="text-[11px] text-slate-400">Total Observations</div>
              <div className="text-xl font-bold text-white mt-1">{activeSummary?.row_count || 1500}</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
              <div className="text-[11px] text-slate-400">Feature Columns</div>
              <div className="text-xl font-bold text-white mt-1">{activeSummary?.column_count || 22}</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
              <div className="text-[11px] text-slate-400">Synthetic Flag</div>
              <div className="text-xl font-bold text-amber-400 mt-1">
                {activeSummary?.is_synthetic ? 'Synthetic' : 'Ground-Truth'}
              </div>
            </div>
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
              <div className="text-[11px] text-slate-400">Training Eligible</div>
              <div className="text-xl font-bold text-emerald-400 mt-1">
                {activeSummary?.is_training_eligible ? 'Eligible' : 'Needs Target'}
              </div>
            </div>
          </div>

          <div>
            <div className="text-xs font-semibold text-slate-300 mb-2">Column Schema</div>
            <div className="flex flex-wrap gap-1.5">
              {(activeSummary?.columns || [
                'field_id', 'crop', 'season', 'region', 'rainfall_mm', 'temperature_min_c', 'temperature_max_c',
                'humidity', 'soil_ph', 'soil_nitrogen', 'soil_phosphorus', 'soil_potassium', 'soil_moisture',
                'irrigation', 'fertilizer_usage', 'vegetation_index_ndvi', 'previous_season_yield', 'actual_yield_t_ha'
              ]).map((col: string) => (
                <span
                  key={col}
                  className={`text-[11px] font-mono px-2 py-0.5 rounded ${
                    col === 'actual_yield_t_ha'
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold'
                      : 'bg-slate-900 text-slate-400 border border-slate-800'
                  }`}
                >
                  {col}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Dataset Preview Table */}
      <div className="glass-card p-6 rounded-xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-white flex items-center gap-2">
              <Table className="w-4 h-4 text-emerald-400" /> Records Preview
            </h2>
            <p className="text-xs text-slate-400">
              Displaying first {preview?.returned_rows || 15} rows of {preview?.total_rows || datasets[0]?.row_count || 1500} records
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300 border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/60 text-slate-400 uppercase tracking-wider text-[10px]">
                <th className="p-2.5">Field ID</th>
                <th className="p-2.5">Crop</th>
                <th className="p-2.5">Season</th>
                <th className="p-2.5">Region</th>
                <th className="p-2.5">Rainfall (mm)</th>
                <th className="p-2.5">T-Min/Max (°C)</th>
                <th className="p-2.5">Soil pH</th>
                <th className="p-2.5">NPK (kg/ha)</th>
                <th className="p-2.5">NDVI</th>
                <th className="p-2.5 font-bold text-emerald-400">Yield (t/ha)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {preview?.records ? (
                preview.records.map((r: any, idx: number) => (
                  <tr key={idx} className="hover:bg-slate-900/40 transition">
                    <td className="p-2.5 text-white font-sans">{r.field_id}</td>
                    <td className="p-2.5 text-emerald-400 font-sans">{r.crop}</td>
                    <td className="p-2.5 font-sans">{r.season}</td>
                    <td className="p-2.5 font-sans">{r.region}</td>
                    <td className="p-2.5">{r.rainfall_mm}</td>
                    <td className="p-2.5">{r.temperature_min_c} / {r.temperature_max_c}</td>
                    <td className="p-2.5">{r.soil_ph}</td>
                    <td className="p-2.5">{r.soil_nitrogen}/{r.soil_phosphorus}/{r.soil_potassium}</td>
                    <td className="p-2.5">{r.vegetation_index_ndvi ?? '—'}</td>
                    <td className="p-2.5 font-bold text-emerald-400">{r.actual_yield_t_ha}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={10} className="p-6 text-center text-slate-500 font-sans">
                    Loading records preview...
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
