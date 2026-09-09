import React, { useState, useEffect } from 'react';
import { FileText, Download, Copy, Check, Loader2, BookOpen, Scale, Briefcase, Home, Users, FileSignature } from 'lucide-react';
import api from '../api/api';

const TEMPLATES = [
  { id: 'rental', name: 'Rental Agreement', icon: Home, desc: 'Residential/commercial tenancy contract' },
  { id: 'sale', name: 'Sale Agreement', icon: FileText, desc: 'Property or goods sale deed' },
  { id: 'employment', name: 'Employment Contract', icon: Briefcase, desc: 'Hire employees with clear terms' },
  { id: 'partnership', name: 'Partnership Deed', icon: Users, desc: 'Business partnership agreement' },
  { id: 'bail', name: 'Bail Petition', icon: Scale, desc: 'Application for bail under CrPC' },
  { id: 'divorce', name: 'Divorce Petition', icon: FileSignature, desc: 'Family court dissolution petition' },
  { id: 'notice', name: 'Legal Notice', icon: FileText, desc: 'Formal demand or warning notice' },
  { id: 'writ', name: 'Writ Petition', icon: Scale, desc: 'Constitutional remedy petition' },
];

export default function LegalDrafterPage() {
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);

  const handleFieldChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const generateDocument = async () => {
    if (!selectedTemplate) return;
    setLoading(true);
    try {
      const prompt = Object.entries(formData)
        .filter(([_, v]) => v)
        .map(([k, v]) => `${k}: ${v}`)
        .join('; ');

      const res = await api.post('/contracts/generate/freeform', {
        contract_type: selectedTemplate.id,
        prompt: prompt || `Generate a ${selectedTemplate.name}`,
      });
      setResult(res.data);
    } catch (err) {
      setResult({ contract: 'Error generating document. Please try again.', relevant_cases: [] });
    }
    setLoading(false);
  };

  const copyToClipboard = () => {
    if (result?.contract) {
      navigator.clipboard.writeText(result.contract);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const downloadTxt = () => {
    if (!result?.contract) return;
    const blob = new Blob([result.contract], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedTemplate?.name || 'document'}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getFieldsForTemplate = (templateId) => {
    const fields = {
      rental: ['Landlord Name', 'Tenant Name', 'Property Address', 'Monthly Rent (PKR)', 'Duration (months)', 'Security Deposit'],
      sale: ['Seller Name', 'Buyer Name', 'Item/Property Description', 'Sale Price (PKR)', 'Payment Terms', 'Warranty Period'],
      employment: ['Employer Name', 'Employee Name', 'Position/Title', 'Salary (PKR)', 'Joining Date', 'Probation Period', 'Notice Period'],
      partnership: ['Partner 1 Name', 'Partner 2 Name', 'Business Name', 'Business Address', 'Capital Contribution', 'Profit Sharing Ratio'],
      bail: ['Accused Name', "Father's Name", 'Case Number', 'Police Station', 'Offense (Section)', 'Surety Amount'],
      divorce: ['Petitioner Name', 'Respondent Name', 'Marriage Date', 'Children (if any)', 'Grounds for Divorce', 'Relief Sought'],
      notice: ['Sender Name', 'Recipient Name', 'Subject', 'Demand/Claim', 'Deadline Date', 'Legal Basis'],
      writ: ['Petitioner Name', 'Respondent (State Dept)', 'Fundamental Right Violated', 'Facts', 'Relief Sought'],
    };
    return fields[templateId] || ['Party 1 Name', 'Party 2 Name', 'Subject', 'Details'];
  };

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold flex items-center gap-2" style={{ color: 'var(--text-h)' }}>
          <FileText className="w-6 h-6 text-emerald-600" />
          Legal Drafter
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--text)' }}>
          AI-powered legal document generation for Pakistani law
        </p>
      </div>

      {!selectedTemplate ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {TEMPLATES.map(t => {
            const Icon = t.icon;
            return (
              <button
                key={t.id}
                onClick={() => { setSelectedTemplate(t); setFormData({}); setResult(null); }}
                className="p-4 rounded-xl border-2 border-dashed border-gray-200 hover:border-emerald-400 hover:bg-emerald-50 transition-all text-left"
              >
                <Icon className="w-8 h-8 text-emerald-600 mb-2" />
                <h3 className="font-semibold text-sm" style={{ color: 'var(--text-h)' }}>{t.name}</h3>
                <p className="text-xs mt-1" style={{ color: 'var(--text)' }}>{t.desc}</p>
              </button>
            );
          })}
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-4">
            <button
              onClick={() => { setSelectedTemplate(null); setResult(null); }}
              className="text-sm text-emerald-600 hover:underline"
            >
              ← Back to Templates
            </button>
            <h2 className="text-lg font-semibold flex items-center gap-2">
              {React.createElement(selectedTemplate.icon, { className: 'w-5 h-5 text-emerald-600' })}
              {selectedTemplate.name}
            </h2>

            <div className="space-y-3">
              {getFieldsForTemplate(selectedTemplate.id).map(field => (
                <div key={field}>
                  <label className="block text-xs font-medium mb-1" style={{ color: 'var(--text)' }}>
                    {field}
                  </label>
                  <input
                    type="text"
                    value={formData[field] || ''}
                    onChange={e => handleFieldChange(field, e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
                    placeholder={`Enter ${field}`}
                  />
                </div>
              ))}
            </div>

            <button
              onClick={generateDocument}
              disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-lg font-medium text-sm hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
              {loading ? 'Generating...' : 'Generate Document'}
            </button>
          </div>

          <div>
            {result ? (
              <div className="border rounded-xl p-4 bg-gray-50">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-sm">Generated Document</h3>
                  <div className="flex gap-2">
                    <button onClick={copyToClipboard} className="p-1.5 rounded hover:bg-gray-200" title="Copy">
                      {copied ? <Check className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4" />}
                    </button>
                    <button onClick={downloadTxt} className="p-1.5 rounded hover:bg-gray-200" title="Download">
                      <Download className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <div className="bg-white rounded-lg p-4 max-h-[500px] overflow-y-auto text-sm whitespace-pre-wrap border">
                  {result.contract}
                </div>
                {result.relevant_cases?.length > 0 && (
                  <div className="mt-3">
                    <h4 className="text-xs font-medium mb-1">Relevant Cases:</h4>
                    <div className="flex flex-wrap gap-1">
                      {result.relevant_cases.map(c => (
                        <span key={c.case_id} className="text-xs px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded">
                          {c.citation}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="border-2 border-dashed rounded-xl p-8 text-center text-gray-400">
                <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Fill the form and click Generate to create your document</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
