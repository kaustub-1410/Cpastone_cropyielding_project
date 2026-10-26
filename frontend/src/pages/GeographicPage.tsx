import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import {
  MapPin,
  Filter,
  Layers,
  Sprout,
  AlertTriangle,
  Info,
  ChevronRight,
} from 'lucide-react';
import { api } from '../services/api';

// Create custom colored circle markers with Leaflet DivIcon
const createCustomIcon = (yieldVal: number, hasAlert: boolean) => {
  const bgColor = hasAlert
    ? '#f43f5e'
    : yieldVal >= 4.0
    ? '#10b981'
    : yieldVal >= 2.5
    ? '#3b82f6'
    : '#f59e0b';

  return L.divIcon({
    className: 'custom-map-marker',
    html: `<div style="
      background-color: ${bgColor};
      width: 22px;
      height: 22px;
      border-radius: 50%;
      border: 2px solid #ffffff;
      box-shadow: 0 0 10px ${bgColor};
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 10px;
      font-weight: bold;
    "></div>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11],
  });
};

export const GeographicPage: React.FC = () => {
  const [points, setPoints] = useState<any[]>([]);
  const [selectedCrop, setSelectedCrop] = useState('all');
  const [selectedRegion, setSelectedRegion] = useState('all');
  const [selectedPoint, setSelectedPoint] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPoints = async () => {
      setLoading(true);
      try {
        const hist = await api.getPredictionHistory({ limit: 100 });
        const validPoints = (hist.items || []).filter(
          (p: any) => p.latitude && p.longitude
        );

        // If history is small, fetch preview rows from default dataset
        if (validPoints.length < 5) {
          const summary = await api.getDatasetSummary();
          if (summary && summary.dataset_id) {
            const prev = await api.getDatasetPreview(summary.dataset_id, 80);
            const datasetPoints = (prev.records || [])
              .filter((r: any) => r.latitude && r.longitude)
              .map((r: any) => ({
                field_id: r.field_id,
                crop: r.crop,
                region: r.region,
                latitude: r.latitude,
                longitude: r.longitude,
                predicted_yield_t_ha: r.actual_yield_t_ha,
                alerts: r.actual_yield_t_ha < 2.0 ? [{ rule_name: 'Low Harvest Potential' }] : [],
                rainfall_mm: r.rainfall_mm,
                temperature_max_c: r.temperature_max_c,
              }));
            setPoints(datasetPoints);
            if (datasetPoints.length > 0) setSelectedPoint(datasetPoints[0]);
          }
        } else {
          setPoints(validPoints);
          if (validPoints.length > 0) setSelectedPoint(validPoints[0]);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchPoints();
  }, []);

  const filteredPoints = points.filter((p) => {
    if (selectedCrop !== 'all' && p.crop !== selectedCrop) return false;
    if (selectedRegion !== 'all' && p.region !== selectedRegion) return false;
    return true;
  });

  const crops = Array.from(new Set(points.map((p) => p.crop)));
  const regions = Array.from(new Set(points.map((p) => p.region)));

  // Center of India agricultural belt
  const mapCenter: [number, number] = [23.5, 78.5];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white flex items-center gap-3">
            Geographic Agricultural Intelligence
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Spatial distribution of predicted yields, regional hotspots, and agronomic alert markers on OpenStreetMap.
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <Filter className="w-3.5 h-3.5" />
            <span>Filter:</span>
          </div>

          <select
            value={selectedCrop}
            onChange={(e) => setSelectedCrop(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-emerald-500"
          >
            <option value="all">All Crops</option>
            {crops.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>

          <select
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-emerald-500"
          >
            <option value="all">All Regions</option>
            {regions.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Map Container */}
        <div className="lg:col-span-8 glass-card p-4 rounded-xl border border-slate-800 flex flex-col">
          <div className="flex items-center justify-between mb-3 px-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-white">Spatial Yield Map</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400">
                {filteredPoints.length} Plots Displayed
              </span>
            </div>

            {/* Map Legend */}
            <div className="flex items-center gap-4 text-[11px] text-slate-400">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> High Yield (&gt;4 t/ha)
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-500" /> Normal (2.5-4 t/ha)
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> Low (&lt;2.5 t/ha)
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500" /> Alert Triggered
              </span>
            </div>
          </div>

          <div className="h-[480px] w-full rounded-lg overflow-hidden border border-slate-800 relative z-0">
            <MapContainer
              center={mapCenter}
              zoom={5}
              scrollWheelZoom={true}
              style={{ height: '100%', width: '100%', backgroundColor: '#090d16' }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {filteredPoints.map((pt, i) => {
                const hasAlert = (pt.alerts && pt.alerts.length > 0) || pt.predicted_yield_t_ha < 2.0;
                return (
                  <Marker
                    key={i}
                    position={[pt.latitude, pt.longitude]}
                    icon={createCustomIcon(pt.predicted_yield_t_ha, hasAlert)}
                    eventHandlers={{
                      click: () => setSelectedPoint(pt),
                    }}
                  >
                    <Popup className="custom-leaflet-popup">
                      <div className="p-1 text-slate-900">
                        <div className="font-bold text-xs">{pt.field_id} ({pt.crop})</div>
                        <div className="text-[11px] text-slate-700">{pt.region}</div>
                        <div className="text-xs font-semibold text-emerald-700 mt-1">
                          Yield: {pt.predicted_yield_t_ha} t/ha
                        </div>
                      </div>
                    </Popup>
                  </Marker>
                );
              })}
            </MapContainer>
          </div>
        </div>

        {/* Selected Field Details Drawer */}
        <div className="lg:col-span-4 space-y-4">
          {selectedPoint ? (
            <div className="glass-card p-5 rounded-xl border border-slate-800 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <div className="text-xs uppercase tracking-wider text-slate-400 font-medium">Selected Field Plot</div>
                <div className="text-xl font-bold text-white mt-1 flex items-center justify-between">
                  <span>{selectedPoint.field_id}</span>
                  <span className="text-xs px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-normal">
                    {selectedPoint.crop}
                  </span>
                </div>
                <div className="text-xs text-slate-400 mt-0.5">{selectedPoint.region}</div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                  <div className="text-[11px] text-slate-400">Predicted Yield</div>
                  <div className="text-xl font-extrabold text-emerald-400 mt-1">
                    {selectedPoint.predicted_yield_t_ha} <span className="text-xs font-normal text-slate-400">t/ha</span>
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                  <div className="text-[11px] text-slate-400">Alert Status</div>
                  <div className="text-sm font-bold text-white mt-2">
                    {selectedPoint.alerts && selectedPoint.alerts.length > 0 ? (
                      <span className="text-rose-400 flex items-center gap-1 text-xs">
                        <AlertTriangle className="w-3.5 h-3.5" /> Flagged
                      </span>
                    ) : (
                      <span className="text-emerald-400 flex items-center gap-1 text-xs">
                        Normal
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/80">
                  <span className="text-slate-400">Coordinates:</span>
                  <span className="text-slate-200 font-mono">
                    {selectedPoint.latitude}°, {selectedPoint.longitude}°
                  </span>
                </div>
                {selectedPoint.rainfall_mm !== undefined && (
                  <div className="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/80">
                    <span className="text-slate-400">Rainfall:</span>
                    <span className="text-slate-200 font-mono">{selectedPoint.rainfall_mm} mm</span>
                  </div>
                )}
                {selectedPoint.temperature_max_c !== undefined && (
                  <div className="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/80">
                    <span className="text-slate-400">Peak Temperature:</span>
                    <span className="text-slate-200 font-mono">{selectedPoint.temperature_max_c} °C</span>
                  </div>
                )}
              </div>

              <div className="text-[11px] text-slate-500 pt-2 border-t border-slate-800">
                Plot markers link real-time predictive models with geographic coordinates for district-level agricultural decision making.
              </div>
            </div>
          ) : (
            <div className="glass-card p-8 rounded-xl border border-slate-800 text-center flex flex-col items-center justify-center min-h-[300px] text-slate-400 text-xs">
              <MapPin className="w-8 h-8 text-slate-500 mb-2" />
              Click any plot marker on the map to inspect its field-level predictive details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
