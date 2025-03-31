import * as monaco from 'monaco-editor';
import { Socket } from 'socket.io-client';
import { v4 as uuidv4 } from 'uuid';

export interface CodeNavigationConfig {
  ws: Socket;
  projectId: string;
  editor: monaco.editor.IStandaloneCodeEditor;
}

export interface Symbol {
  name: string;
  kind: monaco.languages.SymbolKind;
  location: monaco.languages.Location;
  containerName?: string;
  range: monaco.IRange;
}

export interface OutlineModel {
  symbols: Symbol[];
  structure: any;
}

export interface Location {
  uri: string;
  range: {
    start: { line: number; character: number };
    end: { line: number; character: number };
  };
}

export interface SymbolInformation {
  name: string;
  kind: number;
  location: Location;
  containerName?: string;
}

export interface OutlineItem {
  name: string;
  kind: number;
  range: {
    start: { line: number; character: number };
    end: { line: number; character: number };
  };
  children?: OutlineItem[];
}

export class CodeNavigationService {
  private ws: Socket;
  private projectId: string;
  private sessionId: string;
  private editor: monaco.editor.IStandaloneCodeEditor;
  private outlineView: OutlineModel | null = null;
  private symbolDecorations: string[] = [];
  private referenceDecorations: string[] = [];
  private symbolCache: Map<string, SymbolInformation[]> = new Map();
  private outlineCache: Map<string, OutlineItem[]> = new Map();

  constructor(config: CodeNavigationConfig) {
    this.ws = config.ws;
    this.projectId = config.projectId;
    this.editor = config.editor;
    this.sessionId = uuidv4();
    this.setupEventListeners();
  }

  public async initialize() {
    this.setupEventListeners();
    this.setupEditorListeners();
    this.updateOutlineView();
  }

  private setupEventListeners() {
    this.ws.on('navigation:symbols', (data: { symbols: Symbol[] }) => {
      this.updateSymbolDecorations(data.symbols);
    });

    this.ws.on('navigation:references', (data: { references: monaco.languages.Location[] }) => {
      this.updateReferenceDecorations(data.references);
    });

    this.ws.on('navigation:outline', (data: { outline: OutlineModel }) => {
      this.outlineView = data.outline;
      this.ws.emit('navigation:outline-updated', {
        projectId: this.projectId,
        outline: data.outline
      });
    });

    this.ws.on('navigation:definition', (data: { uri: string; location: Location }) => {
      this.handleDefinition(data);
    });

    this.ws.on('navigation:references', (data: { uri: string; references: Location[] }) => {
      this.handleReferences(data);
    });

    this.ws.on('navigation:outline', (data: { uri: string; outline: OutlineItem[] }) => {
      this.handleOutline(data);
    });
  }

  private setupEditorListeners() {
    // Handle model content changes
    this.editor.onDidChangeModelContent(() => {
      this.updateOutlineView();
    });

    // Handle cursor position changes
    this.editor.onDidChangeCursorPosition((event) => {
      const word = this.editor.getModel()?.getWordAtPosition(event.position);
      if (word) {
        this.findReferences(word);
      }
    });
  }

  public async jumpToDefinition(position: monaco.Position) {
    const model = this.editor.getModel();
    if (!model) return;

    const word = model.getWordAtPosition(position);
    if (!word) return;

    this.ws.emit('navigation:definition', {
      projectId: this.projectId,
      word: word.word,
      position: position
    }, (definition: monaco.languages.Location | null) => {
      if (definition) {
        const targetPosition = new monaco.Position(
          definition.range.startLineNumber,
          definition.range.startColumn
        );
        this.editor.revealPositionInCenter(targetPosition);
        this.editor.setPosition(targetPosition);
      }
    });
  }

  public async findReferences(word: monaco.editor.IWordAtPosition) {
    const model = this.editor.getModel();
    if (!model) return;

    this.ws.emit('navigation:references', {
      projectId: this.projectId,
      word: word.word
    }, (references: monaco.languages.Location[]) => {
      this.updateReferenceDecorations(references);
    });
  }

  private updateOutlineView() {
    const model = this.editor.getModel();
    if (!model) return;

    this.ws.emit('navigation:outline', {
      projectId: this.projectId,
      uri: model.uri.toString()
    });
  }

  private updateSymbolDecorations(symbols: Symbol[]) {
    const model = this.editor.getModel();
    if (!model) return;

    const decorations = symbols.map(symbol => ({
      range: symbol.range,
      options: {
        className: `symbol-${symbol.kind}`,
        hoverMessage: { value: `${symbol.name} (${this.getSymbolKindName(symbol.kind)})` }
      }
    }));

    this.symbolDecorations = this.editor.deltaDecorations(
      this.symbolDecorations,
      decorations
    );
  }

  private updateReferenceDecorations(references: monaco.languages.Location[]) {
    const model = this.editor.getModel();
    if (!model) return;

    const decorations = references.map(reference => ({
      range: reference.range,
      options: {
        className: 'reference-highlight',
        hoverMessage: { value: 'Reference' }
      }
    }));

    this.referenceDecorations = this.editor.deltaDecorations(
      this.referenceDecorations,
      decorations
    );
  }

  private getSymbolKindName(kind: monaco.languages.SymbolKind): string {
    const kindMap: { [key: number]: string } = {
      [monaco.languages.SymbolKind.File]: 'File',
      [monaco.languages.SymbolKind.Module]: 'Module',
      [monaco.languages.SymbolKind.Namespace]: 'Namespace',
      [monaco.languages.SymbolKind.Package]: 'Package',
      [monaco.languages.SymbolKind.Class]: 'Class',
      [monaco.languages.SymbolKind.Method]: 'Method',
      [monaco.languages.SymbolKind.Property]: 'Property',
      [monaco.languages.SymbolKind.Field]: 'Field',
      [monaco.languages.SymbolKind.Constructor]: 'Constructor',
      [monaco.languages.SymbolKind.Enum]: 'Enum',
      [monaco.languages.SymbolKind.Interface]: 'Interface',
      [monaco.languages.SymbolKind.Function]: 'Function',
      [monaco.languages.SymbolKind.Variable]: 'Variable',
      [monaco.languages.SymbolKind.Constant]: 'Constant',
      [monaco.languages.SymbolKind.String]: 'String',
      [monaco.languages.SymbolKind.Number]: 'Number',
      [monaco.languages.SymbolKind.Boolean]: 'Boolean',
      [monaco.languages.SymbolKind.Array]: 'Array',
      [monaco.languages.SymbolKind.Object]: 'Object',
      [monaco.languages.SymbolKind.Key]: 'Key',
      [monaco.languages.SymbolKind.Null]: 'Null',
      [monaco.languages.SymbolKind.EnumMember]: 'Enum Member',
      [monaco.languages.SymbolKind.Struct]: 'Struct',
      [monaco.languages.SymbolKind.Event]: 'Event',
      [monaco.languages.SymbolKind.Operator]: 'Operator',
      [monaco.languages.SymbolKind.TypeParameter]: 'Type Parameter'
    };
    return kindMap[kind] || 'Unknown';
  }

  public async findDefinition(uri: string, position: { line: number; character: number }): Promise<Location | null> {
    return new Promise((resolve) => {
      this.ws.emit('navigation:find-definition', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        uri,
        position
      });

      const handler = (data: { uri: string; location: Location }) => {
        if (data.uri === uri) {
          this.ws.off('navigation:definition', handler);
          resolve(data.location);
        }
      };

      this.ws.on('navigation:definition', handler);
    });
  }

  public async findReferences(uri: string, position: { line: number; character: number }): Promise<Location[]> {
    return new Promise((resolve) => {
      this.ws.emit('navigation:find-references', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        uri,
        position
      });

      const handler = (data: { uri: string; references: Location[] }) => {
        if (data.uri === uri) {
          this.ws.off('navigation:references', handler);
          resolve(data.references);
        }
      };

      this.ws.on('navigation:references', handler);
    });
  }

  public async getDocumentSymbols(uri: string): Promise<SymbolInformation[]> {
    // Check cache first
    if (this.symbolCache.has(uri)) {
      return this.symbolCache.get(uri)!;
    }

    return new Promise((resolve) => {
      this.ws.emit('navigation:document-symbols', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        uri
      });

      const handler = (data: { uri: string; symbols: SymbolInformation[] }) => {
        if (data.uri === uri) {
          this.symbolCache.set(uri, data.symbols);
          this.ws.off('navigation:document-symbols', handler);
          resolve(data.symbols);
        }
      };

      this.ws.on('navigation:document-symbols', handler);
    });
  }

  public async getOutline(uri: string): Promise<OutlineItem[]> {
    // Check cache first
    if (this.outlineCache.has(uri)) {
      return this.outlineCache.get(uri)!;
    }

    return new Promise((resolve) => {
      this.ws.emit('navigation:outline', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        uri
      });

      const handler = (data: { uri: string; outline: OutlineItem[] }) => {
        if (data.uri === uri) {
          this.outlineCache.set(uri, data.outline);
          this.ws.off('navigation:outline', handler);
          resolve(data.outline);
        }
      };

      this.ws.on('navigation:outline', handler);
    });
  }

  private handleDefinition(data: { uri: string; location: Location }): void {
    this.ws.emit('ide:definition', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      uri: data.uri,
      location: data.location
    });
  }

  private handleReferences(data: { uri: string; references: Location[] }): void {
    this.ws.emit('ide:references', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      uri: data.uri,
      references: data.references
    });
  }

  private handleOutline(data: { uri: string; outline: OutlineItem[] }): void {
    this.ws.emit('ide:outline', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      uri: data.uri,
      outline: data.outline
    });
  }

  public dispose() {
    this.editor.deltaDecorations(this.symbolDecorations, []);
    this.editor.deltaDecorations(this.referenceDecorations, []);
    this.outlineView = null;
    this.symbolCache.clear();
    this.outlineCache.clear();
  }
} 