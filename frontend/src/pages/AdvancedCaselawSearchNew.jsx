import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { Checkbox } from '../components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { useToast } from '../components/ui/use-toast';
import { Search, Loader2, Filter, Calendar, BookOpen, ChevronDown, ChevronUp } from 'lucide-react';
import { Helmet } from 'react-helmet';

const AdvancedCaselawSearchNew = () => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  const [searchParams, setSearchParams] = useState({
    keywords: '',
    title: '',
    citation: '',
    court: '',
    judge: '',
    petitioner: '',
    respondent: '',
    advocate: '',
    dateFrom: '',
    dateTo: '',
    caseType: '',
    fullText: false,
    headnotes: true,
    citedStatutes: ''
  });

  const courts = [
    'All Courts',
    'Supreme Court',
    'Lahore High Court',
    'Sindh High Court',
    'Peshawar High Court',
    'Balochistan High Court',
    'Islamabad High Court',
    'Federal Shariat Court'
  ];

  const caseTypes = [
    'All Types',
    'Civil',
    'Criminal',
    'Constitutional',
    'Commercial',
    'Family',
    'Labor'
  ];

  const handleSearch = async () => {
    try {
      setLoading(true);
      
      // Simulate search
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockResults = [
        {
          id: 1,
          title: "Constitutional Petition No. 45 of 2024",
          citation: "PLD 2024 SC 120",
          court: "Supreme Court",
          date: "2024-03-15",
          judge: "Justice Ali Ahmad",
          petitioner: "Muhammad Khan",
          respondent: "Federation of Pakistan",
          type: "Constitutional",
          summary: "Challenge to the constitutional validity of recent amendments...",
          relevance: 95
        },
        {
          id: 2,
          title: "Civil Appeal No. 234 of 2023",
          citation: "2024 CLC 89",
          court: "Lahore High Court",
          date: "2024-02-28",
          judge: "Justice Sarah Bukhari",
          petitioner: "ABC Corporation",
          respondent: "XYZ Limited",
          type: "Civil",
          summary: "Property dispute and interpretation of Transfer of Property Act...",
          relevance: 88
        }
      ];
      
      setResults(mockResults);
      
      toast({
        title: "Search Complete",
        description: `Found ${mockResults.length} matching cases`
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
            <p className="text-slate-600 mt-2">Search with precision using multiple criteria</p>
          </div>

          <Card className="p-6 mb-6">
            {/* Basic Search */}
            <div className="space-y-4">
              <div>
                <Label htmlFor="keywords">Keywords</Label>
                <div className="flex gap-2">
                  <Input
                    id="keywords"
                    placeholder="Enter search keywords..."
                    value={searchParams.keywords}
                    onChange={(e) => handleInputChange('keywords', e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  />
                  <Button onClick={handleSearch} disabled={loading}>
                    {loading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Search className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </div>

              {/* Toggle Advanced */}
              <Button
                variant="outline"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="w-full"
              >
                <Filter className="w-4 h-4 mr-2" />
                {showAdvanced ? 'Hide' : 'Show'} Advanced Filters
                {showAdvanced ? (
                  <ChevronUp className="w-4 h-4 ml-2" />
                ) : (
                  <ChevronDown className="w-4 h-4 ml-2" />
                )}
              </Button>

              {/* Advanced Filters */}
              {showAdvanced && (
                <div className="space-y-4 pt-4 border-t">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="title">Case Title</Label>
                      <Input
                        id="title"
                        placeholder="Case title..."
                        value={searchParams.title}
                        onChange={(e) => handleInputChange('title', e.target.value)}
                      />
                    </div>
                    <div>
                      <Label htmlFor="citation">Citation</Label>
                      <Input
                        id="citation"
                        placeholder="e.g., PLD 2024 SC 1"
                        value={searchParams.citation}
                        onChange={(e) => handleInputChange('citation', e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="court">Court</Label>
                      <Select
                        value={searchParams.court}
                        onValueChange={(value) => handleInputChange('court', value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select Court" />
                        </SelectTrigger>
                        <SelectContent>
                          {courts.map(court => (
                            <SelectItem key={court} value={court}>{court}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="caseType">Case Type</Label>
                      <Select
                        value={searchParams.caseType}
                        onValueChange={(value) => handleInputChange('caseType', value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select Type" />
                        </SelectTrigger>
                        <SelectContent>
                          {caseTypes.map(type => (
                            <SelectItem key={type} value={type}>{type}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="judge">Judge</Label>
                      <Input
                        id="judge"
                        placeholder="Judge name..."
                        value={searchParams.judge}
                        onChange={(e) => handleInputChange('judge', e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="dateFrom">Date From</Label>
                      <Input
                        id="dateFrom"
                        type="date"
                        value={searchParams.dateFrom}
                        onChange={(e) => handleInputChange('dateFrom', e.target.value)}
                      />
                    </div>
                    <div>
                      <Label htmlFor="dateTo">Date To</Label>
                      <Input
                        id="dateTo"
                        type="date"
                        value={searchParams.dateTo}
                        onChange={(e) => handleInputChange('dateTo', e.target.value)}
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="citedStatutes">Cited Statutes</Label>
                    <Input
                      id="citedStatutes"
                      placeholder="Statutes cited in the case..."
                      value={searchParams.citedStatutes}
                      onChange={(e) => handleInputChange('citedStatutes', e.target.value)}
                    />
                  </div>

                  <div className="flex gap-4">
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
                        id="headnotes"
                        checked={searchParams.headnotes}
                        onCheckedChange={(checked) => handleInputChange('headnotes', checked)}
                      />
                      <Label htmlFor="headnotes">Search headnotes</Label>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </Card>

          {/* Results */}
          {results.length > 0 ? (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold">{results.length} Results Found</h2>
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
                      <h3 className="text-lg font-semibold text-slate-900">{result.title}</h3>
                      <p className="text-slate-600 text-sm mt-1">{result.citation}</p>
                      <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
                        <p><span className="font-medium">Judge:</span> {result.judge}</p>
                        <p><span className="font-medium">Petitioner:</span> {result.petitioner}</p>
                        <p><span className="font-medium">Respondent:</span> {result.respondent}</p>
                      </div>
                      <p className="text-slate-700 mt-2">{result.summary}</p>
                    </div>
                    <div className="ml-4 text-center">
                      <div className="text-2xl font-bold text-blue-600">{result.relevance}%</div>
                      <div className="text-xs text-slate-500">relevance</div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-12 text-center">
              <BookOpen className="w-12 h-12 mx-auto mb-4 text-slate-400" />
              <p className="text-slate-600">No results found. Try adjusting your search criteria.</p>
            </Card>
          )}
        </div>
      </div>
    </>
  );
};

export default AdvancedCaselawSearchNew;
