# Admin Context

This directory contains the context providers and utilities for the admin interface, focusing on user authentication, permissions, and audit logging.

## Components

### UserContext

`UserContext.jsx` provides a comprehensive context for managing user authentication and permissions:

#### Features
- User authentication state management
- Permission checking utilities
- Role-based component rendering
- Audit logging system

#### Permission System
- Hierarchical permission structure
- Role-based permission mapping
- Permission checking hooks
- Permission-based component rendering

#### Audit Logging
- Comprehensive action logging
- User activity tracking
- Security event monitoring
- Operation history

## Usage

### Setting up the Context

```jsx
import { UserProvider } from './context/UserContext';

function App() {
  return (
    <UserProvider>
      <AdminPanel />
    </UserProvider>
  );
}
```

### Using Permissions

```jsx
import { useUser, RequirePermission } from './context/UserContext';

function MyComponent() {
  const { hasPermission } = useUser();
  
  if (!hasPermission('some.permission')) {
    return null;
  }
  
  return <div>Protected Content</div>;
}
```

### Using Permission-Based Components

```jsx
import { RequirePermission } from './context/UserContext';

function MyComponent() {
  return (
    <RequirePermission permission="some.permission">
      <div>Protected Content</div>
    </RequirePermission>
  );
}
```

### Audit Logging

```jsx
import { useUser } from './context/UserContext';

function MyComponent() {
  const { logAuditEvent } = useUser();
  
  const handleAction = () => {
    logAuditEvent('ACTION_NAME', {
      // Additional context
    });
  };
}
```

## Available Permissions

### Operations
- `operations.view`
- `operations.users.view`
- `operations.users.edit`
- `operations.deployments.view`
- `operations.deployments.edit`

### Security
- `security.view`
- `security.access.view`
- `security.access.edit`
- `security.data.view`
- `security.data.edit`

### Architecture
- `architecture.view`
- `architecture.components.view`
- `architecture.components.edit`
- `architecture.components.deploy`
- `architecture.components.delete`
- `architecture.components.monitor`
- `architecture.models.view`
- `architecture.models.edit`
- `architecture.models.deploy`

### Integrations
- `integrations.view`
- `integrations.services.view`
- `integrations.services.edit`
- `integrations.services.delete`
- `integrations.marketplace.view`
- `integrations.marketplace.edit`
- `integrations.marketplace.delete`

## Dependencies

- React Context API
- React Router for navigation
- Material-UI for components
- Authentication service
- Audit logging service 