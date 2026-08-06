import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { BookOpen, Download, FileText, Share2, Printer, ArrowLeft, Search } from 'lucide-react';
import { getCaseDetail, getCaseReferences, searchWithinCase } from '../api/api';
import CaseSearchBox from '../components/CaseSearchBox';
import AICaseWidget from '../components/AICaseWidget';

export default function CaseDetailPage() {
  const { caseId } = useParams();
  const [case_, setCase] = useState(null);
  const [references, setReferences] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('content');

  useEffect(() => {
    async function loadCase() {
      setLoading(true);
      try {
        const [caseData, refsData] = await Promise.all([
          getCaseDetail(caseId),
          getCaseReferences(caseId),
        ]);
        setCase(caseData);
        setReferences(refsData);
      } catch (e) {
        console.error('Failed to load case:', e);
      } finally {
        setLoading(false);
      }
    }
    loadCase();
  }, [caseId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#1a365d]"></div>
      </div>
    );
  }

  if (!case_) {
    return (
      <div className="p-6 max-w-7xl mx-auto text-center">
        <BookOpen className="mx-auto h-12 w-12 text-gray-300 mb-4" />
        <p className="text-gray-500 text-lg">Case not found.</p>
        <Link to="/cases" className="text-[#1a365d] hover:underline mt-4 inline-block">
          Back to all cases
        </Link>
      </div>
    );
  }

  const tabs = [
    { id: 'content', label: 'Full Text', icon: FileText },
    { id: 'headnotes', label: 'Headnotes', icon: BookOpen },
    { id: 'references', label: 'References', icon: Share2 },
    { id: 'ai', label: 'AI Analysis', icon: Search },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <Link to="/cases" className="flex items-center gap-2 text-gray-500 hover:text-[#1a365d] mb-4">
        <ArrowLeft size={18} />
        Back to cases
      </Link>

      <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
        <h1 className="text-2xl font-bold text-[#1a365d] mb-2">
          {case_.citation || case_.title}
        </h1>
        <div className="flex flex-wrap gap-4 text-sm text-gray-500 mb-4">
          {case_.court && <span className="flex items-center gap-1"><Scale size={14} /> {case_.court}</span>}
          {case_.year && <span>{case_.year}</span>}
          {case_.judges && <span>Bench: {case_.judges}</span>}
          {case_.parties && <span>Parties: {case_.parties}</span>}
        </div>

        <div className="flex gap-2">
          <button className="flex items-center gap-2 px-4 py-2 bg-[#1a365d] text-white rounded-lg hover:bg-[#234e8e] text-sm">
            <Download size={16} />
            Download
          </button>
          <button className="flex items-center gap-2 px-4 py-2 border rounded-lg hover:bg-gray-50 text-sm">
            <Share2 size={16} />
            Share
          </button>
          <button className="flex items-center gap-2 px-4 py-2 border rounded-lg hover:bg-gray-50 text-sm">
            <Printer size={16} />
            Print
          </button>
        </div>
      </div>

      {/* Search within case */}
      <CaseSearchBox caseId={caseId} />

      {/* AI Widget */}
      <AICaseWidget caseId={caseId} caseData={case_} />

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="flex border-b">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-4 text-sm font-medium transition-colors
                  ${activeTab === tab.id 
                    ? 'border-b-2 border-[#1a365d] text-[#1a365d]' 
                    : 'text-gray-500 hover:text-gray-700'}`}
              >
                <Icon size={16} />
                {tab.label}
              </button>
            );
          })}
        </div>

        <div className="p-6">
          {activeTab === 'content' && (
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap text-sm leading-relaxed text-gray-700 font-mono">
                {case_.full_content || case_.raw_text || 'No content available'}
              </pre>
            </div>
          )}

          {activeTab === 'headnotes' && (
            <div>
              {case_.headnotes ? (
                <div className="prose max-w-none">
                  <p className="text-sm leading-relaxed text-gray-700">{case_.headnotes}</p>
                </div>
              ) : case_.ai_headnotes ? (
                <div className="prose max-w-none">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                    <p className="text-sm text-blue-700 font-medium">AI-Generated Headnotes</p>
                  </div>
                  <p className="text-sm leading-relaxed text-gray-700">{case_.ai_headnotes}</p>
                </div>
              ) : (
                <div className="text-center py-8">
                  <BookOpen className="mx-auto h-10 w-10 text-gray-300 mb-3" />
                  <p className="text-gray-500">No headnotes available for this case.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'references' && (
            <div>
              {references && references.references ? (
                <div className="space-y-6">
                  {references.references.sections?.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-[#1a365d] mb-2">Referenced Sections</h3>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                        {references.references.sections.map((ref, i) => (
                          <div key={i} className="bg-gray-50 rounded-lg p-2 text-sm">
                            <span className="font-medium">{ref.text}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {references.references.cited_cases?.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-[#1a365d] mb-2">Cited Cases</h3>
                      <div className="space-y-2">
                        {references.references.cited_cases.map((ref, i) => (
                          <div key={i} className="bg-gray-50 rounded-lg p-2 text-sm">
                            <span className="font-medium">{ref.text}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {references.references.legal_terms?.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-[#1a365d] mb-2">Legal Terms</h3>
                      <div className="flex flex-wrap gap-2">
                        {references.references.legal_terms.map((ref, i) => (
                          <span key={i} className="bg-gray-100 px-2 py-1 rounded text-sm">{ref.text}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {references.references.courts?.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-[#1a365d] mb-2">Mentioned Courts</h3>
                      <div className="flex flex-wrap gap-2">
                        {references.references.courts.map((ref, i) => (
                          <span key={i} className="bg-gray-100 px-2 py-1 rounded text-sm">{ref.text}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Share2 className="mx-auto h-10 w-10 text-gray-300 mb-3" />
                  <p className="text-gray-500">No references found.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'ai' && (
            <div className="text-center py-8">
              <Search className="mx-auto h-10 w-10 text-gray-300 mb-3" />
              <p className="text-gray-500">AI analysis features are available through the AI widget above.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
