import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Sprout,
  Database,
  BarChart3,
  MapPin,
  AlertTriangle,
  History,
  Info,
  Menu,
  X,
  Activity,
  Cpu,
  Layers,
  ShieldCheck,
} from 'lucide-react';
import { api } from '../../services/api';
import { SystemHealth } from '../../types';

export const AppLayout: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const location = useLocation();

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const data = await api.getHealth();
        setHealth(data);
      } catch (err) {
        setHealth(null);
      }
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 20000);
    return () => clearInterval(interval);
  }, []);

  const navLinks = [
    { to: '/', label: 'Overview', icon: LayoutDashboard },
    { to: '/predict', label: 'Yield Prediction', icon: Sprout },
    { to: '/datasets', label: 'Dataset Management', icon: Database },
    { to: '/evaluation', label: 'Model Evaluation', icon: BarChart3 },
    { to: '/geographic', label: 'Geographic Analysis', icon: MapPin },
    { to: '/alerts', label: 'Alerts & Anomalies', icon: AlertTriangle },
    { to: '/history', label: 'Prediction History', icon: History },
    { to: '/about', label: 'Project Info (BT195)', icon: Info },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col md:flex-row">
      {/* Sidebar - Desktop */}
      <aside className="hidden md:flex flex-col w-72 bg-slate-900 border-r border-slate-800 p-4 shrink-0 justify-between">
        <div>
          {/* Logo / Header */}
          <div className="flex items-center space-x-3 px-2 py-3 border-b border-slate-800 mb-6">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-green-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Sprout className="w-6 h-6 text-slate-950 font-bold" />
            </div>
            <div>
              <div className="text-sm font-semibold tracking-wide text-emerald-400 uppercase">Crop Yield AI</div>
              <div className="text-xs text-slate-400 font-medium">Capstone BT195</div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="space-y-1">
            {navLinks.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30'
                        : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                    }`
                  }
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Bottom System Status Widget */}
        <div className="mt-6 pt-4 border-t border-slate-800 space-y-3">
          <div className="bg-slate-950/70 p-3 rounded-lg border border-slate-800 text-xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-slate-400" /> Backend
              </span>
              <span
                className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                  health?.status === 'healthy'
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                }`}
              >
                {health?.status === 'healthy' ? 'ONLINE' : 'DEGRADED'}
              </span>
            </div>

            <div className="flex items-center justify-between text-slate-400">
              <span className="flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-slate-400" /> Active Model
              </span>
              <span className="text-slate-200 font-medium truncate max-w-[100px]">
                {health?.active_model || 'Ridge Regressor'}
              </span>
            </div>

            <div className="flex items-center justify-between text-slate-400">
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-slate-400" /> Version
              </span>
              <span className="text-slate-300">v{health?.backend_version || '1.0.0'}</span>
            </div>
          </div>

          <div className="text-[11px] text-slate-500 px-1 text-center">
            Pawan Singh & Ishika Pandey<br />
            <span className="text-slate-600">Supervisor: Mr. Rishabh Srivastava</span>
          </div>
        </div>
      </aside>

      {/* Mobile Header */}
      <header className="md:hidden flex items-center justify-between p-4 bg-slate-900 border-b border-slate-800 sticky top-0 z-50">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center">
            <Sprout className="w-5 h-5 text-slate-950 font-bold" />
          </div>
          <div>
            <span className="font-bold text-sm text-emerald-400">Crop Yield AI</span>
            <span className="text-xs text-slate-400 ml-1.5">(BT195)</span>
          </div>
        </div>
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-2 rounded-lg bg-slate-800 text-slate-300"
        >
          {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </header>

      {/* Mobile Dropdown Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-slate-900 border-b border-slate-800 p-4 space-y-1">
          {navLinks.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setMobileMenuOpen(false)}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium ${
                    isActive ? 'bg-emerald-600/20 text-emerald-400' : 'text-slate-400'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </div>
      )}

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto p-4 md:p-8 bg-slate-950">
        <Outlet />
      </main>
    </div>
  );
};
