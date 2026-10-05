import React from 'react';
import { Layers, ArrowRight } from 'lucide-react';

export default function FutureScope() {
  const steps = [
    { title: 'Real IoT Sensor Integration', desc: 'Hardware microcontrollers & MQTT gateways' },
    { title: 'Real-Time CCTV Analysis', desc: 'Computer vision vehicle detection & optical flow' },
    { title: '3D Digital Twin', desc: 'Three.js / Cesium city-scale 3D mesh visualization' },
    { title: 'Satellite Data Integration', desc: 'Copernicus & Landsat multispectral flood mapping' },
    { title: 'Autonomous Traffic Management', desc: 'Adaptive AI traffic light signal control' },
    { title: 'Smart Emergency Response', desc: 'Automated green corridor routing for ambulances' },
    { title: 'City-Scale Cloud Deployment', desc: 'Kubernetes microservices on AWS/GCP' }
  ];

  return (
    <div className="card" style={{ marginTop: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
        <Layers style={{ width: '18px', height: '18px', color: '#2563EB' }} />
        <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#0F172A' }}>
          Future Development & Architecture Roadmap
        </h3>
      </div>
      <p style={{ fontSize: '0.8rem', color: '#64748B', marginBottom: '1rem' }}>
        Next-phase extension vectors planned beyond the initial college project MVP prototype.
      </p>

      <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
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
