import { ProjectConfig } from './ide';

export interface Project {
    id: string;
    name: string;
    description: string;
    config: ProjectConfig;
    createdAt: string;
    updatedAt: string;
    owner: User;
    collaborators: Collaborator[];
    branches: Branch[];
    tags: Tag[];
    settings: ProjectSettings;
    statistics: ProjectStatistics;
}

export interface User {
    id: string;
    username: string;
    email: string;
    avatar?: string;
    role: 'owner' | 'admin' | 'editor' | 'viewer';
    preferences: UserPreferences;
}

export interface Collaborator {
    user: User;
    role: 'admin' | 'editor' | 'viewer';
    joinedAt: string;
    lastActive: string;
    permissions: Permission[];
}

export interface Branch {
    name: string;
    commit: string;
    isDefault: boolean;
    isProtected: boolean;
    lastUpdated: string;
    ahead: number;
    behind: number;
}

export interface Tag {
    name: string;
    commit: string;
    description?: string;
    createdAt: string;
    createdBy: User;
}

export interface ProjectSettings {
    visibility: 'private' | 'public' | 'organization';
    defaultBranch: string;
    protectedBranches: string[];
    mergeStrategy: 'merge' | 'rebase' | 'squash';
    autoMerge: boolean;
    requiredReviews: number;
    codeOwners: string[];
    fileTemplates: FileTemplate[];
    issueTemplates: IssueTemplate[];
    ciConfig: CIConfig;
}

export interface FileTemplate {
    name: string;
    description: string;
    content: string;
    language: string;
    path: string;
}

export interface IssueTemplate {
    name: string;
    description: string;
    labels: string[];
    assignees: string[];
    body: string;
}

export interface CIConfig {
    enabled: boolean;
    providers: string[];
    workflows: Workflow[];
    secrets: Secret[];
}

export interface Workflow {
    name: string;
    trigger: 'push' | 'pull_request' | 'tag' | 'schedule';
    jobs: Job[];
    environment: string;
}

export interface Job {
    name: string;
    runsOn: string;
    steps: Step[];
    timeout: number;
    environment: string;
}

export interface Step {
    name: string;
    uses?: string;
    run?: string;
    with?: Record<string, any>;
    env?: Record<string, string>;
}

export interface Secret {
    name: string;
    value: string;
    environment: string;
    createdAt: string;
    updatedAt: string;
}

export interface Permission {
    resource: string;
    actions: string[];
    conditions?: Record<string, any>;
}

export interface UserPreferences {
    theme: 'light' | 'dark' | 'system';
    language: string;
    editor: {
        fontSize: number;
        tabSize: number;
        wordWrap: boolean;
        minimap: boolean;
    };
    terminal: {
        fontSize: number;
        theme: string;
    };
    notifications: {
        email: boolean;
        desktop: boolean;
        inApp: boolean;
    };
}

export interface ProjectStatistics {
    commits: number;
    branches: number;
    tags: number;
    collaborators: number;
    issues: number;
    pullRequests: number;
    lastActivity: string;
    size: number;
    languages: Record<string, number>;
}

export interface ProjectActivity {
    id: string;
    type: 'commit' | 'branch' | 'tag' | 'issue' | 'pull_request' | 'collaborator';
    user: User;
    timestamp: string;
    details: any;
    repository: string;
    branch?: string;
}

export interface ProjectSearch {
    query: string;
    filters: {
        type: string[];
        language: string[];
        date: {
            from: string;
            to: string;
        };
        author: string[];
    };
    results: SearchResult[];
    total: number;
    page: number;
    perPage: number;
}

export interface SearchResult {
    type: 'file' | 'commit' | 'issue' | 'pull_request';
    title: string;
    description: string;
    path: string;
    language?: string;
    score: number;
    highlights: {
        field: string;
        matches: string[];
    }[];
} 