import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Link2, Search, Loader2, Scale, ChevronRight, BookOpen, X } from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import SidebarLayout from '../components/SidebarLayout';
import api from '../api/api';

const StatuteCaseLinksPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [statutes, setStatutes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [selectedStatute, setSelectedStatute] = useState(searchParams.get('statute') || null);
  const [sections, setSections] = useState([]);
  const [sectionsLoading, setSectionsLoading] = useState(false);

  useEffect(() => { fetchStatutes(); }, []);
  useEffect(() => { if (selectedStatute) fetchSections(selectedStatute); }, [selectedStatute]);

  const fetchStatutes = async () => {
    setLoading(true);
    try {
      const response = await api.pls.getStatutes({ limit: 500 });
      setStatutes(response.data || []);
    } catch (e) {
      setStatutes([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchSections = async (statuteName) => {
    setSectionsLoading(true);
    try {
      const response = await api.pls.getStatuteSections({ statute: statuteName });
      setSections(response.data || []);
    } catch (e) {
      setSections([]);
    } finally {
      setSectionsLoading(false);
    }
  };

  const filteredStatutes = statutes.filter(s => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (s.name && s.name.toLowerCase().includes(q)) ||
           (s.category && s.category.toLowerCase().includes(q)) ||
           (s.year && String(s.year).includes(q));
  });

  const handleStatuteClick = (name) => {
    setSelectedStatute(name);
    setSearchParams({ statute: name });
  };

  const handleBack = () => {
    setSelectedStatute(null);
    setSections([]);
    setSearchParams({ q: searchQuery });
  };

  if (selectedStatute) {
    return (
      <SidebarLayout>
        <div className="min-h-screen bg-background" data-testid="statute-sections-page">
          <div className="bg-white dark:bg-card border-b border-border">
            <div className="max-w-screen-2xl mx-auto px-6 py-4">
              <Button variant="ghost" onClick={handleBack} className="mb-3"><X size={16} className="mr-2" /> Close</Button>
              <h1 className="text-2xl font-bold text-foreground flex items-center gap-3"><BookOpen className="text-primary" size={24} /> {selectedStatute}</h1>
              <p className="text-sm text-muted-foreground mt-2">{sections.length} sections found</p>
            </div>
          </div>
          <div className="max-w-screen-2xl mx-auto px-6 py-6">
            <div className="bg-white dark:bg-card rounded-xl border border-border overflow-hidden">
              {sectionsLoading ? (
                <div className="p-12 text-center"><Loader2 size={32} className="animate-spin text-primary mx-auto mb-3" /><p className="text-muted-foreground">Loading sections...</p></div>
              ) : sections.length === 0 ? (
                <div className="p-12 text-center"><Scale size={48} className="text-muted-foreground mx-auto mb-3" /><p className="text-muted-foreground">No sections found</p></div>
              ) : (
                <div className="divide-y divide-border">
                  {sections.map((section, idx) => (
                    <div key={idx} className="p-4 hover:bg-accent/40 transition-colors">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1"><Badge variant="outline">{section.section || section.number || idx + 1}</Badge>{section.title && <span className="font-semibold text-foreground">{section.title}</span>}</div>
                          {section.content && <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{section.content.substring(0, 200)}...</p>}
                          {section.cases && section.cases.length > 0 && (
                            <div className="mt-2 flex flex-wrap gap-1.5">
                              {section.cases.slice(0, 5).map((c, i) => (
                                <Badge key={i} variant="secondary" className="text-xs cursor-pointer hover:bg-primary/10" onClick={() => c.case_id && navigate(`/case/${c.case_id}`)}>{c.case_name || c.citation || `Case ${i + 1}`}</Badge>
                              ))}
                              {section.cases.length > 5 && <Badge variant="outline" className="text-xs">+{section.cases.length - 5} more</Badge>}
                            </div>
                          )}
                        </div>
                        {section.cases && section.cases.length > 0 && <Badge className="text-xs">{section.cases.length} cases</Badge>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </SidebarLayout>
    );
  }

  return (
    <SidebarLayout>
      <div className="min-h-screen bg-background" data-testid="statute-case-links-page">
        <div className="bg-white dark:bg-card border-b border-border">
          <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-6">
            <h1 className="text-2xl sm:text-3xl font-serif font-bold text-foreground flex items-center gap-3"><Link2 className="text-primary" size={24} /> Statute-Case Links</h1>
            <p className="text-sm text-muted-foreground mt-2">{statutes.length} statutes • Click to view sections and linked cases</p>
          </div>
        </div>
        <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-8">
          <div className="flex gap-3 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
              <Input placeholder="Search statutes..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="pl-10" />
            </div>
          </div>
          <div className="bg-white dark:bg-card rounded-xl border border-border overflow-hidden">
            {loading ? (
              <div className="p-12 text-center"><Loader2 size={32} className="animate-spin text-primary mx-auto mb-3" /><p className="text-muted-foreground">Loading...</p></div>
            ) : filteredStatutes.length === 0 ? (
              <div className="p-16 text-center"><BookOpen size={48} className="text-muted-foreground mx-auto mb-4" /><p className="text-muted-foreground font-medium">No statutes found</p></div>
            ) : (
              <div className="divide-y divide-border">
                {filteredStatutes.map((statute, idx) => (
                  <div key={idx} className="p-4 hover:bg-accent/40 transition-colors cursor-pointer" onClick={() => handleStatuteClick(statute.name)}>
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1"><span className="font-semibold text-primary">{statute.name}</span>{statute.year && <Badge variant="outline" className="text-xs">{statute.year}</Badge>}{statute.category && <Badge variant="secondary" className="text-xs">{statute.category}</Badge>}</div>
                        {statute.description && <p className="text-xs text-muted-foreground line-clamp-1">{statute.description}</p>}
                      </div>
                      <ChevronRight size={16} className="text-muted-foreground" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </SidebarLayout>
  );
};

export default StatuteCaseLinksPage;
