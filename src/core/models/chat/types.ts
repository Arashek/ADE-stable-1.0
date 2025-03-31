export enum MessageType {
  TEXT = 'text',
  FILE = 'file',
  IMAGE = 'image',
  VOICE = 'voice'
}

export interface MediaMetadata {
  fileName: string;
  fileSize: number;
  mimeType: string;
  duration?: number; // For voice messages
  width?: number;    // For images
  height?: number;   // For images
  thumbnailUrl?: string; // For images and files
}

export interface ChatMessage {
  id: string;
  type: MessageType;
  content: string;
  senderId: string;
  timestamp: Date;
  mediaMetadata?: MediaMetadata;
  mediaUrl?: string;
  isEdited: boolean;
  isDeleted: boolean;
  replyTo?: string;
  reactions: Record<string, string[]>; // userId -> reaction
}

export interface ChatRoom {
  id: string;
  name: string;
  participants: string[];
  lastMessage?: ChatMessage;
  createdAt: Date;
  updatedAt: Date;
  isGroup: boolean;
  avatar?: string;
  settings: {
    allowMediaUpload: boolean;
    maxFileSize: number;
    allowedFileTypes: string[];
  };
}

export interface ChatSettings {
  maxFileSize: number;
  allowedFileTypes: string[];
  maxImageDimension: number;
  maxVoiceDuration: number;
  storageQuota: number;
  compressionEnabled: boolean;
} 