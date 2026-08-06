import React, { useState, useEffect } from 'react';
import { statuteService } from '../services/statuteService';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { useToast } from '../components/ui/use-toast';
import { Search, BookOpen, Loader2, ChevronRight, ExternalLink } from 'lucide-react';
import { Helmet } from 'react-helmet';

const statuteCategories = [
  { id: 'constitutional', name: 'Constitutional Law' },
  { id: 'civil', name: 'Civil Law' },
  { id: 'criminal', name: 'Criminal Law' },
  { id: 'commercial', name: 'Commercial Law' },
  { id: 'family', name: 'Family Law' },
  { id: 'labor', name: 'Labor Law' },
  { id: 'property', name: 'Property Law' },
  { id: 'tax', name: 'Tax Law' },
  { id: 'environmental', name: 'Environmental Law' },
  { id: 'banking', name: 'Banking Law' }
];

const statuteTypes = [
  { id: 'act', name: 'Act of Parliament' },
  { id: 'ordinance', name: 'Ordinance' },
  { id: 'regulation', name: 'Regulation' },
  { id: 'rule', name: 'Rule' },
  { id: 'order', name: 'Order' },
  { id: 'notification', name: 'Notification' }
];

const StatuteExplorerPage = () => {
  const { toast } = useToast();
  const [statutes, setStatutes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [selectedStatute, setSelectedStatute] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchStatutes();
  }, [selectedCategory, selectedType, currentPage]);

  const fetchStatutes = async () => {
    try {
      setLoading(true);
      const params = {
        page: currentPage,
        limit: 20
      };
      
      if (selectedCategory) {
        params.category = selectedCategory;
      }
      
      if (selectedType) {
        params.type = selectedType;
      }
      
      const response = await statuteService.getStatutes(params);
      setStatutes(response.statutes || []);
      setTotalPages(response.totalPages || 1);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load statutes",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchStatutes();
      return;
    }

    try {
      setLoading(true);
      const response = await statuteService.searchStatutes(searchQuery);
      setStatutes(response.statutes || []);
      setTotalPages(1);
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

  const handleStatuteSelect = async (statuteId) => {
    try {
      setLoading(true);
      const statute = await statuteService.getStatuteById(statuteId);
      setSelectedStatute(statute);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load statute details",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const filteredStatutes = statutes.filter(statute =>
    statute.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    statute.citation?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <>
      <Helmet>
        <title>Statute Explorer | Pakistan Law App</title>
      </Helmet>

      <div className="min-h-screen bg-slate-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-900">Statute Explorer</h1>
            <p className="text-slate-600 mt-2">Browse and search Pakistani statutes and legislation</p>
          </div>

          {/* Search and Filters */}
          <Card className="p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="md:col-span-2">
                <label className="text-sm font-medium mb-2 block">Search Statutes</label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Search by title or citation..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  />
                  <Button onClick={handleSearch}>
                    <Search className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Category</label>
                <Select
                  value={selectedCategory}
                  onValueChange={(value) => {
                    setSelectedCategory(value);
                    setCurrentPage(1);
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="All Categories" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All Categories</SelectItem>
                    {statuteCategories.map(cat => (
                      <SelectItem key={cat.id} value={cat.id}>
                        {cat.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Type</label>
                <Select
                  value={selectedType}
                  onValueChange={(value) => {
                    setSelectedType(value);
                    setCurrentPage(1);
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="All Types" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All Types</SelectItem>
                    {statuteTypes.map(type => (
                      <SelectItem key={type.id} value={type.id}>
                        {type.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Statute List */}
            <div className="lg:col-span-2">
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-slate-400" />
                </div>
              ) : filteredStatutes.length > 0 ? (
                <div className="space-y-4">
                  {filteredStatutes.map(statute => (
                    <Card
                      key={statute.id}
                      className={`p-6 cursor-pointer transition-all hover:shadow-md ${
                        selectedStatute?.id === statute.id ? 'ring-2 ring-blue-500' : ''
                      }`}
                      onClick={() => handleStatuteSelect(statute.id)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="secondary">
                              {statuteTypes.find(t => t.id === statute.type)?.name || statute.type}
                            </Badge>
                            <Badge variant="outline">
                              {statuteCategories.find(c => c.id === statute.category)?.name || statute.category}
                            </Badge>
                          </div>
                          <h3 className="text-lg font-semibold text-slate-900">
                            {statute.title}
                          </h3>
                          <p className="text-slate-600 text-sm mt-1">
                            {statute.citation}
                          </p>
                          <p className="text-slate-700 mt-3 line-clamp-2">
                            {statute.description}
                          </p>
                          <div className="flex items-center gap-4 mt-3 text-sm text-slate-500">
                            <span>Enacted: {statute.year || 'N/A'}</span>
                            <span>Sections: {statute.sections_count || 0}</span>
                          </div>
                        </div>
                        <ChevronRight className="w-5 h-5 text-slate-400 mt-2" />
                      </div>
                    </Card>
                  ))}

                  {/* Pagination */}
                  {totalPages > 1 && (
                    <div className="flex items-center justify-center gap-4 mt-8">
                      <Button
                        variant="outline"
                        onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                        disabled={currentPage === 1}
                      >
                        Previous
                      </Button>
                      <span className="text-slate-600">
                        Page {currentPage} of {totalPages}
                      </span>
                      <Button
                        variant="outline"
                        onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                        disabled={currentPage === totalPages}
                      >
                        Next
                      </Button>
                    </div>
                  )}
                </div>
              ) : (
                <Card className="p-12 text-center">
                  <BookOpen className="w-12 h-12 mx-auto mb-4 text-slate-400" />
                  <p className="text-slate-600">No statutes found</p>
                </Card>
              )}
            </div>

            {/* Statute Details */}
            <div>
              {selectedStatute ? (
                <Card className="p-6 sticky top-4">
                  <h2 className="text-xl font-bold text-slate-900 mb-4">
                    {selectedStatute.title}
                  </h2>
                  
                  <div className="space-y-3 mb-6">
                    <div>
                      <span className="text-sm font-medium text-slate-500">Citation</span>
                      <p className="text-slate-900">{selectedStatute.citation}</p>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-slate-500">Type</span>
                      <p className="text-slate-900">
                        {statuteTypes.find(t => t.id === selectedStatute.type)?.name || selectedStatute.type}
                      </p>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-slate-500">Category</span>
                      <p className="text-slate-900">
                        {statuteCategories.find(c => c.id === selectedStatute.category)?.name || selectedStatute.category}
                      </p>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-slate-500">Year</span>
                      <p className="text-slate-900">{selectedStatute.year || 'N/A'}</p>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-slate-500">Status</span>
                      <Badge variant={selectedStatute.status === 'active' ? 'default' : 'secondary'}>
                        {selectedStatute.status || 'Unknown'}
                      </Badge>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Button className="w-full">
                      <ExternalLink className="w-4 h-4 mr-2" />
                      View Full Text
                    </Button>
                    <Button variant="outline" className="w-full">
                      <BookOpen className="w-4 h-4 mr-2" />
                      Download PDF
                    </Button>
                  </div>

                  {selectedStatute.sections && selectedStatute.sections.length > 0 && (
                    <div className="mt-6">
                      <h3 className="font-semibold text-slate-900 mb-3">Sections</h3>
                      <div className="space-y-2 max-h-64 overflow-y-auto">
                        {selectedStatute.sections.map(section => (
                          <div
                            key={section.id}
                            className="p-3 bg-slate-50 rounded-lg text-sm"
                          >
                            <span className="font-medium">{section.number}</span>
                            <span className="text-slate-600 ml-2">{section.title}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </Card>
              ) : (
                <Card className="p-6 text-center">
                  <BookOpen className="w-12 h-12 mx-auto mb-4 text-slate-400" />
                  <p className="text-slate-600">Select a statute to view details</p>
                </Card>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default StatuteExplorerPage;
