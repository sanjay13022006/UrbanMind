import React from 'react';
import { Gauge, Wind, Droplets, AlertTriangle, ShieldAlert, CloudRain, Car } from 'lucide-react';

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
      title: 'Traffic Condition',
      value: statusData.traffic_status || 'Normal',
      sub: `Avg Speed: ${statusData.avg_speed_display || '-- km/h'}`,
      sourceTag: 'TomTom Traffic API',
      icon: Car,
      badge: getStatusBadge(statusData.traffic_status)
    },
    {
      title: 'Current Traffic Speed',
      value: statusData.avg_speed_display || '-- km/h',
      sub: `Congestion: ${statusData.avg_congestion_display || '0%'}`,
      sourceTag: 'TomTom Traffic Flow',
      icon: Gauge,
      badge: 'badge-blue'
    },
    {
      title: 'Air Quality (AQI)',
      value: statusData.aqi_display || 'AQI --',
      sub: statusData.aqi_category || 'Moderate',
      sourceTag: 'OpenAQ CPCB Station',
      icon: Wind,
      badge: getStatusBadge(statusData.aqi_category)
    },
    {
      title: 'Rainfall / Weather',
      value: statusData.rainfall_display || '0.0 mm/h',
      sub: `${statusData.weather_condition || 'Clear'} (${statusData.temperature_display || '--'})`,
      sourceTag: 'OpenWeather API',
      icon: CloudRain,
      badge: statusData.rainfall_val > 0 ? 'badge-blue' : 'badge-green'
    },
    {
      title: 'Flood Risk Horizon',
      value: statusData.flood_risk || 'Low',
      sub: '30-min ML Forecast',
      sourceTag: 'Random Forest Model',
      icon: Droplets,
      badge: getStatusBadge(statusData.flood_risk)
    },
    {
      title: 'Active Alerts',
      value: `${statusData.active_alerts_count || 0}`,
      sub: statusData.active_alerts_count > 0 ? 'Threshold breached' : 'Sensors nominal',
      sourceTag: 'Threshold Alert Engine',
      icon: AlertTriangle,
      badge: statusData.active_alerts_count > 0 ? 'badge-red' : 'badge-green'
    },
    {
      title: 'Composite City Risk',
      value: `${statusData.overall_risk_score || 0} / 100`,
      sub: statusData.overall_risk_label || 'Low',
      sourceTag: 'Multi-Modal Risk Engine',
      icon: ShieldAlert,
      badge: getStatusBadge(statusData.overall_risk_label)
    }
  ];

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
        gap: '0.875rem',
        marginBottom: '1.25rem'
      }}
    >
      {cards.map((c, idx) => {
        const Icon = c.icon;
        return (
          <div key={idx} className="card" style={{ padding: '0.875rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.375rem' }}>
                <span style={{ fontSize: '0.78rem', color: '#64748B', fontWeight: 600 }}>{c.title}</span>
                <Icon style={{ width: '16px', height: '16px', color: '#94A3B8' }} />
              </div>
              <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#0F172A', marginBottom: '0.25rem' }}>
                {c.value}
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                <span style={{ fontSize: '0.72rem', color: '#475569', fontWeight: 500 }}>{c.sub}</span>
                <span className={`badge ${c.badge}`}>{c.value.includes('/ 100') ? statusData.overall_risk_label : (statusData[c.title.toLowerCase().replace(/ /g, '_')] || c.sub)}</span>
              </div>
              <div style={{ fontSize: '0.66rem', color: '#94A3B8', borderTop: '1px dashed #E2E8F0', paddingTop: '0.25rem' }}>
                Source: <strong>{c.sourceTag}</strong>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
