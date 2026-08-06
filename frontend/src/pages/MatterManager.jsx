import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { useToast } from '../components/ui/use-toast';
import { Plus, Folder, Calendar, Users, FileText, Clock, Loader2 } from 'lucide-react';
import { Helmet } from 'react-helmet';

const MatterManager = () => {
  const { toast } = useToast();
  const [matters, setMatters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNewMatter, setShowNewMatter] = useState(false);
  const [selectedMatter, setSelectedMatter] = useState(null);
  
  const [newMatter, setNewMatter] = useState({
    title: '',
    client: '',
    caseNumber: '',
    court: '',
    status: 'active',
    type: '',
    description: '',
    startDate: '',
    expectedEndDate: ''
  });

  useEffect(() => {
    fetchMatters();
  }, []);

  const fetchMatters = async () => {
    try {
      setLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockMatters = [
        {
          id: 1,
          title: "Property Dispute - Phase 1",
          client: "ABC Corporation",
          caseNumber: "Civil Suit 123/2024",
          court: "Lahore High Court",
          status: "active",
          type: "Civil",
          description: "Property dispute regarding commercial land in Lahore.",
          startDate: "2024-01-15",
          expectedEndDate: "2024-12-31",
          tasks: [
            { id: 1, title: "File petition", status: "completed", dueDate: "2024-01-20" },
            { id: 2, title: "Prepare evidence", status: "in_progress", dueDate: "2024-02-15" }
          ]
        },
        {
          id: 2,
          title: "Constitutional Petition",
          client: "Individual Client",
          caseNumber: "Const. Petition 45/2024",
          court: "Supreme Court",
          status: "pending",
          type: "Constitutional",
          description: "Challenge to constitutional validity of recent legislation.",
          startDate: "2024-02-01",
          expectedEndDate: "2024-06-30",
          tasks: [
            { id: 1, title: "Research precedents", status: "in_progress", dueDate: "2024-02-20" }
          ]
        }
      ];
      
      setMatters(mockMatters);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load matters",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateMatter = async () => {
    try {
      if (!newMatter.title || !newMatter.client) {
        toast({
          title: "Validation Error",
          description: "Title and client are required",
          variant: "destructive"
        });
        return;
      }

      const matter = {
        id: matters.length + 1,
        ...newMatter,
        tasks: []
      };

      setMatters(prev => [...prev, matter]);
      setShowNewMatter(false);
      setNewMatter({
        title: '',
        client: '',
        caseNumber: '',
        court: '',
        status: 'active',
        type: '',
        description: '',
        startDate: '',
        expectedEndDate: ''
      });

      toast({
        title: "Matter Created",
        description: "New matter has been created successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create matter",
        variant: "destructive"
      });
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800">Active</Badge>;
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800">Pending</Badge>;
      case 'closed':
        return <Badge className="bg-gray-100 text-gray-800">Closed</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-slate-400" />
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>Matter Manager | Pakistan Law App</title>
      </Helmet>

      <div className="min-h-screen bg-slate-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Matter Manager</h1>
              <p className="text-slate-600 mt-2">Manage your legal cases and matters</p>
            </div>
            <Button onClick={() => setShowNewMatter(true)}>
              <Plus className="w-4 h-4 mr-2" />
              New Matter
            </Button>
          </div>

          {showNewMatter && (
            <Card className="p-6 mb-6">
              <h2 className="text-lg font-semibold mb-4">Create New Matter</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="title">Matter Title</Label>
                  <Input
                    id="title"
                    value={newMatter.title}
                    onChange={(e) => setNewMatter(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="Enter matter title"
                  />
                </div>
                <div>
                  <Label htmlFor="client">Client</Label>
                  <Input
                    id="client"
                    value={newMatter.client}
                    onChange={(e) => setNewMatter(prev => ({ ...prev, client: e.target.value }))}
                    placeholder="Client name"
                  />
                </div>
                <div>
                  <Label htmlFor="caseNumber">Case Number</Label>
                  <Input
                    id="caseNumber"
                    value={newMatter.caseNumber}
                    onChange={(e) => setNewMatter(prev => ({ ...prev, caseNumber: e.target.value }))}
                    placeholder="Case number"
                  />
                </div>
                <div>
                  <Label htmlFor="court">Court</Label>
                  <Input
                    id="court"
                    value={newMatter.court}
                    onChange={(e) => setNewMatter(prev => ({ ...prev, court: e.target.value }))}
                    placeholder="Court name"
                  />
                </div>
                <div>
                  <Label htmlFor="type">Type</Label>
                  <Select
                    value={newMatter.type}
                    onValueChange={(value) => setNewMatter(prev => ({ ...prev, type: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Civil">Civil</SelectItem>
                      <SelectItem value="Criminal">Criminal</SelectItem>
                      <SelectItem value="Constitutional">Constitutional</SelectItem>
                      <SelectItem value="Commercial">Commercial</SelectItem>
                      <SelectItem value="Family">Family</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="status">Status</Label>
                  <Select
                    value={newMatter.status}
                    onValueChange={(value) => setNewMatter(prev => ({ ...prev, status: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="closed">Closed</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="md:col-span-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={newMatter.description}
                    onChange={(e) => setNewMatter(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Matter description..."
                    rows={3}
                  />
                </div>
                <div>
                  <Label htmlFor="startDate">Start Date</Label>
                  <Input
                    id="startDate"
                    type="date"
                    value={newMatter.startDate}
                    onChange={(e) => setNewMatter(prev => ({ ...prev, startDate: e.target.value }))}
                  />
                </div>
                <div>
                  <Label htmlFor="expectedEndDate">Expected End Date</Label>
                  <Input
                    id="expectedEndDate"
                    type="date"
                    value={newMatter.expectedEndDate}
                    onChange={(e) => setNewMatter(prev => ({ ...prev, expectedEndDate: e.target.value }))}
                  />
                </div>
              </div>
              <div className="flex gap-2 mt-4">
                <Button onClick={handleCreateMatter}>Create Matter</Button>
                <Button variant="outline" onClick={() => setShowNewMatter(false)}>Cancel</Button>
              </div>
            </Card>
          )}

          {/* Matters List */}
          <div className="grid gap-4">
            {matters.map(matter => (
              <Card key={matter.id} className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {getStatusBadge(matter.status)}
                      <Badge variant="outline">{matter.type}</Badge>
                    </div>
                    <h3 className="text-lg font-semibold text-slate-900">{matter.title}</h3>
                    <p className="text-slate-600 text-sm mt-1">
                      <Users className="w-3 h-3 inline mr-1" />
                      {matter.client}
                    </p>
                    <div className="mt-2 text-sm text-slate-600">
                      <p><span className="font-medium">Case:</span> {matter.caseNumber}</p>
                      <p><span className="font-medium">Court:</span> {matter.court}</p>
                    </div>
                    <p className="text-slate-700 mt-3">{matter.description}</p>
                    <div className="flex items-center gap-4 mt-3 text-sm text-slate-500">
                      <span>
                        <Calendar className="w-3 h-3 inline mr-1" />
                        Started: {matter.startDate}
                      </span>
                      <span>
                        <Clock className="w-3 h-3 inline mr-1" />
                        Expected: {matter.expectedEndDate}
                      </span>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    <FileText className="w-4 h-4 mr-2" />
                    View Details
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </>
  );
};

export default MatterManager;
