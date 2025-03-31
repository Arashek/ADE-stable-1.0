import { CommandCenterLayout } from './command-center';

export interface IDELayout {
    commandCenter: CommandCenterLayout;
    fileExplorer: {
        width: number;
        collapsed: boolean;
        root: FileNode;
    };
    editor: {
        tabs: EditorTab[];
        activeTab: string;
        splitView: boolean;
        theme: string;
        fontSize: number;
        lineNumbers: boolean;
        minimap: boolean;
    };
    terminal: {
        height: number;
        collapsed: boolean;
        sessions: TerminalSession[];
    };
    statusBar: {
        height: number;
        components: StatusBarComponent[];
    };
}

export interface FileNode {
    id: string;
    name: string;
    type: 'file' | 'directory';
    path: string;
    children?: FileNode[];
    content?: string;
    language?: string;
    size?: number;
    lastModified?: string;
    isOpen?: boolean;
    isExpanded?: boolean;
}

export interface EditorTab {
    id: string;
    title: string;
    path: string;
    language: string;
    isDirty: boolean;
    isActive: boolean;
    content: string;
    cursor: {
        line: number;
        column: number;
    };
    scroll: {
        top: number;
        left: number;
    };
}

export interface StatusBarComponent {
    id: string;
    type: 'git' | 'language' | 'encoding' | 'line-ending' | 'indentation' | 'position' | 'errors' | 'warnings';
    content: string;
    tooltip?: string;
    action?: () => void;
}

export interface IDEFeatures {
    codeEditing: {
        syntaxHighlighting: boolean;
        autoComplete: boolean;
        codeFolding: boolean;
        bracketMatching: boolean;
        lineHighlighting: boolean;
    };
    git: {
        enabled: boolean;
        branch: string;
        status: 'clean' | 'dirty' | 'conflict';
        changes: {
            staged: number;
            unstaged: number;
            untracked: number;
        };
    };
    debugging: {
        enabled: boolean;
        breakpoints: Breakpoint[];
        variables: Variable[];
        callStack: CallStack[];
    };
    terminal: {
        sessions: TerminalSession[];
        splitView: boolean;
        theme: string;
    };
}

export interface Breakpoint {
    id: string;
    line: number;
    enabled: boolean;
    condition?: string;
    hitCount?: number;
}

export interface Variable {
    name: string;
    value: any;
    type: string;
    scope: string;
    isExpanded?: boolean;
}

export interface CallStack {
    id: string;
    name: string;
    file: string;
    line: number;
    column: number;
}

export interface IDEConfig {
    editor: {
        theme: string;
        fontSize: number;
        tabSize: number;
        insertSpaces: boolean;
        wordWrap: boolean;
        minimap: boolean;
        lineNumbers: boolean;
        bracketMatching: boolean;
        autoComplete: boolean;
    };
    terminal: {
        theme: string;
        fontSize: number;
        cursorStyle: string;
        cursorBlink: boolean;
    };
    git: {
        enabled: boolean;
        autoFetch: boolean;
        showGutter: boolean;
    };
    debugging: {
        enabled: boolean;
        autoAttach: boolean;
        breakOnError: boolean;
    };
    fileExplorer: {
        showHidden: boolean;
        sortBy: 'name' | 'type' | 'modified';
        groupBy: 'none' | 'type' | 'modified';
    };
}

export interface ProjectConfig {
    name: string;
    root: string;
    type: 'local' | 'git' | 'remote';
    git?: {
        remote: string;
        branch: string;
    };
    exclude: string[];
    include: string[];
    settings: {
        editor: Partial<IDEConfig['editor']>;
        terminal: Partial<IDEConfig['terminal']>;
        git: Partial<IDEConfig['git']>;
        debugging: Partial<IDEConfig['debugging']>;
    };
} 