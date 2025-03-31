import * as monaco from 'monaco-editor';

// Configure Monaco Editor's worker
window.MonacoEnvironment = {
  getWorkerUrl: function (moduleId, label) {
    if (label === 'json') {
      return '/monaco-editor/json.worker.js';
    }
    if (label === 'css' || label === 'scss' || label === 'less') {
      return '/monaco-editor/css.worker.js';
    }
    if (label === 'html' || label === 'handlebars' || label === 'razor') {
      return '/monaco-editor/html.worker.js';
    }
    if (label === 'typescript' || label === 'javascript') {
      return '/monaco-editor/ts.worker.js';
    }
    return '/monaco-editor/editor.worker.js';
  }
};

// Configure Monaco Editor's theme
monaco.editor.defineTheme('vs-dark-custom', {
  base: 'vs-dark',
  inherit: true,
  rules: [],
  colors: {
    'editor.background': '#1e1e1e',
    'editor.foreground': '#d4d4d4',
    'editor.lineHighlightBackground': '#2a2d2e',
    'editorCursor.foreground': '#ffffff',
    'editor.selectionBackground': '#264f78',
    'editor.inactiveSelectionBackground': '#3a3d41',
    'editorLineNumber.foreground': '#858585',
    'editorLineNumber.activeForeground': '#c6c6c6',
    'editorGutter.background': '#1e1e1e',
    'editorGutter.modifiedBackground': '#1b81b883',
    'editorGutter.addedBackground': '#81b88b',
    'editorGutter.deletedBackground': '#ff0000'
  }
});

// Register the custom theme
monaco.editor.setTheme('vs-dark-custom');

// Configure Monaco Editor's default options
export const defaultEditorOptions: monaco.editor.IStandaloneEditorConstructionOptions = {
  minimap: { enabled: true },
  scrollBeyondLastLine: false,
  fontSize: 14,
  lineNumbers: 'on',
  roundedSelection: false,
  scrollbar: {
    vertical: 'visible',
    horizontal: 'visible'
  },
  automaticLayout: true,
  wordWrap: 'on',
  renderWhitespace: 'selection',
  tabSize: 2,
  insertSpaces: true,
  bracketPairColorization: {
    enabled: true
  },
  guides: {
    bracketPairs: true
  }
}; 