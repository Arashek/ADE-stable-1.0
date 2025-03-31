import '@testing-library/jest-dom';
import { TextEncoder, TextDecoder } from 'util';
import { server } from './mocks/server';

// Polyfill for TextEncoder/TextDecoder
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Mock WebSocket
class MockWebSocket {
  static OPEN = 1;
  static CLOSED = 3;
  readyState = MockWebSocket.OPEN;
  onopen: (() => void) | null = null;
  onmessage: ((event: any) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: ((error: any) => void) | null = null;

  constructor(url: string) {
    setTimeout(() => {
      if (this.onopen) this.onopen();
    }, 0);
  }

  send(data: string) {
    // Mock send implementation
  }

  close() {
    this.readyState = MockWebSocket.CLOSED;
    if (this.onclose) this.onclose();
  }
}

global.WebSocket = MockWebSocket as any;

// Mock IntersectionObserver
class MockIntersectionObserver {
  observe = jest.fn();
  disconnect = jest.fn();
  unobserve = jest.fn();
}

Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  configurable: true,
  value: MockIntersectionObserver,
});

// Mock ResizeObserver
class MockResizeObserver {
  observe = jest.fn();
  disconnect = jest.fn();
  unobserve = jest.fn();
}

Object.defineProperty(window, 'ResizeObserver', {
  writable: true,
  configurable: true,
  value: MockResizeObserver,
});

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
});

// Setup MSW
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Custom matchers
expect.extend({
  toHaveStyle(received, style) {
    const pass = Object.entries(style).every(([key, value]) => {
      const element = received;
      const computedStyle = window.getComputedStyle(element);
      return computedStyle[key as any] === value;
    });

    return {
      message: () =>
        `expected ${received} to have style ${JSON.stringify(style)}`,
      pass,
    };
  },
  toBeInTheDocument(received) {
    const pass = received !== null;
    return {
      message: () =>
        `expected ${received} to be in the document`,
      pass,
    };
  },
  toHaveTextContent(received, text) {
    const pass = received.textContent?.includes(text) ?? false;
    return {
      message: () =>
        `expected ${received} to have text content ${text}`,
      pass,
    };
  },
});

// Mock performance API
const performanceMock = {
  now: jest.fn(() => Date.now()),
  getEntriesByType: jest.fn(() => []),
  mark: jest.fn(),
  measure: jest.fn(),
  clearMarks: jest.fn(),
  clearMeasures: jest.fn(),
};

Object.defineProperty(window, 'performance', {
  value: performanceMock,
});

// Mock requestAnimationFrame
let rafCallbacks: { [key: number]: () => void } = {};
let rafId = 0;

const requestAnimationFrameMock = jest.fn((callback) => {
  rafId++;
  rafCallbacks[rafId] = callback;
  return rafId;
});

const cancelAnimationFrameMock = jest.fn((id) => {
  delete rafCallbacks[id];
});

Object.defineProperty(window, 'requestAnimationFrame', {
  value: requestAnimationFrameMock,
});

Object.defineProperty(window, 'cancelAnimationFrame', {
  value: cancelAnimationFrameMock,
});

// Helper function to trigger animation frame callbacks
export const triggerAnimationFrame = () => {
  Object.values(rafCallbacks).forEach(callback => callback());
  rafCallbacks = {};
};

// Mock Three.js
jest.mock('three', () => ({
  Scene: jest.fn(),
  PerspectiveCamera: jest.fn(),
  WebGLRenderer: jest.fn(),
  AmbientLight: jest.fn(),
  DirectionalLight: jest.fn(),
  Vector3: jest.fn(),
  Color: jest.fn(),
  SphereGeometry: jest.fn(),
  MeshPhongMaterial: jest.fn(),
  Mesh: jest.fn(),
  BufferGeometry: jest.fn(),
  LineBasicMaterial: jest.fn(),
  Line: jest.fn(),
}));

// Mock OrbitControls
jest.mock('three/examples/jsm/controls/OrbitControls', () => ({
  OrbitControls: jest.fn().mockImplementation(() => ({
    enableDamping: jest.fn(),
    dampingFactor: 0.05,
    update: jest.fn(),
  })),
}));

// Mock Monaco Editor
jest.mock('monaco-editor', () => ({
  editor: {
    IStandaloneCodeEditor: jest.fn(),
    create: jest.fn(),
    defineTheme: jest.fn(),
    setTheme: jest.fn(),
  },
}));

// Mock Socket.IO
jest.mock('socket.io-client', () => ({
  io: jest.fn(),
})); 