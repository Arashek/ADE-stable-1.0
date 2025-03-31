import {
  DesignCanvas,
  DesignCollaboration,
} from '../frontend/src/services/InteractiveDesignService';

export interface DatabaseService {
  getCanvas(projectId: string): Promise<DesignCanvas | null>;
  saveCanvas(projectId: string, canvas: DesignCanvas): Promise<void>;
  getCollaboration(projectId: string): Promise<DesignCollaboration | null>;
  saveCollaboration(projectId: string, collaboration: DesignCollaboration): Promise<void>;
} 