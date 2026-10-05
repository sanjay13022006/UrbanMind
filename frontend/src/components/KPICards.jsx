import React from 'react';
import { Car, Wind, Droplets, AlertTriangle, ShieldAlert } from 'lucide-react';

export default function KPICards({ statusData }) {
  if (!statusData) return null;

  const getStatusBadge = (level) => {
    switch (level) {
      case 'Low':
      case 'Good':
      case 'Normal':
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

  const cards = [
    {
      title: 'Traffic Status',
      value: statusData.traffic_status || 'Normal',
      sub: statusData.avg_traffic || '-- vehicles/min',
      icon: Car,
      badge: getStatusBadge(statusData.traffic_status)
    },
    {
      title: 'Average Traffic',
      value: `${statusData.avg_traffic_val || 0} veh/min`,
      sub: 'City-wide average volume',
      icon: Car,
      badge: 'badge-blue'
    },
    {
      title: 'Air Quality',
      value: statusData.aqi_display || 'AQI --',
      sub: statusData.aqi_category || 'Moderate',
      icon: Wind,
      badge: getStatusBadge(statusData.aqi_category)
    },
    {
      title: 'Flood Risk',
      value: statusData.flood_risk || 'Low',
      sub: 'Hydrological & rain metric',
      icon: Droplets,
      badge: getStatusBadge(statusData.flood_risk)
    },
    {
      title: 'Active Alerts',
      value: `${statusData.active_alerts_count || 0}`,
      sub: statusData.active_alerts_count > 0 ? 'Action required' : 'System nominal',
      icon: AlertTriangle,
      badge: statusData.active_alerts_count > 0 ? 'badge-red' : 'badge-green'
    },
    {
      title: 'Overall City Risk',
      value: `${statusData.overall_risk_score || 0} / 100`,
      sub: statusData.overall_risk_label || 'Low',
      icon: ShieldAlert,
      badge: getStatusBadge(statusData.overall_risk_label)
    }
  ];

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1rem',
        marginBottom: '1.25rem'
      }}
    >
      {cards.map((c, idx) => {
        const Icon = c.icon;
        return (
          <div key={idx} className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.8rem', color: '#64748B', fontWeight: 500 }}>{c.title}</span>
              <Icon style={{ width: '16px', height: '16px', color: '#94A3B8' }} />
            </div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
              <span style={{ fontSize: '1.35rem', fontWeight: 700, color: '#0F172A' }}>{c.value}</span>
            </div>
            <div style={{ marginTop: '0.375rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.75rem', color: '#64748B' }}>{c.sub}</span>
              <span className={`badge ${c.badge}`}>{c.value.includes('/ 100') ? statusData.overall_risk_label : (statusData[c.title.toLowerCase().replace(/ /g, '_')] || c.sub)}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
