import React from 'react';
import { Layers, ArrowRight, ShieldCheck, Info } from 'lucide-react';

export default function FutureScope() {
  const steps = [
    { title: 'Authorized River Gauges', desc: 'Real hydrological radar/ultrasonic sensor API integration' },
    { title: 'Computer Vision CCTV', desc: 'Live optical vehicle detection and anomaly tracking' },
    { title: '3D Twin Mesh', desc: 'Three.js / Cesium city-scale 3D digital twin rendering' },
    { title: 'Satellite Earth Observation', desc: 'Copernicus & Sentinel multispectral flood mapping' },
    { title: 'Autonomous Signal Timing', desc: 'Adaptive AI traffic light green corridor routing' },
    { title: 'Cloud Microservices', desc: 'Kubernetes cluster deployment on AWS/GCP' }
  ];

  return (
    <div className="card" style={{ marginTop: '1.25rem' }}>
      {/* Honest Technical Claim Banner (Requirement 32) */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.625rem',
          padding: '0.75rem 1rem',
          backgroundColor: '#EFF6FF',
          border: '1px solid #BFDBFE',
          borderRadius: '6px',
          marginBottom: '1rem'
        }}
      >
        <Info style={{ width: '18px', height: '18px', color: '#2563EB', flexShrink: 0 }} />
        <span style={{ fontSize: '0.8rem', color: '#1E40AF', fontWeight: 500 }}>
          <strong>Architecture Notice:</strong> UrbanTwin AI integrates real external weather (OpenWeather), air-quality (OpenAQ), and traffic data (TomTom), while water-level data is currently simulated for the MVP.
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
        <Layers style={{ width: '18px', height: '18px', color: '#2563EB' }} />
        <h3 style={{ fontSize: '0.98rem', fontWeight: 700, color: '#0F172A', margin: 0 }}>
          Future Development & Architecture Roadmap
        </h3>
      </div>
      <p style={{ fontSize: '0.78rem', color: '#64748B', marginBottom: '1rem', margin: 0 }}>
        Next-phase extension vectors planned beyond the initial college project MVP prototype.
      </p>

      <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.75rem' }}>
        {steps.map((step, idx) => (
          <React.Fragment key={idx}>
            <div
              style={{
                backgroundColor: '#FFFFFF',
                border: '1px solid #CBD5E1',
                padding: '0.625rem 0.875rem',
                borderRadius: '6px',
                fontSize: '0.78rem',
                boxShadow: '0 1px 2px rgba(0,0,0,0.03)'
              }}
            >
              <div style={{ fontWeight: 600, color: '#0F172A' }}>{idx + 1}. {step.title}</div>
              <div style={{ color: '#64748B', fontSize: '0.72rem', marginTop: '0.125rem' }}>{step.desc}</div>
            </div>
            {idx < steps.length - 1 && (
              <ArrowRight style={{ width: '14px', height: '14px', color: '#94A3B8', flexShrink: 0 }} />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
