import React from 'react';
import styled from 'styled-components';
import Sidebar from '../common/Sidebar';

const LayoutContainer = styled.div`
  display: flex;
  min-height: 100vh;
`;

const MainContent = styled.main`
  flex: 1;
  margin-left: ${props => (props.isCollapsed ? '60px' : '250px')};
  transition: margin-left 0.3s ease;
  padding: 24px;
  background-color: #f8fafc;
  min-height: 100vh;

  @media (max-width: 768px) {
    margin-left: 0;
  }
`;

const Overlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
  opacity: ${props => (props.isVisible ? '1' : '0')};
  visibility: ${props => (props.isVisible ? 'visible' : 'hidden')};
  transition: opacity 0.3s ease, visibility 0.3s ease;

  @media (min-width: 769px) {
    display: none;
  }
`;

const Layout = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);

  const handleOverlayClick = () => {
    setIsSidebarOpen(false);
  };

  return (
    <LayoutContainer>
      <Sidebar 
        isOpen={isSidebarOpen} 
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
      />
      <Overlay 
        isVisible={isSidebarOpen} 
        onClick={handleOverlayClick}
      />
      <MainContent isCollapsed={!isSidebarOpen}>
        {children}
      </MainContent>
    </LayoutContainer>
  );
};

export default Layout; 