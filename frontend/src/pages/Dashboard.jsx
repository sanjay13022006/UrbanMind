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
import MainLocationHero from '../components/MainLocationHero';
import TomTomSearchModal from '../components/TomTomSearchModal';

import {
  getCityStatus,
  getLocations,
  getPredictions,
  getAlerts,
  getAnalytics,
  getDataSourcesStatus,
  triggerSimulation,
  switchToLiveMode,
  syncLocationsFromTomTom
} from '../services/api';
import { AlertCircle, RefreshCw, X } from 'lucide-react';

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
  const [inspectModalLocation, setInspectModalLocation] = useState(null);
  const [isSearchModalOpen, setIsSearchModalOpen] = useState(false);
  const [isSyncingTomTom, setIsSyncingTomTom] = useState(false);
  const [syncFeedback, setSyncFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isError, setIsError] = useState(false);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      const results = await Promise.allSettled([
        getCityStatus(),
        getLocations(),
        getPredictions(),
        getAlerts(),
        getAnalytics(),
        getDataSourcesStatus()
      ]);

      const statusRes = results[0].status === 'fulfilled' ? results[0].value : null;
      const locsRes = results[1].status === 'fulfilled' ? results[1].value : [];
      const predsRes = results[2].status === 'fulfilled' ? results[2].value : [];
      const alertsRes = results[3].status === 'fulfilled' ? results[3].value : [];
      const analyticsRes = results[4].status === 'fulfilled' ? results[4].value : [];
      const sourcesRes = results[5].status === 'fulfilled' ? results[5].value : [];

      if (statusRes || (locsRes && locsRes.length > 0)) {
        if (statusRes) setCityStatus(statusRes);
        if (locsRes && locsRes.length > 0) {
          setLocations(locsRes);
          setSelectedLocation((prev) => {
            if (!prev) return null;
            const updated = locsRes.find((l) => l.location_id === prev.location_id);
            return updated || prev;
          });
        }
        if (predsRes) setPredictions(predsRes);
        if (alertsRes) setAlerts(alertsRes);
        if (analyticsRes) setAnalytics(analyticsRes);
        if (sourcesRes) setDataSources(sourcesRes);

        if (statusRes) {
          setIsLive(statusRes.is_live ?? true);
          if (statusRes.demo_scenario) {
            setCurrentScenario(statusRes.demo_scenario);
          }
        }
        setIsError(false);
      } else {
        setIsError(true);
      }
    } catch (err) {
      console.error('Error connecting to UrbanMind backend:', err);
      setIsError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSyncTomTom = async () => {
    try {
      setIsSyncingTomTom(true);
      setSyncFeedback(null);
      const res = await syncLocationsFromTomTom();
      await fetchDashboardData();
      setSyncFeedback({
        type: 'success',
        message: res.message || 'Synced new locations from TomTom API successfully!'
      });
      setTimeout(() => setSyncFeedback(null), 5000);
    } catch (err) {
      console.error('Error syncing with TomTom API:', err);
      setSyncFeedback({
        type: 'error',
        message: 'Could not sync from TomTom API. Please ensure backend is reachable.'
      });
      setTimeout(() => setSyncFeedback(null), 5000);
    } finally {
      setIsSyncingTomTom(false);
    }
  };

  const handleLocationAdded = async (newPlace) => {
    await fetchDashboardData();
    const refreshedLocs = await getLocations();
    setLocations(refreshedLocs);
    const found = refreshedLocs.find((l) => l.location_id === newPlace.id);
    if (found) {
      setSelectedLocation(found);
    }
    setSyncFeedback({
      type: 'success',
      message: `Added "${newPlace.name}" to the Coimbatore Digital Twin!`
    });
    setTimeout(() => setSyncFeedback(null), 5000);
  };

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
              <strong style={{ fontSize: '0.9rem' }}>Unable to connect to UrbanMind service.</strong>
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

      {/* Sync Feedback Alert Toast */}
      {syncFeedback && (
        <div
          style={{
            marginBottom: '1rem',
            padding: '0.75rem 1rem',
            backgroundColor: syncFeedback.type === 'error' ? '#FEF2F2' : '#F0FDF4',
            border: syncFeedback.type === 'error' ? '1px solid #FECACA' : '1px solid #BBF7D0',
            borderRadius: '6px',
            color: syncFeedback.type === 'error' ? '#B91C1C' : '#166534',
            fontSize: '0.82rem',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
          }}
        >
          <span>{syncFeedback.message}</span>
          <button
            onClick={() => setSyncFeedback(null)}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', padding: '0.2rem' }}
          >
            <X style={{ width: '15px', height: '15px' }} />
          </button>
        </div>
      )}

      {/* Main Location Hero & Dynamic Grid Explorer */}
      <MainLocationHero
        locations={locations}
        selectedLocation={selectedLocation}
        onSelectLocation={(loc) => setSelectedLocation(loc)}
        onOpenDetailsModal={(loc) => setInspectModalLocation(loc || selectedLocation)}
        onSyncTomTom={handleSyncTomTom}
        onOpenSearchModal={() => setIsSearchModalOpen(true)}
        isSyncing={isSyncingTomTom}
      />

      {/* Main Spatial & AI Predictions Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '1.25rem', marginBottom: '1.25rem' }}>
        {/* Left Column: Interactive Map (7 Cols) */}
        <div style={{ gridColumn: 'span 7' }}>
          <CityMap
            locations={locations}
            selectedLocation={selectedLocation}
            onSelectLocation={(loc) => setSelectedLocation(loc)}
            onOpenDetailsModal={(loc) => {
              setSelectedLocation(loc);
              setInspectModalLocation(loc);
            }}
          />
        </div>

        {/* Right Column: AI Predictions (5 Cols) */}
        <div style={{ gridColumn: 'span 5', display: 'flex', flexDirection: 'column' }}>
          <div style={{ flex: 1 }}>
            <Predictions
              predictions={predictions}
              selectedLocation={selectedLocation}
              onSelectLocation={(loc) => {
                const match = locations.find((l) => l.location_id === loc.location_id);
                setSelectedLocation(match || loc);
              }}
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

      {/* Optional Location Details Inspector Modal */}
      {inspectModalLocation && (
        <LocationDetails
          location={inspectModalLocation}
          onClose={() => setInspectModalLocation(null)}
        />
      )}

      {/* TomTom API Place Search & Add Modal */}
      <TomTomSearchModal
        isOpen={isSearchModalOpen}
        onClose={() => setIsSearchModalOpen(false)}
        onLocationAdded={handleLocationAdded}
      />
    </div>
  );
}
