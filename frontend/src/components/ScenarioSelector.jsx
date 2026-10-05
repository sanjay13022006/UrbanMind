import React from 'react';
import { Play, Zap, CloudRain, Sun, Clock } from 'lucide-react';

export default function ScenarioSelector({ currentScenario, onSelectScenario, onRunSimulation, loading }) {
  const scenarios = [
    { id: 'normal', label: 'Normal', icon: Sun, desc: 'Baseline flow, low traffic & clear weather' },
    { id: 'rush_hour', label: 'Rush Hour', icon: Clock, desc: 'High vehicle count & low speeds' },
    { id: 'heavy_rain', label: 'Heavy Rain', icon: CloudRain, desc: 'High rainfall & flood warning' },
  ];

  return (
    <div className="card" style={{ marginBottom: '1.25rem', backgroundColor: '#F8FAFC' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Zap style={{ width: '18px', height: '18px', color: '#D97706' }} />
            <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#0F172A' }}>
              Simulation Scenario Selector
            </h3>
          </div>
          <p style={{ fontSize: '0.8rem', color: '#64748B', marginTop: '0.125rem' }}>
            Select a predefined city condition to immediately test Digital Twin AI response during presentation.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', backgroundColor: '#E2E8F0', borderRadius: '6px', padding: '0.1875rem' }}>
            {scenarios.map((sc) => {
              const Icon = sc.icon;
              const isActive = currentScenario === sc.id;
              return (
                <button
                  key={sc.id}
                  onClick={() => onSelectScenario(sc.id)}
                  title={sc.desc}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.375rem',
                    padding: '0.375rem 0.75rem',
                    borderRadius: '4px',
                    border: 'none',
                    backgroundColor: isActive ? '#FFFFFF' : 'transparent',
                    color: isActive ? '#0F172A' : '#64748B',
                    fontWeight: isActive ? 600 : 500,
                    fontSize: '0.8125rem',
                    boxShadow: isActive ? '0 1px 2px rgba(0,0,0,0.08)' : 'none',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <Icon style={{ width: '14px', height: '14px', color: isActive ? '#2563EB' : '#64748B' }} />
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
              gap: '0.5rem',
              padding: '0.45rem 1rem',
              backgroundColor: '#2563EB',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '6px',
              fontSize: '0.85rem',
              fontWeight: 600,
              boxShadow: '0 1px 2px rgba(37,99,235,0.2)',
              opacity: loading ? 0.7 : 1
            }}
          >
            <Play style={{ width: '14px', height: '14px', fill: '#FFFFFF' }} />
            Run Simulation
          </button>
        </div>
      </div>
    </div>
  );
}
