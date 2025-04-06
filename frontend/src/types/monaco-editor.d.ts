declare module 'monaco-editor' {
  // Basic definitions for monaco-editor
  export interface IDisposable {
    dispose(): void;
  }
  
  export interface IEditor extends IDisposable {
    getValue(): string;
    setValue(value: string): void;
    getModel(): any;
    updateOptions(options: any): void;
    layout(dimension?: { width: number; height: number }): void;
    focus(): void;
    onDidChangeModelContent(listener: (e: any) => void): IDisposable;
  }

  export interface IStandaloneCodeEditor extends IEditor {
    getDomNode(): HTMLElement | null;
  }

  export interface IEditorConstructionOptions {
    value?: string;
    language?: string;
    theme?: string;
    readOnly?: boolean;
    automaticLayout?: boolean;
    scrollBeyondLastLine?: boolean;
    minimap?: {
      enabled?: boolean;
    };
    lineNumbers?: 'on' | 'off' | 'relative' | 'interval';
    wordWrap?: 'off' | 'on' | 'wordWrapColumn' | 'bounded';
    [key: string]: any;
  }

  export namespace editor {
    export function create(element: HTMLElement, options?: IEditorConstructionOptions): IStandaloneCodeEditor;
    export function colorizeElement(element: HTMLElement, options: any): Promise<void>;
    export function setTheme(theme: string): void;
    export function defineTheme(theme: string, options: any): void;
    export type IStandaloneCodeEditor = IStandaloneCodeEditor;
  }

  export const KeyMod: {
    CtrlCmd: number;
    Shift: number;
    Alt: number;
    WinCtrl: number;
  };

  export const KeyCode: {
    Enter: number;
    F1: number;
    F2: number;
    F3: number;
    F4: number;
    F5: number;
    F6: number;
    F7: number;
    F8: number;
    F9: number;
    F10: number;
    F11: number;
    F12: number;
    F13: number;
    F14: number;
    F15: number;
    F16: number;
    F17: number;
    F18: number;
    F19: number;
    Escape: number;
    Tab: number;
    Backspace: number;
    Delete: number;
    Space: number;
    [key: string]: number;
  };

  export namespace languages {
    export function register(language: any): void;
    export function setMonarchTokensProvider(languageId: string, provider: any): IDisposable;
    export function setLanguageConfiguration(languageId: string, configuration: any): IDisposable;
    export function registerCompletionItemProvider(languageId: string, provider: any): IDisposable;
    export function registerHoverProvider(languageId: string, provider: any): IDisposable;
    
    export enum CompletionItemKind {
      Method = 0,
      Function = 1,
      Constructor = 2,
      Field = 3,
      Variable = 4,
      Class = 5,
      Struct = 6,
      Interface = 7,
      Module = 8,
      Property = 9,
      Event = 10,
      Operator = 11,
      Unit = 12,
      Value = 13,
      Constant = 14,
      Enum = 15,
      EnumMember = 16,
      Keyword = 17,
      Text = 18,
      Color = 19,
      File = 20,
      Reference = 21,
      Customcolor = 22,
      Folder = 23,
      TypeParameter = 24,
      Snippet = 25
    }
  }
}
