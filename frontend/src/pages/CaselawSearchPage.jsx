import React, { useState } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { useToast } from '../components/ui/use-toast';
import { Search, Loader2, BookOpen, Filter } from 'lucide-react';
import { Helmet } from 'react-helmet';

const CaselawSearchPage = () => {
  const { toast } = useToast();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [selectedCourt, setSelectedCourt] = useState('');
  const [selectedYear, setSelectedYear] = useState('');
  const [caseType, setCaseType] = useState('');

  const courts = [
    'All Courts',
    'Supreme Court',
    'Lahore High Court',
    'Sindh High Court',
    'Peshawar High Court',
    'Balochistan High Court',
    'Islamabad High Court'
  ];

  const caseTypes = [
    'All Types',
    'Civil',
    'Criminal',
    'Constitutional',
    'Commercial',
    'Family'
  ];

  const years = Array.from({ length: 30 }, (_, i) => (2024 - i).toString());

  const handleSearch = async () => {
    if (!query.trim()) {
      toast({
        title: "Empty Query",
        description: "Please enter a search query",
        variant: "destructive"
      });
      return;
    }

    try {
      setLoading(true);
      
      // Simulate search API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock results
      const mockResults = [
        {
          id: 1,
          title: "Constitutional Validity of Land Reforms",
          citation: "PLD 2024 SC 1",
          court: "Supreme Court",
          date: "2024-01-15",
          type: "Constitutional",
          summary: "This case deals with the constitutional validity of land reform measures and their impact on property rights.",
          relevance: 98
        },
        {
          id: 2,
          title: "Property Rights and Inheritance",
          citation: "2024 CLC 45",
          court: "Lahore High Court",
          date: "2024-02-20",
          type: "Civil",
          summary: "Interpretation of property rights under Islamic law and statutory provisions.",
          relevance: 85
        },
        {
          id: 3,
          title: "Criminal Procedure Code Interpretation",
          citation: "PLD 2023 Karachi 100",
          court: "Sindh High Court",
          date: "2023-12-10",
          type: "Criminal",
          summary: "Analysis of Section 561-A and powers of High Court under Cr.P.C.",
          relevance: 72
        }
      ];

      setResults(mockResults);
      
      toast({
        title: "Search Complete",
        description: `Found ${mockResults.length} cases`
      });
    } catch (error) {
      toast({
        title: "Search Failed",
        description: error.message,
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <>
      <Helmet>
        <title>Caselaw Search | Pakistan Law App</title>
      </Helmet>

      <div className="min-h-screen bg-slate-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-slate-900">Caselaw Search</h1>
            <p className="text-slate-600 mt-2">
              Search through thousands of Pakistani legal cases
            </p>
          </div>

          {/* Search Section */}
          <Card className="p-6 mb-6">
            <div className="space-y-4">
              <div className="relative">
                <Input
                  placeholder="Search cases by keyword, citation, or case title..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="w-full pr-20"
                />
                <Button
                  className="absolute right-0 top-0 h-full"
                  onClick={handleSearch}
                  disabled={loading}
                >
                  {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Search className="w-4 h-4" />
                  )}
                </Button>
              </div>

              {/* Filters */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Court</label>
                  <Select
                    value={selectedCourt}
                    onValueChange={setSelectedCourt}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select Court" />
                    </SelectTrigger>
                    <SelectContent>
                      {courts.map(court => (
                        <SelectItem key={court} value={court}>
                          {court}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Case Type</label>
                  <Select
                    value={caseType}
                    onValueChange={setCaseType}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select Type" />
                    </SelectTrigger>
                    <SelectContent>
                      {caseTypes.map(type => (
                        <SelectItem key={type} value={type}>
                          {type}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Year</label>
                  <Select
                    value={selectedYear}
                    onValueChange={setSelectedYear}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select Year" />
                    </SelectTrigger>
                    <SelectContent>
                      {years.map(year => (
                        <SelectItem key={year} value={year}>
                          {year}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          </Card>

          {/* Results */}
          {results.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">Search Results</h2>
                <span className="text-sm text-slate-600">
                  {results.length} cases found
                </span>
              </div>

              {results.map(result => (
                <Card key={result.id} className="p-6 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="secondary">{result.court}</Badge>
                        <Badge variant="outline">{result.type}</Badge>
                        <span className="text-sm text-slate-500">
                          {result.date}
                        </span>
                      </div>
                      
                      <h3 className="text-lg font-semibold text-slate-900 mb-1">
                        {result.title}
                      </h3>
                      
                      <p className="text-slate-600 text-sm mb-3">
                        {result.citation}
                      </p>
                      
                      <p className="text-slate-700 text-sm">
                        {result.summary}
                      </p>
                    </div>

                    <div className="ml-6 text-right">
                      <div className="text-2xl font-bold text-blue-600">
                        {result.relevance}%
                      </div>
                      <div className="text-xs text-slate-500">relevance</div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}

          {results.length === 0 && !loading && query && (
            <Card className="p-12 text-center">
              <BookOpen className="w-12 h-12 mx-auto mb-4 text-slate-400" />
              <p className="text-slate-600">No cases found matching your search</p>
              <p className="text-slate-500 text-sm mt-2">
                Try adjusting your search terms or filters
              </p>
            </Card>
          )}

          {!query && !loading && (
            <Card className="p-12 text-center">
              <Search className="w-12 h-12 mx-auto mb-4 text-slate-400" />
              <p className="text-slate-600">Enter a search query to find cases</p>
            </Card>
          )}
        </div>
      </div>
    </>
  );
};

export default CaselawSearchPage;
