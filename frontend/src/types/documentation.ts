/**
 * Documentation types for the ADE platform
 * These types support the multi-agent architecture by providing structured
 * documentation formats that can be generated and maintained by specialized agents
 */

export enum DocType {
  API = 'api',
  COMPONENT = 'component',
  ARCHITECTURE = 'architecture',
  DEPLOYMENT = 'deployment',
  GUIDE = 'guide'
}

/**
 * Represents a section within a documentation document
 */
export interface DocSection {
  id: string;
  title: string;
  content: string;
  order: number;
  examples?: string[];
}

/**
 * Represents a complete documentation document
 */
export interface Documentation {
  id: string;
  title: string;
  type: DocType;
  description: string;
  sections: DocSection[];
  createdAt: number;
  updatedAt: number;
  tags: string[];
  relatedDocs?: string[];
}

/**
 * Request to create a new documentation
 */
export interface CreateDocumentationRequest {
  title: string;
  type: DocType;
  description: string;
  codeContext?: {
    files: string[];
    components: string[];
  };
}

/**
 * Request to update an existing documentation
 */
export interface UpdateDocumentationRequest {
  title?: string;
  description?: string;
  tags?: string[];
  relatedDocs?: string[];
}
