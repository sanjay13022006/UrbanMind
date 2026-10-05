import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Gauge, Wind, Thermometer, CloudRain, Droplets, ShieldAlert } from 'lucide-react';

const createCustomIcon = (color) => {
  const hexColor = color === 'green' ? '#16A34A' : color === 'yellow' ? '#D97706' : '#DC2626';
  return L.divIcon({
    className: 'custom-leaflet-marker',
    html: `<div style="
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background-color: ${hexColor};
      border: 3px solid #FFFFFF;
      box-shadow: 0 2px 6px rgba(0,0,0,0.35);
    "></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -14]
  });
};

function MapViewRecenter({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, 13);
    }
  }, [center, map]);
  return null;
}

export default function CityMap({ locations, selectedLocation, onSelectLocation }) {
  // Center of Coimbatore
  const centerLat = 11.0168;
  const centerLng = 76.9558;

  return (
    <div className="card" style={{ padding: '1rem', height: '520px', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div>
          <h3 style={{ fontSize: '0.98rem', fontWeight: 700, color: '#0F172A', margin: 0 }}>
            Interactive Coimbatore Digital Twin Map
          </h3>
          <p style={{ fontSize: '0.76rem', color: '#64748B', margin: '0.15rem 0 0 0' }}>
            Real-time IoT zone status & spatial markers. Click any marker for telemetry & predictions.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', fontSize: '0.72rem' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#16A34A' }} /> Normal
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#D97706' }} /> Moderate / Warning
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#DC2626' }} /> Critical
          </span>
        </div>
      </div>

      <div style={{ flex: 1, borderRadius: '6px', overflow: 'hidden', border: '1px solid #E2E8F0', zIndex: 1 }}>
        <MapContainer
          center={[centerLat, centerLng]}
          zoom={13}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={false}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <MapViewRecenter center={[centerLat, centerLng]} />

          {locations && locations.map((loc) => {
            const icon = createCustomIcon(loc.status_color || 'green');
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
                  <div style={{ minWidth: '220px', fontSize: '0.8rem', padding: '0.2rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.25rem' }}>
                      <h4 style={{ margin: 0, color: '#0F172A', fontSize: '0.92rem', fontWeight: 700 }}>
                        {loc.location_name}
                      </h4>
                      <span className={`badge badge-${loc.status_color}`}>{loc.risk_label}</span>
                    </div>
                    <div style={{ color: '#64748B', fontSize: '0.72rem', marginBottom: '0.5rem' }}>
                      {loc.zone_type}
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.35rem 0.6rem', marginBottom: '0.5rem', backgroundColor: '#F8FAFC', padding: '0.5rem', borderRadius: '4px', border: '1px solid #E2E8F0' }}>
                      <div>Traffic: <strong>{loc.traffic_level}</strong></div>
                      <div>Speed: <strong>{loc.current_speed} km/h</strong></div>
                      <div>Free Flow: <strong>{loc.free_flow_speed} km/h</strong></div>
                      <div>Congestion: <strong>{loc.congestion_percentage}%</strong></div>
                      <div>AQI: <strong>{loc.aqi} ({loc.aqi_category})</strong></div>
                      <div>Temp: <strong>{loc.temperature}°C</strong></div>
                      <div>Rain: <strong>{loc.rainfall} mm/h</strong></div>
                      <div>Water: <strong>{loc.water_level} m</strong></div>
                    </div>

                    <div style={{ fontSize: '0.68rem', color: '#64748B', display: 'flex', flexDirection: 'column', gap: '0.15rem', borderTop: '1px solid #E2E8F0', paddingTop: '0.35rem', marginBottom: '0.5rem' }}>
                      <div>Traffic Source: <strong style={{ color: '#0F172A' }}>{loc.traffic_source || 'TomTom'}</strong></div>
                      <div>Weather Source: <strong style={{ color: '#0F172A' }}>{loc.weather_source || 'OpenWeather'}</strong></div>
                      <div>Air Quality Source: <strong style={{ color: '#0F172A' }}>{loc.aqi_source || 'OpenAQ'}</strong></div>
                      <div>Water Level: <strong style={{ color: '#2563EB' }}>{loc.water_level_source || 'Simulated'}</strong></div>
                    </div>

                    <button
                      onClick={() => onSelectLocation(loc)}
                      style={{
                        width: '100%',
                        padding: '0.35rem',
                        backgroundColor: '#2563EB',
                        color: '#FFFFFF',
                        border: 'none',
                        borderRadius: '4px',
                        fontSize: '0.74rem',
                        fontWeight: 600,
                        cursor: 'pointer'
                      }}
                    >
                      View AI Inferences & Telemetry
                    </button>
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>
    </div>
  );
}
