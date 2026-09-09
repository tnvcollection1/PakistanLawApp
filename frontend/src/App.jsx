import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SidebarLayout from './components/SidebarLayout';
import HomePage from './pages/HomePage';
import CitationSearchPage from './pages/CitationSearchPage';
import CasesPage from './pages/CasesPage';
import CourtsPage from './pages/CourtsPage';
import LawsPage from './pages/LawsPage';
import JournalsPage from './pages/JournalsPage';
import LawBotPage from './pages/LawBotPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/lawbot" element={<LawBotPage />} />
        <Route path="*" element={
          <SidebarLayout>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/citation-search" element={<CitationSearchPage />} />
              <Route path="/cases" element={<CasesPage />} />
              <Route path="/courts" element={<CourtsPage />} />
              <Route path="/laws" element={<LawsPage />} />
              <Route path="/journals" element={<JournalsPage />} />
            </Routes>
          </SidebarLayout>
        } />
      </Routes>
    </Router>
  );
}

export default App;
