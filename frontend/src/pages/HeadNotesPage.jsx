import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { caseService } from '../services/caseService';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Separator } from '../components/ui/separator';
import { ArrowLeft, Printer, Download } from 'lucide-react';
import { useToast } from '../components/ui/use-toast';
import { Helmet } from 'react-helmet';

const HeadNotesPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCase = async () => {
      try {
        setLoading(true);
        const data = await caseService.getCaseById(id);
        setCaseData(data);
      } catch (err) {
        setError(err.message);
        toast({
          title: "Error",
          description: "Failed to load case headnotes",
          variant: "destructive"
        });
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchCase();
    }
  }, [id, toast]);

  const handlePrint = () => {
    window.print();
  };

  const handleDownload = () => {
    if (!caseData) return;
    
    const content = `
HEADNOTES

${caseData.title || 'Untitled Case'}
${caseData.citation || ''}

${caseData.headnotes || 'No headnotes available'}
    `.trim();

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `headnotes-${id}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    toast({
      title: "Downloaded",
      description: "Headnotes downloaded successfully"
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error || !caseData) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center gap-4">
        <p className="text-red-600">{error || 'Case not found'}</p>
        <Button onClick={() => navigate(-1)}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Go Back
        </Button>
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>Headnotes - {caseData.title || 'Case'} | Pakistan Law App</title>
      </Helmet>

      <div className="min-h-screen bg-slate-50 print:bg-white">
        <div className="max-w-4xl mx-auto px-4 py-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-6 print:hidden">
            <Button variant="outline" onClick={() => navigate(-1)}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <div className="flex gap-2">
              <Button variant="outline" onClick={handlePrint}>
                <Printer className="w-4 h-4 mr-2" />
                Print
              </Button>
              <Button variant="outline" onClick={handleDownload}>
                <Download className="w-4 h-4 mr-2" />
                Download
              </Button>
            </div>
          </div>

          <Card className="p-8 print:shadow-none print:border-none">
            {/* Title */}
            <div className="text-center mb-8">
              <h1 className="text-2xl font-bold text-slate-900 mb-2">
                {caseData.title || 'Untitled Case'}
              </h1>
              {caseData.citation && (
                <p className="text-slate-600">{caseData.citation}</p>
              )}
            </div>

            <Separator className="my-6" />

            {/* Headnotes */}
            <div className="prose max-w-none">
              <h2 className="text-xl font-bold text-slate-900 mb-4">HEADNOTES</h2>
              <div className="text-slate-700 leading-relaxed whitespace-pre-wrap">
                {caseData.headnotes || 'No headnotes available for this case.'}
              </div>
            </div>

            <Separator className="my-6" />

            {/* Case Details */}
            <div className="grid grid-cols-2 gap-4 text-sm text-slate-600">
              <div>
                <span className="font-semibold">Court:</span> {caseData.court || 'N/A'}
              </div>
              <div>
                <span className="font-semibold">Date:</span> {caseData.date ? new Date(caseData.date).toLocaleDateString() : 'N/A'}
              </div>
              <div>
                <span className="font-semibold">Category:</span> {caseData.category || 'N/A'}
              </div>
              <div>
                <span className="font-semibold">Status:</span> {caseData.status || 'N/A'}
              </div>
            </div>
          </Card>
        </div>
      </div>
    </>
  );
};

export default HeadNotesPage;
