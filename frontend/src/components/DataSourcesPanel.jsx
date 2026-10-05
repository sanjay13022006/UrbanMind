import React from 'react';
import { Database, CheckCircle2, AlertTriangle, Radio, CloudRain } from 'lucide-react';

export default function DataSourcesPanel({ sources, isLive, onRefreshSources }) {
  if (!sources || sources.length === 0) return null;

  const getStatusBadge = (status) => {
    switch (status?.toLowerCase()) {
      case 'connected':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', color: '#16A34A', fontWeight: 600, fontSize: '0.78rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#16A34A', display: 'inline-block' }} />
            Connected
          </span>
        );
      case 'simulated':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', color: '#2563EB', fontWeight: 600, fontSize: '0.78rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#2563EB', display: 'inline-block' }} />
            Simulated
          </span>
        );
      case 'stale':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', color: '#D97706', fontWeight: 600, fontSize: '0.78rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#D97706', display: 'inline-block' }} />
            Stale / Preserved
          </span>
        );
      default:
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', color: '#DC2626', fontWeight: 600, fontSize: '0.78rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#DC2626', display: 'inline-block' }} />
            Unavailable
          </span>
        );
    }
  };

  return (
    <div className="card" style={{ marginBottom: '1.25rem', padding: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Database style={{ width: '18px', height: '18px', color: '#2563EB' }} />
          <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0F172A', margin: 0 }}>
            Live Telemetry Ingestion Sources
          </h3>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.75rem', color: '#64748B' }}>
          <span>Mode: <strong style={{ color: isLive ? '#16A34A' : '#D97706' }}>{isLive ? 'LIVE (Real External APIs)' : 'DEMO SCENARIO'}</strong></span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.75rem' }}>
        {sources.map((src, idx) => (
          <div
            key={idx}
            style={{
              padding: '0.75rem',
              backgroundColor: '#F8FAFC',
              borderRadius: '6px',
              border: '1px solid #E2E8F0',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.375rem' }}>
              <span style={{ fontWeight: 600, fontSize: '0.85rem', color: '#0F172A' }}>{src.name}</span>
              {getStatusBadge(src.status)}
            </div>
            <div style={{ fontSize: '0.72rem', color: '#64748B', display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
              <div>Coverage: <span style={{ color: '#334155', fontWeight: 500 }}>{src.coverage || 'City-wide'}</span></div>
              <div>Last Sync: <span style={{ color: '#334155', fontWeight: 500 }}>{src.last_update || 'Active'}</span></div>
              {src.note && (
                <div style={{ fontStyle: 'italic', color: '#64748B', fontSize: '0.68rem', marginTop: '0.25rem' }}>
                  *{src.note}
                </div>
              )}
              {src.warning && (
                <div style={{ color: '#B45309', fontSize: '0.7rem', marginTop: '0.2rem' }}>
                  {src.warning}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
