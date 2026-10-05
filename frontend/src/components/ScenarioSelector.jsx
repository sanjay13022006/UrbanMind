import React from 'react';
import { Radio, Zap, CloudRain, Sun, Clock, Play, RotateCcw, ShieldCheck } from 'lucide-react';

export default function ScenarioSelector({
  isLive,
  currentScenario,
  onSelectScenario,
  onRunSimulation,
  onSwitchToLive,
  loading
}) {
  const scenarios = [
    { id: 'normal', label: 'Normal Demo', icon: Sun, desc: 'Baseline urban traffic flow & dry weather' },
    { id: 'rush_hour', label: 'Rush Hour Congestion', icon: Clock, desc: 'Heavy traffic volume, low speeds (10-18 km/h), elevated AQI' },
    { id: 'heavy_rain', label: 'Heavy Rain & Flash Flood', icon: CloudRain, desc: '60-85 mm/h downpour, rapid water level surge, critical flood risk' },
  ];

  return (
    <div style={{ marginBottom: '1.25rem' }}>
      {/* Prominent Demo Mode Banner if in DEMO MODE */}
      {!isLive && (
        <div
          style={{
            marginBottom: '0.75rem',
            padding: '0.75rem 1rem',
            backgroundColor: '#FEF3C7',
            border: '1px solid #FCD34D',
            borderRadius: '6px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '0.75rem'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#92400E' }}>
            <Zap style={{ width: '18px', height: '18px', color: '#D97706', flexShrink: 0 }} />
            <div>
              <strong style={{ fontSize: '0.85rem' }}>DEMO SCENARIO — DATA IS SIMULATED</strong>
              <div style={{ fontSize: '0.75rem', color: '#B45309' }}>
                Controlled evaluation scenario active: <strong>{currentScenario?.replace('_', ' ').toUpperCase()}</strong>. Real external APIs are paused.
              </div>
            </div>
          </div>

          <button
            onClick={onSwitchToLive}
            disabled={loading}
            style={{
              padding: '0.4rem 0.85rem',
              backgroundColor: '#16A34A',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '5px',
              fontWeight: 600,
              fontSize: '0.78rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              cursor: 'pointer',
              boxShadow: '0 1px 2px rgba(22,163,74,0.2)'
            }}
          >
            <ShieldCheck style={{ width: '14px', height: '14px' }} /> Return to LIVE API Mode
          </button>
        </div>
      )}

      {/* Mode & Scenario Control Bar */}
      <div className="card" style={{ padding: '0.875rem 1rem', backgroundColor: '#F8FAFC' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Radio style={{ width: '18px', height: '18px', color: isLive ? '#16A34A' : '#D97706' }} />
              <h3 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0F172A', margin: 0 }}>
                Digital Twin Operation Mode
              </h3>
              <span
                style={{
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  padding: '0.15rem 0.5rem',
                  borderRadius: '12px',
                  backgroundColor: isLive ? '#DCFCE7' : '#FEF3C7',
                  color: isLive ? '#15803D' : '#B45309',
                  border: `1px solid ${isLive ? '#86EFAC' : '#FDE68A'}`
                }}
              >
                {isLive ? 'LIVE DATA (OpenWeather + OpenAQ + TomTom)' : 'DEMO MODE (Simulated Scenarios)'}
              </span>
            </div>
            <p style={{ fontSize: '0.76rem', color: '#64748B', marginTop: '0.2rem', margin: 0 }}>
              Live Mode ingests genuine external APIs. Demo Scenarios allow testing extreme ML edge cases during panel presentation.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            {/* Live Mode Button */}
            <button
              onClick={onSwitchToLive}
              disabled={loading || isLive}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.35rem',
                padding: '0.4rem 0.8rem',
                borderRadius: '5px',
                border: isLive ? '1.5px solid #16A34A' : '1px solid #CBD5E1',
                backgroundColor: isLive ? '#F0FDF4' : '#FFFFFF',
                color: isLive ? '#15803D' : '#475569',
                fontWeight: isLive ? 700 : 500,
                fontSize: '0.8rem',
                cursor: isLive ? 'default' : 'pointer'
              }}
            >
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: isLive ? '#16A34A' : '#94A3B8' }} />
              Live Mode
            </button>

            {/* Scenario buttons */}
            <div style={{ display: 'flex', backgroundColor: '#E2E8F0', borderRadius: '6px', padding: '0.1875rem' }}>
              {scenarios.map((sc) => {
                const Icon = sc.icon;
                const isActive = !isLive && currentScenario === sc.id;
                return (
                  <button
                    key={sc.id}
                    onClick={() => onSelectScenario(sc.id)}
                    title={sc.desc}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.35rem',
                      padding: '0.35rem 0.65rem',
                      borderRadius: '4px',
                      border: 'none',
                      backgroundColor: isActive ? '#FFFFFF' : 'transparent',
                      color: isActive ? '#0F172A' : '#64748B',
                      fontWeight: isActive ? 700 : 500,
                      fontSize: '0.78rem',
                      boxShadow: isActive ? '0 1px 2px rgba(0,0,0,0.08)' : 'none',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    <Icon style={{ width: '13px', height: '13px', color: isActive ? '#D97706' : '#64748B' }} />
                    {sc.label}
                  </button>
                );
              })}
            </div>

            <button
              onClick={() => onRunSimulation(currentScenario)}
              disabled={loading}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '0.42rem 0.85rem',
                backgroundColor: '#2563EB',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '5px',
                fontSize: '0.8rem',
                fontWeight: 600,
                cursor: 'pointer',
                opacity: loading ? 0.7 : 1
              }}
            >
              <Play style={{ width: '13px', height: '13px', fill: '#FFFFFF' }} />
              Trigger Scenario
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
