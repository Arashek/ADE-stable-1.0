declare module '@monaco-editor/react' {
  import * as React from 'react';

  export interface EditorProps {
    height?: string | number;
    width?: string | number;
    value?: string;
    defaultValue?: string;
    language?: string;
    theme?: string;
    options?: Record<string, any>;
    onChange?: (value: string | undefined) => void;
    onMount?: (editor: any, monaco: any) => void;
    beforeMount?: (monaco: any) => void;
    onValidate?: (markers: any[]) => void;
  }

  export interface DiffEditorProps extends EditorProps {
    original?: string;
    modified?: string;
    onMount?: (editor: any, monaco: any) => void;
  }

  export function Editor(props: EditorProps): React.ReactElement;
  export function DiffEditor(props: DiffEditorProps): React.ReactElement;
  export function useMonaco(): any;
  export function loader: any;
}

declare module 'react-force-graph-2d' {
  import * as React from 'react';

  export interface GraphData {
    nodes: Array<{
      id: string;
      [key: string]: any;
    }>;
    links: Array<{
      source: string;
      target: string;
      [key: string]: any;
    }>;
  }

  export interface ForceGraphProps {
    graphData: GraphData;
    nodeLabel?: string | ((node: any) => string);
    linkLabel?: string | ((link: any) => string);
    nodeColor?: string | ((node: any) => string);
    linkColor?: string | ((link: any) => string);
    width?: number;
    height?: number;
    onNodeClick?: (node: any, event: any) => void;
    onLinkClick?: (link: any, event: any) => void;
    [key: string]: any;
  }

  export default class ForceGraph2D extends React.Component<ForceGraphProps> {}
}

declare module 'jsoneditor-react' {
  import * as React from 'react';

  export interface JsonEditorProps {
    value?: any;
    onChange?: (value: any) => void;
    mode?: 'tree' | 'view' | 'form' | 'code' | 'text';
    history?: boolean;
    search?: boolean;
    navigationBar?: boolean;
    statusBar?: boolean;
    [key: string]: any;
  }

  export class JsonEditor extends React.Component<JsonEditorProps> {}
} 