import React, { useState } from 'react';
import {
  Sprout,
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  TrendingUp,
  ShieldAlert,
  ArrowRight,
  Info,
  RotateCcw,
  Sparkles,
} from 'lucide-react';
import { api } from '../services/api';
import { PredictionInput, PredictionResponse } from '../types';

const PRESETS: Record<string, Partial<PredictionInput>> = {
  'Wheat in Punjab (Optimal)': {
    field_id: 'FLD-PB-101',
    crop: 'Wheat',
    season: 'Rabi',
    region: 'Punjab',
    latitude: 30.90,
    longitude: 75.85,
    rainfall_mm: 480.0,
    temperature_min_c: 11.5,
    temperature_max_c: 25.0,
    humidity: 65.0,
    soil_ph: 6.9,
    soil_nitrogen: 155.0,
    soil_phosphorus: 55.0,
    soil_potassium: 52.0,
    soil_moisture: 33.0,
    irrigation: 'Canal',
    fertilizer_usage: 175.0,
    vegetation_index_ndvi: 0.74,
    previous_season_yield: 4.4,
  },
  'Rice in West Bengal (High Rain)': {
    field_id: 'FLD-WB-202',
    crop: 'Rice',
    season: 'Kharif',
    region: 'West Bengal',
    latitude: 23.23,
    longitude: 87.86,
    rainfall_mm: 1150.0,
    temperature_min_c: 23.0,
    temperature_max_c: 34.0,
    humidity: 82.0,
    soil_ph: 6.5,
    soil_nitrogen: 135.0,
    soil_phosphorus: 48.0,
    soil_potassium: 58.0,
    soil_moisture: 42.0,
    irrigation: 'Canal',
    fertilizer_usage: 160.0,
    vegetation_index_ndvi: 0.78,
    previous_season_yield: 3.9,
  },
  'Maize in Karnataka (Drought Stressed)': {
    field_id: 'FLD-KA-303',
    crop: 'Maize',
    season: 'Kharif',
    region: 'Karnataka',
    latitude: 15.45,
    longitude: 75.00,
    rainfall_mm: 180.0, // Drought stress
    temperature_min_c: 21.0,
    temperature_max_c: 39.5, // High temperature
    humidity: 35.0,
    soil_ph: 6.7,
    soil_nitrogen: 90.0,
    soil_phosphorus: 35.0,
    soil_potassium: 40.0,
    soil_moisture: 14.0,
    irrigation: 'Rainfed',
    fertilizer_usage: 110.0,
    vegetation_index_ndvi: 0.32,
    previous_season_yield: 4.2,
  },
  'Cotton in Maharashtra (Alkaline Soil)': {
    field_id: 'FLD-MH-404',
    crop: 'Cotton',
    season: 'Kharif',
    region: 'Maharashtra',
    latitude: 19.99,
    longitude: 73.78,
    rainfall_mm: 680.0,
    temperature_min_c: 21.0,
    temperature_max_c: 34.0,
    humidity: 68.0,
    soil_ph: 8.8, // Alkaline
    soil_nitrogen: 110.0,
    soil_phosphorus: 45.0,
    soil_potassium: 65.0,
    soil_moisture: 28.0,
    irrigation: 'Drip',
    fertilizer_usage: 140.0,
    vegetation_index_ndvi: 0.61,
    previous_season_yield: 2.2,
  },
};

export const PredictionPage: React.FC = () => {
  const [formData, setFormData] = useState<PredictionInput>({
    field_id: 'FLD-101',
    crop: 'Wheat',
    season: 'Rabi',
    region: 'Punjab',
    latitude: 30.90,
    longitude: 75.85,
    rainfall_mm: 480.0,
    temperature_min_c: 12.0,
    temperature_max_c: 26.0,
    humidity: 65.0,
    soil_ph: 6.8,
    soil_nitrogen: 145.0,
    soil_phosphorus: 55.0,
    soil_potassium: 50.0,
    soil_moisture: 32.0,
    irrigation: 'Canal',
    fertilizer_usage: 165.0,
    vegetation_index_ndvi: 0.72,
    previous_season_yield: 4.2,
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'number' ? (value === '' ? '' : parseFloat(value)) : value,
    }));
  };

  const handleApplyPreset = (presetName: string) => {
    const preset = PRESETS[presetName];
    if (preset) {
      setFormData((prev) => ({ ...prev, ...preset }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.predictYield(formData);
      setResult(res);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to generate prediction.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            Pre-Harvest Crop Yield Predictor
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Input field environmental parameters to calculate expected yield with calibrated uncertainty intervals.
          </p>
        </div>

        {/* Quick Presets */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-400 font-medium flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" /> Presets:
          </span>
          {Object.keys(PRESETS).map((pName) => (
            <button
              key={pName}
              type="button"
              onClick={() => handleApplyPreset(pName)}
              className="text-xs px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
            >
              {pName.split(' ')[0]}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Form Column */}
        <div className="lg:col-span-7">
          <form onSubmit={handleSubmit} className="glass-card p-6 rounded-xl border border-slate-800 space-y-6">
            {/* Section 1: Identification & Location */}
            <div>
              <h2 className="text-sm font-semibold text-emerald-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                1. Crop & Geography
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Field ID</label>
                  <input
                    type="text"
                    name="field_id"
                    value={formData.field_id}
                    onChange={handleChange}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Crop</label>
                  <select
                    name="crop"
                    value={formData.crop}
                    onChange={handleChange}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                    required
                  >
                    {['Wheat', 'Rice', 'Maize', 'Soybean', 'Cotton', 'Barley', 'Sorghum'].map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Season</label>
                  <select
                    name="season"
                    value={formData.season}
                    onChange={handleChange}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                    required
                  >
                    {['Kharif', 'Rabi', 'Zaid'].map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Region / State</label>
                  <select
                    name="region"
                    value={formData.region}
                    onChange={handleChange}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                    required
                  >
                    {['Punjab', 'Haryana', 'Uttar Pradesh', 'Madhya Pradesh', 'Maharashtra', 'Karnataka', 'Bihar', 'Rajasthan', 'West Bengal', 'Gujarat'].map((r) => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Latitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    name="latitude"
                    value={formData.latitude ?? ''}
                    onChange={handleChange}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Longitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    name="longitude"
                    value={formData.longitude ?? ''}
                    onChange={handleChange}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>
            </div>

            {/* Section 2: Weather Observations */}
            <div className="pt-2 border-t border-slate-800">
              <h2 className="text-sm font-semibold text-emerald-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                2. Weather & Climate
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Rainfall (mm)</label>
                  <input
                    type="number"
                    step="0.1"
                    name="rainfall_mm"
                    value={formData.rainfall_mm}
                    onChange={handleChange}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Min Temp (°C)</label>
                  <input
                    type="number"
                    step="0.1"
                    name="temperature_min_c"
                    value={formData.temperature_min_c}
                    onChange={handleChange}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Max Temp (°C)</label>
                  <input
                    type="number"
                    step="0.1"
                    name="temperature_max_c"
                    value={formData.temperature_max_c}
                    onChange={handleChange}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Humidity (%)</label>
                  <input
                    type="number"
                    step="0.1"
                    name="humidity"
                    value={formData.humidity}
                    onChange={handleChange}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>
              </div>
            </div>

            {/* Section 3: Soil Physicochemical Properties */}
            <div className="pt-2 border-t border-slate-800">
              <h2 className="text-sm font-semibold text-emerald-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                3. Soil & Nutrients
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Soil pH</label>
                  <input
                    type="number"
                    step="0.01"
                    name="soil_ph"
                    value={formData.soil_ph}
                    onChange={handleChange}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Nitrogen (N)</label>
                  <input
                    type="number"
                    step="0.1"
                    name="soil_nitrogen"
                    value={formData.soil_nitrogen}
                    onChange={handleChange}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Phosphorus (P)</label>
                  <input
                    type="number"
                    step="0.1"
                    name="soil_phosphorus"
                    value={formData.soil_phosphorus}
                    onChange={handleChange}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Potassium (K)</label>
                  <input
                    type="number"
                    step="0.1"
                    name="soil_potassium"
                    value={formData.soil_potassium}
                    onChange={handleChange}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Moisture (%)</label>
                  <input
                    type="number"
                    step="0.1"
                    name="soil_moisture"
                    value={formData.soil_moisture}
                    onChange={handleChange}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>
              </div>
            </div>

            {/* Section 4: Management & Remote Sensing */}
            <div className="pt-2 border-t border-slate-800">
              <h2 className="text-sm font-semibold text-emerald-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                4. Farm Management & Remote Sensing
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Irrigation</label>
                  <select
                    name="irrigation"
                    value={formData.irrigation}
                    onChange={handleChange}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                    required
                  >
                    {['Canal', 'Tube Well', 'Drip', 'Sprinkler', 'Rainfed'].map((i) => (
                      <option key={i} value={i}>{i}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Fertilizer (kg/ha)</label>
                  <input
                    type="number"
                    step="0.1"
                    name="fertilizer_usage"
                    value={formData.fertilizer_usage}
                    onChange={handleChange}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Sentinel-2 NDVI</label>
                  <input
                    type="number"
                    step="0.01"
                    name="vegetation_index_ndvi"
                    value={formData.vegetation_index_ndvi ?? ''}
                    onChange={handleChange}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Prev Season Yield (t/ha)</label>
                  <input
                    type="number"
                    step="0.01"
                    name="previous_season_yield"
                    value={formData.previous_season_yield ?? ''}
                    onChange={handleChange}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <div className="pt-2 flex items-center justify-between">
              <button
                type="button"
                onClick={() => handleApplyPreset('Wheat in Punjab (Optimal)')}
                className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1.5"
              >
                <RotateCcw className="w-3.5 h-3.5" /> Reset to Default
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-slate-950 font-bold text-sm flex items-center gap-2 shadow-lg shadow-emerald-600/30 transition"
              >
                {loading ? 'Evaluating Model...' : 'Calculate Predicted Yield'}
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>
        </div>

        {/* Prediction Results Display Column */}
        <div className="lg:col-span-5 space-y-6">
          {result ? (
            <div className="glass-card p-6 rounded-xl border border-emerald-500/30 space-y-6">
              {/* Yield Prediction Badge */}
              <div className="text-center pb-6 border-b border-slate-800">
                <div className="text-xs uppercase tracking-wider text-slate-400 font-medium">
                  Forecasted Harvest Yield
                </div>
                <div className="text-5xl font-extrabold text-emerald-400 mt-2 flex items-center justify-center gap-2">
                  {result.predicted_yield_t_ha}
                  <span className="text-lg font-normal text-slate-400">t/ha</span>
                </div>
                {result.lower_bound_t_ha !== undefined && result.upper_bound_t_ha !== undefined && (
                  <div className="mt-2 inline-flex items-center px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 font-medium">
                    90% Calibrated Interval: [{result.lower_bound_t_ha} — {result.upper_bound_t_ha}] t/ha
                  </div>
                )}
                <div className="text-[11px] text-slate-500 mt-2">
                  Estimated via {result.model_name} ({result.model_version})
                </div>
              </div>

              {/* Explainable AI Drivers */}
              <div>
                <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <TrendingUp className="w-3.5 h-3.5 text-emerald-400" /> Key Feature Influences
                </h3>
                <div className="space-y-2">
                  {result.top_drivers.map((d, i) => (
                    <div
                      key={i}
                      className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs flex items-center justify-between"
                    >
                      <div className="space-y-0.5">
                        <span className="font-semibold text-white">{d.feature_name}</span>
                        <div className="text-slate-400 text-[11px]">{d.description}</div>
                      </div>
                      <span
                        className={`font-mono font-bold px-2 py-0.5 rounded text-[11px] ${
                          d.impact >= 0
                            ? 'text-emerald-400 bg-emerald-500/10'
                            : 'text-rose-400 bg-rose-500/10'
                        }`}
                      >
                        {d.impact >= 0 ? `+${d.impact}` : d.impact} t/ha
                      </span>
                    </div>
                  ))}
                </div>
                <div className="text-[10px] text-slate-500 mt-1 italic">
                  *Feature attribution reflects empirical mathematical weights, not verified physiological causation.
                </div>
              </div>

              {/* Detected Anomalies */}
              {result.anomalies.length > 0 && (
                <div>
                  <h3 className="text-xs font-semibold text-rose-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 text-rose-400" /> Agronomic Stress & Anomalies
                  </h3>
                  <div className="space-y-2">
                    {result.anomalies.map((anom, i) => (
                      <div
                        key={i}
                        className="p-2.5 rounded-lg bg-rose-950/30 border border-rose-800/60 text-xs space-y-1"
                      >
                        <div className="flex items-center justify-between font-semibold text-rose-300">
                          <span>{anom.type}</span>
                          <span className="text-[10px] px-1.5 py-0.5 bg-rose-500/20 rounded uppercase">
                            {anom.severity}
                          </span>
                        </div>
                        <p className="text-rose-200/80 text-[11px]">{anom.explanation}</p>
                        <div className="text-slate-300 text-[11px] font-medium">
                          Next Action: {anom.suggested_action}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Low-Yield Alerts */}
              {result.alerts.length > 0 && (
                <div>
                  <h3 className="text-xs font-semibold text-amber-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <ShieldAlert className="w-3.5 h-3.5 text-amber-400" /> Triggered Low-Yield Alerts
                  </h3>
                  <div className="space-y-2">
                    {result.alerts.map((alt, i) => (
                      <div
                        key={i}
                        className="p-2.5 rounded-lg bg-amber-950/30 border border-amber-800/60 text-xs space-y-1"
                      >
                        <div className="font-semibold text-amber-300">{alt.rule_name}</div>
                        <p className="text-amber-200/80 text-[11px]">{alt.reason}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Disclaimer */}
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-[11px] text-slate-400">
                <span className="font-semibold text-slate-300">Responsible Use Notice:</span> Yield forecasts provide empirical decision support. Unforeseen biotic pests, sudden hailstorms, and ground management practices may cause variations.
              </div>
            </div>
          ) : (
            <div className="glass-card p-8 rounded-xl border border-slate-800 text-center flex flex-col items-center justify-center min-h-[420px] space-y-3">
              <div className="w-14 h-14 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-emerald-400">
                <Sprout className="w-7 h-7" />
              </div>
              <h3 className="text-base font-semibold text-white">No Prediction Evaluated Yet</h3>
              <p className="text-xs text-slate-400 max-w-xs">
                Fill in the agronomic form on the left or select a preset to generate a pre-harvest yield prediction.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
