import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline, Box, styled } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import theme from './theme';

// Components
import Header from './components/common/Header';
import Sidebar from './components/common/Sidebar';
import CommandHub from './components/dashboard/CommandHub';

// Pages (to be created)
const CodeEditor = () => <div>Code Editor</div>;
const Terminal = () => <div>Terminal</div>;
const Settings = () => <div>Settings</div>;
const Login = () => <div>Login</div>;

const queryClient = new QueryClient();

const MainLayout = styled(Box)(({ theme }) => ({
  display: 'flex',
  minHeight: '100vh',
  backgroundColor: '#f5f7f9',
}));

const ContentWrapper = styled(Box)<{ open: boolean }>(({ theme, open }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
  marginLeft: open ? 260 : 73,
  marginTop: 64,
  transition: theme.transitions.create(['margin', 'width'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
}));

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  return <>{children}</>;
};

const App: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AuthProvider>
          <BrowserRouter>
            <MainLayout>
              <Header />
              <Sidebar open={sidebarOpen} onToggle={toggleSidebar} />
              <ContentWrapper open={sidebarOpen}>
                <Routes>
                  <Route
                    path="/"
                    element={
                      <PrivateRoute>
                        <CommandHub />
                      </PrivateRoute>
                    }
                  />
                  <Route
                    path="/code"
                    element={
                      <PrivateRoute>
                        <CodeEditor />
                      </PrivateRoute>
                    }
                  />
                  <Route
                    path="/terminal"
                    element={
                      <PrivateRoute>
                        <Terminal />
                      </PrivateRoute>
                    }
                  />
                  <Route
                    path="/settings"
                    element={
                      <PrivateRoute>
                        <Settings />
                      </PrivateRoute>
                    }
                  />
                  <Route path="/login" element={<Login />} />
                </Routes>
              </ContentWrapper>
            </MainLayout>
          </BrowserRouter>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App; 