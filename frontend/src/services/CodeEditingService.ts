import * as monaco from 'monaco-editor';
import { Socket } from 'socket.io-client';
import { v4 as uuidv4 } from 'uuid';
import { editor } from 'monaco-editor';

export interface CodeEditingServiceConfig {
  ws: Socket;
  projectId: string;
}

export interface Breakpoint {
  id: string;
  lineNumber: number;
  condition?: string;
  hitCount?: number;
  enabled: boolean;
}

export interface VariableInfo {
  name: string;
  type: string;
  value: any;
  scope: string;
  lineNumber: number;
}

export interface SyntaxError {
  lineNumber: number;
  column: number;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

export interface CodeEdit {
  uri: string;
  range: {
    start: { line: number; character: number };
    end: { line: number; character: number };
  };
  newText: string;
  editId: string;
}

export interface CompletionItem {
  label: string;
  kind: number;
  detail?: string;
  documentation?: string;
  insertText: string;
  insertTextRules?: number;
  commitCharacters?: string[];
}

export interface DebugBreakpoint {
  id: string;
  uri: string;
  line: number;
  condition?: string;
  logMessage?: string;
}

export interface DebugVariable {
  name: string;
  value: string;
  type: string;
  children?: DebugVariable[];
}

export class CodeEditingService {
  private ws: Socket;
  private projectId: string;
  private sessionId: string;
  private breakpoints: Map<string, Breakpoint[]> = new Map();
  private variables: Map<string, VariableInfo[]> = new Map();
  private syntaxErrors: Map<string, SyntaxError[]> = new Map();
  private editor: editor.IStandaloneCodeEditor | null = null;
  private completionProvider: monaco.IDisposable | null = null;
  private hoverProvider: monaco.IDisposable | null = null;
  private definitionProvider: monaco.IDisposable | null = null;
  private referenceProvider: monaco.IDisposable | null = null;
  private activeBreakpoints: Map<string, DebugBreakpoint> = new Map();
  private completionCache: Map<string, CompletionItem[]> = new Map();

  constructor(config: CodeEditingServiceConfig) {
    this.ws = config.ws;
    this.projectId = config.projectId;
    this.sessionId = uuidv4();
    this.setupEventListeners();
  }

  public async initialize() {
    this.setupEventListeners();
    this.setupDebugging();
    this.setupSyntaxHighlighting();
  }

  private setupEventListeners() {
    if (!this.editor) return;

    // Breakpoint handling
    this.editor.onMouseDown((e) => {
      if (e.target.type === monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN) {
        const lineNumber = e.target.position?.lineNumber;
        if (lineNumber) {
          this.toggleBreakpoint(lineNumber);
        }
      }
    });

    // Code change handling
    this.editor.onDidChangeModelContent(() => {
      const content = this.editor?.getValue() || '';
      this.ws.emit('editor:change', {
        projectId: this.projectId,
        content
      });
    });

    // Cursor position handling
    this.editor.onDidChangeCursorPosition((e) => {
      this.ws.emit('editor:cursor', {
        projectId: this.projectId,
        position: e.position
      });
    });

    // Debugging events
    this.ws.on('debug:breakpoint-hit', (data: { fileId: string; breakpointId: string }) => {
      this.handleBreakpointHit(data);
    });

    this.ws.on('debug:variable-update', (data: { fileId: string; variables: VariableInfo[] }) => {
      this.handleVariableUpdate(data);
    });

    // Syntax highlighting events
    this.ws.on('syntax:errors', (data: { fileId: string; errors: SyntaxError[] }) => {
      this.handleSyntaxErrors(data);
    });

    this.ws.on('code:completion', (data: { uri: string; items: CompletionItem[] }) => {
      this.handleCompletion(data);
    });

    this.ws.on('code:diagnostics', (data: { uri: string; diagnostics: any[] }) => {
      this.handleDiagnostics(data);
    });

    this.ws.on('debug:breakpoint-hit', (data: { breakpointId: string; variables: DebugVariable[] }) => {
      this.handleBreakpointHit(data);
    });
  }

  private setupDebugging() {
    if (this.editor) {
      // Add breakpoint decoration
      this.editor.onMouseDown((e) => {
        const lineNumber = e.target.position?.lineNumber;
        if (lineNumber) {
          this.toggleBreakpoint(lineNumber);
        }
      });

      // Add variable inspection
      this.editor.onMouseMove((e) => {
        const position = e.target.position;
        if (position) {
          this.inspectVariable(position);
        }
      });
    }
  }

  private setupSyntaxHighlighting() {
    if (this.editor) {
      // Configure Monaco editor syntax highlighting
      this.editor.updateOptions({
        minimap: { enabled: true },
        scrollBeyondLastLine: false,
        automaticLayout: true,
        theme: 'vs-dark',
        fontSize: 14,
        lineNumbers: 'on',
        roundedSelection: false,
        scrollbar: {
          vertical: 'visible',
          horizontal: 'visible'
        }
      });
    }
  }

  private registerProviders() {
    if (!this.editor) return;

    // Completion provider
    this.completionProvider = monaco.languages.registerCompletionItemProvider(
      this.editor.getModel()?.getLanguageId() || 'plaintext',
      {
        provideCompletionItems: async (model, position) => {
          const word = model.getWordUntilPosition(position);
          const suggestions = await this.getCompletionSuggestions(word);
          return { suggestions };
        }
      }
    );

    // Hover provider
    this.hoverProvider = monaco.languages.registerHoverProvider(
      this.editor.getModel()?.getLanguageId() || 'plaintext',
      {
        provideHover: async (model, position) => {
          const word = model.getWordAtPosition(position);
          if (!word) return null;
          const hoverContent = await this.getHoverContent(word);
          return {
            contents: [{ value: hoverContent }]
          };
        }
      }
    );

    // Definition provider
    this.definitionProvider = monaco.languages.registerDefinitionProvider(
      this.editor.getModel()?.getLanguageId() || 'plaintext',
      {
        provideDefinition: async (model, position) => {
          const word = model.getWordAtPosition(position);
          if (!word) return null;
          const definition = await this.getDefinition(word);
          return definition;
        }
      }
    );

    // Reference provider
    this.referenceProvider = monaco.languages.registerReferenceProvider(
      this.editor.getModel()?.getLanguageId() || 'plaintext',
      {
        provideReferences: async (model, position) => {
          const word = model.getWordAtPosition(position);
          if (!word) return null;
          const references = await this.getReferences(word);
          return references;
        }
      }
    );
  }

  private async getCompletionSuggestions(word: monaco.editor.IWordAtPosition) {
    return new Promise<monaco.languages.CompletionItem[]>((resolve) => {
      this.ws.emit('editor:completion', {
        projectId: this.projectId,
        word: word.word,
        position: word.startColumn
      }, (suggestions: monaco.languages.CompletionItem[]) => {
        resolve(suggestions);
      });
    });
  }

  private async getHoverContent(word: monaco.editor.IWordAtPosition) {
    return new Promise<string>((resolve) => {
      this.ws.emit('editor:hover', {
        projectId: this.projectId,
        word: word.word
      }, (content: string) => {
        resolve(content);
      });
    });
  }

  private async getDefinition(word: monaco.editor.IWordAtPosition) {
    return new Promise<monaco.languages.Definition>((resolve) => {
      this.ws.emit('editor:definition', {
        projectId: this.projectId,
        word: word.word
      }, (definition: monaco.languages.Definition) => {
        resolve(definition);
      });
    });
  }

  private async getReferences(word: monaco.editor.IWordAtPosition) {
    return new Promise<monaco.languages.Location[]>((resolve) => {
      this.ws.emit('editor:references', {
        projectId: this.projectId,
        word: word.word
      }, (references: monaco.languages.Location[]) => {
        resolve(references);
      });
    });
  }

  public async toggleBreakpoint(lineNumber: number) {
    const fileId = this.getCurrentFileId();
    if (!fileId) return;

    const existingBreakpoint = this.breakpoints.get(fileId)?.find(bp => bp.lineNumber === lineNumber);
    
    if (existingBreakpoint) {
      // Remove breakpoint
      this.breakpoints.set(
        fileId,
        this.breakpoints.get(fileId)!.filter(bp => bp.id !== existingBreakpoint.id)
      );
      this.removeBreakpointDecoration(lineNumber);
    } else {
      // Add breakpoint
      const newBreakpoint: Breakpoint = {
        id: uuidv4(),
        lineNumber,
        enabled: true
      };
      
      this.breakpoints.set(fileId, [
        ...(this.breakpoints.get(fileId) || []),
        newBreakpoint
      ]);
      
      this.addBreakpointDecoration(lineNumber);
    }

    this.ws.emit('debug:breakpoint-update', {
      projectId: this.projectId,
      fileId,
      breakpoints: this.breakpoints.get(fileId)
    });
  }

  private addBreakpointDecoration(lineNumber: number) {
    if (!this.editor) return;

    const decorations = this.editor.deltaDecorations([], [{
      range: {
        startLineNumber: lineNumber,
        startColumn: 1,
        endLineNumber: lineNumber,
        endColumn: 1
      },
      options: {
        isWholeLine: false,
        glyphMarginClassName: 'breakpoint-glyph',
        glyphMarginHoverMessage: { value: 'Breakpoint' }
      }
    }]);
  }

  private removeBreakpointDecoration(lineNumber: number) {
    if (!this.editor) return;

    const decorations = this.editor.getModel()?.getAllDecorations();
    if (decorations) {
      const decorationToRemove = decorations.find(d => 
        d.range.startLineNumber === lineNumber && 
        d.options.glyphMarginClassName === 'breakpoint-glyph'
      );
      
      if (decorationToRemove) {
        this.editor.deltaDecorations([decorationToRemove.id], []);
      }
    }
  }

  public async inspectVariable(position: editor.IPosition) {
    const fileId = this.getCurrentFileId();
    if (!fileId) return;

    const word = this.editor?.getModel()?.getWordAtPosition(position);
    if (!word) return;

    this.ws.emit('debug:inspect-variable', {
      projectId: this.projectId,
      fileId,
      variable: word.word,
      lineNumber: position.lineNumber,
      column: position.column
    });
  }

  private handleBreakpointHit(data: { fileId: string; breakpointId: string }) {
    const breakpoint = this.breakpoints.get(data.fileId)?.find(bp => bp.id === data.breakpointId);
    if (breakpoint) {
      // Highlight the current line
      this.highlightCurrentLine(breakpoint.lineNumber);
      
      // Update variables
      this.ws.emit('debug:request-variables', {
        projectId: this.projectId,
        fileId: data.fileId,
        lineNumber: breakpoint.lineNumber
      });
    }
  }

  private handleVariableUpdate(data: { fileId: string; variables: VariableInfo[] }) {
    this.variables.set(data.fileId, data.variables);
    this.updateVariableHover();
  }

  private handleSyntaxErrors(data: { fileId: string; errors: SyntaxError[] }) {
    this.syntaxErrors.set(data.fileId, data.errors);
    this.updateErrorDecorations();
  }

  private updateErrorDecorations() {
    if (!this.editor) return;

    const fileId = this.getCurrentFileId();
    if (!fileId) return;

    const errors = this.syntaxErrors.get(fileId) || [];
    const decorations = errors.map(error => ({
      range: {
        startLineNumber: error.lineNumber,
        startColumn: error.column,
        endLineNumber: error.lineNumber,
        endColumn: error.column + 1
      },
      options: {
        isWholeLine: false,
        className: `syntax-error-${error.severity}`,
        hoverMessage: { value: error.message }
      }
    }));

    this.editor.deltaDecorations([], decorations);
  }

  private updateVariableHover() {
    if (!this.editor) return;

    const fileId = this.getCurrentFileId();
    if (!fileId) return;

    const variables = this.variables.get(fileId) || [];
    const decorations = variables.map(variable => ({
      range: {
        startLineNumber: variable.lineNumber,
        startColumn: 1,
        endLineNumber: variable.lineNumber,
        endColumn: 1
      },
      options: {
        isWholeLine: false,
        hoverMessage: {
          value: `${variable.name}: ${variable.type} = ${JSON.stringify(variable.value)}`
        }
      }
    }));

    this.editor.deltaDecorations([], decorations);
  }

  private highlightCurrentLine(lineNumber: number) {
    if (!this.editor) return;

    this.editor.deltaDecorations([], [{
      range: {
        startLineNumber: lineNumber,
        startColumn: 1,
        endLineNumber: lineNumber,
        endColumn: 1
      },
      options: {
        isWholeLine: true,
        className: 'current-line-highlight'
      }
    }]);
  }

  private getCurrentFileId(): string | null {
    // Implementation to get current file ID
    return null;
  }

  public async applyEdit(edit: CodeEdit): Promise<void> {
    this.ws.emit('code:edit', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      edit
    });
  }

  public async requestCompletion(uri: string, position: { line: number; character: number }): Promise<CompletionItem[]> {
    // Check cache first
    const cacheKey = `${uri}:${position.line}:${position.character}`;
    if (this.completionCache.has(cacheKey)) {
      return this.completionCache.get(cacheKey)!;
    }

    return new Promise((resolve) => {
      this.ws.emit('code:completion-request', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        uri,
        position
      });

      const handler = (data: { uri: string; items: CompletionItem[] }) => {
        if (data.uri === uri) {
          this.completionCache.set(cacheKey, data.items);
          this.ws.off('code:completion', handler);
          resolve(data.items);
        }
      };

      this.ws.on('code:completion', handler);
    });
  }

  public async setBreakpoint(breakpoint: DebugBreakpoint): Promise<void> {
    this.activeBreakpoints.set(breakpoint.id, breakpoint);
    this.ws.emit('debug:set-breakpoint', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      breakpoint
    });
  }

  public async removeBreakpoint(breakpointId: string): Promise<void> {
    this.activeBreakpoints.delete(breakpointId);
    this.ws.emit('debug:remove-breakpoint', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      breakpointId
    });
  }

  public async startDebugging(config: any): Promise<void> {
    this.ws.emit('debug:start', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      configuration: config
    });
  }

  public async stopDebugging(): Promise<void> {
    this.ws.emit('debug:stop', {
      projectId: this.projectId,
      sessionId: this.sessionId
    });
  }

  private handleCompletion(data: { uri: string; items: CompletionItem[] }): void {
    // Handle completion response
    this.completionCache.set(data.uri, data.items);
  }

  private handleDiagnostics(data: { uri: string; diagnostics: any[] }): void {
    // Handle code diagnostics (errors, warnings, etc.)
    this.ws.emit('ide:diagnostics', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      uri: data.uri,
      diagnostics: data.diagnostics
    });
  }

  private handleBreakpointHit(data: { breakpointId: string; variables: DebugVariable[] }): void {
    // Handle breakpoint hit with variable inspection
    this.ws.emit('ide:breakpoint-hit', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      breakpointId: data.breakpointId,
      variables: data.variables
    });
  }

  public dispose() {
    this.completionProvider?.dispose();
    this.hoverProvider?.dispose();
    this.definitionProvider?.dispose();
    this.referenceProvider?.dispose();
    this.ws.emit('code-editing:dispose', {
      projectId: this.projectId,
      sessionId: this.sessionId
    });
    this.breakpoints.clear();
    this.variables.clear();
    this.syntaxErrors.clear();
    this.activeBreakpoints.clear();
    this.completionCache.clear();
  }
} 