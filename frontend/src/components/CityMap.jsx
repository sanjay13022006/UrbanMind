import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Gauge, Wind, Thermometer, CloudRain, Droplets, ShieldAlert } from 'lucide-react';

const createCustomIcon = (color, isSelected = false) => {
  const hexColor = color === 'green' ? '#16A34A' : color === 'yellow' ? '#D97706' : '#DC2626';
  const size = isSelected ? 30 : 22;
  const border = isSelected ? '4px solid #FFFFFF' : '2.5px solid #FFFFFF';
  const boxShadow = isSelected
    ? '0 0 0 5px rgba(37, 99, 235, 0.5), 0 4px 12px rgba(0,0,0,0.4)'
    : '0 2px 6px rgba(0,0,0,0.35)';
  return L.divIcon({
    className: 'custom-leaflet-marker',
    html: `<div style="
      width: ${size}px;
      height: ${size}px;
      border-radius: 50%;
      background-color: ${hexColor};
      border: ${border};
      box-shadow: ${boxShadow};
      transition: all 0.2s ease;
      cursor: pointer;
    "></div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2]
  });
};

function MapViewRecenter({ center, zoom = 13 }) {
  const map = useMap();
  useEffect(() => {
    if (center && center[0] && center[1]) {
      map.flyTo(center, zoom, { duration: 1.2 });
    }
  }, [center, zoom, map]);
  return null;
}

export default function CityMap({ locations, selectedLocation, onSelectLocation, onOpenDetailsModal }) {
  // Center of Coimbatore
  const defaultCenter = [11.0168, 76.9558];
  const activeCenter = selectedLocation ? [selectedLocation.lat, selectedLocation.lng] : defaultCenter;
  const activeZoom = selectedLocation ? 14 : 13;

  return (
    <div className="card" style={{ padding: '1rem', height: '520px', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div>
          <h3 style={{ fontSize: '0.98rem', fontWeight: 700, color: '#0F172A', margin: 0 }}>
            Interactive Coimbatore Digital Twin Map ({locations ? locations.length : 0} Nodes)
          </h3>
          <p style={{ fontSize: '0.76rem', color: '#64748B', margin: '0.15rem 0 0 0' }}>
            {selectedLocation ? `Active Focus: ${selectedLocation.location_name} (${selectedLocation.zone_type})` : 'Click any zone marker to focus and inspect full multi-modal telemetry.'}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', fontSize: '0.72rem' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#16A34A' }} /> Normal
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#D97706' }} /> Moderate
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#DC2626' }} /> Critical
          </span>
        </div>
      </div>

      <div style={{ flex: 1, borderRadius: '6px', overflow: 'hidden', border: '1px solid #E2E8F0', zIndex: 1 }}>
        <MapContainer
          center={defaultCenter}
          zoom={13}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={false}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <MapViewRecenter center={activeCenter} zoom={activeZoom} />

          {locations && locations.map((loc) => {
            const isSelected = selectedLocation && selectedLocation.location_id === loc.location_id;
            const icon = createCustomIcon(loc.status_color || 'green', isSelected);
            return (
              <Marker
                key={loc.location_id}
                position={[loc.lat, loc.lng]}
                icon={icon}
                eventHandlers={{
                  click: () => onSelectLocation(loc)
                }}
              >
                <Popup>
                  <div style={{ minWidth: '240px', fontSize: '0.8rem', padding: '0.25rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.35rem' }}>
                      <div>
                        <h4 style={{ margin: 0, color: '#0F172A', fontSize: '0.95rem', fontWeight: 800 }}>
                          {loc.location_name}
                        </h4>
                        <div style={{ color: '#64748B', fontSize: '0.72rem', marginTop: '0.1rem' }}>
                          {loc.zone_type}
                        </div>
                      </div>
                      <span className={`badge badge-${loc.status_color}`}>{loc.risk_label}</span>
                    </div>

                    {isSelected && (
                      <div style={{ backgroundColor: '#EFF6FF', color: '#2563EB', fontSize: '0.7rem', fontWeight: 700, padding: '0.2rem 0.4rem', borderRadius: '4px', marginBottom: '0.5rem', textAlign: 'center' }}>
                        ✓ SELECTED AS ACTIVE MAIN LOCATION
                      </div>
                    )}

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.35rem 0.6rem', marginBottom: '0.5rem', backgroundColor: '#F8FAFC', padding: '0.5rem', borderRadius: '4px', border: '1px solid #E2E8F0' }}>
                      <div>Speed: <strong>{loc.current_speed} km/h</strong></div>
                      <div>Free Flow: <strong>{loc.free_flow_speed} km/h</strong></div>
                      <div>Delay: <strong>{loc.delay_seconds != null ? `${loc.delay_seconds}s` : (loc.traffic_status === 'error' || loc.traffic_status === 'unavailable' ? 'Unavailable' : '--')}</strong></div>
                      <div>Congestion: <strong>{loc.congestion_percentage}%</strong></div>
                      <div>Traffic: <strong>{loc.traffic_level}</strong></div>
                      <div>AQI: <strong>{loc.aqi} ({loc.aqi_category})</strong></div>
                      <div>Temp: <strong>{loc.temperature}°C</strong></div>
                      <div>Water Level: <strong>{loc.water_level} m</strong></div>
                    </div>

                    <div style={{ fontSize: '0.68rem', color: '#64748B', display: 'flex', flexDirection: 'column', gap: '0.15rem', borderTop: '1px solid #E2E8F0', paddingTop: '0.35rem', marginBottom: '0.5rem' }}>
                      <div>Traffic API: <strong style={{ color: '#0F172A' }}>{loc.traffic_source || 'TomTom Flow API'}</strong></div>
                      <div>Weather API: <strong style={{ color: '#0F172A' }}>{loc.weather_source || 'OpenWeather API'}</strong></div>
                      <div>Air Quality: <strong style={{ color: '#0F172A' }}>{loc.aqi_source || 'OpenAQ CAAQMS'}</strong></div>
                      <div>Hydrology: <strong style={{ color: '#2563EB' }}>{loc.water_level_source || 'Basin Simulation'}</strong></div>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                      <button
                        onClick={() => {
                          onSelectLocation(loc);
                          if (onOpenDetailsModal) onOpenDetailsModal(loc);
                        }}
                        style={{
                          width: '100%',
                          padding: '0.45rem',
                          backgroundColor: '#2563EB',
                          color: '#FFFFFF',
                          border: 'none',
                          borderRadius: '4px',
                          fontSize: '0.76rem',
                          fontWeight: 700,
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '0.3rem'
                        }}
                      >
                        Open Full Telemetry & AI Predictions Modal →
                      </button>
                      <button
                        onClick={() => onSelectLocation(loc)}
                        style={{
                          width: '100%',
                          padding: '0.3rem',
                          backgroundColor: '#F1F5F9',
                          color: '#334155',
                          border: '1px solid #CBD5E1',
                          borderRadius: '4px',
                          fontSize: '0.72rem',
                          fontWeight: 600,
                          cursor: 'pointer'
                        }}
                      >
                        Set as Active Main Location
                      </button>
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>

      {/* Docked Selected Location Real-Time Telemetry Inspector Bar */}
      {selectedLocation && (
        <div
          style={{
            marginTop: '0.75rem',
            padding: '0.75rem 1rem',
            backgroundColor: '#F8FAFC',
            border: '2px solid #3B82F6',
            borderRadius: '6px',
            boxShadow: '0 2px 8px rgba(37, 99, 235, 0.1)',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: '#2563EB',
                  boxShadow: '0 0 0 3px rgba(37, 99, 235, 0.25)'
                }}
              />
              <strong style={{ fontSize: '0.9rem', color: '#0F172A' }}>
                {selectedLocation.location_name}
              </strong>
              <span style={{ fontSize: '0.72rem', color: '#64748B' }}>
                ({selectedLocation.zone_type})
              </span>
              <span className={`badge badge-${selectedLocation.status_color || 'green'}`}>
                {selectedLocation.risk_label} ({selectedLocation.risk_score || 0}/100)
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <button
                onClick={() => onOpenDetailsModal && onOpenDetailsModal(selectedLocation)}
                style={{
                  padding: '0.35rem 0.75rem',
                  backgroundColor: '#2563EB',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.35rem'
                }}
              >
                Inspect Full Telemetry & AI Modal →
              </button>
              <button
                onClick={() => onSelectLocation(null)}
                title="Reset to City Overview"
                style={{
                  padding: '0.35rem 0.55rem',
                  backgroundColor: '#FFFFFF',
                  color: '#64748B',
                  border: '1px solid #CBD5E1',
                  borderRadius: '4px',
                  fontSize: '0.72rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                ✕ Deselect
              </button>
            </div>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
              gap: '0.4rem',
              fontSize: '0.75rem'
            }}
          >
            <div style={{ backgroundColor: '#FFFFFF', padding: '0.35rem 0.5rem', borderRadius: '4px', border: '1px solid #E2E8F0' }}>
              <span style={{ color: '#64748B', fontSize: '0.68rem', display: 'block' }}>Speed & Delay</span>
              <strong style={{ color: '#0F172A' }}>{selectedLocation.current_speed} km/h</strong>
              <span style={{ color: '#64748B', fontSize: '0.68rem' }}> • Delay: <strong>{selectedLocation.delay_seconds != null ? `${selectedLocation.delay_seconds}s` : (selectedLocation.traffic_status === 'error' || selectedLocation.traffic_status === 'unavailable' ? 'Unavailable' : '--')}</strong></span>
            </div>

            <div style={{ backgroundColor: '#FFFFFF', padding: '0.35rem 0.5rem', borderRadius: '4px', border: '1px solid #E2E8F0' }}>
              <span style={{ color: '#64748B', fontSize: '0.68rem', display: 'block' }}>Congestion</span>
              <strong style={{ color: selectedLocation.congestion_percentage > 40 ? '#DC2626' : '#0F172A' }}>
                {selectedLocation.congestion_percentage}%
              </strong>
              <span style={{ color: '#64748B', fontSize: '0.68rem' }}> ({selectedLocation.traffic_level})</span>
            </div>

            <div style={{ backgroundColor: '#FFFFFF', padding: '0.35rem 0.5rem', borderRadius: '4px', border: '1px solid #E2E8F0' }}>
              <span style={{ color: '#64748B', fontSize: '0.68rem', display: 'block' }}>AI Traffic (30m)</span>
              <strong style={{ color: '#2563EB' }}>{selectedLocation.traffic_pred || 'Moderate'}</strong>
              <span style={{ color: '#64748B', fontSize: '0.68rem' }}> ({selectedLocation.traffic_confidence || 85}%)</span>
            </div>

            <div style={{ backgroundColor: '#FFFFFF', padding: '0.35rem 0.5rem', borderRadius: '4px', border: '1px solid #E2E8F0' }}>
              <span style={{ color: '#64748B', fontSize: '0.68rem', display: 'block' }}>Air Quality (OpenAQ)</span>
              <strong style={{ color: '#0F172A' }}>AQI {selectedLocation.aqi}</strong>
              <span style={{ color: '#64748B', fontSize: '0.68rem' }}> ({selectedLocation.aqi_category})</span>
            </div>

            <div style={{ backgroundColor: '#FFFFFF', padding: '0.35rem 0.5rem', borderRadius: '4px', border: '1px solid #E2E8F0' }}>
              <span style={{ color: '#64748B', fontSize: '0.68rem', display: 'block' }}>Weather (OpenWeather)</span>
              <strong style={{ color: '#0F172A' }}>{selectedLocation.temperature}°C</strong>
              <span style={{ color: '#64748B', fontSize: '0.68rem' }}>, {selectedLocation.rainfall} mm/h</span>
            </div>

            <div style={{ backgroundColor: '#FFFFFF', padding: '0.35rem 0.5rem', borderRadius: '4px', border: '1px solid #E2E8F0' }}>
              <span style={{ color: '#64748B', fontSize: '0.68rem', display: 'block' }}>AI Flood Risk</span>
              <strong style={{ color: selectedLocation.flood_pred === 'High' ? '#DC2626' : '#16A34A' }}>
                {selectedLocation.flood_pred || 'Low'}
              </strong>
              <span style={{ color: '#64748B', fontSize: '0.68rem' }}> (Water: {selectedLocation.water_level}m)</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
