import React from 'react';
import { Routes, Route } from 'react-router-dom';
import HomePage from '../pages/HomePage';
import SearchPage from '../pages/SearchPage';
import CasePage from '../pages/CasePage';
import StatutePage from '../pages/StatutePage';
import AboutPage from '../pages/AboutPage';
import NotFoundPage from '../pages/NotFoundPage';

const MainContent = () => {
  return (
    <main className="flex-1 container mx-auto px-4 py-6">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/search/:query" element={<SearchPage />} />
        <Route path="/case/:id" element={<CasePage />} />
        <Route path="/statute/:id" element={<StatutePage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </main>
  );
};

export default MainContent;
