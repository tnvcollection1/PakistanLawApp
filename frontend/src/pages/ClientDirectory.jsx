import React, { useState, useEffect, useMemo } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import {
  Users, Search, ChevronLeft, Plus, Phone, Mail, Building2, Trash2, Edit2, Star, FileText
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/use-toast";
import {
  Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogFooter
} from "@/components/ui/dialog";
import PageHeader from "@/components/PageHeader";
import Sidebar from "@/components/Sidebar";
import api from "@/lib/api";

const typeColors = {
  client: "bg-green-500/20 text-green-400",
  lawyer: "bg-blue-500/20 text-blue-400",
  judge: "bg-amber-500/20 text-amber-400",
  firm: "bg-purple-500/20 text-purple-400",
  other: "bg-gray-500/20 text-gray-400",
};

const statusColors = {
  active: "text-green-400",
  inactive: "text-gray-400",
};

export default function ClientDirectory() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [contacts, setContacts] = useState([]);
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [selectedType, setSelectedType] = useState("all");
  const [newContact, setNewContact] = useState({
    name: "", firm: "", email: "", phone: "", type: "client", notes: ""
  });
  const [editingContact, setEditingContact] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    fetchContacts();
  }, []);

  const fetchContacts = async () => {
    setIsLoading(true);
    try {
      const res = await api.get("/contacts");
      setContacts(res.data);
    } catch (err) {
      setContacts([]);
    } finally {
      setIsLoading(false);
    }
  };

  const filtered = useMemo(() => {
    return contacts.filter(c => {
      const matchSearch = !search || c.name?.toLowerCase().includes(search.toLowerCase()) || c.firm?.toLowerCase().includes(search.toLowerCase()) || c.email?.toLowerCase().includes(search.toLowerCase());
      const matchType = selectedType === "all" || c.type === selectedType;
      return matchSearch && matchType;
    });
  }, [contacts, search, selectedType]);

  const handleAddContact = async () => {
    if (!newContact.name.trim()) {
      toast({ title: "Name is required", variant: "destructive" });
      return;
    }
    try {
      const res = await api.post("/contacts", newContact);
      setContacts(prev => [res.data, ...prev]);
      setNewContact({ name: "", firm: "", email: "", phone: "", type: "client", notes: "" });
      setDialogOpen(false);
      toast({ title: "Contact added successfully" });
    } catch (err) {
      toast({ title: "Failed to add contact", variant: "destructive" });
    }
  };

  const handleEditContact = async () => {
    if (!editingContact || !editingContact.name.trim()) {
      toast({ title: "Name is required", variant: "destructive" });
      return;
    }
    try {
      await api.patch(`/contacts/${editingContact.id}`, editingContact);
      setContacts(prev => prev.map(c => c.id === editingContact.id ? editingContact : c));
      setEditingContact(null);
      setDialogOpen(false);
      toast({ title: "Contact updated successfully" });
    } catch (err) {
      toast({ title: "Failed to update contact", variant: "destructive" });
    }
  };

  const handleDeleteContact = async (id) => {
    if (!window.confirm("Delete this contact permanently?")) return;
    try {
      await api.delete(`/contacts/${id}`);
      setContacts(prev => prev.filter(c => c.id !== id));
      toast({ title: "Contact deleted" });
    } catch (err) {
      toast({ title: "Failed to delete contact", variant: "destructive" });
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-[#0B1120] via-[#0F172A] to-[#1E293B]">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <PageHeader title="Client Directory" onMenuClick={() => setSidebarOpen(true)} />

        <div className="p-6 overflow-y-auto">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <div className="flex items-center gap-4 mb-4">
              <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
                <ChevronLeft className="w-5 h-5 text-slate-300" />
              </Button>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-sky-500/20 flex items-center justify-center">
                  <Users className="w-5 h-5 text-sky-400" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">Client Directory</h1>
                  <p className="text-slate-400 text-sm">Manage your professional contacts</p>
                </div>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 mb-4">
              <div className="relative flex-1 w-full">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <Input
                  placeholder="Search contacts..."
                  className="pl-10 bg-slate-800/60 border-slate-700 text-white"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>
              <select
                className="px-3 py-2 rounded-md bg-slate-800/60 border border-slate-700 text-white text-sm"
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
              >
                <option value="all">All Types</option>
                <option value="client">Client</option>
                <option value="lawyer">Lawyer</option>
                <option value="judge">Judge</option>
                <option value="firm">Law Firm</option>
                <option value="other">Other</option>
              </select>
              <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="bg-sky-600 hover:bg-sky-700" onClick={() => { setEditingContact(null); setNewContact({ name: "", firm: "", email: "", phone: "", type: "client", notes: "" }); }}>
                    <Plus className="w-4 h-4 mr-1" /> Add Contact
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-slate-900 border-slate-700 max-w-md">
                  <DialogHeader>
                    <DialogTitle className="text-white">
                      {editingContact ? "Edit Contact" : "Add Contact"}
                    </DialogTitle>
                  </DialogHeader>
                  <div className="space-y-3 py-2">
                    <Input placeholder="Full Name" className="bg-slate-800 border-slate-700 text-white"
                      value={editingContact ? editingContact.name : newContact.name}
                      onChange={(e) => editingContact ? setEditingContact({ ...editingContact, name: e.target.value }) : setNewContact({ ...newContact, name: e.target.value })}
                    />
                    <Input placeholder="Firm / Organization" className="bg-slate-800 border-slate-700 text-white"
                      value={editingContact ? editingContact.firm : newContact.firm}
                      onChange={(e) => editingContact ? setEditingContact({ ...editingContact, firm: e.target.value }) : setNewContact({ ...newContact, firm: e.target.value })}
                    />
                    <div className="flex gap-3">
                      <Input placeholder="Email" className="bg-slate-800 border-slate-700 text-white"
                        value={editingContact ? editingContact.email : newContact.email}
                        onChange={(e) => editingContact ? setEditingContact({ ...editingContact, email: e.target.value }) : setNewContact({ ...newContact, email: e.target.value })}
                      />
                      <Input placeholder="Phone" className="bg-slate-800 border-slate-700 text-white"
                        value={editingContact ? editingContact.phone : newContact.phone}
                        onChange={(e) => editingContact ? setEditingContact({ ...editingContact, phone: e.target.value }) : setNewContact({ ...newContact, phone: e.target.value })}
                      />
                    </div>
                    <select
                      className="w-full px-3 py-2 rounded-md bg-slate-800 border border-slate-700 text-white text-sm"
                      value={editingContact ? editingContact.type : newContact.type}
                      onChange={(e) => editingContact ? setEditingContact({ ...editingContact, type: e.target.value }) : setNewContact({ ...newContact, type: e.target.value })}
                    >
                      <option value="client">Client</option>
                      <option value="lawyer">Lawyer</option>
                      <option value="judge">Judge</option>
                      <option value="firm">Law Firm</option>
                      <option value="other">Other</option>
                    </select>
                    <Input placeholder="Notes" className="bg-slate-800 border-slate-700 text-white"
                      value={editingContact ? editingContact.notes : newContact.notes}
                      onChange={(e) => editingContact ? setEditingContact({ ...editingContact, notes: e.target.value }) : setNewContact({ ...newContact, notes: e.target.value })}
                    />
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
                    <Button className="bg-sky-600 hover:bg-sky-700" onClick={editingContact ? handleEditContact : handleAddContact}>
                      {editingContact ? "Update" : "Add"} Contact
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="grid gap-3"
          >
            {isLoading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="h-24 rounded-xl bg-slate-800/40 animate-pulse" />
              ))
            ) : filtered.length === 0 ? (
              <div className="text-center py-12 text-slate-400">
                <Users className="w-10 h-10 mx-auto mb-3 opacity-30" />
                <p>No contacts found.</p>
              </div>
            ) : (
              filtered.map((contact, idx) => (
                <motion.div
                  key={contact.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="rounded-xl border border-slate-700/50 bg-slate-800/40 p-4 flex flex-col sm:flex-row items-start sm:items-center gap-4 hover:bg-slate-800/60 transition-colors cursor-pointer"
                  onClick={() => { setEditingContact(contact); setDialogOpen(true); }}
                >
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 flex items-center justify-center text-white font-bold text-lg shrink-0">
                    {contact.name?.charAt(0)?.toUpperCase() || "?"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="text-white font-semibold truncate">{contact.name}</h3>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${typeColors[contact.type] || typeColors.other}`}>
                        {contact.type || "other"}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 mt-1 text-sm text-slate-400 flex-wrap">
                      {contact.firm && (
                        <span className="flex items-center gap-1"><Building2 className="w-3 h-3" /> {contact.firm}</span>
                      )}
                      {contact.email && (
                        <span className="flex items-center gap-1"><Mail className="w-3 h-3" /> {contact.email}</span>
                      )}
                      {contact.phone && (
                        <span className="flex items-center gap-1"><Phone className="w-3 h-3" /> {contact.phone}</span>
                      )}
                    </div>
                    {contact.notes && (
                      <p className="text-slate-500 text-xs mt-1 truncate">{contact.notes}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Button variant="ghost" size="icon" className="text-slate-400 hover:text-sky-400"
                      onClick={(e) => { e.stopPropagation(); setEditingContact(contact); setDialogOpen(true); }}
                    >
                      <Edit2 className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" className="text-slate-400 hover:text-red-400"
                      onClick={(e) => { e.stopPropagation(); handleDeleteContact(contact.id); }}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </motion.div>
              ))
            )}
          </motion.div>
        </div>
      </main>
    </div>
  );
}
