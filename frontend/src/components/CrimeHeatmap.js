import React, { useState, useEffect, useCallback, useRef } from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const CHENNAI_COORDINATES = [13.0827, 80.2707];

const CrimeHeatmap = () => {
  const [crimeData, setCrimeData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('week');
  const { token } = useAuth();
  const mapRef = useRef(null);
  const heatLayerRef = useRef(null);

  const getIntensity = (crimeType, severity) => {
    // Base intensity by crime type
    const typeIntensities = {
      'Assault': 0.8,
      'Robbery': 0.7,
      'Burglary': 0.6,
      'Theft': 0.5,
      'Fraud': 0.4,
      'Cybercrime': 0.3,
      'Harassment': 0.4
    };

    // Severity multiplier
    const severityMultipliers = {
      'Critical': 1.2,
      'High': 1.0,
      'Medium': 0.8,
      'Low': 0.6
    };

    const baseIntensity = typeIntensities[crimeType] || 0.3;
    const multiplier = severityMultipliers[severity] || 1.0;
    
    return baseIntensity * multiplier;
  };

  const updateHeatmap = (data) => {
    if (!mapRef.current) return;

    if (heatLayerRef.current) {
      heatLayerRef.current.remove();
    }

    const heatmapPoints = data.map(crime => {
      const [lng, lat] = crime.location.coordinates;
      const intensity = getIntensity(crime.crime_type, crime.severity);
      return [lat, lng, intensity];
    });

    heatLayerRef.current = L.heatLayer(heatmapPoints, {
      radius: 25,
      blur: 15,
      maxZoom: 10,
      max: 1.0,
      gradient: {
        0.2: 'blue',
        0.4: 'lime',
        0.6: 'yellow',
        0.8: 'orange',
        1.0: 'red'
      }
    }).addTo(mapRef.current);
  };

  const fetchCrimeData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL}/api/crimes/heatmap`,
        {
          params: { timeRange },
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setCrimeData(response.data);
      updateHeatmap(response.data);
    } catch (err) {
      setError('Failed to fetch crime data');
      console.error('Error fetching crime data:', err);
    } finally {
      setLoading(false);
    }
  }, [timeRange, token]);

  useEffect(() => {
    fetchCrimeData();
    const interval = setInterval(fetchCrimeData, 300000); // Update every 5 minutes
    return () => clearInterval(interval);
  }, [fetchCrimeData]);

  if (loading) return <div className="loading">Loading crime data...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="crime-heatmap">
      <div className="map-controls">
        <select 
          value={timeRange} 
          onChange={(e) => setTimeRange(e.target.value)}
          className="time-range-select"
        >
          <option value="day">Last 24 Hours</option>
          <option value="week">Last Week</option>
          <option value="month">Last Month</option>
        </select>
      </div>

      <MapContainer
        center={CHENNAI_COORDINATES}
        zoom={12}
        style={{ height: '600px', width: '100%' }}
        whenCreated={(map) => {
          mapRef.current = map;
        }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
      </MapContainer>

      <div className="legend">
        <h4>Crime Intensity</h4>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: 'red' }}></span>
          <span>Critical</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: 'orange' }}></span>
          <span>High</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: 'yellow' }}></span>
          <span>Medium</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: 'lime' }}></span>
          <span>Low</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: 'blue' }}></span>
          <span>Very Low</span>
        </div>
      </div>
    </div>
  );
};

export default CrimeHeatmap;
