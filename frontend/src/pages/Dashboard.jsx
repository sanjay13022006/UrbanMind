import React, { useState, useEffect, useCallback } from 'react';
import Header from '../components/Header';
import ScenarioSelector from '../components/ScenarioSelector';
import DataSourcesPanel from '../components/DataSourcesPanel';
import KPICards from '../components/KPICards';
import CityMap from '../components/CityMap';
import Predictions from '../components/Predictions';
import Alerts from '../components/Alerts';
import Analytics from '../components/Analytics';
import LocationDetails from '../components/LocationDetails';
import FutureScope from '../components/FutureScope';

import {
  getCityStatus,
  getLocations,
  getPredictions,
  getAlerts,
  getAnalytics,
  getDataSourcesStatus,
  triggerSimulation,
  switchToLiveMode
} from '../services/api';
import { AlertCircle, RefreshCw } from 'lucide-react';

export default function Dashboard() {
  const [cityStatus, setCityStatus] = useState(null);
  const [locations, setLocations] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [analytics, setAnalytics] = useState([]);
  const [dataSources, setDataSources] = useState([]);

  const [currentScenario, setCurrentScenario] = useState('normal');
  const [isLive, setIsLive] = useState(true);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isError, setIsError] = useState(false);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      const [statusRes, locsRes, predsRes, alertsRes, analyticsRes, sourcesRes] = await Promise.all([
        getCityStatus(),
        getLocations(),
        getPredictions(),
        getAlerts(),
        getAnalytics(),
        getDataSourcesStatus()
      ]);

      setCityStatus(statusRes);
      setLocations(locsRes);
      setPredictions(predsRes);
      setAlerts(alertsRes);
      setAnalytics(analyticsRes);
      setDataSources(sourcesRes);

      if (statusRes) {
        setIsLive(statusRes.is_live ?? true);
        if (statusRes.demo_scenario) {
          setCurrentScenario(statusRes.demo_scenario);
        }
      }
      setIsError(false);
    } catch (err) {
      console.error('Error connecting to UrbanTwin AI backend:', err);
      setIsError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load and 6-second auto refresh interval (reads cached observations without spamming APIs)
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(() => {
      fetchDashboardData();
    }, 6000);
    return () => clearInterval(interval);
  }, [fetchDashboardData]);

  const handleSelectScenario = async (scenarioId) => {
    try {
      setLoading(true);
      setCurrentScenario(scenarioId);
      setIsLive(false);
      await triggerSimulation('DEMO', scenarioId);
      await fetchDashboardData();
    } catch (err) {
      console.error('Error setting demo scenario:', err);
      setIsError(true);
    } finally {
      setLoading(false);
    }
  };

  const handleSwitchToLive = async () => {
    try {
      setLoading(true);
      await switchToLiveMode();
      setIsLive(true);
      await fetchDashboardData();
    } catch (err) {
      console.error('Error switching to live mode:', err);
      setIsError(true);
    } finally {
      setLoading(false);
    }
  };

  const handleRunSimulation = async (scenarioId = currentScenario) => {
    try {
      setLoading(true);
      await triggerSimulation('DEMO', scenarioId);
      await fetchDashboardData();
    } catch (err) {
      console.error('Error running simulation:', err);
      setIsError(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Header
        statusData={cityStatus}
        onRefresh={fetchDashboardData}
        loading={loading}
        isError={isError}
      />

      {isError && (
        <div
          style={{
            marginBottom: '1.25rem',
            padding: '1rem',
            backgroundColor: '#FEF2F2',
            border: '1px solid #FECACA',
            borderRadius: '6px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '1rem'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', color: '#B91C1C' }}>
            <AlertCircle style={{ width: '20px', height: '20px' }} />
            <div>
              <strong style={{ fontSize: '0.9rem' }}>Unable to connect to UrbanTwin AI service.</strong>
              <div style={{ fontSize: '0.8rem', color: '#7F1D1D' }}>
                Please ensure the FastAPI backend is running on http://127.0.0.1:8000.
              </div>
            </div>
          </div>
          <button
            onClick={fetchDashboardData}
            style={{
              padding: '0.4rem 0.875rem',
              backgroundColor: '#DC2626',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '4px',
              fontWeight: 600,
              fontSize: '0.8rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.375rem',
              cursor: 'pointer'
            }}
          >
            <RefreshCw style={{ width: '14px', height: '14px' }} /> Retry Connection
          </button>
        </div>
      )}

      {/* Scenario & Operation Mode Selector */}
      <ScenarioSelector
        isLive={isLive}
        currentScenario={currentScenario}
        onSelectScenario={handleSelectScenario}
        onRunSimulation={handleRunSimulation}
        onSwitchToLive={handleSwitchToLive}
        loading={loading}
      />

      {/* External Data Sources Status Panel */}
      <DataSourcesPanel
        sources={dataSources}
        isLive={isLive}
        onRefreshSources={fetchDashboardData}
      />

      {/* KPI Overview Cards */}
      <KPICards statusData={cityStatus} />

      {/* Main Spatial & AI Predictions Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '1.25rem', marginBottom: '1.25rem' }}>
        {/* Left Column: Interactive Map (7 Cols) */}
        <div style={{ gridColumn: 'span 7' }}>
          <CityMap
            locations={locations}
            selectedLocation={selectedLocation}
            onSelectLocation={(loc) => setSelectedLocation(loc)}
          />
        </div>

        {/* Right Column: AI Predictions (5 Cols) */}
        <div style={{ gridColumn: 'span 5', display: 'flex', flexDirection: 'column' }}>
          <div style={{ flex: 1 }}>
            <Predictions
              predictions={predictions}
              onSelectLocation={(loc) => setSelectedLocation(loc)}
            />
          </div>
        </div>
      </div>

      {/* Active Threshold Alerts Panel */}
      <div style={{ marginBottom: '1.25rem' }}>
        <Alerts alerts={alerts} />
      </div>

      {/* Historical Telemetry Analytics */}
      <Analytics analyticsData={analytics} />

      {/* Future Scope & Honest Architectural Notes */}
      <FutureScope />

      {/* Location Details Inspector Modal */}
      {selectedLocation && (
        <LocationDetails
          location={selectedLocation}
          onClose={() => setSelectedLocation(null)}
        />
      )}
    </div>
  );
}
