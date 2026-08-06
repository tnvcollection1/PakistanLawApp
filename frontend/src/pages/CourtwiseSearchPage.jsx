import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Search, Loader2, Building2, ChevronRight, BarChart3, ArrowUpDown, Calendar, MapPin } from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import SidebarLayout from '../components/SidebarLayout';
import api from '../api/api';

const CourtwiseSearchPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [courts, setCourts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [sortBy, setSortBy] = useState('name');
  const [sortDir, setSortDir] = useState('asc');

  useEffect(() => {
    fetchCourts();
  }, []);

  const fetchCourts = async () => {
    setLoading(true);
    try {
      const response = await api.courts.list({ limit: 200 });
      setCourts(response.data || []);
    } catch (e) {
      console.error('Error fetching courts:', e);
      setCourts([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setSearchParams({ q: searchQuery });
  };

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortDir('asc');
    }
  };

  const filteredCourts = courts.filter(c => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (c.name && c.name.toLowerCase().includes(q)) ||
           (c.type && c.type.toLowerCase().includes(q)) ||
           (c.location && c.location.toLowerCase().includes(q));
  }).sort((a, b) => {
    let valA = a[sortBy] || '';
    let valB = b[sortBy] || '';
    if (typeof valA === 'string') valA = valA.toLowerCase();
    if (typeof valB === 'string') valB = valB.toLowerCase();
    if (valA < valB) return sortDir === 'asc' ? -1 : 1;
    if (valA > valB) return sortDir === 'asc' ? 1 : -1;
    return 0;
  });

  return (
    <SidebarLayout>
      <div className="min-h-screen bg-background" data-testid="courtwise-search-page">
        <div className="bg-white dark:bg-card border-b border-border">
          <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-6">
            <h1 className="text-2xl sm:text-3xl font-serif font-bold text-foreground flex items-center gap-3">
              <Building2 className="text-primary" size={24} />
              Courtwise Search
            </h1>
            <p className="text-sm text-muted-foreground mt-2">{courts.length} courts • Browse cases by court</p>
          </div>
        </div>

        <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-8">
          {/* Search */}
          <div className="flex gap-3 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
              <Input placeholder="Search courts by name, type, or location..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleSearch()} className="pl-10" />
            </div>
            <Button onClick={handleSearch}>Search</Button>
          </div>

          {/* Sort Controls */}
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xs text-muted-foreground">Sort by:</span>
            {[{ label: 'Name', field: 'name' }, { label: 'Cases', field: 'case_count' }, { label: 'Type', field: 'type' }].map(s => (
              <Button key={s.field} variant="ghost" size="sm" onClick={() => handleSort(s.field)} className={sortBy === s.field ? 'text-primary bg-primary/5' : ''}>
                <ArrowUpDown size={12} className="mr-1" /> {s.label}
              </Button>
            ))}
          </div>

          {/* Courts Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {loading ? (
              <div className="col-span-full p-12 text-center"><Loader2 size={32} className="animate-spin text-primary mx-auto mb-3" /><p className="text-muted-foreground">Loading courts...</p></div>
            ) : filteredCourts.length === 0 ? (
              <div className="col-span-full p-16 text-center"><Building2 size={48} className="text-muted-foreground mx-auto mb-4" /><p className="text-muted-foreground font-medium">No courts found</p></div>
            ) : (
              filteredCourts.map((court, idx) => (
                <div key={idx} className="bg-white dark:bg-card rounded-xl border border-border p-5 hover:border-primary/30 hover:shadow-sm transition-all cursor-pointer" onClick={() => navigate(`/search?court=${encodeURIComponent(court.name)}`)}>
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="font-semibold text-foreground">{court.name}</h3>
                    <ChevronRight size={16} className="text-muted-foreground" />
                  </div>
                  <div className="space-y-1.5">
                    {court.type && <p className="text-xs text-muted-foreground flex items-center gap-1"><Building2 size={12} /> {court.type}</p>}
                    {court.location && <p className="text-xs text-muted-foreground flex items-center gap-1"><MapPin size={12} /> {court.location}</p>}
                    {court.case_count !== undefined && <p className="text-xs text-muted-foreground flex items-center gap-1"><BarChart3 size={12} /> {court.case_count.toLocaleString()} cases</p>}
                    {court.last_case_date && <p className="text-xs text-muted-foreground flex items-center gap-1"><Calendar size={12} /> Last: {court.last_case_date}</p>}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </SidebarLayout>
  );
};

export default CourtwiseSearchPage;
