import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import styled from 'styled-components';
import Sidebar from './components/common/Sidebar';
import Header from './components/common/Header';
import Layout from './components/layout/Layout';

// Page Components
import DashboardPage from './pages/DashboardPage';
import ProjectsPage from './pages/ProjectsPage';
import TasksPage from './pages/TasksPage';
import AgentsPage from './pages/AgentsPage';
import SettingsPage from './pages/SettingsPage';

// Context Providers
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';

const AppContainer = styled.div`
  min-height: 100vh;
  background-color: #f5f7f9;
`;

const App = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <Router>
      <ThemeProvider>
        <AuthProvider>
          <AppContainer>
            <Layout>
              <Sidebar isOpen={isSidebarOpen} onToggle={toggleSidebar} />
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <Header title="ADE Platform" />
                <main style={{ flex: 1, padding: '24px' }}>
                  <Routes>
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="/dashboard" element={<DashboardPage />} />
                    <Route path="/projects/*" element={<ProjectsPage />} />
                    <Route path="/tasks/*" element={<TasksPage />} />
                    <Route path="/agents/*" element={<AgentsPage />} />
                    <Route path="/settings/*" element={<SettingsPage />} />
                  </Routes>
                </main>
              </div>
            </Layout>
          </AppContainer>
        </AuthProvider>
      </ThemeProvider>
    </Router>
  );
};

export default App; 