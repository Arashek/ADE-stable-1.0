import axios, { AxiosInstance } from 'axios';
import { DatabaseService } from '../../DatabaseService';
import { FileService } from '../../FileService';

interface FigmaConfig {
  accessToken: string;
  teamId?: string;
  projectId?: string;
}

interface FigmaFile {
  key: string;
  name: string;
  lastModified: string;
  thumbnailUrl?: string;
}

interface FigmaComponent {
  key: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  thumbnail_url?: string;
  component_set_id?: string;
}

interface FigmaStyle {
  key: string;
  name: string;
  description?: string;
  remote: boolean;
  styleType: 'FILL' | 'TEXT' | 'EFFECT' | 'GRID';
}

interface FigmaNode {
  id: string;
  name: string;
  type: string;
  children?: FigmaNode[];
  componentProperties?: Record<string, any>;
  styles?: Record<string, string>;
}

export class FigmaService {
  private client: AxiosInstance;
  private config: FigmaConfig;
  private db: DatabaseService;
  private fileService: FileService;

  constructor(config: FigmaConfig, db: DatabaseService, fileService: FileService) {
    this.config = config;
    this.db = db;
    this.fileService = fileService;

    this.client = axios.create({
      baseURL: 'https://api.figma.com/v1',
      headers: {
        'X-Figma-Token': config.accessToken,
      },
    });
  }

  // Authentication and Authorization
  async validateAccessToken(): Promise<boolean> {
    try {
      await this.client.get('/me');
      return true;
    } catch (error) {
      console.error('Failed to validate Figma access token:', error);
      return false;
    }
  }

  // File Operations
  async getFile(fileKey: string): Promise<FigmaFile> {
    try {
      const response = await this.client.get(`/files/${fileKey}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get Figma file:', error);
      throw error;
    }
  }

  async getFileNodes(fileKey: string, nodeIds: string[]): Promise<Record<string, FigmaNode>> {
    try {
      const response = await this.client.get(`/files/${fileKey}/nodes`, {
        params: {
          ids: nodeIds.join(','),
        },
      });
      return response.data.nodes;
    } catch (error) {
      console.error('Failed to get Figma file nodes:', error);
      throw error;
    }
  }

  // Component Operations
  async getTeamComponents(teamId: string): Promise<FigmaComponent[]> {
    try {
      const response = await this.client.get(`/teams/${teamId}/components`);
      return response.data.meta.components;
    } catch (error) {
      console.error('Failed to get team components:', error);
      throw error;
    }
  }

  async getComponentSet(teamId: string, componentSetId: string): Promise<FigmaComponent[]> {
    try {
      const response = await this.client.get(`/teams/${teamId}/component_sets/${componentSetId}`);
      return response.data.meta.components;
    } catch (error) {
      console.error('Failed to get component set:', error);
      throw error;
    }
  }

  // Style Operations
  async getTeamStyles(teamId: string): Promise<FigmaStyle[]> {
    try {
      const response = await this.client.get(`/teams/${teamId}/styles`);
      return response.data.meta.styles;
    } catch (error) {
      console.error('Failed to get team styles:', error);
      throw error;
    }
  }

  // Sync Operations
  async syncComponents(teamId: string): Promise<void> {
    try {
      const components = await this.getTeamComponents(teamId);
      await this.db.saveComponents(components);
    } catch (error) {
      console.error('Failed to sync components:', error);
      throw error;
    }
  }

  async syncStyles(teamId: string): Promise<void> {
    try {
      const styles = await this.getTeamStyles(teamId);
      await this.db.saveStyles(styles);
    } catch (error) {
      console.error('Failed to sync styles:', error);
      throw error;
    }
  }

  // Version Control
  async getFileVersions(fileKey: string): Promise<any[]> {
    try {
      const response = await this.client.get(`/files/${fileKey}/versions`);
      return response.data.versions;
    } catch (error) {
      console.error('Failed to get file versions:', error);
      throw error;
    }
  }

  async getVersion(fileKey: string, versionId: string): Promise<any> {
    try {
      const response = await this.client.get(`/files/${fileKey}/versions/${versionId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get version:', error);
      throw error;
    }
  }

  // Real-time Collaboration
  async getFileComments(fileKey: string): Promise<any[]> {
    try {
      const response = await this.client.get(`/files/${fileKey}/comments`);
      return response.data.comments;
    } catch (error) {
      console.error('Failed to get file comments:', error);
      throw error;
    }
  }

  async addComment(fileKey: string, nodeId: string, comment: string): Promise<void> {
    try {
      await this.client.post(`/files/${fileKey}/comments`, {
        message: comment,
        client_meta: {
          node_id: nodeId,
        },
      });
    } catch (error) {
      console.error('Failed to add comment:', error);
      throw error;
    }
  }

  // Image Operations
  async getImage(fileKey: string, nodeId: string, format: 'png' | 'jpg' | 'svg' = 'png'): Promise<string> {
    try {
      const response = await this.client.get(`/images/${fileKey}`, {
        params: {
          ids: nodeId,
          format,
        },
      });
      return response.data.images[nodeId];
    } catch (error) {
      console.error('Failed to get image:', error);
      throw error;
    }
  }

  // Export Operations
  async exportNode(fileKey: string, nodeId: string, format: 'png' | 'jpg' | 'svg' = 'png'): Promise<void> {
    try {
      const imageUrl = await this.getImage(fileKey, nodeId, format);
      const response = await axios.get(imageUrl, { responseType: 'arraybuffer' });
      await this.fileService.saveFile(`exports/${nodeId}.${format}`, response.data);
    } catch (error) {
      console.error('Failed to export node:', error);
      throw error;
    }
  }
} 