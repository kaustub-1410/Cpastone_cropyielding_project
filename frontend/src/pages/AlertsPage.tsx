import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  ShieldAlert,
  CheckCircle2,
  Filter,
  RefreshCw,
  Search,
  Check,
  Clock,
  Eye,
  Info,
} from 'lucide-react';
import { api } from '../services/api';
import { AlertItem } from '../types';

export const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const data = await api.getAlerts({
        severity: severityFilter !== 'all' ? severityFilter : undefined,
        status: statusFilter !== 'all' ? statusFilter : undefined,
        limit: 100,
      });
      setAlerts(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [severityFilter, statusFilter]);

  const handleUpdateStatus = async (alertId: string, newStatus: 'acknowledged' | 'resolved') => {
    setUpdatingId(alertId);
    try {
      await api.updateAlertStatus(alertId, newStatus);
      fetchAlerts();
    } catch (err) {
      console.error(err);
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            Agronomic Stress & Low-Yield Alerts
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Rule-based threshold triggers, drought/heat anomaly flags, and lifecycle review actions.
          </p>
        </div>

        <button
          onClick={fetchAlerts}
          className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium border border-slate-700 flex items-center gap-2 transition w-fit"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Refresh Alerts
        </button>
      </div>

      {/* Filter Bar */}
      <div className="glass-card p-4 rounded-xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <span className="text-xs text-slate-400 flex items-center gap-1.5 font-medium">
            <Filter className="w-3.5 h-3.5" /> Filter By:
          </span>

          {/* Severity Filter */}
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-emerald-500"
          >
            <option value="all">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Warning">Warning</option>
            <option value="Info">Info</option>
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-emerald-500"
          >
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="acknowledged">Acknowledged</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>

        <div className="text-xs text-slate-400">
          Showing <span className="text-white font-semibold">{alerts.length}</span> recorded alerts
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {loading && alerts.length === 0 ? (
          <div className="py-12 text-center text-slate-500 text-sm">Loading alerts...</div>
        ) : alerts.length > 0 ? (
          alerts.map((alt) => (
            <div
              key={alt.alert_id}
              className={`p-5 rounded-xl border transition ${
                alt.status === 'resolved'
                  ? 'bg-slate-900/40 border-slate-800/80 opacity-70'
                  : alt.severity === 'Critical'
                  ? 'glass-card border-rose-500/40'
                  : alt.severity === 'High'
                  ? 'glass-card border-amber-500/30'
                  : 'glass-card border-slate-800'
              }`}
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-xs font-bold text-slate-400">{alt.alert_id}</span>
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
                    <span className="text-xs font-semibold text-white">
                      {alt.field_id} &bull; {alt.crop} ({alt.region})
                    </span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded font-medium ${
                        alt.status === 'resolved'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : alt.status === 'acknowledged'
                          ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                          : 'bg-slate-800 text-slate-300'
                      }`}
                    >
                      {alt.status.toUpperCase()}
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-white mt-1">{alt.rule_name}</h3>
                  <p className="text-xs text-slate-300">{alt.reason}</p>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-2 self-start md:self-center shrink-0">
                  {alt.status === 'active' && (
                    <button
                      onClick={() => handleUpdateStatus(alt.alert_id, 'acknowledged')}
                      disabled={updatingId === alt.alert_id}
                      className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 flex items-center gap-1.5 transition"
                    >
                      <Eye className="w-3.5 h-3.5 text-blue-400" /> Acknowledge
                    </button>
                  )}
                  {alt.status !== 'resolved' && (
                    <button
                      onClick={() => handleUpdateStatus(alt.alert_id, 'resolved')}
                      disabled={updatingId === alt.alert_id}
                      className="px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 text-xs font-medium flex items-center gap-1.5 transition"
                    >
                      <Check className="w-3.5 h-3.5 text-emerald-400" /> Resolve
                    </button>
                  )}
                </div>
              </div>

              {/* Action Recommendation */}
              <div className="mt-3 pt-3 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between text-xs text-slate-400 gap-2">
                <div>
                  <span className="font-semibold text-slate-300">Suggested Action:</span> {alt.suggested_action}
                </div>
                <div className="text-[11px] text-slate-500 flex items-center gap-1 shrink-0">
                  <Clock className="w-3 h-3" />
                  {alt.created_at ? new Date(alt.created_at).toLocaleString() : 'Recent'}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="glass-card p-12 rounded-xl border border-slate-800 text-center flex flex-col items-center justify-center space-y-2">
            <CheckCircle2 className="w-10 h-10 text-emerald-400" />
            <h3 className="text-base font-semibold text-white">No Matching Alerts</h3>
            <p className="text-xs text-slate-400">All agricultural observations are within nominal yield and climate bounds.</p>
          </div>
        )}
      </div>
    </div>
  );
};
