import React from 'react';
import { X, MapPin, Gauge, Wind, Thermometer, CloudRain, Droplets, Cpu, ShieldAlert, Navigation, Layers, Info } from 'lucide-react';

export default function LocationDetails({ location, onClose }) {
  if (!location) return null;

  const getBadgeClass = (val) => {
    switch (val) {
      case 'Low':
      case 'Good':
        return 'badge-green';
      case 'Moderate':
        return 'badge-yellow';
      case 'High':
      case 'Critical':
      case 'Unhealthy':
        return 'badge-red';
      default:
        return 'badge-blue';
    }
  };

  const trafficProb = location.traffic_probability || location.traffic_confidence || 85.0;
  const floodProb = location.flood_probability || location.flood_confidence || 85.0;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(15, 23, 42, 0.45)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 9999,
        padding: '1rem'
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{
          width: '100%',
          maxWidth: '580px',
          backgroundColor: '#FFFFFF',
          maxHeight: '92vh',
          overflowY: 'auto',
          boxShadow: '0 10px 30px -5px rgba(0,0,0,0.15)',
          padding: '1.25rem'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem', borderBottom: '1px solid #E2E8F0', paddingBottom: '0.75rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <MapPin style={{ width: '20px', height: '20px', color: '#2563EB' }} />
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#0F172A', margin: 0 }}>
                {location.location_name || location.name}
              </h2>
            </div>
            <p style={{ fontSize: '0.78rem', color: '#64748B', marginTop: '0.2rem', margin: 0 }}>
              {location.zone_type} — {location.description}
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              border: 'none',
              background: 'none',
              padding: '0.25rem',
              borderRadius: '4px',
              color: '#64748B',
              cursor: 'pointer'
            }}
          >
            <X style={{ width: '20px', height: '20px' }} />
          </button>
        </div>

        {/* Current Risk Banner */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            backgroundColor: '#F8FAFC',
            border: '1px solid #E2E8F0',
            padding: '0.75rem 1rem',
            borderRadius: '6px',
            marginBottom: '1.25rem'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldAlert style={{ width: '18px', height: '18px', color: '#2563EB' }} />
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>Composite Zone Risk</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0F172A' }}>{location.risk_score} / 100</span>
            <span className={`badge ${getBadgeClass(location.risk_label)}`}>{location.risk_label}</span>
          </div>
        </div>

        {/* Real API Telemetry Grid */}
        <h4 style={{ fontSize: '0.82rem', fontWeight: 700, color: '#0F172A', marginBottom: '0.625rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          Real-Time Sensor Telemetry
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1.25rem' }}>
          {/* Speed */}
          <div style={{ backgroundColor: '#F8FAFC', padding: '0.75rem', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.74rem', color: '#64748B', marginBottom: '0.2rem' }}>
              <Navigation style={{ width: '14px', height: '14px', color: '#2563EB' }} /> Current Speed
            </div>
            <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0F172A' }}>
              {location.current_speed || location.traffic_speed} <span style={{ fontSize: '0.75rem', fontWeight: 400, color: '#64748B' }}>km/h</span>
            </div>
            <div style={{ fontSize: '0.68rem', color: '#64748B', marginTop: '0.2rem' }}>
              Free Flow: {location.free_flow_speed || 45} km/h (TomTom)
            </div>
          </div>

          {/* Congestion */}
          <div style={{ backgroundColor: '#F8FAFC', padding: '0.75rem', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.74rem', color: '#64748B', marginBottom: '0.2rem' }}>
              <Gauge style={{ width: '14px', height: '14px', color: '#D97706' }} /> Congestion Level
            </div>
            <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0F172A' }}>
              {location.congestion_percentage || 0}% <span style={{ fontSize: '0.75rem', fontWeight: 400, color: '#64748B' }}>({location.traffic_level})</span>
            </div>
            <div style={{ fontSize: '0.68rem', color: '#64748B', marginTop: '0.2rem' }}>
              Delay: {location.delay_seconds || 0}s (TomTom)
            </div>
          </div>

          {/* Air Quality */}
          <div style={{ backgroundColor: '#F8FAFC', padding: '0.75rem', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.74rem', color: '#64748B', marginBottom: '0.2rem' }}>
              <Wind style={{ width: '14px', height: '14px', color: '#10B981' }} /> Air Quality (AQI)
            </div>
            <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0F172A' }}>
              {location.aqi} <span style={{ fontSize: '0.75rem', fontWeight: 400, color: '#64748B' }}>({location.aqi_category})</span>
            </div>
            <div style={{ fontSize: '0.68rem', color: '#64748B', marginTop: '0.2rem' }}>
              PM2.5: {location.pm25 || '--'} µg/m³ (OpenAQ CPCB)
            </div>
          </div>

          {/* Weather & Temp */}
          <div style={{ backgroundColor: '#F8FAFC', padding: '0.75rem', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.74rem', color: '#64748B', marginBottom: '0.2rem' }}>
              <Thermometer style={{ width: '14px', height: '14px', color: '#EF4444' }} /> Weather & Temp
            </div>
            <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0F172A' }}>
              {location.temperature}°C <span style={{ fontSize: '0.75rem', fontWeight: 400, color: '#64748B' }}>({location.weather_condition})</span>
            </div>
            <div style={{ fontSize: '0.68rem', color: '#64748B', marginTop: '0.2rem' }}>
              Humidity: {location.humidity || 60}% (OpenWeather)
            </div>
          </div>

          {/* Rainfall */}
          <div style={{ backgroundColor: '#F8FAFC', padding: '0.75rem', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.74rem', color: '#64748B', marginBottom: '0.2rem' }}>
              <CloudRain style={{ width: '14px', height: '14px', color: '#3B82F6' }} /> Precipitation
            </div>
            <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0F172A' }}>
              {location.rainfall} <span style={{ fontSize: '0.75rem', fontWeight: 400, color: '#64748B' }}>mm/h</span>
            </div>
            <div style={{ fontSize: '0.68rem', color: '#64748B', marginTop: '0.2rem' }}>
              Source: OpenWeather Rain Telemetry
            </div>
          </div>

          {/* Water Level */}
          <div style={{ backgroundColor: '#F8FAFC', padding: '0.75rem', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.74rem', color: '#64748B', marginBottom: '0.2rem' }}>
              <Droplets style={{ width: '14px', height: '14px', color: '#06B6D4' }} /> Water Level
            </div>
            <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0F172A' }}>
              {location.water_level} <span style={{ fontSize: '0.75rem', fontWeight: 400, color: '#64748B' }}>m</span>
            </div>
            <div style={{ fontSize: '0.68rem', color: '#2563EB', fontWeight: 500, marginTop: '0.2rem' }}>
              *Hydrological Simulation (Rain-driven)
            </div>
          </div>
        </div>

        {/* AI Predictions */}
        <h4 style={{ fontSize: '0.82rem', fontWeight: 700, color: '#0F172A', marginBottom: '0.625rem', display: 'flex', alignItems: 'center', gap: '0.35rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          <Cpu style={{ width: '16px', height: '16px', color: '#2563EB' }} /> Random Forest Predictions (30m Horizon)
        </h4>
        <div style={{ backgroundColor: '#F8FAFC', border: '1px solid #E2E8F0', padding: '0.875rem', borderRadius: '6px', fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.625rem', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>Traffic Congestion Forecast:</span>
            <span className={`badge ${getBadgeClass(location.traffic_pred)}`}>
              {location.traffic_pred} (Prediction Probability: {trafficProb}%)
            </span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>Flood Risk Forecast:</span>
            <span className={`badge ${getBadgeClass(location.flood_pred)}`}>
              {location.flood_pred} (Prediction Probability: {floodProb}%)
            </span>
          </div>
        </div>

        <button
          onClick={onClose}
          style={{
            width: '100%',
            padding: '0.625rem',
            backgroundColor: '#0F172A',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '6px',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer'
          }}
        >
          Close Inspector
        </button>
      </div>
    </div>
  );
}
