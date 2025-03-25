import React, { useState, useEffect } from 'react';
import {
  PieChart, Pie, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, Cell,
  ResponsiveContainer
} from 'recharts';
import axios from 'axios';

const AnalyticsDashboard = () => {
  const [crimeStats, setCrimeStats] = useState({
    byType: [],
    byTime: [],
    bySeverity: [],
    byStatus: []
  });
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('month');

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

  const processData = (data) => {
    // Process crime types
    const typeCount = {};
    data.forEach(crime => {
      typeCount[crime.crime_type] = (typeCount[crime.crime_type] || 0) + 1;
    });
    const byType = Object.entries(typeCount).map(([type, count]) => ({
      name: type,
      value: count
    }));

    // Process time trends (by day)
    const timeCount = {};
    data.forEach(crime => {
      const date = new Date(crime.timestamp).toLocaleDateString();
      timeCount[date] = (timeCount[date] || 0) + 1;
    });
    const byTime = Object.entries(timeCount).map(([date, count]) => ({
      date,
      count
    })).sort((a, b) => new Date(a.date) - new Date(b.date));

    // Process severity distribution
    const severityCount = {};
    data.forEach(crime => {
      severityCount[crime.severity] = (severityCount[crime.severity] || 0) + 1;
    });
    const bySeverity = Object.entries(severityCount).map(([severity, count]) => ({
      name: severity,
      value: count
    }));

    // Process status distribution
    const statusCount = {};
    data.forEach(crime => {
      statusCount[crime.status] = (statusCount[crime.status] || 0) + 1;
    });
    const byStatus = Object.entries(statusCount).map(([status, count]) => ({
      name: status,
      value: count
    }));

    return { byType, byTime, bySeverity, byStatus };
  };

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/api/crimes/analytics`, {
        params: { timeRange }
      });
      const processedData = processData(response.data);
      setCrimeStats(processedData);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  if (loading) {
    return <div className="loading">Loading analytics...</div>;
  }

  return (
    <div className="analytics-dashboard">
      <div className="time-range-selector">
        <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
          <option value="week">Last Week</option>
          <option value="month">Last Month</option>
          <option value="year">Last Year</option>
        </select>
      </div>

      <div className="dashboard-grid">
        <div className="chart-container">
          <h3>Crimes by Type</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={crimeStats.byType}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                label
              >
                {crimeStats.byType.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Crime Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={crimeStats.byTime}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="count" stroke="#8884d8" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Crime Severity Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={crimeStats.bySeverity}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Case Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={crimeStats.byStatus}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                label
              >
                {crimeStats.byStatus.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;

