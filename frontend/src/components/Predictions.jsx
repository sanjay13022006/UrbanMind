import React, { useState } from 'react';
import { Cpu, TrendingUp, AlertTriangle, Activity, Search } from 'lucide-react';

export default function Predictions({ predictions, selectedLocation, onSelectLocation }) {
  const [filterQuery, setFilterQuery] = useState('');

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

  const filtered = predictions.filter((p) =>
    p.location_name?.toLowerCase().includes(filterQuery.toLowerCase())
  );

  // If a location is selected, move it to the top so the user sees it immediately
  const sorted = [...filtered].sort((a, b) => {
    if (selectedLocation) {
      if (a.location_id === selectedLocation.location_id) return -1;
      if (b.location_id === selectedLocation.location_id) return 1;
    }
    return 0;
  });

  return (
    <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Cpu style={{ width: '18px', height: '18px', color: '#2563EB' }} />
          <h3 style={{ fontSize: '0.98rem', fontWeight: 700, color: '#0F172A', margin: 0 }}>
            AI Random Forest Predictions ({predictions.length} Zones)
          </h3>
        </div>
        <span style={{ fontSize: '0.72rem', color: '#475569', backgroundColor: '#F1F5F9', padding: '0.2rem 0.5rem', borderRadius: '4px', fontWeight: 500 }}>
          Scikit-Learn ML Model
        </span>
      </div>

      {/* Filter search */}
      <div style={{ position: 'relative', marginBottom: '0.75rem' }}>
        <Search style={{ position: 'absolute', left: '8px', top: '50%', transform: 'translateY(-50%)', width: '13px', height: '13px', color: '#94A3B8' }} />
        <input
          type="text"
          placeholder="Search predictions..."
          value={filterQuery}
          onChange={(e) => setFilterQuery(e.target.value)}
          style={{
            width: '100%',
            padding: '0.35rem 0.6rem 0.35rem 1.8rem',
            borderRadius: '4px',
            border: '1px solid #E2E8F0',
            fontSize: '0.76rem',
            backgroundColor: '#F8FAFC',
            outline: 'none'
          }}
        />
      </div>

      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '420px', paddingRight: '0.25rem' }}>
        {sorted.map((p) => {
          const isSelected = selectedLocation && selectedLocation.location_id === p.location_id;
          const trafficProb = p.traffic_probability || p.traffic_confidence || 85.0;
          const floodProb = p.flood_probability || p.flood_confidence || 85.0;

          return (
            <div
              key={p.location_id}
              onClick={() => onSelectLocation && onSelectLocation(p)}
              style={{
                padding: '0.75rem',
                backgroundColor: isSelected ? '#EFF6FF' : '#FFFFFF',
                border: isSelected ? '2px solid #2563EB' : '1px solid #E2E8F0',
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                boxShadow: isSelected ? '0 2px 8px rgba(37,99,235,0.15)' : 'none'
              }}
              onMouseEnter={(e) => {
                if (!isSelected) e.currentTarget.style.borderColor = '#94A3B8';
              }}
              onMouseLeave={(e) => {
                if (!isSelected) e.currentTarget.style.borderColor = '#E2E8F0';
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <strong style={{ fontSize: '0.85rem', color: '#0F172A' }}>{p.location_name}</strong>
                  {isSelected && (
                    <span style={{ fontSize: '0.65rem', backgroundColor: '#2563EB', color: '#FFFFFF', padding: '0.1rem 0.35rem', borderRadius: '3px', fontWeight: 700 }}>
                      MAP FOCUS
                    </span>
                  )}
                </div>
                <span style={{ fontSize: '0.72rem', color: '#64748B' }}>
                  Horizon: <strong>{p.prediction_horizon || '30 minutes'}</strong>
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.76rem' }}>
                {/* Traffic Prediction */}
                <div style={{ backgroundColor: '#F8FAFC', padding: '0.5rem', borderRadius: '4px', border: '1px solid #F1F5F9' }}>
                  <div style={{ color: '#64748B', marginBottom: '0.25rem', fontSize: '0.72rem' }}>30m Traffic Prediction</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', flexWrap: 'wrap' }}>
                    <span style={{ color: '#64748B' }}>Now:</span>
                    <span className={`badge ${getBadgeClass(p.current_traffic)}`}>{p.current_traffic}</span>
                    <span style={{ color: '#64748B' }}>→</span>
                    <span className={`badge ${getBadgeClass(p.predicted_traffic)}`}>{p.predicted_traffic}</span>
                  </div>
                  <div style={{ fontSize: '0.7rem', color: '#475569', marginTop: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <TrendingUp style={{ width: '12px', height: '12px', color: '#2563EB' }} />
                    Prediction Probability: <strong>{trafficProb}%</strong>
                  </div>
                </div>

                {/* Flood Risk Prediction */}
                <div style={{ backgroundColor: '#F8FAFC', padding: '0.5rem', borderRadius: '4px', border: '1px solid #F1F5F9' }}>
                  <div style={{ color: '#64748B', marginBottom: '0.25rem', fontSize: '0.72rem' }}>30m Flood Prediction</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', flexWrap: 'wrap' }}>
                    <span style={{ color: '#64748B' }}>Now:</span>
                    <span className={`badge ${getBadgeClass(p.current_flood_risk)}`}>{p.current_flood_risk}</span>
                    <span style={{ color: '#64748B' }}>→</span>
                    <span className={`badge ${getBadgeClass(p.predicted_flood_risk)}`}>{p.predicted_flood_risk}</span>
                  </div>
                  <div style={{ fontSize: '0.7rem', color: '#475569', marginTop: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <TrendingUp style={{ width: '12px', height: '12px', color: '#2563EB' }} />
                    Prediction Probability: <strong>{floodProb}%</strong>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
