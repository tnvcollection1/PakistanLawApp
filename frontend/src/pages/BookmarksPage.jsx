import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bookmark, Trash2, Plus, Search, Loader2, Folder, ChevronRight, ExternalLink, BookMarked } from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import SidebarLayout from '../components/SidebarLayout';
import api from '../api/api';

const BookmarksPage = () => {
  const navigate = useNavigate();
  const [bookmarks, setBookmarks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [folders, setFolders] = useState(['Default', 'Research', 'Important']);
  const [selectedFolder, setSelectedFolder] = useState('All');
  const [showNewFolder, setShowNewFolder] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');

  useEffect(() => {
    fetchBookmarks();
  }, []);

  const fetchBookmarks = async () => {
    setLoading(true);
    try {
      const response = await api.user.getBookmarks();
      setBookmarks(response.data || []);
    } catch (e) {
      console.error('Error fetching bookmarks:', e);
      setBookmarks([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.user.deleteBookmark(id);
      setBookmarks(prev => prev.filter(b => b.id !== id));
    } catch (e) {
      console.error('Error deleting bookmark:', e);
    }
  };

  const handleCreateFolder = () => {
    if (newFolderName.trim() && !folders.includes(newFolderName.trim())) {
      setFolders(prev => [...prev, newFolderName.trim()]);
      setNewFolderName('');
      setShowNewFolder(false);
    }
  };

  const filteredBookmarks = bookmarks.filter(b => {
    const matchesSearch = !searchQuery || 
      (b.case_name && b.case_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (b.citation && b.citation.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (b.note && b.note.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesFolder = selectedFolder === 'All' || b.folder === selectedFolder;
    return matchesSearch && matchesFolder;
  });

  const folderCounts = folders.reduce((acc, folder) => {
    acc[folder] = bookmarks.filter(b => b.folder === folder).length;
    return acc;
  }, { All: bookmarks.length });

  return (
    <SidebarLayout>
      <div className="min-h-screen bg-background" data-testid="bookmarks-page">
        <div className="bg-white dark:bg-card border-b border-border">
          <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-6">
            <h1 className="text-2xl sm:text-3xl font-serif font-bold text-foreground flex items-center gap-3">
              <Bookmark className="text-primary" size={24} />
              Bookmarks
            </h1>
            <p className="text-sm text-muted-foreground mt-2">{bookmarks.length} saved cases</p>
          </div>
        </div>

        <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-8">
          {/* Search and Filter */}
          <div className="flex flex-col sm:flex-row gap-3 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
              <Input placeholder="Search bookmarks..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="pl-10" />
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              <Button variant="outline" size="sm" onClick={() => setSelectedFolder('All')} className={selectedFolder === 'All' ? 'bg-primary/10 text-primary' : ''}>
                <Folder size={14} className="mr-1" /> All ({folderCounts.All})
              </Button>
              {folders.map(folder => (
                <Button key={folder} variant="outline" size="sm" onClick={() => setSelectedFolder(folder)} className={selectedFolder === folder ? 'bg-primary/10 text-primary' : ''}>
                  <Folder size={14} className="mr-1" /> {folder} ({folderCounts[folder]})
                </Button>
              ))}
              <Button variant="ghost" size="sm" onClick={() => setShowNewFolder(!showNewFolder)}><Plus size={14} /></Button>
            </div>
          </div>

          {showNewFolder && (
            <div className="flex gap-2 mb-6">
              <Input placeholder="New folder name..." value={newFolderName} onChange={(e) => setNewFolderName(e.target.value)} className="max-w-xs" />
              <Button size="sm" onClick={handleCreateFolder}>Create</Button>
            </div>
          )}

          {/* Bookmarks List */}
          <div className="bg-white dark:bg-card rounded-xl border border-border overflow-hidden">
            {loading ? (
              <div className="p-12 text-center"><Loader2 size={32} className="animate-spin text-primary mx-auto mb-3" /><p className="text-muted-foreground">Loading...</p></div>
            ) : filteredBookmarks.length === 0 ? (
              <div className="p-16 text-center"><BookMarked size={48} className="text-muted-foreground mx-auto mb-4" /><p className="text-muted-foreground font-medium">No bookmarks found</p><p className="text-muted-foreground text-sm mt-1">Save cases from search results to see them here</p></div>
            ) : (
              <div className="divide-y divide-border">
                {filteredBookmarks.map((bookmark) => (
                  <div key={bookmark.id} className="p-4 hover:bg-accent/40 transition-colors">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 cursor-pointer" onClick={() => navigate(`/case/${bookmark.case_id}`)}>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-semibold text-primary">{bookmark.citation || bookmark.case_id}</span>
                          {bookmark.year && <Badge variant="outline" className="text-xs">{bookmark.year}</Badge>}
                          {bookmark.folder && <Badge variant="secondary" className="text-xs">{bookmark.folder}</Badge>}
                        </div>
                        <p className="text-sm font-medium text-foreground">{bookmark.case_name || `${bookmark.petitioner || ''} vs ${bookmark.respondent || ''}`}</p>
                        <p className="text-xs text-muted-foreground mt-1">{bookmark.court} {bookmark.judge && `| Judge: ${bookmark.judge}`}</p>
                        {bookmark.note && <p className="text-xs text-muted-foreground mt-2 italic bg-muted/30 p-2 rounded">"{bookmark.note}"</p>}
                      </div>
                      <div className="flex items-center gap-2">
                        <Button variant="ghost" size="sm" onClick={() => navigate(`/case/${bookmark.case_id}`)}><ExternalLink size={14} /></Button>
                        <Button variant="ghost" size="sm" className="text-red-500 hover:text-red-600" onClick={() => handleDelete(bookmark.id)}><Trash2 size={14} /></Button>
                      </div>
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

export default BookmarksPage;
