import React, { useState, useEffect } from 'react';
import { journalService } from '../services/journalService';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { useToast } from '../components/ui/use-toast';
import { Calendar, BookOpen, Download, Loader2, ChevronLeft, ChevronRight } from 'lucide-react';
import { Helmet } from 'react-helmet';

const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

const YEARS = Array.from({ length: 10 }, (_, i) => 2016 + i);

const MonthlyJournalsPage = () => {
  const { toast } = useToast();
  const [journals, setJournals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth());
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchJournals();
  }, [selectedMonth, selectedYear, currentPage]);

  const fetchJournals = async () => {
    try {
      setLoading(true);
      const response = await journalService.getJournals({
        month: selectedMonth + 1,
        year: selectedYear,
        page: currentPage,
        limit: 20
      });
      setJournals(response.journals || []);
      setTotalPages(response.totalPages || 1);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load journals",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (journalId) => {
    try {
      await journalService.downloadJournal(journalId);
      toast({
        title: "Download Started",
        description: "Journal download has started"
      });
    } catch (error) {
      toast({
        title: "Download Failed",
        description: error.message,
        variant: "destructive"
      });
    }
  };

  const filteredJournals = journals.filter(journal =>
    journal.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    journal.citation?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <>
      <Helmet>
        <title>Monthly Journals | Pakistan Law App</title>
      </Helmet>

      <div className="min-h-screen bg-slate-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-900">Monthly Journals</h1>
            <p className="text-slate-600 mt-2">Browse legal journals by month and year</p>
          </div>

          {/* Filters */}
          <Card className="p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Month</label>
                <Select
                  value={String(selectedMonth)}
                  onValueChange={(value) => {
                    setSelectedMonth(parseInt(value));
                    setCurrentPage(1);
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select month" />
                  </SelectTrigger>
                  <SelectContent>
                    {MONTHS.map((month, index) => (
                      <SelectItem key={index} value={String(index)}>
                        {month}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Year</label>
                <Select
                  value={String(selectedYear)}
                  onValueChange={(value) => {
                    setSelectedYear(parseInt(value));
                    setCurrentPage(1);
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select year" />
                  </SelectTrigger>
                  <SelectContent>
                    {YEARS.map(year => (
                      <SelectItem key={year} value={String(year)}>
                        {year}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="md:col-span-2">
                <label className="text-sm font-medium mb-2 block">Search</label>
                <Input
                  placeholder="Search journals..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>
          </Card>

          {/* Results */}
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-slate-400" />
            </div>
          ) : filteredJournals.length > 0 ? (
            <>
              <div className="grid gap-4">
                {filteredJournals.map(journal => (
                  <Card key={journal.id} className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge variant="secondary">
                            <Calendar className="w-3 h-3 mr-1" />
                            {MONTHS[journal.month - 1]} {journal.year}
                          </Badge>
                          <Badge variant="outline">{journal.court}</Badge>
                        </div>
                        <h3 className="text-lg font-semibold text-slate-900">
                          {journal.title}
                        </h3>
                        <p className="text-slate-600 text-sm mt-1">
                          {journal.citation}
                        </p>
                        <p className="text-slate-700 mt-3 line-clamp-3">
                          {journal.summary}
                        </p>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDownload(journal.id)}
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Download
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-center gap-4 mt-8">
                  <Button
                    variant="outline"
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                  >
                    <ChevronLeft className="w-4 h-4 mr-2" />
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
                    <ChevronRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              )}
            </>
          ) : (
            <Card className="p-12 text-center">
              <BookOpen className="w-12 h-12 mx-auto mb-4 text-slate-400" />
              <p className="text-slate-600">No journals found for the selected period</p>
            </Card>
          )}
        </div>
      </div>
    </>
  );
};

export default MonthlyJournalsPage;
