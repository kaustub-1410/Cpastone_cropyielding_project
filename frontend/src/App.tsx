import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { OverviewPage } from './pages/OverviewPage';
import { PredictionPage } from './pages/PredictionPage';
import { DatasetsPage } from './pages/DatasetsPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { GeographicPage } from './pages/GeographicPage';
import { AlertsPage } from './pages/AlertsPage';
import { HistoryPage } from './pages/HistoryPage';
import { AboutPage } from './pages/AboutPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<OverviewPage />} />
          <Route path="predict" element={<PredictionPage />} />
          <Route path="datasets" element={<DatasetsPage />} />
          <Route path="evaluation" element={<EvaluationPage />} />
          <Route path="geographic" element={<GeographicPage />} />
          <Route path="alerts" element={<AlertsPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="about" element={<AboutPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
