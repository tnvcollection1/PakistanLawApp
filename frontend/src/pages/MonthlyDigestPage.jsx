import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { useToast } from '../components/ui/use-toast';
import { Calendar, BookOpen, Download, Loader2, Filter } from 'lucide-react';
import { Helmet } from 'react-helmet';

const MonthlyDigestPage = () => {
  const { toast } = useToast();
  const [digests, setDigests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth());
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('all');

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const years = Array.from({ length: 10 }, (_, i) => 2016 + i);

  const categories = [
    { id: 'all', name: 'All Updates' },
    { id: 'cases', name: 'New Cases' },
    { id: 'statutes', name: 'New Statutes' },
    { id: 'amendments', name: 'Amendments' },
    { id: 'notifications', name: 'Notifications' },
    { id: 'circulars', name: 'Circulars' }
  ];

  useEffect(() => {
    fetchDigests();
  }, [selectedMonth, selectedYear]);

  const fetchDigests = async () => {
    try {
      setLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Generate mock data
      const mockDigests = generateMockDigests();
      setDigests(mockDigests);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load monthly digest",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const generateMockDigests = () => {
    const mockData = [
      {
        id: 1,
        title: "Supreme Court Judgment on Constitutional Interpretation",
        type: "cases",
        court: "Supreme Court",
        date: `${selectedYear}-${String(selectedMonth + 1).padStart(2, '0')}-15`,
        citation: "PLD 2024 SC 45",
        summary: "The Supreme Court ruled on the interpretation of Article 184(3)...",
        category: "constitutional"
      },
      {
        id: 2,
        title: "Amendment to Civil Procedure Code",
        type: "amendments",
        date: `${selectedYear}-${String(selectedMonth + 1).padStart(2, '0')}-10`,
        description: "Changes to Order V Rule 20 regarding service of summons...",
        effectiveDate: "2024-03-01",
        category: "civil"
      },
      {
        id: 3,
        title: "New Banking Regulations Notification",
        type: "notifications",
        authority: "State Bank of Pakistan",
        date: `${selectedYear}-${String(selectedMonth + 1).padStart(2, '0')}-05`,
        description: "Updated guidelines for digital banking operations...",
        category: "banking"
      },
      {
        id: 4,
        title: "Lahore High Court Decision on Property Rights",
        type: "cases",
        court: "Lahore High Court",
        date: `${selectedYear}-${String(selectedMonth + 1).padStart(2, '0')}-20`,
        citation: "2024 CLC 123",
        summary: "Important ruling on transfer of property rights...",
        category: "property"
      },
      {
        id: 5,
        title: "Federal Government Ordinance on Taxation",
        type: "statutes",
        date: `${selectedYear}-${String(selectedMonth + 1).padStart(2, '0')}-12`,
        description: "New ordinance regarding income tax amendments...",
        category: "tax"
      }
    ];

    return mockData;
  };

  const filteredDigests = digests.filter(digest => {
    const matchesSearch = digest.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         digest.citation?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         digest.description?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesCategory = activeTab === 'all' || digest.type === activeTab;
    
    return matchesSearch && matchesCategory;
  });

  const getTypeIcon = (type) => {
    switch (type) {
      case 'cases':
        return <BookOpen className="w-4 h-4" />;
      case 'statutes':
        return <Calendar className="w-4 h-4" />;
      case 'amendments':
        return <Filter className="w-4 h-4" />;
      default:
        return <Calendar className="w-4 h-4" />;
    }
  };

  const getTypeBadge = (type) => {
    switch (type) {
      case 'cases':
        return <Badge variant="default">Case</Badge>;
      case 'statutes':
        return <Badge variant="secondary">Statute</Badge>;
      case 'amendments':
        return <Badge variant="outline">Amendment</Badge>;
      case 'notifications':
        return <Badge variant="destructive">Notification</Badge>;
      case 'circulars':
        return <Badge variant="outline">Circular</Badge>;
      default:
        return <Badge>Other</Badge>;
    }
  };

  const handleDownload = () => {
    // Generate digest content
    const content = generateDigestContent();
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `monthly-digest-${months[selectedMonth]}-${selectedYear}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    toast({
      title: "Downloaded",
      description: "Monthly digest downloaded successfully"
    });
  };

  const generateDigestContent = () => {
    let content = `MONTHLY LEGAL DIGEST\n`;
    content += `${months[selectedMonth]} ${selectedYear}\n`;
    content += '='.repeat(50) + '\n\n';

    filteredDigests.forEach(digest => {
      content += `${digest.title}\n`;
      content += `Type: ${digest.type}\n`;
      if (digest.citation) content += `Citation: ${digest.citation}\n`;
      if (digest.court) content += `Court: ${digest.court}\n`;
      if (digest.authority) content += `Authority: ${digest.authority}\n`;
      content += `Date: ${digest.date}\n`;
      if (digest.summary) content += `Summary: ${digest.summary}\n`;
      if (digest.description) content += `Description: ${digest.description}\n`;
      content += '-'.repeat(30) + '\n\n';
    });

    return content;
  };

  return (
    <>
      <Helmet>
        <title>Monthly Digest | Pakistan Law App</title>
      </Helmet>

      <div className="min-h-screen bg-slate-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-900">Monthly Digest</h1>
            <p className="text-slate-600 mt-2">Monthly updates on cases, statutes, and legal developments</p>
          </div>

          {/* Controls */}
          <Card className="p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Month</label>
                <select
                  value={selectedMonth}
                  onChange={(e) => setSelectedMonth(parseInt(e.target.value))}
                  className="w-full p-2 border rounded-md"
                >
                  {months.map((month, index) => (
                    <option key={index} value={index}>{month}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Year</label>
                <select
                  value={selectedYear}
                  onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                  className="w-full p-2 border rounded-md"
                >
                  {years.map(year => (
                    <option key={year} value={year}>{year}</option>
                  ))}
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="text-sm font-medium mb-2 block">Search</label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Search digests..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  <Button variant="outline" onClick={handleDownload}>
                    <Download className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </Card>

          {/* Category Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-6">
            <TabsList className="grid grid-cols-6">
              {categories.map(category => (
                <TabsTrigger key={category.id} value={category.id}>
                  {category.name}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>

          {/* Results */}
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-slate-400" />
            </div>
          ) : filteredDigests.length > 0 ? (
            <div className="space-y-4">
              {filteredDigests.map(digest => (
                <Card key={digest.id} className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        {getTypeBadge(digest.type)}
                        <span className="text-sm text-slate-500">
                          {new Date(digest.date).toLocaleDateString()}
                        </span>
                      </div>
                      <h3 className="text-lg font-semibold text-slate-900">
                        {digest.title}
                      </h3>
                      {digest.citation && (
                        <p className="text-slate-600 text-sm mt-1">{digest.citation}</p>
                      )}
                      {digest.court && (
                        <p className="text-slate-600 text-sm">{digest.court}</p>
                      )}
                      {digest.authority && (
                        <p className="text-slate-600 text-sm">{digest.authority}</p>
                      )}
                      <p className="text-slate-700 mt-3">
                        {digest.summary || digest.description}
                      </p>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-12 text-center">
              <Calendar className="w-12 h-12 mx-auto mb-4 text-slate-400" />
              <p className="text-slate-600">No updates found for the selected period</p>
            </Card>
          )}
        </div>
      </div>
    </>
  );
};

export default MonthlyDigestPage;
