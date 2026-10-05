import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';

// Create custom colored div icons for status pins
const createCustomIcon = (color) => {
  const hexColor = color === 'green' ? '#16A34A' : color === 'yellow' ? '#D97706' : '#DC2626';
  return L.divIcon({
    className: 'custom-leaflet-marker',
    html: `<div style="
      width: 22px;
      height: 22px;
      border-radius: 50%;
      background-color: ${hexColor};
      border: 3px solid #FFFFFF;
      box-shadow: 0 2px 5px rgba(0,0,0,0.25);
    "></div>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11],
    popupAnchor: [0, -12]
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
  const centerLat = 12.9650;
  const centerLng = 77.5950;

  return (
    <div className="card" style={{ padding: '1rem', height: '480px', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <div>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#0F172A' }}>
            Interactive City Digital Twin Map
          </h3>
          <p style={{ fontSize: '0.78rem', color: '#64748B' }}>
            Real-time IoT zone status & spatial markers. Click any marker for telemetry & predictions.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', fontSize: '0.75rem' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#16A34A' }}></span> Normal
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#D97706' }}></span> Warning
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#DC2626' }}></span> Critical
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
                  <div style={{ minWidth: '180px', fontSize: '0.8125rem' }}>
                    <h4 style={{ margin: '0 0 0.375rem 0', color: '#0F172A', fontSize: '0.9rem', fontWeight: 700 }}>
                      {loc.location_name}
                    </h4>
                    <p style={{ margin: '0 0 0.5rem 0', color: '#64748B', fontSize: '0.75rem' }}>
                      {loc.zone_type}
                    </p>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.25rem 0.5rem', marginBottom: '0.5rem' }}>
                      <div>Traffic: <strong>{loc.traffic_level}</strong></div>
                      <div>Vehicles: <strong>{loc.vehicle_count}/m</strong></div>
                      <div>AQI: <strong>{loc.aqi}</strong></div>
                      <div>Temp: <strong>{loc.temperature}°C</strong></div>
                      <div>Rain: <strong>{loc.rainfall}mm</strong></div>
                      <div>Water: <strong>{loc.water_level}m</strong></div>
                    </div>
                    <div style={{ marginTop: '0.375rem', paddingTop: '0.375rem', borderTop: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Risk Level:</span>
                      <span className={`badge badge-${loc.status_color}`}>{loc.risk_label} ({loc.risk_score})</span>
                    </div>
                    <button
                      onClick={() => onSelectLocation(loc)}
                      style={{
                        marginTop: '0.5rem',
                        width: '100%',
                        padding: '0.3rem',
                        backgroundColor: '#2563EB',
                        color: '#FFFFFF',
                        border: 'none',
                        borderRadius: '4px',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        cursor: 'pointer'
                      }}
                    >
                      View Full Details & AI
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
