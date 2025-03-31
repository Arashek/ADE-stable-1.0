import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

// Mock user roles and permissions - Replace with actual data from your backend
const ROLES = {
  OWNER: 'owner',
  ADMIN: 'admin',
  OPERATOR: 'operator',
  VIEWER: 'viewer',
};

const PERMISSIONS = {
  // Operations permissions
  MANAGE_USERS: 'operations.users.manage',
  VIEW_USERS: 'operations.users.view',
  MANAGE_DEPLOYMENTS: 'operations.deployments.manage',
  VIEW_DEPLOYMENTS: 'operations.deployments.view',
  
  // Security permissions
  MANAGE_ACCESS: 'security.access.manage',
  VIEW_ACCESS: 'security.access.view',
  MANAGE_DATA: 'security.data.manage',
  VIEW_DATA: 'security.data.view',
  
  // Architecture permissions
  MANAGE_COMPONENTS: 'architecture.components.manage',
  VIEW_COMPONENTS: 'architecture.components.view',
  MANAGE_MODELS: 'architecture.models.manage',
  VIEW_MODELS: 'architecture.models.view',
  
  // Integration permissions
  MANAGE_SERVICES: 'integrations.services.manage',
  VIEW_SERVICES: 'integrations.services.view',
  MANAGE_MARKETPLACE: 'integrations.marketplace.manage',
  VIEW_MARKETPLACE: 'integrations.marketplace.view',
};

// Role-based permission mapping
const ROLE_PERMISSIONS = {
  [ROLES.OWNER]: Object.values(PERMISSIONS),
  [ROLES.ADMIN]: [
    PERMISSIONS.MANAGE_USERS,
    PERMISSIONS.VIEW_USERS,
    PERMISSIONS.MANAGE_DEPLOYMENTS,
    PERMISSIONS.VIEW_DEPLOYMENTS,
    PERMISSIONS.VIEW_ACCESS,
    PERMISSIONS.VIEW_DATA,
    PERMISSIONS.MANAGE_COMPONENTS,
    PERMISSIONS.VIEW_COMPONENTS,
    PERMISSIONS.MANAGE_MODELS,
    PERMISSIONS.VIEW_MODELS,
    PERMISSIONS.MANAGE_SERVICES,
    PERMISSIONS.VIEW_SERVICES,
    PERMISSIONS.MANAGE_MARKETPLACE,
    PERMISSIONS.VIEW_MARKETPLACE,
  ],
  [ROLES.OPERATOR]: [
    PERMISSIONS.VIEW_USERS,
    PERMISSIONS.MANAGE_DEPLOYMENTS,
    PERMISSIONS.VIEW_DEPLOYMENTS,
    PERMISSIONS.VIEW_ACCESS,
    PERMISSIONS.VIEW_DATA,
    PERMISSIONS.VIEW_COMPONENTS,
    PERMISSIONS.VIEW_MODELS,
    PERMISSIONS.VIEW_SERVICES,
    PERMISSIONS.VIEW_MARKETPLACE,
  ],
  [ROLES.VIEWER]: [
    PERMISSIONS.VIEW_USERS,
    PERMISSIONS.VIEW_DEPLOYMENTS,
    PERMISSIONS.VIEW_ACCESS,
    PERMISSIONS.VIEW_DATA,
    PERMISSIONS.VIEW_COMPONENTS,
    PERMISSIONS.VIEW_MODELS,
    PERMISSIONS.VIEW_SERVICES,
    PERMISSIONS.VIEW_MARKETPLACE,
  ],
};

const UserContext = createContext(null);

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Mock authentication check - Replace with actual authentication logic
    const checkAuth = async () => {
      try {
        // Simulate API call to check authentication
        const mockUserData = {
          id: '1',
          name: 'John Doe',
          email: 'john.doe@example.com',
          role: ROLES.OWNER,
          permissions: ROLE_PERMISSIONS[ROLES.OWNER],
          lastLogin: new Date().toISOString(),
        };
        setUser(mockUserData);
      } catch (error) {
        console.error('Authentication check failed:', error);
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [navigate]);

  const login = async (credentials) => {
    try {
      // Implement actual login logic here
      const mockUserData = {
        id: '1',
        name: 'John Doe',
        email: 'john.doe@example.com',
        role: ROLES.OWNER,
        permissions: ROLE_PERMISSIONS[ROLES.OWNER],
        lastLogin: new Date().toISOString(),
      };
      setUser(mockUserData);
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const logout = async () => {
    try {
      // Implement actual logout logic here
      setUser(null);
      navigate('/login');
      return true;
    } catch (error) {
      console.error('Logout failed:', error);
      return false;
    }
  };

  const hasPermission = (permission) => {
    if (!user) return false;
    return user.permissions.includes(permission);
  };

  const hasAnyPermission = (permissions) => {
    if (!user) return false;
    return permissions.some(permission => user.permissions.includes(permission));
  };

  const hasAllPermissions = (permissions) => {
    if (!user) return false;
    return permissions.every(permission => user.permissions.includes(permission));
  };

  const isOwner = () => {
    return user?.role === ROLES.OWNER;
  };

  const isAdmin = () => {
    return user?.role === ROLES.ADMIN;
  };

  const isOperator = () => {
    return user?.role === ROLES.OPERATOR;
  };

  const isViewer = () => {
    return user?.role === ROLES.VIEWER;
  };

  const logAuditEvent = async (action, details) => {
    try {
      // Implement actual audit logging logic here
      const auditEvent = {
        userId: user?.id,
        action,
        details,
        timestamp: new Date().toISOString(),
      };
      console.log('Audit Event:', auditEvent);
      // Send to audit log service
    } catch (error) {
      console.error('Failed to log audit event:', error);
    }
  };

  const value = {
    user,
    loading,
    login,
    logout,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    isOwner,
    isAdmin,
    isOperator,
    isViewer,
    logAuditEvent,
    ROLES,
    PERMISSIONS,
  };

  if (loading) {
    return <div>Loading...</div>; // Replace with proper loading component
  }

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

// Higher-order component for permission-based rendering
export const withPermission = (WrappedComponent, requiredPermission) => {
  return function WithPermissionComponent(props) {
    const { hasPermission } = useUser();
    
    if (!hasPermission(requiredPermission)) {
      return null;
    }
    
    return <WrappedComponent {...props} />;
  };
};

// Higher-order component for role-based rendering
export const withRole = (WrappedComponent, requiredRole) => {
  return function WithRoleComponent(props) {
    const { user } = useUser();
    
    if (!user || user.role !== requiredRole) {
      return null;
    }
    
    return <WrappedComponent {...props} />;
  };
};

// Component for conditional rendering based on permissions
export const RequirePermission = ({ permission, children }) => {
  const { hasPermission } = useUser();
  
  if (!hasPermission(permission)) {
    return null;
  }
  
  return children;
};

// Component for conditional rendering based on roles
export const RequireRole = ({ role, children }) => {
  const { user } = useUser();
  
  if (!user || user.role !== role) {
    return null;
  }
  
  return children;
}; 