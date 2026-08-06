import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { useToast } from '../components/ui/use-toast';
import { BookOpen, Plus, Edit, Trash2, Loader2 } from 'lucide-react';

const StatuteManagement = () => {
  const { toast } = useToast();
  const [statutes, setStatutes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingStatute, setEditingStatute] = useState(null);
  
  const [formData, setFormData] = useState({
    title: '',
    citation: '',
    category: '',
    type: '',
    year: '',
    description: '',
    status: 'active'
  });

  useEffect(() => {
    fetchStatutes();
  }, []);

  const fetchStatutes = async () => {
    try {
      setLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockStatutes = [
        {
          id: 1,
          title: "Constitution of Pakistan",
          citation: "PLD 1973 Central Statutes 1",
          category: "Constitutional",
          type: "Act",
          year: 1973,
          description: "The Constitution of the Islamic Republic of Pakistan.",
          status: "active",
          sections_count: 280
        },
        {
          id: 2,
          title: "Pakistan Penal Code",
          citation: "Act XLV of 1860",
          category: "Criminal",
          type: "Act",
          year: 1860,
          description: "The main criminal code of Pakistan.",
          status: "active",
          sections_count: 511
        }
      ];
      
      setStatutes(mockStatutes);
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

  const handleSubmit = async () => {
    try {
      if (editingStatute) {
        // Update existing
        setStatutes(prev => prev.map(s => 
          s.id === editingStatute.id ? { ...formData, id: s.id } : s
        ));
        toast({ title: "Statute Updated" });
      } else {
        // Create new
        const newStatute = {
          ...formData,
          id: statutes.length + 1,
          sections_count: 0
        };
        setStatutes(prev => [...prev, newStatute]);
        toast({ title: "Statute Created" });
      }
      
      resetForm();
    } catch (error) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive"
      });
    }
  };

  const handleEdit = (statute) => {
    setEditingStatute(statute);
    setFormData({
      title: statute.title,
      citation: statute.citation,
      category: statute.category,
      type: statute.type,
      year: statute.year,
      description: statute.description,
      status: statute.status
    });
    setShowForm(true);
  };

  const handleDelete = (statuteId) => {
    if (confirm('Are you sure you want to delete this statute?')) {
      setStatutes(prev => prev.filter(s => s.id !== statuteId));
      toast({ title: "Statute Deleted" });
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      citation: '',
      category: '',
      type: '',
      year: '',
      description: '',
      status: 'active'
    });
    setEditingStatute(null);
    setShowForm(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-slate-400" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Statute Management</h2>
        <Button onClick={() => setShowForm(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Statute
        </Button>
      </div>

      {showForm && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">
            {editingStatute ? 'Edit Statute' : 'Add New Statute'}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Statute title"
              />
            </div>
            <div>
              <Label htmlFor="citation">Citation</Label>
              <Input
                id="citation"
                value={formData.citation}
                onChange={(e) => setFormData(prev => ({ ...prev, citation: e.target.value }))}
                placeholder="Citation"
              />
            </div>
            <div>
              <Label htmlFor="category">Category</Label>
              <Input
                id="category"
                value={formData.category}
                onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                placeholder="Category"
              />
            </div>
            <div>
              <Label htmlFor="type">Type</Label>
              <Input
                id="type"
                value={formData.type}
                onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value }))}
                placeholder="Type (Act, Ordinance, etc.)"
              />
            </div>
            <div>
              <Label htmlFor="year">Year</Label>
              <Input
                id="year"
                type="number"
                value={formData.year}
                onChange={(e) => setFormData(prev => ({ ...prev, year: e.target.value }))}
                placeholder="Year"
              />
            </div>
            <div>
              <Label htmlFor="status">Status</Label>
              <select
                id="status"
                value={formData.status}
                onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value }))}
                className="w-full p-2 border rounded-md"
              >
                <option value="active">Active</option>
                <option value="repealed">Repealed</option>
                <option value="amended">Amended</option>
                <option value="draft">Draft</option>
              </select>
            </div>
            <div className="md:col-span-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Statute description..."
                rows={3}
              />
            </div>
          </div>
          <div className="flex gap-2 mt-4">
            <Button onClick={handleSubmit}>
              {editingStatute ? 'Update' : 'Create'}
            </Button>
            <Button variant="outline" onClick={resetForm}>Cancel</Button>
          </div>
        </Card>
      )}

      {/* Statutes List */}
      <div className="grid gap-4">
        {statutes.map(statute => (
          <Card key={statute.id} className="p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <BookOpen className="w-4 h-4 text-blue-600" />
                  <Badge variant={statute.status === 'active' ? 'default' : 'secondary'}>
                    {statute.status}
                  </Badge>
                  <Badge variant="outline">{statute.type}</Badge>
                </div>
                <h3 className="text-lg font-semibold">{statute.title}</h3>
                <p className="text-slate-600 text-sm">{statute.citation}</p>
                <div className="mt-2 text-sm text-slate-600">
                  <span className="mr-4">Category: {statute.category}</span>
                  <span className="mr-4">Year: {statute.year}</span>
                  <span>Sections: {statute.sections_count}</span>
                </div>
                <p className="text-slate-700 mt-2">{statute.description}</p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => handleEdit(statute)}>
                  <Edit className="w-4 h-4" />
                </Button>
                <Button variant="destructive" size="sm" onClick={() => handleDelete(statute.id)}>
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default StatuteManagement;
