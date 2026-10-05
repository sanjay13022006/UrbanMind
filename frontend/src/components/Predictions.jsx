import React from 'react';
import { Cpu, TrendingUp, AlertTriangle } from 'lucide-react';

export default function Predictions({ predictions, onSelectLocation }) {
  if (!predictions || predictions.length === 0) return null;

  const getBadgeClass = (val) => {
    switch (val) {
      case 'Low': return 'badge-green';
      case 'Moderate': return 'badge-yellow';
      case 'High':
      case 'Critical': return 'badge-red';
      default: return 'badge-blue';
    }
  };

  return (
    <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.875rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Cpu style={{ width: '18px', height: '18px', color: '#2563EB' }} />
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#0F172A' }}>
            AI Model Predictions
          </h3>
        </div>
        <span style={{ fontSize: '0.75rem', color: '#64748B', backgroundColor: '#F1F5F9', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
          Random Forest ML Engine
        </span>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '420px', paddingRight: '0.25rem' }}>
        {predictions.map((p) => (
          <div
            key={p.location_id}
            onClick={() => onSelectLocation && onSelectLocation(p)}
            style={{
              padding: '0.875rem',
              backgroundColor: '#FFFFFF',
              border: '1px solid #E2E8F0',
              borderRadius: '6px',
              cursor: 'pointer',
              transition: 'border-color 0.15s ease'
            }}
            onMouseEnter={(e) => e.currentTarget.style.borderColor = '#94A3B8'}
            onMouseLeave={(e) => e.currentTarget.style.borderColor = '#E2E8F0'}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <strong style={{ fontSize: '0.875rem', color: '#0F172A' }}>{p.location_name}</strong>
              <span style={{ fontSize: '0.75rem', color: '#64748B' }}>
                Horizon: <strong>{p.prediction_horizon}</strong>
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.78rem' }}>
              {/* Traffic Prediction */}
              <div style={{ backgroundColor: '#F8FAFC', padding: '0.5rem', borderRadius: '4px', border: '1px solid #F1F5F9' }}>
                <div style={{ color: '#64748B', marginBottom: '0.25rem' }}>Traffic Prediction</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', flexWrap: 'wrap' }}>
                  <span style={{ color: '#64748B' }}>Current:</span> 
                  <span className={`badge ${getBadgeClass(p.current_traffic)}`}>{p.current_traffic}</span>
                  <span style={{ color: '#64748B' }}>→</span>
                  <span className={`badge ${getBadgeClass(p.predicted_traffic)}`}>{p.predicted_traffic}</span>
                </div>
                <div style={{ fontSize: '0.72rem', color: '#475569', marginTop: '0.375rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <TrendingUp style={{ width: '12px', height: '12px', color: '#2563EB' }} />
                  Model Confidence: <strong>{p.traffic_confidence}%</strong>
                </div>
              </div>

              {/* Flood Prediction */}
              <div style={{ backgroundColor: '#F8FAFC', padding: '0.5rem', borderRadius: '4px', border: '1px solid #F1F5F9' }}>
                <div style={{ color: '#64748B', marginBottom: '0.25rem' }}>Flood Risk Prediction</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', flexWrap: 'wrap' }}>
                  <span style={{ color: '#64748B' }}>Current:</span>
                  <span className={`badge ${getBadgeClass(p.current_flood_risk)}`}>{p.current_flood_risk}</span>
                  <span style={{ color: '#64748B' }}>→</span>
                  <span className={`badge ${getBadgeClass(p.predicted_flood_risk)}`}>{p.predicted_flood_risk}</span>
                </div>
                <div style={{ fontSize: '0.72rem', color: '#475569', marginTop: '0.375rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <TrendingUp style={{ width: '12px', height: '12px', color: '#2563EB' }} />
                  Model Confidence: <strong>{p.flood_confidence}%</strong>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
