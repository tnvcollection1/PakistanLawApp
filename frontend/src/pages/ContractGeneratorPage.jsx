import React, { useState } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { useToast } from '../components/ui/use-toast';
import { FileText, Download, Copy, Loader2 } from 'lucide-react';
import { Helmet } from 'react-helmet';

const contractTemplates = [
  {
    id: 'general',
    name: 'General Contract',
    description: 'A general-purpose contract template'
  },
  {
    id: 'service',
    name: 'Service Agreement',
    description: 'For service-based engagements'
  },
  {
    id: 'employment',
    name: 'Employment Contract',
    description: 'Standard employment agreement'
  },
  {
    id: 'nda',
    name: 'Non-Disclosure Agreement',
    description: 'Confidentiality agreement'
  },
  {
    id: 'rental',
    name: 'Rental Agreement',
    description: 'Property rental contract'
  },
  {
    id: 'sales',
    name: 'Sales Agreement',
    description: 'Goods sales contract'
  }
];

const ContractGeneratorPage = () => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [generatedContract, setGeneratedContract] = useState('');
  const [formData, setFormData] = useState({
    party1Name: '',
    party1Address: '',
    party2Name: '',
    party2Address: '',
    contractDate: '',
    contractValue: '',
    description: '',
    duration: '',
    governingLaw: 'Islamic Republic of Pakistan',
    jurisdiction: '',
    specificTerms: ''
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const generateContract = async () => {
    try {
      setLoading(true);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const contract = generateContractText();
      setGeneratedContract(contract);
      
      toast({
        title: "Contract Generated",
        description: "Your contract has been generated successfully"
      });
    } catch (error) {
      toast({
        title: "Generation Failed",
        description: error.message,
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const generateContractText = () => {
    const template = contractTemplates.find(t => t.id === selectedTemplate);
    
    let contract = '';
    
    contract += `${template?.name || 'CONTRACT'}\n`;
    contract += '='.repeat(60) + '\n\n';
    
    contract += `Date: ${formData.contractDate || '[DATE]'}\n\n`;
    
    contract += `PARTIES\n`;
    contract += '-'.repeat(30) + '\n';
    contract += `Party 1 (First Party):\n`;
    contract += `Name: ${formData.party1Name || '[NAME]'}\n`;
    contract += `Address: ${formData.party1Address || '[ADDRESS]'}\n\n`;
    
    contract += `Party 2 (Second Party):\n`;
    contract += `Name: ${formData.party2Name || '[NAME]'}\n`;
    contract += `Address: ${formData.party2Address || '[ADDRESS]'}\n\n`;
    
    contract += `RECITALS\n`;
    contract += '-'.repeat(30) + '\n';
    contract += `WHEREAS, the parties wish to enter into this ${template?.name || 'agreement'};\n`;
    contract += `WHEREAS, both parties have the legal capacity to enter into this contract;\n`;
    contract += `NOW, THEREFORE, the parties agree as follows:\n\n`;
    
    contract += `TERMS AND CONDITIONS\n`;
    contract += '-'.repeat(30) + '\n';
    
    if (formData.description) {
      contract += `1. DESCRIPTION OF ${template?.id === 'service' ? 'SERVICES' : 'GOODS'}\n`;
      contract += `${formData.description}\n\n`;
    }
    
    if (formData.contractValue) {
      contract += `2. COMPENSATION\n`;
      contract += `The total value of this contract is PKR ${formData.contractValue}.\n\n`;
    }
    
    if (formData.duration) {
      contract += `3. DURATION\n`;
      contract += `This contract shall be effective for ${formData.duration}.\n\n`;
    }
    
    contract += `4. GOVERNING LAW\n`;
    contract += `This contract shall be governed by the laws of ${formData.governingLaw}.\n\n`;
    
    if (formData.jurisdiction) {
      contract += `5. JURISDICTION\n`;
      contract += `Any disputes shall be resolved in the courts of ${formData.jurisdiction}.\n\n`;
    }
    
    if (formData.specificTerms) {
      contract += `6. ADDITIONAL TERMS\n`;
      contract += `${formData.specificTerms}\n\n`;
    }
    
    contract += `SIGNATURES\n`;
    contract += '-'.repeat(30) + '\n\n';
    
    contract += `First Party:\n`;
    contract += `Signature: _________________________\n`;
    contract += `Name: ${formData.party1Name || '[NAME]'}\n`;
    contract += `Date: _________________________\n\n`;
    
    contract += `Second Party:\n`;
    contract += `Signature: _________________________\n`;
    contract += `Name: ${formData.party2Name || '[NAME]'}\n`;
    contract += `Date: _________________________\n\n`;
    
    contract += `WITNESS (if required):\n`;
    contract += `Signature: _________________________\n`;
    contract += `Name: _________________________\n`;
    contract += `Date: _________________________\n\n`;
    
    contract += '-'.repeat(60) + '\n';
    contract += `Generated by Pakistan Law App\n`;
    contract += `This is a template and should be reviewed by a legal professional.\n`;
    
    return contract;
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generatedContract);
    toast({
      title: "Copied",
      description: "Contract copied to clipboard"
    });
  };

  const handleDownload = () => {
    const blob = new Blob([generatedContract], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `contract-${selectedTemplate}-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    toast({
      title: "Downloaded",
      description: "Contract downloaded successfully"
    });
  };

  return (
    <>
      <Helmet>
        <title>Contract Generator | Pakistan Law App</title>
      </Helmet>

      <div className="min-h-screen bg-slate-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-900">Contract Generator</h1>
            <p className="text-slate-600 mt-2">Generate legal contracts from professional templates</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Form */}
            <div className="space-y-6">
              <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Select Template</h2>
                <Select
                  value={selectedTemplate}
                  onValueChange={setSelectedTemplate}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a contract template" />
                  </SelectTrigger>
                  <SelectContent>
                    {contractTemplates.map(template => (
                      <SelectItem key={template.id} value={template.id}>
                        <div>
                          <div className="font-medium">{template.name}</div>
                          <div className="text-sm text-slate-500">{template.description}</div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </Card>

              {selectedTemplate && (
                <>
                  <Card className="p-6">
                    <h2 className="text-lg font-semibold mb-4">Party Information</h2>
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="party1Name">First Party Name</Label>
                          <Input
                            id="party1Name"
                            name="party1Name"
                            value={formData.party1Name}
                            onChange={handleInputChange}
                            placeholder="Enter name"
                          />
                        </div>
                        <div>
                          <Label htmlFor="party2Name">Second Party Name</Label>
                          <Input
                            id="party2Name"
                            name="party2Name"
                            value={formData.party2Name}
                            onChange={handleInputChange}
                            placeholder="Enter name"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="party1Address">First Party Address</Label>
                          <Textarea
                            id="party1Address"
                            name="party1Address"
                            value={formData.party1Address}
                            onChange={handleInputChange}
                            placeholder="Enter address"
                            rows={2}
                          />
                        </div>
                        <div>
                          <Label htmlFor="party2Address">Second Party Address</Label>
                          <Textarea
                            id="party2Address"
                            name="party2Address"
                            value={formData.party2Address}
                            onChange={handleInputChange}
                            placeholder="Enter address"
                            rows={2}
                          />
                        </div>
                      </div>
                    </div>
                  </Card>

                  <Card className="p-6">
                    <h2 className="text-lg font-semibold mb-4">Contract Details</h2>
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="contractDate">Contract Date</Label>
                          <Input
                            id="contractDate"
                            name="contractDate"
                            type="date"
                            value={formData.contractDate}
                            onChange={handleInputChange}
                          />
                        </div>
                        <div>
                          <Label htmlFor="contractValue">Contract Value (PKR)</Label>
                          <Input
                            id="contractValue"
                            name="contractValue"
                            type="number"
                            value={formData.contractValue}
                            onChange={handleInputChange}
                            placeholder="Enter amount"
                          />
                        </div>
                      </div>

                      <div>
                        <Label htmlFor="description">Description</Label>
                        <Textarea
                          id="description"
                          name="description"
                          value={formData.description}
                          onChange={handleInputChange}
                          placeholder="Describe the purpose of this contract..."
                          rows={3}
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="duration">Duration</Label>
                          <Input
                            id="duration"
                            name="duration"
                            value={formData.duration}
                            onChange={handleInputChange}
                            placeholder="e.g., 1 year"
                          />
                        </div>
                        <div>
                          <Label htmlFor="jurisdiction">Jurisdiction</Label>
                          <Input
                            id="jurisdiction"
                            name="jurisdiction"
                            value={formData.jurisdiction}
                            onChange={handleInputChange}
                            placeholder="e.g., Lahore"
                          />
                        </div>
                      </div>

                      <div>
                        <Label htmlFor="specificTerms">Specific Terms</Label>
                        <Textarea
                          id="specificTerms"
                          name="specificTerms"
                          value={formData.specificTerms}
                          onChange={handleInputChange}
                          placeholder="Enter any specific terms or conditions..."
                          rows={4}
                        />
                      </div>
                    </div>
                  </Card>

                  <Button
                    className="w-full"
                    onClick={generateContract}
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <FileText className="w-4 h-4 mr-2" />
                        Generate Contract
                      </>
                    )}
                  </Button>
                </>
              )}
            </div>

            {/* Preview */}
            <div>
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold">Contract Preview</h2>
                  {generatedContract && (
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={handleCopy}>
                        <Copy className="w-4 h-4 mr-2" />
                        Copy
                      </Button>
                      <Button variant="outline" size="sm" onClick={handleDownload}>
                        <Download className="w-4 h-4 mr-2" />
                        Download
                      </Button>
                    </div>
                  )}
                </div>
                
                {generatedContract ? (
                  <pre className="bg-slate-50 p-4 rounded-lg text-sm whitespace-pre-wrap font-mono max-h-[800px] overflow-y-auto">
                    {generatedContract}
                  </pre>
                ) : (
                  <div className="text-center py-12 text-slate-500">
                    <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Select a template and fill in the details to generate a contract</p>
                  </div>
                )}
              </Card>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ContractGeneratorPage;
