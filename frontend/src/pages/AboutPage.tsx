import React from 'react';
import {
  Info,
  ShieldCheck,
  Cpu,
  Layers,
  Sprout,
  Users,
  Award,
  BookOpen,
  AlertTriangle,
} from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="border-b border-slate-800 pb-5">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-2">
          Capstone Project BT195
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">
          Crop Yield Prediction System Using AI/ML
        </h1>
        <p className="text-slate-400 text-sm mt-1 max-w-3xl">
          An empirical decision support platform developed for precision agriculture, combining meteorological time-series,
          soil physicochemical profiles, Sentinel-2 remote sensing (NDVI), and machine learning regression.
        </p>
      </div>

      {/* Team & Institutional Attribution */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass-card p-5 rounded-xl border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 uppercase tracking-wider">
            <Users className="w-4 h-4" /> Project Authors & Team
          </div>
          <div className="space-y-1.5 text-sm">
            <div className="font-bold text-white text-base">Pawan Singh & Ishika Pandey</div>
            <div className="text-xs text-slate-400">Department of Computer Science & Engineering</div>
            <div className="text-xs text-slate-400">Project Identification Code: <span className="font-mono text-emerald-400">BT195</span></div>
          </div>
        </div>

        <div className="glass-card p-5 rounded-xl border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 uppercase tracking-wider">
            <Award className="w-4 h-4" /> Project Supervision
          </div>
          <div className="space-y-1.5 text-sm">
            <div className="font-bold text-white text-base">Mr. Rishabh Srivastava</div>
            <div className="text-xs text-slate-400">Project Supervisor & Academic Advisor</div>
            <div className="text-xs text-slate-400">Domain: Artificial Intelligence & Precision Agriculture</div>
          </div>
        </div>
      </div>

      {/* System Pipeline & Architecture */}
      <div className="glass-card p-6 rounded-xl border border-slate-800 space-y-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <Layers className="w-5 h-5 text-emerald-400" /> End-to-End Architectural Pipeline
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
          <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
            <div className="font-bold text-emerald-400">1. Data Ingestion</div>
            <p className="text-slate-400">
              CSV schema validation, missing-value imputation (median/mode), duplicate handling, and target leakage prevention.
            </p>
          </div>
          <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
            <div className="font-bold text-blue-400">2. Feature Engineering</div>
            <p className="text-slate-400">
              Growing Degree Days (GDD), De Martonne aridity quotient, NPK macronutrient ratios, and satellite NDVI potential.
            </p>
          </div>
          <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
            <div className="font-bold text-amber-400">3. ML Benchmarking</div>
            <p className="text-slate-400">
              Model selection on validation split: Dummy Baseline vs Ridge Regression vs Random Forest vs XGBoost.
            </p>
          </div>
          <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
            <div className="font-bold text-purple-400">4. Conformal XAI & Alerts</div>
            <p className="text-slate-400">
              Residual-calibrated 90% confidence intervals, SHAP feature attribution, and physiological anomaly detectors.
            </p>
          </div>
        </div>
      </div>

      {/* Agronomic Formulas & Methodologies */}
      <div className="glass-card p-6 rounded-xl border border-slate-800 space-y-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-emerald-400" /> Mathematical & Agronomic Formulations
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-lg bg-slate-900/80 border border-slate-800 space-y-2">
            <div className="font-semibold text-white">Growing Degree Days (GDD)</div>
            <code className="block bg-slate-950 p-2 rounded text-emerald-300 font-mono text-[11px]">
              GDD = max(0, ((T_min + T_max) / 2) - 10.0)
            </code>
            <p className="text-slate-400">
              Quantifies accumulated physiological thermal energy driving crop phenological stages past base temperature (10°C).
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-900/80 border border-slate-800 space-y-2">
            <div className="font-semibold text-white">De Martonne Aridity / Moisture Index</div>
            <code className="block bg-slate-950 p-2 rounded text-blue-300 font-mono text-[11px]">
              I_aridity = Rainfall_mm / (T_avg + 10.0)
            </code>
            <p className="text-slate-400">
              Measures meteorological moisture adequacy relative to evaporative atmospheric demand.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-900/80 border border-slate-800 space-y-2">
            <div className="font-semibold text-white">Finite-Sample Conformal Prediction Interval</div>
            <code className="block bg-slate-950 p-2 rounded text-amber-300 font-mono text-[11px]">
              q_val = Quantile(|y_val - ŷ_val|, (1 - α)(1 + 1/n_val))
            </code>
            <p className="text-slate-400">
              Statistically calibrated 90% confidence interval [ŷ - q, ŷ + q] with guaranteed empirical test coverage.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-900/80 border border-slate-800 space-y-2">
            <div className="font-semibold text-white">Liebig Law of the Minimum on NPK</div>
            <code className="block bg-slate-950 p-2 rounded text-purple-300 font-mono text-[11px]">
              Fertility_Index = min(N/N_req, P/P_req, K/K_req)
            </code>
            <p className="text-slate-400">
              Crop vegetative productivity is constrained by whichever primary macronutrient is most depleted.
            </p>
          </div>
        </div>
      </div>

      {/* Responsible Use & Governance */}
      <div className="p-5 rounded-xl bg-amber-950/20 border border-amber-600/30 text-xs text-amber-200/90 space-y-2">
        <div className="font-bold text-amber-300 text-sm flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          Responsible Agronomic AI & Transparency Disclaimer
        </div>
        <p>
          Yield forecasts provide statistical guidance for agronomists, regional planners, and farmers. Predictions are empirical estimations
          derived from historical correlations and do not guarantee actual harvest totals. Field-level microclimates, unexpected pathogen
          infestations, acute hailstorms, and farm-specific management interventions can cause variations from model forecasts.
        </p>
      </div>
    </div>
  );
};
