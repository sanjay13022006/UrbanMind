import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';
import { BarChart3 } from 'lucide-react';

export default function Analytics({ analyticsData }) {
  if (!analyticsData || analyticsData.length === 0) return null;

  return (
    <div className="card" style={{ marginTop: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <BarChart3 style={{ width: '20px', height: '20px', color: '#2563EB' }} />
          <h3 style={{ fontSize: '1.02rem', fontWeight: 700, color: '#0F172A', margin: 0 }}>
            Historical City Telemetry & Trend Analytics
          </h3>
        </div>
        <span style={{ fontSize: '0.76rem', color: '#64748B' }}>
          Real Time-Series Observations (SQLite Timestamped Logs)
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
        {/* Chart 1: Traffic Speed & Congestion Trend */}
        <div style={{ backgroundColor: '#FFFFFF', padding: '1rem', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155', margin: 0 }}>
              Traffic Speed (km/h) & Congestion (%)
            </h4>
            <span style={{ fontSize: '0.68rem', color: '#64748B' }}>TomTom Flow API</span>
          </div>
          <div style={{ height: '190px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analyticsData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis dataKey="time_label" tick={{ fontSize: 10, fill: '#64748B' }} />
                <YAxis tick={{ fontSize: 10, fill: '#64748B' }} />
                <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '4px', border: '1px solid #E2E8F0' }} />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Line type="monotone" dataKey="avg_speed" name="Speed (km/h)" stroke="#2563EB" strokeWidth={2} dot={{ r: 2 }} />
                <Line type="monotone" dataKey="avg_congestion" name="Congestion (%)" stroke="#D97706" strokeWidth={2} dot={{ r: 2 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: AQI Trend */}
        <div style={{ backgroundColor: '#FFFFFF', padding: '1rem', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155', margin: 0 }}>
              Air Quality Index (AQI) Trend
            </h4>
            <span style={{ fontSize: '0.68rem', color: '#64748B' }}>OpenAQ CPCB Station</span>
          </div>
          <div style={{ height: '190px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analyticsData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis dataKey="time_label" tick={{ fontSize: 10, fill: '#64748B' }} />
                <YAxis domain={[0, 'auto']} tick={{ fontSize: 10, fill: '#64748B' }} />
                <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '4px', border: '1px solid #E2E8F0' }} />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Line type="monotone" dataKey="avg_aqi" name="CPCB AQI" stroke="#10B981" strokeWidth={2} dot={{ r: 2 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: City Risk Score & Rainfall */}
        <div style={{ backgroundColor: '#FFFFFF', padding: '1rem', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155', margin: 0 }}>
              Composite Risk Score (0-100) & Rainfall
            </h4>
            <span style={{ fontSize: '0.68rem', color: '#64748B' }}>Risk Engine + OpenWeather</span>
          </div>
          <div style={{ height: '190px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analyticsData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis dataKey="time_label" tick={{ fontSize: 10, fill: '#64748B' }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#64748B' }} />
                <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '4px', border: '1px solid #E2E8F0' }} />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Line type="monotone" dataKey="risk_score" name="City Risk (0-100)" stroke="#DC2626" strokeWidth={2} dot={{ r: 2 }} />
                <Line type="monotone" dataKey="avg_rainfall" name="Rainfall (mm/h)" stroke="#06B6D4" strokeWidth={1.5} dot={{ r: 2 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
