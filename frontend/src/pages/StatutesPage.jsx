import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, Book, Bookmark, ChevronRight, ExternalLink, Download, Share2, AlertTriangle } from 'lucide-react';
import { statuteService } from '../services/statuteService';
import { searchService } from '../services/searchService';
import { useAuth } from '../hooks/useAuth';
import LoadingSpinner from '../components/LoadingSpinner';
import Toast from '../components/common/Toast';
import '../styles/statutes.css';

const StatutesPage = () => {
  const [statutes, setStatutes] = useState([]);
  const [filteredStatutes, setFilteredStatutes] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [bookmarkedStatutes, setBookmarkedStatutes] = useState([]);
  const [toast, setToast] = useState(null);
  const [categories, setCategories] = useState([]);
  const { user } = useAuth();

  useEffect(() => {
    fetchStatutes();
    loadBookmarkedStatutes();
  }, []);

  useEffect(() => {
    filterStatutes();
  }, [searchQuery, selectedCategory, statutes]);

  const fetchStatutes = async () => {
    try {
      setLoading(true);
      const response = await statuteService.getAllStatutes();
      if (response.success) {
        setStatutes(response.data);
        setFilteredStatutes(response.data);
        const uniqueCategories = [...new Set(response.data.map(s => s.category))];
        setCategories(uniqueCategories);
      } else {
        throw new Error(response.error || 'Failed to fetch statutes');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filterStatutes = () => {
    let filtered = [...statutes];

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(statute =>
        statute.title.toLowerCase().includes(query) ||
        statute.description.toLowerCase().includes(query) ||
        statute.number.toLowerCase().includes(query) ||
        statute.year.toString().includes(query)
      );
    }

    if (selectedCategory !== 'all') {
      filtered = filtered.filter(statute => statute.category === selectedCategory);
    }

    setFilteredStatutes(filtered);
  };

  const loadBookmarkedStatutes = () => {
    const saved = localStorage.getItem('bookmarkedStatutes');
    if (saved) {
      setBookmarkedStatutes(JSON.parse(saved));
    }
  };

  const toggleBookmark = (statuteId) => {
    const updated = bookmarkedStatutes.includes(statuteId)
      ? bookmarkedStatutes.filter(id => id !== statuteId)
      : [...bookmarkedStatutes, statuteId];
    
    setBookmarkedStatutes(updated);
    localStorage.setItem('bookmarkedStatutes', JSON.stringify(updated));
    setToast({
      message: bookmarkedStatutes.includes(statuteId) ? 'Removed from bookmarks' : 'Added to bookmarks',
      type: 'success'
    });
  };

  const handleShare = (statute) => {
    if (navigator.share) {
      navigator.share({
        title: statute.title,
        text: `Check out ${statute.title} on Pakistan Law App`,
        url: window.location.href
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      setToast({ message: 'Link copied to clipboard', type: 'success' });
    }
  };

  const handleDownload = async (statute) => {
    try {
      const response = await statuteService.downloadStatute(statute.id);
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${statute.title.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      setToast({ message: 'Download started', type: 'success' });
    } catch (err) {
      setToast({ message: 'Download failed', type: 'error' });
    }
  };

  if (loading) return <LoadingSpinner />;

  if (error) {
    return (
      <div className="statutes-page">
        <div className="error-container">
          <AlertTriangle size={48} />
          <h2>Error Loading Statutes</h2>
          <p>{error}</p>
          <button onClick={fetchStatutes} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="statutes-page">
      <div className="statutes-header">
        <h1>Statutes of Pakistan</h1>
        <p>Comprehensive collection of Pakistani laws and statutes</p>
      </div>

      <div className="search-filters">
        <div className="search-bar">
          <Search size={20} />
          <input
            type="text"
            placeholder="Search statutes by title, number, year..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="category-filter">
          <Filter size={20} />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            <option value="all">All Categories</option>
            {categories.map(category => (
              <option key={category} value={category}>
                {category.replace(/_/g, ' ').toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="statutes-grid">
        {filteredStatutes.map((statute, index) => (
          <motion.div
            key={statute.id}
            className="statute-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
          >
            <div className="statute-header">
              <Book size={24} />
              <span className="statute-number">{statute.number}</span>
            </div>

            <h3 className="statute-title">{statute.title}</h3>
            <p className="statute-description">{statute.description}</p>

            <div className="statute-meta">
              <span className="statute-year">Year: {statute.year}</span>
              <span className="statute-category">{statute.category}</span>
            </div>

            <div className="statute-actions">
              <button
                onClick={() => toggleBookmark(statute.id)}
                className={`bookmark-btn ${bookmarkedStatutes.includes(statute.id) ? 'active' : ''}`}
              >
                <Bookmark size={18} />
              </button>
              <button onClick={() => handleShare(statute)} className="share-btn">
                <Share2 size={18} />
              </button>
              <button onClick={() => handleDownload(statute)} className="download-btn">
                <Download size={18} />
              </button>
              <a href={`/statutes/${statute.id}`} className="view-btn">
                <ExternalLink size={18} />
                View
              </a>
            </div>
          </motion.div>
        ))}
      </div>

      {filteredStatutes.length === 0 && (
        <div className="no-results">
          <Search size={48} />
          <h3>No statutes found</h3>
          <p>Try adjusting your search criteria</p>
        </div>
      )}

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
};

export default StatutesPage;
