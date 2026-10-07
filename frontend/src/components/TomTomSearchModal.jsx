import React, { useState } from 'react';
import { Search, X, MapPin, Plus, Check, Loader2, Navigation, ExternalLink } from 'lucide-react';
import { searchLocationsFromApi, addCustomLocation } from '../services/api';

export default function TomTomSearchModal({ isOpen, onClose, onLocationAdded }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [addingId, setAddingId] = useState(null);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleSearch = async (e) => {
    e && e.preventDefault();
    if (!query.trim() || query.length < 2) return;

    try {
      setLoading(true);
      setError(null);
      const res = await searchLocationsFromApi(query.trim());
      setResults(res || []);
      if (!res || res.length === 0) {
        setError('No locations found in Coimbatore matching this query via TomTom Search API.');
      }
    } catch (err) {
      console.error('Error searching TomTom places:', err);
      setError('Failed to reach TomTom Places API. Ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async (place) => {
    try {
      setAddingId(place.id);
      await addCustomLocation({
        id: place.id,
        name: place.name,
        lat: place.lat,
        lng: place.lng,
        zone_type: place.zone_type,
        type: place.type,
        description: place.description
      });
      if (onLocationAdded) {
        await onLocationAdded(place);
      }
      onClose();
    } catch (err) {
      console.error('Error adding location from TomTom:', err);
      setError('Could not add location to digital twin network.');
    } finally {
      setAddingId(null);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(15, 23, 42, 0.55)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 9999,
        padding: '1rem'
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{
          width: '100%',
          maxWidth: '560px',
          backgroundColor: '#FFFFFF',
          maxHeight: '85vh',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.2)',
          padding: '1.25rem',
          borderRadius: '8px'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid #E2E8F0', paddingBottom: '0.75rem' }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0F172A', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Navigation style={{ width: '18px', height: '18px', color: '#2563EB' }} />
              Discover Locations via TomTom API
            </h3>
            <p style={{ fontSize: '0.76rem', color: '#64748B', margin: '0.2rem 0 0 0' }}>
              Queries live TomTom Places & Geocoding API across Coimbatore to add any corridor.
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              border: 'none',
              background: 'none',
              cursor: 'pointer',
              color: '#64748B',
              padding: '0.25rem'
            }}
          >
            <X style={{ width: '20px', height: '20px' }} />
          </button>
        </div>

        {/* Search input form */}
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search
              style={{
                position: 'absolute',
                left: '10px',
                top: '50%',
                transform: 'translateY(-50%)',
                width: '16px',
                height: '16px',
                color: '#94A3B8'
              }}
            />
            <input
              type="text"
              placeholder="e.g. Peelamedu, Brookefields, Airport, KMCH, PSG Tech..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              style={{
                width: '100%',
                padding: '0.6rem 0.75rem 0.6rem 2.2rem',
                borderRadius: '6px',
                border: '1px solid #CBD5E1',
                fontSize: '0.85rem',
                outline: 'none'
              }}
              autoFocus
            />
          </div>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            style={{
              padding: '0.6rem 1rem',
              backgroundColor: '#2563EB',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '6px',
              fontWeight: 600,
              fontSize: '0.82rem',
              cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem'
            }}
          >
            {loading ? 'Searching...' : 'Search API'}
          </button>
        </form>

        {error && (
          <div style={{ padding: '0.6rem 0.8rem', backgroundColor: '#FEF2F2', border: '1px solid #FECACA', borderRadius: '4px', color: '#B91C1C', fontSize: '0.78rem', marginBottom: '0.75rem' }}>
            {error}
          </div>
        )}

        {/* Results List */}
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '360px' }}>
          {results.length === 0 && !loading && !error && (
            <div style={{ textAlign: 'center', padding: '2rem 1rem', color: '#94A3B8', fontSize: '0.82rem' }}>
              Type any neighborhood, junction, hospital, or landmark in Coimbatore and press <strong>Search API</strong>.
            </div>
          )}

          {results.map((place) => (
            <div
              key={place.id}
              style={{
                padding: '0.75rem',
                backgroundColor: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '6px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: '0.75rem'
              }}
            >
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.2rem' }}>
                  <MapPin style={{ width: '14px', height: '14px', color: '#2563EB' }} />
                  <strong style={{ fontSize: '0.85rem', color: '#0F172A' }}>{place.name}</strong>
                  <span style={{ fontSize: '0.68rem', backgroundColor: '#E2E8F0', padding: '0.1rem 0.4rem', borderRadius: '4px', color: '#475569' }}>
                    {place.zone_type}
                  </span>
                </div>
                <div style={{ fontSize: '0.73rem', color: '#64748B' }}>
                  {place.description}
                </div>
                <div style={{ fontSize: '0.68rem', color: '#94A3B8', marginTop: '0.15rem' }}>
                  Coordinates: {place.lat}, {place.lng}
                </div>
              </div>

              <button
                onClick={() => handleAdd(place)}
                disabled={addingId === place.id}
                style={{
                  padding: '0.45rem 0.75rem',
                  backgroundColor: '#16A34A',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.25rem',
                  whiteSpace: 'nowrap'
                }}
              >
                <Plus style={{ width: '13px', height: '13px' }} />
                {addingId === place.id ? 'Adding...' : 'Add to Twin'}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
