import React, { useState } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { Label } from '../components/ui/label';
import { Checkbox } from '../components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Slider } from '../components/ui/slider';
import { useToast } from '../components/ui/use-toast';
import { Search, Loader2, FileText, Filter, BookOpen } from 'lucide-react';
import { Helmet } from 'react-helmet';

const FulltextSearchPage = () => {
  const { toast } = useToast();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [showFilters, setShowFilters] = useState(false);
  
  // Filter states
  const [filters, setFilters] = useState({
    courts: [],
    dateRange: { from: '', to: '' },
    caseTypes: [],
    relevanceThreshold: 50,
    exactMatch: false,
    includeSynonyms: true
  });

  const courts = [
    'Supreme Court',
    'Lahore High Court',
    'Sindh High Court',
    'Peshawar High Court',
    'Balochistan High Court',
    'Islamabad High Court'
  ];

  const caseTypes = [
    'Civil',
    'Criminal',
    'Constitutional',
    'Commercial',
    'Family',
    'Labor'
  ];

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
      
      // Simulate search
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockResults = generateMockResults();
      setResults(mockResults);
      
      toast({
        title: "Search Complete",
        description: `Found ${mockResults.length} results`
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

  const generateMockResults = () => {
    return [
      {
        id: 1,
        title: "Constitutional Validity of Land Acquisition",
        citation: "PLD 2023 SC 123",
        court: "Supreme Court",
        date: "2023-05-15",
        relevance: 98,
        excerpt: "...the court held that the acquisition of land for public purpose must be in accordance with the principles of fairness and equity...",
        fullText: "This is the full text of the case..."
      },
      {
        id: 2,
        title: "Property Rights and Fundamental Freedoms",
        citation: "2023 CLC 456",
        court: "Lahore High Court",
        date: "2023-04-20",
        relevance: 85,
        excerpt: "...property rights are protected under Article 23 and 24 of the Constitution...",
        fullText: "This is the full text of the case..."
      },
      {
        id: 3,
        title: "Commercial Dispute Resolution",
        citation: "PLD 2023 Karachi 789",
        court: "Sindh High Court",
        date: "2023-03-10",
        relevance: 72,
        excerpt: "...in commercial disputes, the parties are encouraged to pursue alternative dispute resolution...",
        fullText: "This is the full text of the case..."
      }
    ];
  };

  const handleCourtToggle = (court) => {
    setFilters(prev => ({
      ...prev,
      courts: prev.courts.includes(court)
        ? prev.courts.filter(c => c !== court)
        : [...prev.courts, court]
    }));
  };

  const handleCaseTypeToggle = (caseType) => {
    setFilters(prev => ({
      ...prev,
      caseTypes: prev.caseTypes.includes(caseType)
        ? prev.caseTypes.filter(c => c !== caseType)
        : [...prev.caseTypes, caseType]
    }));
  };

  return (
    <>
      <Helmet>
        <title>Fulltext Search | Pakistan Law App</title>
      </Helmet>

      <div className="min-h-screen bg-slate-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-slate-900">Fulltext Search</h1>
            <p className="text-slate-600 mt-2">
              Search within the full text of cases and statutes
            </p>
          </div>

          {/* Search Box */}
          <Card className="p-6 mb-6">
            <div className="space-y-4">
              <div>
                <Label htmlFor="query">Search Query</Label>
                <Textarea
                  id="query"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Enter your search query. Use quotes for exact phrases, OR/AND for boolean logic..."
                  rows={3}
                />
              </div>
              
              <div className="flex gap-4">
                <Button
                  onClick={handleSearch}
                  disabled={loading}
                  className="flex-1"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <Search className="w-4 h-4 mr-2" />
                      Search Full Text
                    </>
                  )}
                </Button>
                
                <Button
                  variant="outline"
                  onClick={() => setShowFilters(!showFilters)}
                >
                  <Filter className="w-4 h-4 mr-2" />
                  Filters
                </Button>
              </div>
            </div>
          </Card>

          {/* Filters */}
          {showFilters && (
            <Card className="p-6 mb-6">
              <h2 className="text-lg font-semibold mb-4">Search Filters</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Courts */}
                <div>
                  <h3 className="text-sm font-medium mb-3">Courts</h3>
                  <div className="space-y-2">
                    {courts.map(court => (
                      <div key={court} className="flex items-center space-x-2">
                        <Checkbox
                          id={court}
                          checked={filters.courts.includes(court)}
                          onCheckedChange={() => handleCourtToggle(court)}
                        />
                        <Label htmlFor={court}>{court}</Label>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Case Types */}
                <div>
                  <h3 className="text-sm font-medium mb-3">Case Types</h3>
                  <div className="space-y-2">
                    {caseTypes.map(type => (
                      <div key={type} className="flex items-center space-x-2">
                        <Checkbox
                          id={type}
                          checked={filters.caseTypes.includes(type)}
                          onCheckedChange={() => handleCaseTypeToggle(type)}
                        />
                        <Label htmlFor={type}>{type}</Label>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Date Range */}
                <div>
                  <h3 className="text-sm font-medium mb-3">Date Range</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="dateFrom">From</Label>
                      <Input
                        id="dateFrom"
                        type="date"
                        value={filters.dateRange.from}
                        onChange={(e) => setFilters(prev => ({
                          ...prev,
                          dateRange: { ...prev.dateRange, from: e.target.value }
                        }))}
                      />
                    </div>
                    <div>
                      <Label htmlFor="dateTo">To</Label>
                      <Input
                        id="dateTo"
                        type="date"
                        value={filters.dateRange.to}
                        onChange={(e) => setFilters(prev => ({
                          ...prev,
                          dateRange: { ...prev.dateRange, to: e.target.value }
                        }))}
                      />
                    </div>
                  </div>
                </div>

                {/* Relevance Threshold */}
                <div>
                  <h3 className="text-sm font-medium mb-3">Relevance Threshold</h3>
                  <Slider
                    value={[filters.relevanceThreshold]}
                    onValueChange={(value) => setFilters(prev => ({
                      ...prev,
                      relevanceThreshold: value[0]
                    }))}
                    max={100}
                    step={5}
                  />
                  <div className="text-sm text-slate-600 mt-1">
                    Minimum relevance: {filters.relevanceThreshold}%
                  </div>
                </div>

                {/* Options */}
                <div>
                  <h3 className="text-sm font-medium mb-3">Search Options</h3>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="exactMatch"
                        checked={filters.exactMatch}
                        onCheckedChange={(checked) => setFilters(prev => ({
                          ...prev,
                          exactMatch: checked
                        }))}
                      />
                      <Label htmlFor="exactMatch">Exact match only</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="synonyms"
                        checked={filters.includeSynonyms}
                        onCheckedChange={(checked) => setFilters(prev => ({
                          ...prev,
                          includeSynonyms: checked
                        }))}
                      />
                      <Label htmlFor="synonyms">Include synonyms</Label>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          )}

          {/* Results */}
          {results.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold">Search Results</h2>
              {results.map(result => (
                <Card key={result.id} className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="secondary">{result.court}</Badge>
                        <span className="text-sm text-slate-500">
                          {new Date(result.date).toLocaleDateString()}
                        </span>
                      </div>
                      <h3 className="text-lg font-semibold text-slate-900">
                        {result.title}
                      </h3>
                      <p className="text-slate-600 text-sm mt-1">{result.citation}</p>
                      <div className="mt-3 p-3 bg-slate-50 rounded-lg">
                        <p className="text-slate-700 text-sm italic">
                          "{result.excerpt}"
                        </p>
                      </div>
                    </div>
                    <div className="ml-4 text-center">
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
              <FileText className="w-12 h-12 mx-auto mb-4 text-slate-400" />
              <p className="text-slate-600">No results found</p>
              <p className="text-slate-500 text-sm mt-2">
                Try adjusting your search query or filters
              </p>
            </Card>
          )}

          {!query && !loading && (
            <Card className="p-12 text-center">
              <BookOpen className="w-12 h-12 mx-auto mb-4 text-slate-400" />
              <p className="text-slate-600">Enter a search query to find cases</p>
            </Card>
          )}
        </div>
      </div>
    </>
  );
};

export default FulltextSearchPage;
