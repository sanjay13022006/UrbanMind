import React from 'react';
import { RefreshCw, Activity, CheckCircle, AlertCircle } from 'lucide-react';

export default function Header({ statusData, onRefresh, loading, isError }) {
  const isOnline = !isError && statusData?.system_status === 'Online';

  return (
    <header className="card" style={{ marginBottom: '1.25rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
            <Activity style={{ width: '24px', height: '24px', color: '#2563EB' }} />
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0F172A', letterSpacing: '-0.02em' }}>
              Urban Mind
            </h1>
          </div>
          <p style={{ fontSize: '0.875rem', color: '#64748B', marginTop: '0.125rem' }}>
            AI-Powered Smart City Digital Twin
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}>
            <span style={{ color: '#64748B' }}>System Status:</span>
            {isOnline ? (
              <span className="badge badge-green">
                <CheckCircle style={{ width: '12px', height: '12px' }} />
                Online
              </span>
            ) : (
              <span className="badge badge-red">
                <AlertCircle style={{ width: '12px', height: '12px' }} />
                Offline
              </span>
            )}
          </div>

          {statusData?.last_updated && (
            <div style={{ fontSize: '0.875rem', color: '#64748B' }}>
              Last Updated: <strong style={{ color: '#0F172A' }}>{statusData.last_updated}</strong>
            </div>
          )}

          <button
            onClick={onRefresh}
            disabled={loading}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem 0.875rem',
              backgroundColor: '#FFFFFF',
              border: '1px solid #CBD5E1',
              borderRadius: '6px',
              fontSize: '0.875rem',
              fontWeight: 500,
              color: '#334155',
              boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
              opacity: loading ? 0.7 : 1
            }}
          >
            <RefreshCw style={{ width: '14px', height: '14px', animation: loading ? 'spin 1s linear infinite' : 'none' }} />
            Refresh
          </button>
        </div>
      </div>
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </header>
  );
}
