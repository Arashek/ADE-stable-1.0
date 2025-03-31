import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import {
  FaHome,
  FaProjectDiagram,
  FaTasks,
  FaRobot,
  FaCog,
  FaBars,
  FaTimes,
  FaUser,
  FaChevronDown,
  FaChevronRight,
  FaSignOutAlt,
} from 'react-icons/fa';
import { useAuth } from '../../contexts/AuthContext';

const SidebarContainer = styled.div`
  background-color: #212936;
  color: white;
  height: 100vh;
  width: ${props => (props.isCollapsed ? '60px' : '250px')};
  transition: width 0.3s ease;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
`;

const LogoContainer = styled.div`
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
`;

const LogoText = styled.span`
  opacity: ${props => (props.isCollapsed ? '0' : '1')};
  transition: opacity 0.3s ease;
`;

const ToggleButton = styled.button`
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: auto;
  transition: transform 0.3s ease;

  &:hover {
    color: #60a5fa;
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.5);
    border-radius: 4px;
  }
`;

const NavItems = styled.nav`
  padding: 20px 0;
  flex: 1;
  overflow-y: auto;
`;

const NavItem = styled(Link)`
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: ${props => (props.active ? '#60a5fa' : 'rgba(255, 255, 255, 0.7)')};
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
  white-space: nowrap;
  overflow: hidden;

  &:hover {
    color: #60a5fa;
    background-color: rgba(255, 255, 255, 0.1);
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.5);
    border-radius: 4px;
  }

  &.active {
    background-color: rgba(96, 165, 250, 0.1);
  }
`;

const NestedNavItem = styled.div`
  padding: 12px 20px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.3s ease;

  &:hover {
    color: #60a5fa;
    background-color: rgba(255, 255, 255, 0.1);
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.5);
    border-radius: 4px;
  }
`;

const NestedItems = styled.div`
  background-color: rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: max-height 0.3s ease;
  max-height: ${props => (props.isOpen ? '500px' : '0')};
`;

const IconWrapper = styled.div`
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
`;

const ItemText = styled.span`
  margin-left: 12px;
  opacity: ${props => (props.isCollapsed ? '0' : '1')};
  transition: opacity 0.3s ease;
`;

const ActiveIndicator = styled.div`
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 24px;
  background-color: #60a5fa;
  border-radius: 0 3px 3px 0;
  opacity: ${props => (props.active ? '1' : '0')};
`;

const UserProfile = styled.div`
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 12px;
`;

const UserInfo = styled.div`
  flex: 1;
  min-width: 0;
`;

const UserName = styled.div`
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const UserEmail = styled.div`
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const LogoutButton = styled.button`
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.3s ease;

  &:hover {
    color: #ef4444;
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.5);
    border-radius: 4px;
  }
`;

const navigationItems = [
  { path: '/dashboard', icon: <FaHome />, text: 'Dashboard' },
  {
    path: '/projects',
    icon: <FaProjectDiagram />,
    text: 'Projects',
    nested: [
      { path: '/projects/active', text: 'Active Projects' },
      { path: '/projects/archived', text: 'Archived Projects' },
      { path: '/projects/templates', text: 'Templates' },
    ],
  },
  {
    path: '/tasks',
    icon: <FaTasks />,
    text: 'Tasks',
    nested: [
      { path: '/tasks/todo', text: 'To Do' },
      { path: '/tasks/in-progress', text: 'In Progress' },
      { path: '/tasks/completed', text: 'Completed' },
    ],
  },
  { path: '/agents', icon: <FaRobot />, text: 'Agents' },
  { path: '/settings', icon: <FaCog />, text: 'Settings' },
];

const Sidebar = ({ isOpen, onToggle }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [openNestedItems, setOpenNestedItems] = useState({});
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const sidebarRef = useRef(null);

  // Handle responsive behavior
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setIsCollapsed(true);
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onToggle();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onToggle]);

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
    onToggle();
  };

  const toggleNestedItems = (path) => {
    setOpenNestedItems(prev => ({
      ...prev,
      [path]: !prev[path],
    }));
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const renderNavItem = (item) => {
    const isActive = location.pathname === item.path;
    const hasNested = item.nested && item.nested.length > 0;
    const isNestedActive = hasNested && item.nested.some(nested => 
      location.pathname.startsWith(nested.path)
    );

    if (hasNested) {
      return (
        <div key={item.path}>
          <NestedNavItem
            onClick={() => toggleNestedItems(item.path)}
            tabIndex={0}
            role="button"
            aria-expanded={openNestedItems[item.path]}
          >
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <IconWrapper>{item.icon}</IconWrapper>
              <ItemText isCollapsed={isCollapsed}>{item.text}</ItemText>
            </div>
            {!isCollapsed && (
              <FaChevronRight
                style={{
                  transform: openNestedItems[item.path] ? 'rotate(90deg)' : 'none',
                  transition: 'transform 0.3s ease',
                }}
              />
            )}
          </NestedNavItem>
          <NestedItems isOpen={openNestedItems[item.path]}>
            {item.nested.map(nested => (
              <NavItem
                key={nested.path}
                to={nested.path}
                active={location.pathname === nested.path}
                className={location.pathname === nested.path ? 'active' : ''}
                style={{ paddingLeft: '48px' }}
              >
                <ActiveIndicator active={location.pathname === nested.path} />
                <ItemText isCollapsed={isCollapsed}>{nested.text}</ItemText>
              </NavItem>
            ))}
          </NestedItems>
        </div>
      );
    }

    return (
      <NavItem
        key={item.path}
        to={item.path}
        active={isActive}
        className={isActive ? 'active' : ''}
      >
        <ActiveIndicator active={isActive} />
        <IconWrapper>{item.icon}</IconWrapper>
        <ItemText isCollapsed={isCollapsed}>{item.text}</ItemText>
      </NavItem>
    );
  };

  return (
    <SidebarContainer isCollapsed={isCollapsed} ref={sidebarRef}>
      <LogoContainer>
        <Logo>
          <IconWrapper>
            <FaRobot />
          </IconWrapper>
          <LogoText isCollapsed={isCollapsed}>ADE Platform</LogoText>
        </Logo>
        <ToggleButton onClick={toggleSidebar}>
          {isCollapsed ? <FaBars /> : <FaTimes />}
        </ToggleButton>
      </LogoContainer>

      <NavItems>
        {navigationItems.map(renderNavItem)}
      </NavItems>

      {!isCollapsed && user && (
        <UserProfile>
          <IconWrapper>
            <FaUser />
          </IconWrapper>
          <UserInfo>
            <UserName>{user.name}</UserName>
            <UserEmail>{user.email}</UserEmail>
          </UserInfo>
          <LogoutButton onClick={handleLogout}>
            <FaSignOutAlt />
          </LogoutButton>
        </UserProfile>
      )}
    </SidebarContainer>
  );
};

export default Sidebar; 