import { Socket } from 'socket.io-client';
import { v4 as uuidv4 } from 'uuid';
import * as monaco from 'monaco-editor';

export interface CollaborativeEditingConfig {
  ws: Socket;
  projectId: string;
  editor: monaco.editor.IStandaloneCodeEditor;
}

export interface User {
  id: string;
  name: string;
  avatar?: string;
  presence: 'online' | 'away' | 'offline';
}

export interface Change {
  uri: string;
  version: number;
  changes: {
    range: {
      start: { line: number; character: number };
      end: { line: number; character: number };
    };
    text: string;
  }[];
  userId: string;
  timestamp: number;
}

export interface Conflict {
  uri: string;
  version: number;
  localChange: Change;
  remoteChange: Change;
  resolution?: Change;
}

export class CollaborativeEditingService {
  private ws: Socket;
  private projectId: string;
  private sessionId: string;
  private activeUsers: Map<string, User> = new Map();
  private changeHistory: Map<string, Change[]> = new Map();
  private conflicts: Map<string, Conflict[]> = new Map();
  private documentVersions: Map<string, number> = new Map();
  private editor: monaco.editor.IStandaloneCodeEditor;

  constructor(config: CollaborativeEditingConfig) {
    this.ws = config.ws;
    this.projectId = config.projectId;
    this.editor = config.editor;
    this.sessionId = uuidv4();
    this.setupEventListeners();
  }

  private setupEventListeners() {
    this.ws.on('collaboration:user-joined', (data: { user: User }) => {
      this.handleUserJoined(data);
    });

    this.ws.on('collaboration:user-left', (data: { userId: string }) => {
      this.handleUserLeft(data);
    });

    this.ws.on('collaboration:user-presence', (data: { userId: string; presence: User['presence'] }) => {
      this.handleUserPresence(data);
    });

    this.ws.on('collaboration:change', (data: { change: Change }) => {
      this.handleChange(data);
    });

    this.ws.on('collaboration:conflict', (data: { conflict: Conflict }) => {
      this.handleConflict(data);
    });
  }

  public async joinDocument(uri: string): Promise<void> {
    this.ws.emit('collaboration:join-document', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      uri
    });
  }

  public async leaveDocument(uri: string): Promise<void> {
    this.ws.emit('collaboration:leave-document', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      uri
    });
  }

  public async applyChange(change: Change): Promise<void> {
    const currentVersion = this.documentVersions.get(change.uri) || 0;
    if (change.version !== currentVersion) {
      // Version mismatch, potential conflict
      this.ws.emit('collaboration:version-mismatch', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        uri: change.uri,
        localVersion: currentVersion,
        remoteVersion: change.version
      });
      return;
    }

    this.ws.emit('collaboration:change', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      change
    });

    // Update local version
    this.documentVersions.set(change.uri, currentVersion + 1);
  }

  public async resolveConflict(conflict: Conflict): Promise<void> {
    this.ws.emit('collaboration:resolve-conflict', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      conflict
    });

    // Update local version
    this.documentVersions.set(conflict.uri, conflict.version + 1);
  }

  public getActiveUsers(): User[] {
    return Array.from(this.activeUsers.values());
  }

  public getChangeHistory(uri: string): Change[] {
    return this.changeHistory.get(uri) || [];
  }

  public getConflicts(uri: string): Conflict[] {
    return this.conflicts.get(uri) || [];
  }

  private handleUserJoined(data: { user: User }): void {
    this.activeUsers.set(data.user.id, data.user);
    this.ws.emit('ide:user-joined', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      user: data.user
    });
  }

  private handleUserLeft(data: { userId: string }): void {
    this.activeUsers.delete(data.userId);
    this.ws.emit('ide:user-left', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      userId: data.userId
    });
  }

  private handleUserPresence(data: { userId: string; presence: User['presence'] }): void {
    const user = this.activeUsers.get(data.userId);
    if (user) {
      user.presence = data.presence;
      this.ws.emit('ide:user-presence', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        userId: data.userId,
        presence: data.presence
      });
    }
  }

  private handleChange(data: { change: Change }): void {
    const history = this.changeHistory.get(data.change.uri) || [];
    history.push(data.change);
    this.changeHistory.set(data.change.uri, history);

    this.ws.emit('ide:change', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      change: data.change
    });
  }

  private handleConflict(data: { conflict: Conflict }): void {
    const conflicts = this.conflicts.get(data.conflict.uri) || [];
    conflicts.push(data.conflict);
    this.conflicts.set(data.conflict.uri, conflicts);

    this.ws.emit('ide:conflict', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      conflict: data.conflict
    });
  }

  public dispose(): void {
    this.activeUsers.clear();
    this.changeHistory.clear();
    this.conflicts.clear();
    this.documentVersions.clear();
  }
} 