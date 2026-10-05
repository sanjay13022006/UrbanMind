import React from 'react';
import { X, MapPin, Car, Wind, Thermometer, CloudRain, Droplets, Cpu, ShieldAlert, Navigation } from 'lucide-react';

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

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(15, 23, 42, 0.4)',
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
          maxWidth: '560px',
          backgroundColor: '#FFFFFF',
          maxHeight: '90vh',
          overflowY: 'auto',
          boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem', borderBottom: '1px solid #E2E8F0', paddingBottom: '0.75rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <MapPin style={{ width: '20px', height: '20px', color: '#2563EB' }} />
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0F172A' }}>
                {location.location_name || location.name}
              </h2>
            </div>
            <p style={{ fontSize: '0.8rem', color: '#64748B', marginTop: '0.2rem' }}>
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
              color: '#64748B'
            }}
          >
            <X style={{ width: '20px', height: '20px' }} />
          </button>
        </div>

        {/* Current Risk Header Banner */}
        <div
          style={{
            display: 'flex',
            justify: 'space-between',
            alignItems: 'center',
            backgroundColor: '#F8FAFC',
            border: '1px solid #E2E8F0',
            padding: '0.75rem 1rem',
            borderRadius: '6px',
            marginBottom: '1rem'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldAlert style={{ width: '18px', height: '18px', color: '#2563EB' }} />
            <span style={{ fontSize: '0.875rem', fontWeight: 500, color: '#334155' }}>Composite Risk Level</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0F172A' }}>{location.risk_score} / 100</span>
            <span className={`badge ${getBadgeClass(location.risk_label)}`}>{location.risk_label}</span>
          </div>
        </div>

        {/* Live Telemetry Metrics */}
        <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#0F172A', marginBottom: '0.625rem' }}>
          Live Sensor Telemetry
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1.25rem' }}>
          <div style={{ backgroundColor: '#F8FAFC', padding: '0.75rem', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontSize: '0.75rem', color: '#64748B', marginBottom: '0.25rem' }}>
              <Car style={{ width: '14px', height: '14px' }} /> Vehicle Count
            </div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0F172A' }}>
              {location.vehicle_count} <span style={{ fontSize: '0.75rem', fontWeight: 400, color: '#64748B' }}>veh/min</span>
            </div>
          </div>

          <div style={{ backgroundColor: '#F8FAFC', padding: '0.75rem', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontSize: '0.75rem', color: '#64748B', marginBottom: '0.25rem' }}>
              <Navigation style={{ width: '14px', height: '14px' }} /> Average Speed
            </div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0F172A' }}>
              {location.traffic_speed} <span style={{ fontSize: '0.75rem', fontWeight: 400, color: '#64748B' }}>km/h</span>
            </div>
          </div>

          <div style={{ backgroundColor: '#F8FAFC', padding: '0.75rem', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontSize: '0.75rem', color: '#64748B', marginBottom: '0.25rem' }}>
              <Wind style={{ width: '14px', height: '14px' }} /> Air Quality (AQI)
            </div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0F172A' }}>
              {location.aqi} <span style={{ fontSize: '0.75rem', fontWeight: 400, color: '#64748B' }}>({location.aqi_category})</span>
            </div>
          </div>

          <div style={{ backgroundColor: '#F8FAFC', padding: '0.75rem', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontSize: '0.75rem', color: '#64748B', marginBottom: '0.25rem' }}>
              <Thermometer style={{ width: '14px', height: '14px' }} /> Temperature
            </div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0F172A' }}>
              {location.temperature} °C
            </div>
          </div>

          <div style={{ backgroundColor: '#F8FAFC', padding: '0.75rem', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontSize: '0.75rem', color: '#64748B', marginBottom: '0.25rem' }}>
              <CloudRain style={{ width: '14px', height: '14px' }} /> Rainfall
            </div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0F172A' }}>
              {location.rainfall} mm
            </div>
          </div>

          <div style={{ backgroundColor: '#F8FAFC', padding: '0.75rem', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontSize: '0.75rem', color: '#64748B', marginBottom: '0.25rem' }}>
              <Droplets style={{ width: '14px', height: '14px' }} /> Water Level
            </div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0F172A' }}>
              {location.water_level} m
            </div>
          </div>
        </div>

        {/* AI Predictions */}
        <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#0F172A', marginBottom: '0.625rem', display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
          <Cpu style={{ width: '16px', height: '16px', color: '#2563EB' }} /> Random Forest ML Predictions
        </h4>
        <div style={{ backgroundColor: '#F8FAFC', border: '1px solid #E2E8F0', padding: '0.875rem', borderRadius: '6px', fontSize: '0.8125rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span>Traffic Prediction (30m Horizon):</span>
            <span className={`badge ${getBadgeClass(location.traffic_pred)}`}>
              {location.traffic_pred} ({location.traffic_confidence}% confidence)
            </span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Flood Risk Prediction (30m Horizon):</span>
            <span className={`badge ${getBadgeClass(location.flood_pred)}`}>
              {location.flood_pred} ({location.flood_confidence}% confidence)
            </span>
          </div>
        </div>

        <button
          onClick={onClose}
          style={{
            width: '100%',
            marginTop: '1.25rem',
            padding: '0.625rem',
            backgroundColor: '#0F172A',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '6px',
            fontWeight: 600,
            fontSize: '0.875rem'
          }}
        >
          Close Inspector
        </button>
      </div>
    </div>
  );
}
