import React from 'react';
import { AlertOctagon, AlertTriangle, Info, CheckCircle2 } from 'lucide-react';

export default function Alerts({ alerts }) {
  const getIcon = (severity) => {
    switch (severity) {
      case 'Critical':
        return <AlertOctagon style={{ width: '18px', height: '18px', color: '#DC2626', flexShrink: 0 }} />;
      case 'Warning':
        return <AlertTriangle style={{ width: '18px', height: '18px', color: '#D97706', flexShrink: 0 }} />;
      default:
        return <Info style={{ width: '18px', height: '18px', color: '#2563EB', flexShrink: 0 }} />;
    }
  };

  const getBadgeClass = (severity) => {
    switch (severity) {
      case 'Critical': return 'badge-red';
      case 'Warning': return 'badge-yellow';
      default: return 'badge-blue';
    }
  };

  return (
    <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.875rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertOctagon style={{ width: '18px', height: '18px', color: alerts && alerts.length > 0 ? '#DC2626' : '#16A34A' }} />
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#0F172A' }}>
            Active System Alerts
          </h3>
        </div>
        <span className={`badge ${alerts && alerts.length > 0 ? 'badge-red' : 'badge-green'}`}>
          {alerts ? alerts.length : 0} Active
        </span>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.625rem', maxHeight: '420px', paddingRight: '0.25rem' }}>
        {!alerts || alerts.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem 1rem', color: '#64748B', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
            <CheckCircle2 style={{ width: '32px', height: '32px', color: '#16A34A' }} />
            <p style={{ fontSize: '0.875rem', fontWeight: 500, color: '#0F172A' }}>No Active Threshold Alerts</p>
            <p style={{ fontSize: '0.78rem' }}>All city sensors and AI risk indicators are operating within normal nominal ranges.</p>
          </div>
        ) : (
          alerts.map((a, idx) => (
            <div
              key={idx}
              style={{
                padding: '0.75rem',
                backgroundColor: a.severity === 'Critical' ? '#FEF2F2' : a.severity === 'Warning' ? '#FEFCE8' : '#EFF6FF',
                border: `1px solid ${a.severity === 'Critical' ? '#FECACA' : a.severity === 'Warning' ? '#FEF08A' : '#BFDBFE'}`,
                borderRadius: '6px',
                display: 'flex',
                gap: '0.625rem',
                alignItems: 'flex-start'
              }}
            >
              {getIcon(a.severity)}
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                  <span className={`badge ${getBadgeClass(a.severity)}`}>{a.severity}</span>
                  <span style={{ fontSize: '0.72rem', color: '#64748B' }}>{a.timestamp}</span>
                </div>
                <p style={{ fontSize: '0.8125rem', color: '#0F172A', fontWeight: 500, margin: '0.25rem 0' }}>
                  {a.message}
                </p>
                <div style={{ fontSize: '0.72rem', color: '#64748B' }}>
                  Location: <strong>{a.location_name || a.location_id}</strong>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
