import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { useToast } from '../components/ui/use-toast';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { TrendingUp, Users, Search, BookOpen, Loader2, Download } from 'lucide-react';
import { Helmet } from 'react-helmet';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

const AnalyticsDashboard = () => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [timeRange, setTimeRange] = useState('30days');

  useEffect(() => {
    fetchAnalyticsData();
  }, [timeRange]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const mockData = generateMockData();
      setAnalyticsData(mockData);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load analytics data",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const generateMockData = () => {
    return {
      summary: {
        totalSearches: 15420,
        totalUsers: 3200,
        totalCases: 45000,
        totalStatutes: 850,
        activeUsers: 890,
        newUsers: 234
      },
      searchTrends: [
        { name: 'Jan', searches: 1200, users: 800 },
        { name: 'Feb', searches: 1350, users: 850 },
        { name: 'Mar', searches: 1400, users: 900 },
        { name: 'Apr', searches: 1600, users: 950 },
        { name: 'May', searches: 1500, users: 920 },
        { name: 'Jun', searches: 1800, users: 1000 }
      ],
      courtDistribution: [
        { name: 'Supreme Court', value: 35 },
        { name: 'Lahore High Court', value: 25 },
        { name: 'Sindh High Court', value: 20 },
        { name: 'Peshawar High Court', value: 12 },
        { name: 'Balochistan High Court', value: 5 },
        { name: 'Islamabad High Court', value: 3 }
      ],
      caseCategories: [
        { name: 'Civil', cases: 450 },
        { name: 'Criminal', cases: 320 },
        { name: 'Constitutional', cases: 180 },
        { name: 'Commercial', cases: 120 },
        { name: 'Family', cases: 90 },
        { name: 'Labor', cases: 60 }
      ],
      topSearches: [
        { query: 'property rights', count: 234 },
        { query: 'criminal procedure', count: 198 },
        { query: 'constitutional law', count: 176 },
        { query: 'civil procedure', count: 154 },
        { query: 'evidence act', count: 132 }
      ],
      userActivity: [
        { day: 'Mon', active: 450 },
        { day: 'Tue', active: 520 },
        { day: 'Wed', active: 480 },
        { day: 'Thu', active: 550 },
        { day: 'Fri', active: 420 },
        { day: 'Sat', active: 280 },
        { day: 'Sun', active: 200 }
      ]
    };
  };

  const handleExport = () => {
    if (!analyticsData) return;
    
    const content = JSON.stringify(analyticsData, null, 2);
    const blob = new Blob([content], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analytics-${timeRange}-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    toast({
      title: "Exported",
      description: "Analytics data exported successfully"
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-slate-400" />
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <p className="text-slate-600">Failed to load analytics data</p>
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>Analytics Dashboard | Pakistan Law App</title>
      </Helmet>

      <div className="min-h-screen bg-slate-50 py-8">
        <div className="max-w-7xl mx-auto px-4">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Analytics Dashboard</h1>
              <p className="text-slate-600 mt-2">Platform usage and performance metrics</p>
            </div>
            <div className="flex gap-4">
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="p-2 border rounded-md"
              >
                <option value="7days">Last 7 Days</option>
                <option value="30days">Last 30 Days</option>
                <option value="90days">Last 90 Days</option>
                <option value="1year">Last Year</option>
              </select>
              <Button variant="outline" onClick={handleExport}>
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
            </div>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Total Searches</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {analyticsData.summary.totalSearches.toLocaleString()}
                  </p>
                </div>
                <Search className="w-8 h-8 text-blue-500" />
              </div>
              <div className="mt-4 flex items-center text-sm text-green-600">
                <TrendingUp className="w-4 h-4 mr-1" />
                +12% from last period
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Total Users</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {analyticsData.summary.totalUsers.toLocaleString()}
                  </p>
                </div>
                <Users className="w-8 h-8 text-green-500" />
              </div>
              <div className="mt-4 flex items-center text-sm text-green-600">
                <TrendingUp className="w-4 h-4 mr-1" />
                +8% from last period
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Total Cases</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {analyticsData.summary.totalCases.toLocaleString()}
                  </p>
                </div>
                <BookOpen className="w-8 h-8 text-purple-500" />
              </div>
              <div className="mt-4 flex items-center text-sm text-green-600">
                <TrendingUp className="w-4 h-4 mr-1" />
                +5% from last period
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">Active Users</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {analyticsData.summary.activeUsers.toLocaleString()}
                  </p>
                </div>
                <Users className="w-8 h-8 text-orange-500" />
              </div>
              <div className="mt-4 flex items-center text-sm text-green-600">
                <TrendingUp className="w-4 h-4 mr-1" />
                +15% from last period
              </div>
            </Card>
          </div>

          {/* Charts */}
          <Tabs defaultValue="trends" className="mb-8">
            <TabsList>
              <TabsTrigger value="trends">Search Trends</TabsTrigger>
              <TabsTrigger value="courts">Court Distribution</TabsTrigger>
              <TabsTrigger value="categories">Categories</TabsTrigger>
              <TabsTrigger value="activity">User Activity</TabsTrigger>
            </TabsList>

            <TabsContent value="trends">
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Search Trends</h3>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={analyticsData.searchTrends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="searches" stroke="#8884d8" name="Searches" />
                    <Line type="monotone" dataKey="users" stroke="#82ca9d" name="Users" />
                  </LineChart>
                </ResponsiveContainer>
              </Card>
            </TabsContent>

            <TabsContent value="courts">
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Court Distribution</h3>
                <ResponsiveContainer width="100%" height={400}>
                  <PieChart>
                    <Pie
                      data={analyticsData.courtDistribution}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={120}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {analyticsData.courtDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Card>
            </TabsContent>

            <TabsContent value="categories">
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Case Categories</h3>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={analyticsData.caseCategories}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="cases" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </TabsContent>

            <TabsContent value="activity">
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">User Activity</h3>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={analyticsData.userActivity}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="active" fill="#82ca9d" name="Active Users" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Top Searches */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Top Searches</h3>
            <div className="space-y-3">
              {analyticsData.topSearches.map((search, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-medium">
                      {index + 1}
                    </span>
                    <span className="text-slate-900">{search.query}</span>
                  </div>
                  <span className="text-slate-600">{search.count} searches</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </>
  );
};

export default AnalyticsDashboard;
