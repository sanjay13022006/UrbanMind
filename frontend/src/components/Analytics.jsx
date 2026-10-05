import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { BarChart3 } from 'lucide-react';

export default function Analytics({ analyticsData }) {
  if (!analyticsData || analyticsData.length === 0) return null;

  return (
    <div className="card" style={{ marginTop: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <BarChart3 style={{ width: '20px', height: '20px', color: '#2563EB' }} />
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#0F172A' }}>
            Historical City Telemetry & Trend Analytics
          </h3>
        </div>
        <span style={{ fontSize: '0.78rem', color: '#64748B' }}>
          Real-time Time-Series (Last 20 ticks)
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
        {/* Chart 1: Traffic Trend */}
        <div style={{ backgroundColor: '#FFFFFF', padding: '1rem', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
          <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.75rem' }}>
            Traffic Trend (Vehicle Count / min)
          </h4>
          <div style={{ height: '180px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analyticsData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis dataKey="time_label" tick={{ fontSize: 10, fill: '#64748B' }} />
                <YAxis tick={{ fontSize: 10, fill: '#64748B' }} />
                <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '4px', border: '1px solid #E2E8F0' }} />
                <Line type="monotone" dataKey="avg_vehicles" name="Avg Vehicles" stroke="#2563EB" strokeWidth={2} dot={{ r: 2 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: AQI Trend */}
        <div style={{ backgroundColor: '#FFFFFF', padding: '1rem', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
          <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.75rem' }}>
            Air Quality Index Trend (AQI)
          </h4>
          <div style={{ height: '180px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analyticsData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis dataKey="time_label" tick={{ fontSize: 10, fill: '#64748B' }} />
                <YAxis tick={{ fontSize: 10, fill: '#64748B' }} />
                <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '4px', border: '1px solid #E2E8F0' }} />
                <Line type="monotone" dataKey="avg_aqi" name="Avg AQI" stroke="#D97706" strokeWidth={2} dot={{ r: 2 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: City Risk Score Trend */}
        <div style={{ backgroundColor: '#FFFFFF', padding: '1rem', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
          <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.75rem' }}>
            City Risk Score Trend (0 - 100)
          </h4>
          <div style={{ height: '180px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analyticsData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis dataKey="time_label" tick={{ fontSize: 10, fill: '#64748B' }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#64748B' }} />
                <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '4px', border: '1px solid #E2E8F0' }} />
                <Line type="monotone" dataKey="risk_score" name="Risk Score" stroke="#DC2626" strokeWidth={2} dot={{ r: 2 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
