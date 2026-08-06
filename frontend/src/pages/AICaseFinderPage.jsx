import React, { useState } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';
import { useToast } from '../components/ui/use-toast';
import { Search, Loader2, Sparkles, FileText } from 'lucide-react';
import { Helmet } from 'react-helmet';

const AICaseFinderPage = () => {
  const { toast } = useToast();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [suggestions, setSuggestions] = useState([]);

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
      
      // Simulate AI search
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Generate mock results
      const mockResults = generateMockResults(query);
      setResults(mockResults);
      
      // Generate suggestions
      const mockSuggestions = generateSuggestions(query);
      setSuggestions(mockSuggestions);
      
      toast({
        title: "Search Complete",
        description: `Found ${mockResults.length} relevant cases`
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

  const generateMockResults = (query) => {
    const keywords = query.toLowerCase().split(' ');
    
    const mockCases = [
      {
        id: 1,
        title: "Constitutional Validity of Land Reforms",
        citation: "PLD 2020 SC 1",
        court: "Supreme Court",
        date: "2020-01-15",
        relevance: 95,
        summary: "This case deals with the constitutional validity of land reform measures...",
        matchedTerms: ["constitutional", "land", "reforms"]
      },
      {
        id: 2,
        title: "Property Rights and Inheritance",
        citation: "2021 CLC 45",
        court: "Lahore High Court",
        date: "2021-03-20",
        relevance: 88,
        summary: "Interpretation of property rights under Islamic law and statutory provisions...",
        matchedTerms: ["property", "inheritance"]
      },
      {
        id: 3,
        title: "Land Acquisition Act Interpretation",
        citation: "PLD 2019 Lah 123",
        court: "Lahore High Court",
        date: "2019-06-10",
        relevance: 82,
        summary: "Interpretation of the Land Acquisition Act regarding compensation...",
        matchedTerms: ["land", "acquisition"]
      }
    ];
    
    return mockCases.filter(c => 
      c.matchedTerms.some(term => 
        keywords.some(kw => term.includes(kw))
      )
    );
  };

  const generateSuggestions = (query) => {
    const baseTerms = [
      "property rights",
      "constitutional law",
      "land disputes",
      "inheritance law",
      "civil procedure"
    ];
    
    return baseTerms.map(term => ({
      term,
      confidence: Math.floor(Math.random() * 30) + 70
    }));
  };

  return (
    <>
      <Helmet>
        <title>AI Case Finder | Pakistan Law App</title>
      </Helmet>

      <div className="min-h-screen bg-slate-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-slate-900">AI Case Finder</h1>
            <p className="text-slate-600 mt-2">
              Find relevant cases using AI-powered natural language search
            </p>
          </div>

          {/* Search */}
          <Card className="p-6 mb-6">
            <div className="space-y-4">
              <div>
                <Label htmlFor="query">Describe your legal issue</Label>
                <Textarea
                  id="query"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Describe the facts, legal issues, or keywords related to your case..."
                  rows={4}
                />
              </div>
              <Button
                onClick={handleSearch}
                disabled={loading}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Searching...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Find Relevant Cases
                  </>
                )}
              </Button>
            </div>
          </Card>

          {/* Suggestions */}
          {suggestions.length > 0 && (
            <Card className="p-6 mb-6">
              <h3 className="text-lg font-semibold mb-4">Related Topics</h3>
              <div className="flex flex-wrap gap-2">
                {suggestions.map((suggestion, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    onClick={() => setQuery(suggestion.term)}
                  >
                    {suggestion.term}
                    <span className="ml-2 text-xs text-slate-500">
                      {suggestion.confidence}%
                    </span>
                  </Button>
                ))}
              </div>
            </Card>
          )}

          {/* Results */}
          {results.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Search Results</h3>
              {results.map(result => (
                <Card key={result.id} className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold text-lg text-slate-900">
                        {result.title}
                      </h4>
                      <p className="text-slate-600 text-sm mt-1">
                        {result.citation} | {result.court} | {new Date(result.date).toLocaleDateString()}
                      </p>
                      <p className="text-slate-700 mt-3">
                        {result.summary}
                      </p>
                      <div className="flex gap-2 mt-3">
                        {result.matchedTerms.map((term, i) => (
                          <span
                            key={i}
                            className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                          >
                            {term}
                          </span>
                        ))}
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
              <p className="text-slate-600">No cases found matching your query</p>
              <p className="text-slate-500 text-sm mt-2">
                Try using different keywords or a more specific description
              </p>
            </Card>
          )}
        </div>
      </div>
    </>
  );
};

export default AICaseFinderPage;
