import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './components/ui/theme-provider';
import { Toaster } from './components/ui/sonner';

// Layouts
import MainLayout from './layouts/MainLayout';
import AuthLayout from './layouts/AuthLayout';

// Pages
import HomePage from './pages/HomePage';
import SearchPage from './pages/SearchPage';
import CaselawSearchPage from './pages/CaselawSearchPage';
import AdvancedCaselawSearch from './pages/AdvancedCaselawSearch';
import StatuteExplorerPage from './pages/StatuteExplorerPage';
import CaseDetailPage from './pages/CaseDetailPage';
import StatuteDetailPage from './pages/StatuteDetailPage';
import CitationChecker from './pages/CitationChecker';
import HeadNotesPage from './pages/HeadNotesPage';
import ExportBriefPage from './pages/ExportBriefPage';
import ContractGeneratorPage from './pages/ContractGeneratorPage';
import AICaseFinderPage from './pages/AICaseFinderPage';
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import FulltextSearchPage from './pages/FulltextSearchPage';
import MonthlyJournalsPage from './pages/MonthlyJournalsPage';
import MonthlyDigestPage from './pages/MonthlyDigestPage';
import MatterManager from './pages/MatterManager';
import PitchDeckPage from './pages/PitchDeckPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import SettingsPage from './pages/SettingsPage';
import HistoryPage from './pages/HistoryPage';
import FavoritesPage from './pages/FavoritesPage';
import LegalDictionary from './pages/LegalDictionary';
import CitationsPage from './pages/CitationsPage';
import CitationMapPage from './pages/CitationMapPage';
import ReadingListPage from './pages/ReadingListPage';
import AdvancedSearchPage from './pages/AdvancedSearchPage';
import AnalyticsPage from './pages/AnalyticsPage';
import WidgetsPage from './pages/WidgetsPage';
import SitemapPage from './pages/SitemapPage';
import ContactPage from './pages/ContactPage';
import ForumPage from './pages/ForumPage';
import BlogPage from './pages/BlogPage';
import HelpCenterPage from './pages/HelpCenterPage';
import ApiDocsPage from './pages/ApiDocsPage';
import EnterprisePage from './pages/EnterprisePage';
import UploadPage from './pages/UploadPage';
import AdvancedCaselawSearchNew from './pages/AdvancedCaselawSearchNew';
import ErrorBoundary from './components/ErrorBoundary';

// Components
import { AuthProvider } from './components/AuthProvider';
import PrivateRoute from './components/PrivateRoute';
import LoadingScreen from './components/LoadingScreen';
import ScrollToTop from './components/ScrollToTop';

// Services
import { authService } from './services/authService';

function App() {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const user = await authService.getCurrentUser();
        setAuthenticated(!!user);
      } catch (error) {
        setAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <ThemeProvider defaultTheme="light" storageKey="pakistan-law-app-theme">
      <AuthProvider>
        <Router>
          <ScrollToTop />
          <ErrorBoundary>
            <Routes>
              {/* Auth Routes */}
              <Route element={<AuthLayout />}>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
              </Route>

              {/* Main Routes */}
              <Route element={<MainLayout />}>
                <Route path="/" element={<HomePage />} />
                <Route path="/search" element={<SearchPage />} />
                <Route path="/caselaw-search" element={<CaselawSearchPage />} />
                <Route path="/advanced-caselaw-search" element={<AdvancedCaselawSearch />} />
                <Route path="/advanced-caselaw-search-new" element={<AdvancedCaselawSearchNew />} />
                <Route path="/statute-explorer" element={<StatuteExplorerPage />} />
                <Route path="/case/:id" element={<CaseDetailPage />} />
                <Route path="/statute/:id" element={<StatuteDetailPage />} />
                <Route path="/citation-checker" element={<CitationChecker />} />
                <Route path="/citations" element={<CitationsPage />} />
                <Route path="/citation-map" element={<CitationMapPage />} />
                <Route path="/headnotes/:id" element={<HeadNotesPage />} />
                <Route path="/export-brief" element={<ExportBriefPage />} />
                <Route path="/contract-generator" element={<ContractGeneratorPage />} />
                <Route path="/ai-case-finder" element={<AICaseFinderPage />} />
                <Route path="/analytics" element={<AnalyticsDashboard />} />
                <Route path="/fulltext-search" element={<FulltextSearchPage />} />
                <Route path="/monthly-journals" element={<MonthlyJournalsPage />} />
                <Route path="/monthly-digest" element={<MonthlyDigestPage />} />
                <Route path="/legal-dictionary" element={<LegalDictionary />} />
                <Route path="/reading-list" element={<ReadingListPage />} />
                <Route path="/advanced-search" element={<AdvancedSearchPage />} />
                <Route path="/analytics-dashboard" element={<AnalyticsPage />} />
                <Route path="/widgets" element={<WidgetsPage />} />
                <Route path="/sitemap" element={<SitemapPage />} />
                <Route path="/contact" element={<ContactPage />} />
                <Route path="/forum" element={<ForumPage />} />
                <Route path="/blog" element={<BlogPage />} />
                <Route path="/help" element={<HelpCenterPage />} />
                <Route path="/api-docs" element={<ApiDocsPage />} />
                <Route path="/enterprise" element={<EnterprisePage />} />
                <Route path="/upload" element={<UploadPage />} />
                <Route path="/pitch-deck" element={<PitchDeckPage />} />
                
                {/* Protected Routes */}
                <Route element={<PrivateRoute />}>
                  <Route path="/profile" element={<ProfilePage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                  <Route path="/history" element={<HistoryPage />} />
                  <Route path="/favorites" element={<FavoritesPage />} />
                  <Route path="/matters" element={<MatterManager />} />
                </Route>
              </Route>

              {/* Catch-all */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </ErrorBoundary>
          <Toaster />
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
