import { collaborationService } from '../CollaborationService';
import { cache } from '../../../utils/cache';
import { PerformanceMonitor } from '../../../utils/performance';

// Mock dependencies
jest.mock('../../../utils/cache');
jest.mock('../../../utils/performance');
jest.mock('../../../utils/errorHandling', () => ({
  errorHandler: {
    handleError: jest.fn(),
  },
  ErrorSeverity: {
    LOW: 'low',
    MEDIUM: 'medium',
    HIGH: 'high',
  },
}));

describe('CollaborationService', () => {
  const mockUser = {
    id: 'user123',
    name: 'John Doe',
    avatar: 'https://example.com/avatar.jpg',
  };

  const mockDocument = {
    id: 'doc123',
    content: 'Hello, World!',
    language: 'typescript',
    users: [],
    changes: [],
    version: 1,
  };

  const mockChange = {
    type: 'insert' as const,
    position: 10,
    text: 'Hello',
    length: 0,
    userId: mockUser.id,
    timestamp: Date.now(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (cache.get as jest.Mock).mockReturnValue(null);
    (PerformanceMonitor.measure as jest.Mock).mockImplementation((fn) => fn);
    (global.fetch as jest.Mock).mockResolvedValue({ ok: true, json: () => Promise.resolve(mockDocument) });
  });

  describe('joinDocument', () => {
    it('should return cached document if available', async () => {
      (cache.get as jest.Mock).mockReturnValue(mockDocument);

      const result = await collaborationService.joinDocument(mockDocument.id, mockUser);

      expect(result).toEqual(mockDocument);
      expect(cache.get).toHaveBeenCalled();
      expect(fetch).not.toHaveBeenCalled();
    });

    it('should fetch document from server when cache is empty', async () => {
      const result = await collaborationService.joinDocument(mockDocument.id, mockUser);

      expect(result).toEqual(mockDocument);
      expect(fetch).toHaveBeenCalledWith(`/api/documents/${mockDocument.id}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      expect(cache.set).toHaveBeenCalled();
    });

    it('should handle API errors gracefully', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({ ok: false, statusText: 'Not Found' });

      await expect(collaborationService.joinDocument(mockDocument.id, mockUser)).rejects.toThrow();
    });
  });

  describe('applyChange', () => {
    beforeEach(() => {
      collaborationService['documents'].set(mockDocument.id, { ...mockDocument });
    });

    it('should apply insert change correctly', async () => {
      const result = await collaborationService.applyChange(mockDocument.id, mockChange);

      const document = collaborationService.getDocument(mockDocument.id);
      expect(document?.content).toBe('Hello, World!Hello');
      expect(document?.changes).toContainEqual(mockChange);
      expect(document?.version).toBe(2);
      expect(fetch).toHaveBeenCalledWith(`/api/documents/${mockDocument.id}/changes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mockChange),
      });
    });

    it('should apply delete change correctly', async () => {
      const deleteChange = {
        ...mockChange,
        type: 'delete' as const,
        text: '',
        length: 5,
      };

      await collaborationService.applyChange(mockDocument.id, deleteChange);

      const document = collaborationService.getDocument(mockDocument.id);
      expect(document?.content).toBe('World!');
    });

    it('should apply replace change correctly', async () => {
      const replaceChange = {
        ...mockChange,
        type: 'replace' as const,
        text: 'Hi',
        length: 5,
      };

      await collaborationService.applyChange(mockDocument.id, replaceChange);

      const document = collaborationService.getDocument(mockDocument.id);
      expect(document?.content).toBe('Hi, World!');
    });

    it('should handle API errors gracefully', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({ ok: false, statusText: 'Not Found' });

      await expect(collaborationService.applyChange(mockDocument.id, mockChange)).rejects.toThrow();
    });
  });

  describe('leaveDocument', () => {
    beforeEach(() => {
      collaborationService['documents'].set(mockDocument.id, { ...mockDocument, users: [mockUser] });
    });

    it('should remove user from document and notify server', async () => {
      await collaborationService.leaveDocument(mockDocument.id, mockUser.id);

      const document = collaborationService.getDocument(mockDocument.id);
      expect(document?.users).not.toContainEqual(mockUser);
      expect(fetch).toHaveBeenCalledWith(`/api/documents/${mockDocument.id}/leave`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId: mockUser.id }),
      });
    });

    it('should handle API errors gracefully', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({ ok: false, statusText: 'Not Found' });

      await collaborationService.leaveDocument(mockDocument.id, mockUser.id);
      const document = collaborationService.getDocument(mockDocument.id);
      expect(document?.users).not.toContainEqual(mockUser);
    });
  });

  describe('WebSocket handling', () => {
    it('should handle user join message', () => {
      const message = {
        type: 'user_join',
        documentId: mockDocument.id,
        user: mockUser,
      };

      collaborationService['handleWebSocketMessage'](message);

      const document = collaborationService.getDocument(mockDocument.id);
      expect(document?.users).toContainEqual(mockUser);
    });

    it('should handle user leave message', () => {
      collaborationService['documents'].set(mockDocument.id, { ...mockDocument, users: [mockUser] });

      const message = {
        type: 'user_leave',
        documentId: mockDocument.id,
        userId: mockUser.id,
      };

      collaborationService['handleWebSocketMessage'](message);

      const document = collaborationService.getDocument(mockDocument.id);
      expect(document?.users).not.toContainEqual(mockUser);
    });

    it('should handle cursor move message', () => {
      collaborationService['documents'].set(mockDocument.id, { ...mockDocument, users: [mockUser] });

      const message = {
        type: 'cursor_move',
        documentId: mockDocument.id,
        userId: mockUser.id,
        position: 5,
      };

      collaborationService['handleWebSocketMessage'](message);

      const document = collaborationService.getDocument(mockDocument.id);
      const user = document?.users.find(u => u.id === mockUser.id);
      expect(user?.cursor).toBeDefined();
      expect(user?.cursor?.position).toBe(5);
    });
  });
}); 