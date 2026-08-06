import React, { useState } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { useToast } from '../components/ui/use-toast';
import { Search, Loader2, BookOpen, FileText, Scale } from 'lucide-react';
import { Helmet } from 'react-helmet';

const SearchPage = () => {
  const { toast } = useToast();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState({
    cases: [],
    statutes: [],
    articles: []
  });
  const [activeTab, setActiveTab] = useState('cases');

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
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const mockResults = {
        cases: [
          {
            id: 1,
            title: "Constitutional Validity of Land Reforms",
            citation: "PLD 2023 SC 1",
            court: "Supreme Court",
            date: "2023-01-15",
            relevance: 98
          },
          {
            id: 2,
            title: "Property Rights and Inheritance",
            citation: "2023 CLC 45",
            court: "Lahore High Court",
            date: "2023-03-20",
            relevance: 85
          }
        ],
        statutes: [
          {
            id: 1,
            title: "Constitution of Pakistan",
            citation: "PLD 1973 Central Statutes 1",
            year: 1973,
            relevance: 92
          },
          {
            id: 2,
            title: "Pakistan Penal Code",
            citation: "Act XLV of 1860",
            year: 1860,
            relevance: 78
          }
        ],
        articles: [
          {
            id: 1,
            title: "Understanding Property Law in Pakistan",
            author: "Dr. Ahmed Khan",
            journal: "Pakistan Law Review",
            year: 2023,
            relevance: 88
          }
        ]
      };

      setResults(mockResults);
      
      toast({
        title: "Search Complete",
        description: `Found ${mockResults.cases.length + mockResults.statutes.length + mockResults.articles.length} results`
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

  const totalResults = results.cases.length + results.statutes.length + results.articles.length;

  return (
    <>
      <Helmet>
        <title>Search | Pakistan Law App</title>
      </Helmet>

      <div className="min-h-screen bg-slate-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-slate-900">Search</h1>
            <p className="text-slate-600 mt-2">
              Search cases, statutes, and legal articles
            </p>
          </div>

          {/* Search Box */}
          <Card className="p-6 mb-6">
            <div className="relative">
              <Input
                placeholder="Search cases, statutes, articles..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                className="w-full pr-32 h-12 text-lg"
              />
              <Button
                className="absolute right-0 top-0 h-full"
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

          {/* Results */}
          {totalResults > 0 && (
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="mb-6">
                <TabsTrigger value="cases">
                  <Scale className="w-4 h-4 mr-2" />
                  Cases ({results.cases.length})
                </TabsTrigger>
                <TabsTrigger value="statutes">
                  <BookOpen className="w-4 h-4 mr-2" />
                  Statutes ({results.statutes.length})
                </TabsTrigger>
                <TabsTrigger value="articles">
                  <FileText className="w-4 h-4 mr-2" />
                  Articles ({results.articles.length})
                </TabsTrigger>
              </TabsList>

              <TabsContent value="cases">
                <div className="space-y-4">
                  {results.cases.map(case_ => (
                    <Card key={case_.id} className="p-6">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="secondary">{case_.court}</Badge>
                            <span className="text-sm text-slate-500">{case_.date}</span>
                          </div>
                          <h3 className="text-lg font-semibold text-slate-900">{case_.title}</h3>
                          <p className="text-slate-600 text-sm mt-1">{case_.citation}</p>
                        </div>
                        <div className="text-2xl font-bold text-blue-600">{case_.relevance}%</div>
                      </div>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="statutes">
                <div className="space-y-4">
                  {results.statutes.map(statute => (
                    <Card key={statute.id} className="p-6">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="secondary">Statute</Badge>
                            <span className="text-sm text-slate-500">{statute.year}</span>
                          </div>
                          <h3 className="text-lg font-semibold text-slate-900">{statute.title}</h3>
                          <p className="text-slate-600 text-sm mt-1">{statute.citation}</p>
                        </div>
                        <div className="text-2xl font-bold text-blue-600">{statute.relevance}%</div>
                      </div>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="articles">
                <div className="space-y-4">
                  {results.articles.map(article => (
                    <Card key={article.id} className="p-6">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="secondary">Article</Badge>
                            <span className="text-sm text-slate-500">{article.year}</span>
                          </div>
                          <h3 className="text-lg font-semibold text-slate-900">{article.title}</h3>
                          <p className="text-slate-600 text-sm mt-1">{article.author} - {article.journal}</p>
                        </div>
                        <div className="text-2xl font-bold text-blue-600">{article.relevance}%</div>
                      </div>
                    </Card>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          )}

          {totalResults === 0 && !loading && query && (
            <Card className="p-12 text-center">
              <Search className="w-12 h-12 mx-auto mb-4 text-slate-400" />
              <p className="text-slate-600">No results found</p>
              <p className="text-slate-500 text-sm mt-2">Try a different search query</p>
            </Card>
          )}
        </div>
      </div>
    </>
  );
};

export default SearchPage;
