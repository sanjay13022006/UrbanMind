import React from 'react';
import { RefreshCw, Activity, CheckCircle, AlertCircle, Radio, MapPin } from 'lucide-react';

export default function Header({ statusData, onRefresh, loading, isError }) {
  const isOnline = !isError && statusData?.system_status === 'Online';
  const isLive = statusData?.is_live ?? true;

  return (
    <header className="card" style={{ marginBottom: '1.25rem', padding: '1rem 1.25rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
            <Activity style={{ width: '24px', height: '24px', color: '#2563EB' }} />
            <h1 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#0F172A', letterSpacing: '-0.02em', margin: 0 }}>
              UrbanMind
            </h1>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.3rem',
                fontSize: '0.72rem',
                fontWeight: 600,
                color: '#475569',
                backgroundColor: '#F1F5F9',
                padding: '0.2rem 0.5rem',
                borderRadius: '4px',
                border: '1px solid #E2E8F0'
              }}
            >
              <MapPin style={{ width: '12px', height: '12px', color: '#2563EB' }} />
              {statusData?.city_name || 'Coimbatore'}, India
            </span>
          </div>
          <p style={{ fontSize: '0.82rem', color: '#64748B', marginTop: '0.2rem', margin: 0 }}>
            Smart City Digital Twin — Integrated with OpenWeather, OpenAQ & TomTom APIs
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          {/* Mode Pill */}
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.35rem 0.75rem',
              borderRadius: '20px',
              backgroundColor: isLive ? '#DCFCE7' : '#FEF3C7',
              border: `1px solid ${isLive ? '#86EFAC' : '#FDE68A'}`,
              fontSize: '0.76rem',
              fontWeight: 700,
              color: isLive ? '#15803D' : '#B45309'
            }}
          >
            <span
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: isLive ? '#16A34A' : '#D97706',
                display: 'inline-block',
                animation: isLive ? 'pulse 2s infinite' : 'none'
              }}
            />
            {isLive ? 'LIVE DATA' : `DEMO: ${statusData?.demo_scenario?.toUpperCase() || 'SIMULATED'}`}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.82rem' }}>
            <span style={{ color: '#64748B' }}>Backend:</span>
            {isOnline ? (
              <span className="badge badge-green" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                <CheckCircle style={{ width: '11px', height: '11px' }} />
                Online
              </span>
            ) : (
              <span className="badge badge-red" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                <AlertCircle style={{ width: '11px', height: '11px' }} />
                Offline
              </span>
            )}
          </div>

          {statusData?.last_updated && (
            <div style={{ fontSize: '0.82rem', color: '#64748B' }}>
              Last Synced: <strong style={{ color: '#0F172A' }}>{statusData.last_updated}</strong>
            </div>
          )}

          <button
            onClick={onRefresh}
            disabled={loading}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.45rem 0.85rem',
              backgroundColor: '#FFFFFF',
              border: '1px solid #CBD5E1',
              borderRadius: '6px',
              fontSize: '0.82rem',
              fontWeight: 600,
              color: '#334155',
              cursor: 'pointer',
              boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
              opacity: loading ? 0.7 : 1
            }}
          >
            <RefreshCw style={{ width: '13px', height: '13px', animation: loading ? 'spin 1s linear infinite' : 'none' }} />
            Refresh
          </button>
        </div>
      </div>
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0% { transform: scale(0.95); opacity: 0.8; }
          50% { transform: scale(1.2); opacity: 1; }
          100% { transform: scale(0.95); opacity: 0.8; }
        }
      `}</style>
    </header>
  );
}
