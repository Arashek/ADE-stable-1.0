import { DesignSystem, DesignSuggestion } from '../types/design';

export const mockDesignTheme = {
  colors: {
    primary: '#1976d2',
    secondary: '#dc004e',
    background: '#f5f5f5',
    surface: '#ffffff',
    error: '#f44336',
    text: '#212121',
    textSecondary: '#757575'
  },
  typography: {
    fontFamily: 'Roboto, "Helvetica Neue", Arial, sans-serif',
    fontSize: 16,
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
      lineHeight: 1.2,
      letterSpacing: '-0.01562em'
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
      lineHeight: 1.2,
      letterSpacing: '-0.00833em'
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
      lineHeight: 1.2,
      letterSpacing: '0em'
    },
    body: {
      fontSize: '1rem',
      fontWeight: 400,
      lineHeight: 1.5,
      letterSpacing: '0.00938em'
    }
  },
  spacing: {
    unit: 8,
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32
  },
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 16
  },
  breakpoints: {
    xs: 0,
    sm: 600,
    md: 960,
    lg: 1280,
    xl: 1920
  },
  shadows: [
    'none',
    '0px 2px 1px -1px rgba(0,0,0,0.2),0px 1px 1px 0px rgba(0,0,0,0.14),0px 1px 3px 0px rgba(0,0,0,0.12)',
    '0px 3px 1px -2px rgba(0,0,0,0.2),0px 2px 2px 0px rgba(0,0,0,0.14),0px 1px 5px 0px rgba(0,0,0,0.12)',
    '0px 5px 5px -3px rgba(0,0,0,0.2),0px 8px 10px 1px rgba(0,0,0,0.14),0px 3px 14px 2px rgba(0,0,0,0.12)'
  ],
  transitions: {
    duration: {
      short: 250,
      standard: 300,
      complex: 375
    },
    easing: {
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)'
    }
  }
};

export const mockComponents = [
  {
    id: 'comp-1',
    name: 'Header',
    type: 'CONTAINER',
    properties: {
      flex: true,
      direction: 'row',
      justify: 'space-between',
      align: 'center'
    },
    styles: {
      padding: '16px',
      backgroundColor: '#ffffff',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    },
    pageId: 'page-1',
    children: ['comp-2', 'comp-3']
  },
  {
    id: 'comp-2',
    name: 'Logo',
    type: 'IMAGE',
    properties: {
      src: '/logo.png',
      alt: 'Company Logo',
      width: '120px'
    },
    styles: {
      margin: '0'
    },
    pageId: 'page-1',
    parentId: 'comp-1'
  },
  {
    id: 'comp-3',
    name: 'Navigation',
    type: 'CONTAINER',
    properties: {
      flex: true,
      direction: 'row',
      gap: '16px'
    },
    styles: {},
    pageId: 'page-1',
    parentId: 'comp-1',
    children: ['comp-4', 'comp-5', 'comp-6']
  },
  {
    id: 'comp-4',
    name: 'Home Link',
    type: 'LINK',
    properties: {
      text: 'Home',
      href: '/'
    },
    styles: {
      color: '#1976d2',
      fontWeight: '500',
      textDecoration: 'none'
    },
    pageId: 'page-1',
    parentId: 'comp-3'
  },
  {
    id: 'comp-5',
    name: 'About Link',
    type: 'LINK',
    properties: {
      text: 'About',
      href: '/about'
    },
    styles: {
      color: '#1976d2',
      fontWeight: '500',
      textDecoration: 'none'
    },
    pageId: 'page-1',
    parentId: 'comp-3'
  },
  {
    id: 'comp-6',
    name: 'Contact Link',
    type: 'LINK',
    properties: {
      text: 'Contact',
      href: '/contact'
    },
    styles: {
      color: '#1976d2',
      fontWeight: '500',
      textDecoration: 'none'
    },
    pageId: 'page-1',
    parentId: 'comp-3'
  },
  {
    id: 'comp-7',
    name: 'Hero Section',
    type: 'CONTAINER',
    properties: {
      flex: true,
      direction: 'column',
      justify: 'center',
      align: 'center'
    },
    styles: {
      padding: '64px 16px',
      backgroundColor: '#f5f5f5',
      textAlign: 'center'
    },
    pageId: 'page-1',
    children: ['comp-8', 'comp-9', 'comp-10']
  },
  {
    id: 'comp-8',
    name: 'Hero Title',
    type: 'TEXT',
    properties: {
      text: 'Welcome to Our Platform',
      tag: 'h1'
    },
    styles: {
      fontSize: '2.5rem',
      color: '#212121',
      marginBottom: '16px'
    },
    pageId: 'page-1',
    parentId: 'comp-7'
  },
  {
    id: 'comp-9',
    name: 'Hero Description',
    type: 'TEXT',
    properties: {
      text: 'Building the future of design and development',
      tag: 'p'
    },
    styles: {
      fontSize: '1.125rem',
      color: '#757575',
      marginBottom: '32px',
      maxWidth: '600px'
    },
    pageId: 'page-1',
    parentId: 'comp-7'
  },
  {
    id: 'comp-10',
    name: 'CTA Button',
    type: 'BUTTON',
    properties: {
      text: 'Get Started',
      variant: 'contained'
    },
    styles: {
      backgroundColor: '#1976d2',
      color: '#ffffff',
      padding: '12px 24px',
      borderRadius: '4px',
      fontWeight: '500',
      border: 'none',
      cursor: 'pointer'
    },
    pageId: 'page-1',
    parentId: 'comp-7'
  }
];

export const mockPages = [
  {
    id: 'page-1',
    name: 'Home',
    path: '/',
    components: ['comp-1', 'comp-7'],
    styles: [],
    layout: {
      type: 'flex',
      properties: {
        direction: 'column'
      }
    }
  },
  {
    id: 'page-2',
    name: 'About',
    path: '/about',
    components: ['comp-1'],
    styles: [],
    layout: {
      type: 'flex',
      properties: {
        direction: 'column'
      }
    }
  }
];

export const mockImplementation = {
  components: [
    {
      id: 'comp-1',
      code: `<header className="header-container">
  <img src="/logo.png" alt="Company Logo" className="logo" />
  <nav className="navigation">
    <a href="/" className="nav-link">Home</a>
    <a href="/about" className="nav-link">About</a>
    <a href="/contact" className="nav-link">Contact</a>
  </nav>
</header>`,
      dependencies: []
    },
    {
      id: 'comp-7',
      code: `<section className="hero-section">
  <h1 className="hero-title">Welcome to Our Platform</h1>
  <p className="hero-description">Building the future of design and development</p>
  <button className="cta-button">Get Started</button>
</section>`,
      dependencies: []
    }
  ],
  styles: [
    {
      id: 'global',
      code: `body {
  font-family: 'Roboto', 'Helvetica Neue', Arial, sans-serif;
  margin: 0;
  padding: 0;
  color: #212121;
  background-color: #f5f5f5;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.logo {
  width: 120px;
  margin: 0;
}

.navigation {
  display: flex;
  gap: 16px;
}

.nav-link {
  color: #1976d2;
  font-weight: 500;
  text-decoration: none;
}

.hero-section {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 64px 16px;
  background-color: #f5f5f5;
  text-align: center;
}

.hero-title {
  font-size: 2.5rem;
  color: #212121;
  margin-bottom: 16px;
}

.hero-description {
  font-size: 1.125rem;
  color: #757575;
  margin-bottom: 32px;
  max-width: 600px;
}

.cta-button {
  background-color: #1976d2;
  color: #ffffff;
  padding: 12px 24px;
  border-radius: 4px;
  font-weight: 500;
  border: none;
  cursor: pointer;
}`,
      dependencies: []
    }
  ],
  pages: [
    {
      id: 'page-1',
      code: `import React from 'react';

export default function HomePage() {
  return (
    <div className="home-page">
      <header className="header-container">
        <img src="/logo.png" alt="Company Logo" className="logo" />
        <nav className="navigation">
          <a href="/" className="nav-link">Home</a>
          <a href="/about" className="nav-link">About</a>
          <a href="/contact" className="nav-link">Contact</a>
        </nav>
      </header>
      <section className="hero-section">
        <h1 className="hero-title">Welcome to Our Platform</h1>
        <p className="hero-description">Building the future of design and development</p>
        <button className="cta-button">Get Started</button>
      </section>
    </div>
  );
}`,
      dependencies: ['react']
    }
  ],
  layout: {
    type: 'react',
    components: ['comp-1', 'comp-7']
  }
};

export const mockDesignSystem: DesignSystem = {
  id: 'design-1',
  name: 'Company Design System',
  components: mockComponents,
  styles: [
    {
      id: 'style-1',
      name: 'Primary Button',
      type: 'FILL',
      value: '#1976d2',
      scope: 'global'
    },
    {
      id: 'style-2',
      name: 'Heading Text',
      type: 'TEXT',
      value: '#212121',
      scope: 'global'
    }
  ],
  pages: mockPages,
  implementation: mockImplementation,
  metadata: {
    name: 'Company Design System',
    description: 'A modern design system for our web applications',
    version: '1.0.0',
    lastModified: '2025-03-31T01:00:00.000Z',
    createdBy: 'Design Team',
    showGrid: true,
    snapToGrid: true,
    gridSize: 8,
    snapThreshold: 4,
    exportWithComments: true,
    exportWithStyles: true
  },
  currentPage: 'page-1',
  theme: mockDesignTheme,
  version: '1.0.0'
};

export const mockDesignSuggestions: DesignSuggestion[] = [
  {
    id: 'suggestion-1',
    type: 'component',
    description: 'Improve accessibility by adding aria-label to navigation links',
    priority: 'high',
    component: {
      id: 'comp-4',
      name: 'Home Link',
      type: 'LINK',
      properties: {
        text: 'Home',
        href: '/',
        'aria-label': 'Navigate to home page'
      },
      styles: {
        color: '#1976d2',
        fontWeight: '500',
        textDecoration: 'none'
      },
      pageId: 'page-1',
      parentId: 'comp-3'
    },
    preview: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZAAAAGQAQAAAACDXm4AAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAAmJLR0QAAd2KE6QAAAAHdElNRQflAxQGMTmKdJxxAAADIklEQVRo3u3aS24kIQwGYJPLgAQXgPNydx6F2+UyiHMBieUsWWDS3f+MpNmMIp2eJYY2+YKg7GrFzVt4+/W5//y8tdYaxvb+/k73j8cNYFl7Y1+PBzTG97f714MsreH5+Kwe7qulD2/P58V1vPDe334/T+m3xrH3H+0Zuy8GPK5T8LFa39v2HE9v7TluxjHWsYOPBTw/l6sNfjyHbtOvazF8rJ7uXeJcpbVpvD8i3cdtGuPoxx6z6HGOpe/9+OKLr5OV3O9Jyc1mFLN1dkpOJYWZMdwshnlsyLOTY/HFF1984e8j+OD0nEuKlZXFuFlJuZuXmZEZg4FWY5jF9OiUYCbFF198naVMkrvZibrZFmFumYnzKZkZmcXmPAqzc5K/sH6CYYovvvjiazyHTspcUuaW6YwQzMhsmpKZGZm5l9SxI40JY2c6jy+++OLrPD1vvTUmpTNDW4aZ2zRdp+eYnpNJuZmbuc33Y8LQfGHFF198fYyyaUL4lNmSYeaahtCYpGCmacKY2TRNBYeOnYbDLsYXX3zxdZKSsZIyK8nJkrSYZMawMSNnS4aRZbYJY/MNJ7744ovvS3Q+JcCUoWmwZcoGDKbFplGG9pqG5KHzw2MrGdYMfWXDF198naVpCmxoSGqWJZn2jDK0Z5jx7CQjI48+r+Lz9vjii6+vWb9+tujY9HVzFRoaYxZsZp5lI3k2Mc/q+OKLH7XfCkfnSuO/bNhY5dXJ8pCp8B7eeTK+94fCYBXDF1988XWJPn22OL2+hhCYFgZYMDzYEAb/9YktgfDF10eOgm+fjT5e+RuOJTgRtMdrzgbO5mzzxfjii6+jlKGDZQMllgRY2TjLUsyw1NXr7vbZZN+YJfDFF198XaJzwZgmzGrUMM33pimDmaWmYXTOJhU2aBhe2cXwxRdffJ2kuanp1BmbMPTBIaXpmJb0GJz3DDK0mfni4osvvr5E5z2ju4emUQdpOtBMw+iajjBmZHMwcJ5dTK5s4Ysvvvi6RJdpaGfp8Nymfpg+WZqvLPdtmi7MNmVyzzDvnI0vvvji6zwVztbUYt4/HK0N8YeNkRa4FnzxxdcX6j/JGXVr/LhJGgAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAyMS0wMy0yMFQwNjo0OTo1NyswMDowMIylP0QAAAAldEVYdGRhdGU6bW9kaWZ5ADIwMjEtMDMtMjBUMDY6NDk6NTcrMDA6MDD9+If4AAAAAElFTkSuQmCC'
  },
  {
    id: 'suggestion-2',
    type: 'theme',
    description: 'Adjust color contrast for better accessibility',
    priority: 'medium',
    styles: {
      colors: {
        primary: '#0d47a1',
        secondary: '#c2185b',
        text: '#121212'
      }
    },
    preview: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZAAAAGQAQAAAACDXm4AAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAAmJLR0QAAd2KE6QAAAAHdElNRQflAxQGMTmKdJxxAAADIklEQVRo3u3aS24kIQwGYJPLgAQXgPNydx6F2+UyiHMBieUsWWDS3f+MpNmMIp2eJYY2+YKg7GrFzVt4+/W5//y8tdYaxvb+/k73j8cNYFl7Y1+PBzTG97f714MsreH5+Kwe7qulD2/P58V1vPDe334/T+m3xrH3H+0Zuy8GPK5T8LFa39v2HE9v7TluxjHWsYOPBTw/l6sNfjyHbtOvazF8rJ7uXeJcpbVpvD8i3cdtGuPoxx6z6HGOpe/9+OKLr5OV3O9Jyc1mFLN1dkpOJYWZMdwshnlsyLOTY/HFF1984e8j+OD0nEuKlZXFuFlJuZuXmZEZg4FWY5jF9OiUYCbFF198naVMkrvZibrZFmFumYnzKZkZmcXmPAqzc5K/sH6CYYovvvjiazyHTspcUuaW6YwQzMhsmpKZGZm5l9SxI40JY2c6jy+++OLrPD1vvTUmpTNDW4aZ2zRdp+eYnpNJuZmbuc33Y8LQfGHFF198fYyyaUL4lNmSYeaahtCYpGCmacKY2TRNBYeOnYbDLsYXX3zxdZKSsZIyK8nJkrSYZMawMSNnS4aRZbYJY/MNJ7744ovvS3Q+JcCUoWmwZcoGDKbFplGG9pqG5KHzw2MrGdYMfWXDF198naVpCmxoSGqWJZn2jDK0Z5jx7CQjI48+r+Lz9vjii6+vWb9+tujY9HVzFRoaYxZsZp5lI3k2Mc/q+OKLH7XfCkfnSuO/bNhY5dXJ8pCp8B7eeTK+94fCYBXDF1988XWJPn22OL2+hhCYFgZYMDzYEAb/9YktgfDF10eOgm+fjT5e+RuOJTgRtMdrzgbO5mzzxfjii6+jlKGDZQMllgRY2TjLUsyw1NXr7vbZZN+YJfDFF198XaJzwZgmzGrUMM33pimDmaWmYXTOJhU2aBhe2cXwxRdffJ2kuanp1BmbMPTBIaXpmJb0GJz3DDK0mfni4osvvr5E5z2ju4emUQdpOtBMw+iajjBmZHMwcJ5dTK5s4Ysvvvi6RJdpaGfp8Nymfpg+WZqvLPdtmi7MNmVyzzDvnI0vvvji6zwVztbUYt4/HK0N8YeNkRa4FnzxxdcX6j/JGXVr/LhJGgAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAyMS0wMy0yMFQwNjo0OTo1NyswMDowMIylP0QAAAAldEVYdGRhdGU6bW9kaWZ5ADIwMjEtMDMtMjBUMDY6NDk6NTcrMDA6MDD9+If4AAAAAElFTkSuQmCC'
  },
  {
    id: 'suggestion-3',
    type: 'layout',
    description: 'Improve mobile responsiveness by adjusting hero section padding',
    priority: 'low',
    layout: {
      componentId: 'comp-7',
      updates: {
        styles: {
          padding: '32px 16px'
        }
      }
    },
    preview: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZAAAAGQAQAAAACDXm4AAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAAmJLR0QAAd2KE6QAAAAHdElNRQflAxQGMTmKdJxxAAADIklEQVRo3u3aS24kIQwGYJPLgAQXgPNydx6F2+UyiHMBieUsWWDS3f+MpNmMIp2eJYY2+YKg7GrFzVt4+/W5//y8tdYaxvb+/k73j8cNYFl7Y1+PBzTG97f714MsreH5+Kwe7qulD2/P58V1vPDe334/T+m3xrH3H+0Zuy8GPK5T8LFa39v2HE9v7TluxjHWsYOPBTw/l6sNfjyHbtOvazF8rJ7uXeJcpbVpvD8i3cdtGuPoxx6z6HGOpe/9+OKLr5OV3O9Jyc1mFLN1dkpOJYWZMdwshnlsyLOTY/HFF1984e8j+OD0nEuKlZXFuFlJuZuXmZEZg4FWY5jF9OiUYCbFF198naVMkrvZibrZFmFumYnzKZkZmcXmPAqzc5K/sH6CYYovvvjiazyHTspcUuaW6YwQzMhsmpKZGZm5l9SxI40JY2c6jy+++OLrPD1vvTUmpTNDW4aZ2zRdp+eYnpNJuZmbuc33Y8LQfGHFF198fYyyaUL4lNmSYeaahtCYpGCmacKY2TRNBYeOnYbDLsYXX3zxdZKSsZIyK8nJkrSYZMawMSNnS4aRZbYJY/MNJ7744ovvS3Q+JcCUoWmwZcoGDKbFplGG9pqG5KHzw2MrGdYMfWXDF198naVpCmxoSGqWJZn2jDK0Z5jx7CQjI48+r+Lz9vjii6+vWb9+tujY9HVzFRoaYxZsZp5lI3k2Mc/q+OKLH7XfCkfnSuO/bNhY5dXJ8pCp8B7eeTK+94fCYBXDF1988XWJPn22OL2+hhCYFgZYMDzYEAb/9YktgfDF10eOgm+fjT5e+RuOJTgRtMdrzgbO5mzzxfjii6+jlKGDZQMllgRY2TjLUsyw1NXr7vbZZN+YJfDFF198XaJzwZgmzGrUMM33pimDmaWmYXTOJhU2aBhe2cXwxRdffJ2kuanp1BmbMPTBIaXpmJb0GJz3DDK0mfni4osvvr5E5z2ju4emUQdpOtBMw+iajjBmZHMwcJ5dTK5s4Ysvvvi6RJdpaGfp8Nymfpg+WZqvLPdtmi7MNmVyzzDvnI0vvvji6zwVztbUYt4/HK0N8YeNkRa4FnzxxdcX6j/JGXVr/LhJGgAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAyMS0wMy0yMFQwNjo0OTo1NyswMDowMIylP0QAAAAldEVYdGRhdGU6bW9kaWZ5ADIwMjEtMDMtMjBUMDY6NDk6NTcrMDA6MDD9+If4AAAAAElFTkSuQmCC'
  }
];
