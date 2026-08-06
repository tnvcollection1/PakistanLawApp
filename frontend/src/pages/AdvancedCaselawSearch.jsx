import React, { useState } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Checkbox } from '../components/ui/checkbox';
import { Slider } from '../components/ui/slider';
import { useToast } from '../components/ui/use-toast';
import { Search, Loader2, Filter, Calendar, BookOpen } from 'lucide-react';
import { Helmet } from 'react-helmet';

const courts = [
  'Supreme Court',
  'Lahore High Court',
  'Sindh High Court',
  'Peshawar High Court',
  'Balochistan High Court',
  'Islamabad High Court',
  'Federal Shariat Court'
];

const caseTypes = [
  'Civil',
  'Criminal',
  'Constitutional',
  'Commercial',
  'Family',
  'Labor',
  'Tax',
  'Service'
];

const AdvancedCaselawSearch = () => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [showFilters, setShowFilters] = useState(true);
  
  const [searchParams, setSearchParams] = useState({
    keywords: '',
    judge: '',
    petitioner: '',
    respondent: '',
    advocate: '',
    citation: '',
    courts: [],
    caseTypes: [],
    dateFrom: '',
    dateTo: '',
    minYear: 1950,
    maxYear: new Date().getFullYear(),
    fullText: false,
    headnotesOnly: false,
    citedCases: '',
    statutesCited: ''
  });

  const handleSearch = async () => {
    try {
      setLoading(true);
      
      // Simulate search
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockResults = generateMockResults();
      setResults(mockResults);
      
      toast({
        title: "Search Complete",
        description: `Found ${mockResults.length} cases matching your criteria`
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
        title: "Constitutional Petition Regarding Fundamental Rights",
        citation: "PLD 2024 SC 1",
        court: "Supreme Court",
        date: "2024-01-15",
        judge: "Chief Justice",
        petitioner: "Citizen A",
        respondent: "State",
        type: "Constitutional",
        summary: "This case deals with fundamental rights under the Constitution..."
      },
      {
        id: 2,
        title: "Civil Dispute Over Property Rights",
        citation: "2024 CLC 45",
        court: "Lahore High Court",
        date: "2024-02-20",
        judge: "Justice B",
        petitioner: "Plaintiff X",
        respondent: "Defendant Y",
        type: "Civil",
        summary: "Property dispute regarding inheritance rights..."
      }
    ];
  };

  const handleCourtToggle = (court) => {
    setSearchParams(prev => ({
      ...prev,
      courts: prev.courts.includes(court)
        ? prev.courts.filter(c => c !== court)
        : [...prev.courts, court]
    }));
  };

  const handleCaseTypeToggle = (type) => {
    setSearchParams(prev => ({
      ...prev,
      caseTypes: prev.caseTypes.includes(type)
        ? prev.caseTypes.filter(t => t !== type)
        : [...prev.caseTypes, type]
    }));
  };

  const handleInputChange = (field, value) => {
    setSearchParams(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <>
      <Helmet>
        <title>Advanced Caselaw Search | Pakistan Law App</title>
      </Helmet>

      <div className="min-h-screen bg-slate-50 py-8">
        <div className="max-w-7xl mx-auto px-4">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-900">Advanced Caselaw Search</h1>
            <p className="text-slate-600 mt-2">Search cases with detailed filters and criteria</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Filters Panel */}
            <div className="lg:col-span-1">
              <Card className="p-4 sticky top-4">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="font-semibold">Filters</h2>
                  <Filter className="w-4 h-4" />
                </div>

                <div className="space-y-4">
                  {/* Keywords */}
                  <div>
                    <Label htmlFor="keywords">Keywords</Label>
                    <Input
                      id="keywords"
                      placeholder="Search keywords..."
                      value={searchParams.keywords}
                      onChange={(e) => handleInputChange('keywords', e.target.value)}
                    />
                  </div>

                  {/* Judge */}
                  <div>
                    <Label htmlFor="judge">Judge Name</Label>
                    <Input
                      id="judge"
                      placeholder="Judge name..."
                      value={searchParams.judge}
                      onChange={(e) => handleInputChange('judge', e.target.value)}
                    />
                  </div>

                  {/* Parties */}
                  <div>
                    <Label htmlFor="petitioner">Petitioner</Label>
                    <Input
                      id="petitioner"
                      placeholder="Petitioner name..."
                      value={searchParams.petitioner}
                      onChange={(e) => handleInputChange('petitioner', e.target.value)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="respondent">Respondent</Label>
                    <Input
                      id="respondent"
                      placeholder="Respondent name..."
                      value={searchParams.respondent}
                      onChange={(e) => handleInputChange('respondent', e.target.value)}
                    />
                  </div>

                  {/* Citation */}
                  <div>
                    <Label htmlFor="citation">Citation</Label>
                    <Input
                      id="citation"
                      placeholder="e.g., PLD 2024 SC 1"
                      value={searchParams.citation}
                      onChange={(e) => handleInputChange('citation', e.target.value)}
                    />
                  </div>

                  {/* Courts */}
                  <div>
                    <Label className="mb-2 block">Courts</Label>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {courts.map(court => (
                        <div key={court} className="flex items-center space-x-2">
                          <Checkbox
                            id={`court-${court}`}
                            checked={searchParams.courts.includes(court)}
                            onCheckedChange={() => handleCourtToggle(court)}
                          />
                          <Label htmlFor={`court-${court}`} className="text-sm">
                            {court}
                          </Label>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Case Types */}
                  <div>
                    <Label className="mb-2 block">Case Types</Label>
                    <div className="space-y-2">
                      {caseTypes.map(type => (
                        <div key={type} className="flex items-center space-x-2">
                          <Checkbox
                            id={`type-${type}`}
                            checked={searchParams.caseTypes.includes(type)}
                            onCheckedChange={() => handleCaseTypeToggle(type)}
                          />
                          <Label htmlFor={`type-${type}`} className="text-sm">
                            {type}
                          </Label>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Date Range */}
                  <div>
                    <Label className="mb-2 block">Date Range</Label>
                    <div className="space-y-2">
                      <Input
                        type="date"
                        placeholder="From"
                        value={searchParams.dateFrom}
                        onChange={(e) => handleInputChange('dateFrom', e.target.value)}
                      />
                      <Input
                        type="date"
                        placeholder="To"
                        value={searchParams.dateTo}
                        onChange={(e) => handleInputChange('dateTo', e.target.value)}
                      />
                    </div>
                  </div>

                  {/* Options */}
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="fullText"
                        checked={searchParams.fullText}
                        onCheckedChange={(checked) => handleInputChange('fullText', checked)}
                      />
                      <Label htmlFor="fullText">Full text search</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="headnotesOnly"
                        checked={searchParams.headnotesOnly}
                        onCheckedChange={(checked) => handleInputChange('headnotesOnly', checked)}
                      />
                      <Label htmlFor="headnotesOnly">Headnotes only</Label>
                    </div>
                  </div>

                  <Button
                    className="w-full"
                    onClick={handleSearch}
                    disabled={loading}
                  >
                    {loading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        <Search className="w-4 h-4 mr-2" />
                        Search
                      </>
                    )}
                  </Button>
                </div>
              </Card>
            </div>

            {/* Results */}
            <div className="lg:col-span-3">
              {results.length > 0 ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h2 className="text-lg font-semibold">
                      {results.length} Results Found
                    </h2>
                  </div>
                  
                  {results.map(result => (
                    <Card key={result.id} className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="secondary">{result.court}</Badge>
                            <Badge variant="outline">{result.type}</Badge>
                            <span className="text-sm text-slate-500">
                              <Calendar className="w-3 h-3 inline mr-1" />
                              {new Date(result.date).toLocaleDateString()}
                            </span>
                          </div>
                          <h3 className="text-lg font-semibold text-slate-900">
                            {result.title}
                          </h3>
                          <p className="text-slate-600 text-sm mt-1">{result.citation}</p>
                          <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="font-medium">Judge:</span> {result.judge}
                            </div>
                            <div>
                              <span className="font-medium">Petitioner:</span> {result.petitioner}
                            </div>
                            <div>
                              <span className="font-medium">Respondent:</span> {result.respondent}
                            </div>
                          </div>
                          <p className="text-slate-700 mt-3">{result.summary}</p>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              ) : (
                <Card className="p-12 text-center">
                  <BookOpen className="w-12 h-12 mx-auto mb-4 text-slate-400" />
                  <p className="text-slate-600">No results yet. Use the filters to search for cases.</p>
                </Card>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default AdvancedCaselawSearch;
