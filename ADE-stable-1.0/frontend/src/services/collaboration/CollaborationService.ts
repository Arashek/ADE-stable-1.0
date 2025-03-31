import { cache } from '../../utils/cache';
import { PerformanceMonitor } from '../../utils/performance';
import { errorHandler, ErrorSeverity } from '../../utils/errorHandling';

interface User {
  id: string;
  name: string;
  avatar?: string;
  cursor?: {
    position: number;
    color: string;
  };
}

interface Change {
  type: 'insert' | 'delete' | 'replace';
  position: number;
  text: string;
  length: number;
  userId: string;
  timestamp: number;
}

interface Document {
  id: string;
  content: string;
  language: string;
  users: User[];
  changes: Change[];
  version: number;
}

class CollaborationService {
  private static instance: CollaborationService;
  private documents: Map<string, Document> = new Map();
  private readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutes
  private readonly MAX_CHANGES = 1000;
  private readonly DEBOUNCE_MS = 100;

  private constructor() {
    this.initializeWebSocket();
  }

  static getInstance(): CollaborationService {
    if (!CollaborationService.instance) {
      CollaborationService.instance = new CollaborationService();
    }
    return CollaborationService.instance;
  }

  private initializeWebSocket(): void {
    const ws = new WebSocket(process.env.REACT_APP_WS_URL || 'ws://localhost:8080');

    ws.onmessage = (event) => {
      try {
      const data = JSON.parse(event.data);
        this.handleWebSocketMessage(data);
      } catch (error) {
        errorHandler.handleError(error as Error, ErrorSeverity.HIGH, {
          context: 'CollaborationService.handleWebSocketMessage',
          data: event.data,
        });
      }
    };

    ws.onerror = (event: Event) => {
      errorHandler.handleError(new Error('WebSocket connection error'), ErrorSeverity.HIGH, {
        context: 'CollaborationService.WebSocket.error',
        event,
      });
    };

    ws.onclose = () => {
      // Attempt to reconnect after a delay
      setTimeout(() => this.initializeWebSocket(), 5000);
    };
  }

  private handleWebSocketMessage(data: any): void {
    switch (data.type) {
      case 'change':
        this.applyChange(data.documentId, data.change);
        break;
      case 'user_join':
        this.handleUserJoin(data.documentId, data.user);
        break;
      case 'user_leave':
        this.handleUserLeave(data.documentId, data.userId);
        break;
      case 'cursor_move':
        this.handleCursorMove(data.documentId, data.userId, data.position);
        break;
      default:
        console.warn('Unknown message type:', data.type);
    }
  }

  async joinDocument(documentId: string, user: User): Promise<Document> {
    return PerformanceMonitor.measure(async (docId: string, usr: User) => {
      try {
        // Check cache first
        const cacheKey = `document:${docId}`;
        const cachedDoc = cache.get<Document>(cacheKey);
        if (cachedDoc) {
          return cachedDoc;
        }

        // Fetch document from server
        const response = await fetch(`/api/documents/${docId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch document: ${response.statusText}`);
        }

        const document = await response.json();
        document.users = [...(document.users || []), usr];
        this.documents.set(docId, document);

        // Cache the document
        cache.set(cacheKey, document, this.CACHE_TTL);

        return document;
      } catch (error) {
        errorHandler.handleError(error as Error, ErrorSeverity.HIGH, {
          context: 'CollaborationService.joinDocument',
          documentId: docId,
          user: usr,
        });
        throw error;
      }
    })(documentId, user);
  }

  async leaveDocument(documentId: string, userId: string): Promise<void> {
    try {
      const document = this.documents.get(documentId);
      if (document) {
        document.users = document.users.filter(u => u.id !== userId);
        this.documents.set(documentId, document);
      }

      await fetch(`/api/documents/${documentId}/leave`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ userId }),
      });
    } catch (error) {
      errorHandler.handleError(error as Error, ErrorSeverity.MEDIUM, {
        context: 'CollaborationService.leaveDocument',
        documentId,
        userId,
      });
    }
  }

  async applyChange(documentId: string, change: Change): Promise<void> {
    return PerformanceMonitor.measure(async (docId: string, chg: Change) => {
      try {
        const document = this.documents.get(docId);
        if (!document) {
          throw new Error('Document not found');
        }

        // Apply change to document content
        const content = document.content;
        let newContent = content;
        switch (chg.type) {
          case 'insert':
            newContent = content.slice(0, chg.position) + chg.text + content.slice(chg.position);
            break;
          case 'delete':
            newContent = content.slice(0, chg.position) + content.slice(chg.position + chg.length);
          break;
          case 'replace':
            newContent = content.slice(0, chg.position) + chg.text + content.slice(chg.position + chg.length);
          break;
        }

        // Update document
        document.content = newContent;
        document.changes.push(chg);
        document.version += 1;

        // Trim changes history if needed
        if (document.changes.length > this.MAX_CHANGES) {
          document.changes = document.changes.slice(-this.MAX_CHANGES);
        }

        this.documents.set(docId, document);

        // Send change to server
        await fetch(`/api/documents/${docId}/changes`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(chg),
        });
      } catch (error) {
        errorHandler.handleError(error as Error, ErrorSeverity.HIGH, {
          context: 'CollaborationService.applyChange',
          documentId: docId,
          change: chg,
        });
        throw error;
      }
    })(documentId, change);
  }

  private handleUserJoin(documentId: string, user: User): void {
    const document = this.documents.get(documentId);
    if (document) {
      document.users = [...document.users, user];
      this.documents.set(documentId, document);
    }
  }

  private handleUserLeave(documentId: string, userId: string): void {
    const document = this.documents.get(documentId);
    if (document) {
      document.users = document.users.filter(u => u.id !== userId);
      this.documents.set(documentId, document);
    }
  }

  private handleCursorMove(documentId: string, userId: string, position: number): void {
    const document = this.documents.get(documentId);
    if (document) {
      const user = document.users.find(u => u.id === userId);
      if (user) {
        user.cursor = {
          position,
          color: user.cursor?.color || this.generateUserColor(userId),
        };
        this.documents.set(documentId, document);
      }
    }
  }

  private generateUserColor(userId: string): string {
    // Generate a consistent color based on user ID
    const hash = userId.split('').reduce((acc, char) => {
      return char.charCodeAt(0) + ((acc << 5) - acc);
    }, 0);

    const hue = hash % 360;
    return `hsl(${hue}, 70%, 50%)`;
  }

  getDocument(documentId: string): Document | undefined {
    return this.documents.get(documentId);
  }

  getUsers(documentId: string): User[] {
    return this.documents.get(documentId)?.users || [];
  }

  clear(): void {
    this.documents.clear();
  }
}

// Create a singleton instance
export const collaborationService = CollaborationService.getInstance();

// Example usage:
/*
const user: User = {
  id: 'user123',
  name: 'John Doe',
  avatar: 'https://example.com/avatar.jpg',
};

// Join a document
const document = await collaborationService.joinDocument('doc123', user);

// Apply a change
await collaborationService.applyChange('doc123', {
  type: 'insert',
  position: 10,
  text: 'Hello, World!',
  length: 0,
  userId: user.id,
  timestamp: Date.now(),
});

// Leave the document
await collaborationService.leaveDocument('doc123', user.id);
*/ 