import React, { useState, useEffect } from 'react';
import {
  History,
  Search,
  Filter,
  Download,
  ChevronLeft,
  ChevronRight,
  Eye,
  RefreshCw,
  X,
  TrendingUp,
} from 'lucide-react';
import { api } from '../services/api';

export const HistoryPage: React.FC = () => {
  const [items, setItems] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(15);
  const [search, setSearch] = useState('');
  const [cropFilter, setCropFilter] = useState('all');
  const [regionFilter, setRegionFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState<any | null>(null);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await api.getPredictionHistory({
        page,
        limit,
        search: search.trim() || undefined,
        crop: cropFilter !== 'all' ? cropFilter : undefined,
        region: regionFilter !== 'all' ? regionFilter : undefined,
      });
      setItems(data.items || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, cropFilter, regionFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchHistory();
  };

  const handleExportCSV = () => {
    if (items.length === 0) return;
    const headers = [
      'Prediction_ID', 'Field_ID', 'Crop', 'Season', 'Region', 'Predicted_Yield_t_ha',
      'Lower_Bound', 'Upper_Bound', 'Model', 'Created_At'
    ];
    const rows = items.map((r) => [
      r.prediction_id,
      r.field_id,
      r.crop,
      r.season,
      r.region,
      r.predicted_yield_t_ha,
      r.lower_bound_t_ha,
      r.upper_bound_t_ha,
      r.model_id,
      r.created_at,
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `crop_predictions_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            Prediction History & Audit Log
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Searchable historical agricultural forecasts with confidence intervals and persistence audit.
          </p>
        </div>

        <button
          onClick={handleExportCSV}
          disabled={items.length === 0}
          className="px-3.5 py-2 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 disabled:opacity-50 rounded-lg text-xs font-medium flex items-center gap-2 transition w-fit"
        >
          <Download className="w-3.5 h-3.5" /> Export to CSV
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-card p-4 rounded-xl border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 w-full md:w-auto">
          <div className="relative w-full md:w-72">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search Field ID or Prediction UUID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg pl-9 pr-3 py-2 focus:outline-none focus:border-emerald-500"
            />
          </div>
          <button
            type="submit"
            className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium border border-slate-700 transition shrink-0"
          >
            Search
          </button>
        </form>

        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto justify-end">
          <select
            value={cropFilter}
            onChange={(e) => {
              setCropFilter(e.target.value);
              setPage(1);
            }}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-emerald-500"
          >
            <option value="all">All Crops</option>
            {['Wheat', 'Rice', 'Maize', 'Soybean', 'Cotton', 'Barley', 'Sorghum'].map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>

          <select
            value={regionFilter}
            onChange={(e) => {
              setRegionFilter(e.target.value);
              setPage(1);
            }}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-emerald-500"
          >
            <option value="all">All Regions</option>
            {['Punjab', 'Haryana', 'Uttar Pradesh', 'Madhya Pradesh', 'Maharashtra', 'Karnataka', 'Bihar', 'Rajasthan', 'West Bengal', 'Gujarat'].map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>
      </div>

      {/* History Table */}
      <div className="glass-card p-6 rounded-xl border border-slate-800 space-y-4">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/60 text-slate-400 uppercase tracking-wider text-[10px]">
                <th className="p-3">Prediction ID</th>
                <th className="p-3">Field ID</th>
                <th className="p-3">Crop</th>
                <th className="p-3">Season</th>
                <th className="p-3">Region</th>
                <th className="p-3 text-right font-bold text-emerald-400">Yield (t/ha)</th>
                <th className="p-3 text-center">90% Interval</th>
                <th className="p-3">Model</th>
                <th className="p-3">Date</th>
                <th className="p-3 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {loading ? (
                <tr>
                  <td colSpan={10} className="p-8 text-center text-slate-500 font-sans">
                    Loading prediction history records...
                  </td>
                </tr>
              ) : items.length > 0 ? (
                items.map((r) => (
                  <tr key={r.prediction_id} className="hover:bg-slate-900/40 transition">
                    <td className="p-3 text-slate-400">{r.prediction_id}</td>
                    <td className="p-3 text-white font-sans font-semibold">{r.field_id}</td>
                    <td className="p-3 text-emerald-400 font-sans">{r.crop}</td>
                    <td className="p-3 text-slate-300 font-sans">{r.season}</td>
                    <td className="p-3 text-slate-300 font-sans">{r.region}</td>
                    <td className="p-3 text-right font-bold text-emerald-400">{r.predicted_yield_t_ha}</td>
                    <td className="p-3 text-center text-slate-400 text-[11px]">
                      {r.lower_bound_t_ha !== undefined && r.upper_bound_t_ha !== undefined
                        ? `[${r.lower_bound_t_ha} - ${r.upper_bound_t_ha}]`
                        : '—'}
                    </td>
                    <td className="p-3 text-slate-400 text-[11px] font-sans">{r.model_id}</td>
                    <td className="p-3 text-slate-400 text-[11px] font-sans">
                      {r.created_at ? new Date(r.created_at).toLocaleDateString() : '—'}
                    </td>
                    <td className="p-3 text-center">
                      <button
                        onClick={() => setSelectedItem(r)}
                        className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
                        title="View Full Breakdown"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={10} className="p-8 text-center text-slate-500 font-sans">
                    No historical predictions found matching the search criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="flex items-center justify-between pt-2 border-t border-slate-800/80 text-xs text-slate-400">
          <div>
            Showing {(page - 1) * limit + 1} to {Math.min(page * limit, total)} of {total} records
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 disabled:opacity-40 hover:bg-slate-800 transition"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-semibold text-slate-200">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 disabled:opacity-40 hover:bg-slate-800 transition"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Detail Modal / Drawer */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-xl w-full p-6 space-y-4 shadow-2xl relative">
            <button
              onClick={() => setSelectedItem(null)}
              className="absolute right-4 top-4 text-slate-400 hover:text-white p-1"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="border-b border-slate-800 pb-3">
              <span className="text-xs text-slate-400 font-mono">{selectedItem.prediction_id}</span>
              <h2 className="text-lg font-bold text-white mt-1">
                {selectedItem.field_id} &bull; {selectedItem.crop} ({selectedItem.region})
              </h2>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                <div className="text-[11px] text-slate-400">Forecasted Yield</div>
                <div className="text-2xl font-bold text-emerald-400 mt-1">
                  {selectedItem.predicted_yield_t_ha} <span className="text-xs text-slate-400">t/ha</span>
                </div>
              </div>
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                <div className="text-[11px] text-slate-400">90% Calibrated Interval</div>
                <div className="text-sm font-semibold text-slate-200 mt-2 font-mono">
                  [{selectedItem.lower_bound_t_ha} - {selectedItem.upper_bound_t_ha}] t/ha
                </div>
              </div>
            </div>

            {selectedItem.top_drivers && selectedItem.top_drivers.length > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Top Influencing Feature Drivers
                </h3>
                <div className="space-y-1.5">
                  {selectedItem.top_drivers.map((d: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-2 rounded bg-slate-950/80 border border-slate-800 text-xs flex items-center justify-between"
                    >
                      <span>{d.feature_name}</span>
                      <span className="font-mono text-emerald-400">
                        {d.impact >= 0 ? `+${d.impact}` : d.impact} t/ha
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <button
              onClick={() => setSelectedItem(null)}
              className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-medium transition"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
