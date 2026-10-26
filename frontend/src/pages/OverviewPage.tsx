import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  TrendingUp,
  AlertTriangle,
  Layers,
  Sprout,
  ArrowUpRight,
  ShieldAlert,
  Cpu,
  RefreshCw,
  CheckCircle2,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  BarChart,
  Bar,
} from 'recharts';
import { api } from '../services/api';
import { AnalyticsOverview } from '../types';

export const OverviewPage: React.FC = () => {
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [trends, setTrends] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [overviewRes, trendsRes] = await Promise.all([
        api.getAnalyticsOverview(),
        api.getYieldTrends(),
      ]);
      setData(overviewRes);
      setTrends(trendsRes.trends || []);
    } catch (err: any) {
      setError(err?.message || 'Failed to connect to backend service.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading && !data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-3">
        <RefreshCw className="w-8 h-8 text-emerald-400 animate-spin" />
        <p className="text-slate-400 text-sm">Loading agricultural intelligence overview...</p>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="p-6 bg-rose-950/40 border border-rose-800 rounded-xl text-rose-200">
        <div className="flex items-center space-x-2 font-semibold text-lg">
          <AlertTriangle className="w-5 h-5 text-rose-400" />
          <span>Backend Connection Offline</span>
        </div>
        <p className="text-sm mt-1 text-rose-300/80">{error}</p>
        <button
          onClick={fetchData}
          className="mt-4 px-4 py-2 bg-rose-800/80 hover:bg-rose-700 text-white rounded-lg text-sm font-medium flex items-center gap-2"
        >
          <RefreshCw className="w-4 h-4" /> Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Banner & Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            Agricultural Intelligence Dashboard
            <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold tracking-wide uppercase">
              BT195 System
            </span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Pre-harvest predictive analytics synthesized from meteorological, soil physicochemical, and satellite vegetation indices.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchData}
            className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium border border-slate-700 flex items-center gap-2 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Refresh
          </button>
          <Link
            to="/predict"
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-semibold rounded-lg text-xs flex items-center gap-2 shadow-lg shadow-emerald-600/20 transition"
          >
            <Sprout className="w-4 h-4" /> New Prediction
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Fields */}
        <div className="glass-card p-5 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-xs font-medium text-slate-400 uppercase tracking-wider">Monitored Fields</div>
            <div className="text-3xl font-bold text-white mt-1">{data?.total_fields || 0}</div>
            <div className="text-xs text-slate-500 mt-1 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3 text-emerald-400" /> Active GIS plots
            </div>
          </div>
          <div className="w-12 h-12 rounded-xl bg-slate-800/80 border border-slate-700 flex items-center justify-center text-emerald-400">
            <Layers className="w-6 h-6" />
          </div>
        </div>

        {/* Total Predictions */}
        <div className="glass-card p-5 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-xs font-medium text-slate-400 uppercase tracking-wider">Forecasts Generated</div>
            <div className="text-3xl font-bold text-white mt-1">{data?.total_predictions || 0}</div>
            <div className="text-xs text-slate-500 mt-1 flex items-center gap-1">
              <TrendingUp className="w-3 h-3 text-emerald-400" /> Empirical ML inference
            </div>
          </div>
          <div className="w-12 h-12 rounded-xl bg-slate-800/80 border border-slate-700 flex items-center justify-center text-blue-400">
            <TrendingUp className="w-6 h-6" />
          </div>
        </div>

        {/* Avg Yield */}
        <div className="glass-card p-5 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-xs font-medium text-slate-400 uppercase tracking-wider">Average Predicted Yield</div>
            <div className="text-3xl font-bold text-emerald-400 mt-1">
              {data?.average_predicted_yield ? `${data.average_predicted_yield} t/ha` : '—'}
            </div>
            <div className="text-xs text-slate-500 mt-1">Tonnes per hectare</div>
          </div>
          <div className="w-12 h-12 rounded-xl bg-slate-800/80 border border-slate-700 flex items-center justify-center text-amber-400">
            <Sprout className="w-6 h-6" />
          </div>
        </div>

        {/* Active Alerts */}
        <div className="glass-card p-5 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-xs font-medium text-slate-400 uppercase tracking-wider">Low-Yield Alerts</div>
            <div className="text-3xl font-bold text-rose-400 mt-1">{data?.active_alerts_count || 0}</div>
            <div className="text-xs text-slate-500 mt-1">
              {data?.critical_alerts_count || 0} critical severity
            </div>
          </div>
          <div className="w-12 h-12 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
            <ShieldAlert className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Active Model Status Strip */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-slate-900 to-slate-900/80 border border-emerald-500/20 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm font-semibold text-white flex items-center gap-2">
              Production Model: {data?.active_model_name}
              <span className="text-xs text-slate-400">({data?.active_model_version})</span>
            </div>
            <div className="text-xs text-slate-400">
              Selected via validation set benchmarking. Calibrated conformal confidence intervals enabled.
            </div>
          </div>
        </div>
        <div className="flex items-center gap-6 text-xs">
          <div>
            <span className="text-slate-400">Test R² Score:</span>{' '}
            <span className="font-semibold text-emerald-400">
              {data?.active_model_r2 !== undefined ? data.active_model_r2 : 'N/A'}
            </span>
          </div>
          <div>
            <span className="text-slate-400">Test RMSE:</span>{' '}
            <span className="font-semibold text-blue-400">
              {data?.active_model_rmse !== undefined ? `${data.active_model_rmse} t/ha` : 'N/A'}
            </span>
          </div>
          <Link
            to="/evaluation"
            className="text-emerald-400 hover:text-emerald-300 font-medium flex items-center gap-1"
          >
            View Benchmarks <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Yield Trends Chart */}
        <div className="lg:col-span-2 glass-card p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-white">Multi-Year Yield Dynamics by Crop</h2>
              <p className="text-xs text-slate-400">Empirical trend trajectory across agricultural years (t/ha)</p>
            </div>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trends} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="year" stroke="#64748b" tick={{ fontSize: 12 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 12 }} domain={['auto', 'auto']} unit=" t/ha" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#94a3b8' }}
                />
                <Legend />
                <Line type="monotone" dataKey="Wheat" stroke="#10b981" strokeWidth={2.5} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="Rice" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="Maize" stroke="#f59e0b" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="Soybean" stroke="#a855f7" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="Cotton" stroke="#06b6d4" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Crop Breakdown Bar Chart */}
        <div className="glass-card p-5 rounded-xl border border-slate-800">
          <div className="mb-4">
            <h2 className="text-base font-semibold text-white">Crop Distribution</h2>
            <p className="text-xs text-slate-400">Forecast volume and average productivity</p>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.top_crops || []} margin={{ top: 10, right: 10, left: -15, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="crop" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                />
                <Bar dataKey="avg_yield" name="Avg Yield (t/ha)" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Two Column Section: Recent Predictions & Active Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Predictions */}
        <div className="glass-card p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-white">Recent Yield Forecasts</h2>
            <Link to="/history" className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1">
              All history <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          <div className="space-y-3">
            {data?.recent_predictions && data.recent_predictions.length > 0 ? (
              data.recent_predictions.map((p) => (
                <div
                  key={p.prediction_id}
                  className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 flex items-center justify-between hover:border-slate-700 transition"
                >
                  <div className="space-y-0.5">
                    <div className="text-sm font-semibold text-white flex items-center gap-2">
                      {p.field_id}
                      <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-normal">
                        {p.crop}
                      </span>
                    </div>
                    <div className="text-xs text-slate-400">{p.region}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-base font-bold text-emerald-400">
                      {p.predicted_yield_t_ha} <span className="text-xs font-normal text-slate-400">t/ha</span>
                    </div>
                    {p.lower_bound_t_ha !== undefined && p.upper_bound_t_ha !== undefined && (
                      <div className="text-[11px] text-slate-400">
                        CI: [{p.lower_bound_t_ha} - {p.upper_bound_t_ha}]
                      </div>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-sm text-slate-500 py-6 text-center">No predictions generated yet.</div>
            )}
          </div>
        </div>

        {/* Active Alerts Feed */}
        <div className="glass-card p-5 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-white">Active Alerts & Agronomic Stress</h2>
            <Link to="/alerts" className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1">
              Manage alerts <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          <div className="space-y-3">
            {data?.recent_alerts && data.recent_alerts.length > 0 ? (
              data.recent_alerts.map((alt) => (
                <div
                  key={alt.alert_id}
                  className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition space-y-1.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-white flex items-center gap-2">
                      {alt.field_id} ({alt.crop})
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                        alt.severity === 'Critical'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : alt.severity === 'High'
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                      }`}
                    >
                      {alt.severity}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300">{alt.reason}</p>
                </div>
              ))
            ) : (
              <div className="text-sm text-slate-500 py-6 text-center">No active alerts detected. All plots within normal thresholds.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
