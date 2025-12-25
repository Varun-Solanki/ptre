import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import LandingPage from './pages/LandingPage';
import DashboardPage from './pages/DashboardPage';
import SystemPage from './pages/SystemPage';

import FeaturesPage from './pages/FeaturesPage';
import LabelsPage from './pages/LabelsPage';
import ExplanationPage from './pages/ExplanationPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<LandingPage />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="features" element={<FeaturesPage />} />
          <Route path="labels" element={<LabelsPage />} />
          <Route path="system" element={<SystemPage />} />
          <Route path="explanation" element={<ExplanationPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
