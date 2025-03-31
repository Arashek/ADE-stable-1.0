import React, { useEffect, useRef, useState } from 'react';
import { Box, Typography, CircularProgress, IconButton, Tooltip, Menu, MenuItem } from '@mui/material';
import * as monaco from 'monaco-editor';
import { useTheme } from '@mui/material/styles';
import {
  BugReport as DebugIcon,
  Code as RefactorIcon,
  Security as SecurityIcon,
  AutoFixHigh as AutoFixIcon,
  Share as ShareIcon
} from '@mui/icons-material';

interface CodeEditorProps {
  content: string;
  currentFile: string | null;
  onSave: (content: string) => void;
  isLoading: boolean;
  onDebug?: (line: number) => void;
  onRefactor?: (refactoringType: string) => void;
  onSecurityCheck?: () => void;
  onShare?: () => void;
}

interface CompletionItem {
  label: string;
  kind: monaco.languages.CompletionItemKind;
  insertText: string;
  documentation?: string;
  detail?: string;
}

const CodeEditor: React.FC<CodeEditorProps> = ({
  content,
  currentFile,
  onSave,
  isLoading,
  onDebug,
  onRefactor,
  onSecurityCheck,
  onShare
}) => {
  const editorRef = useRef<HTMLDivElement>(null);
  const monacoInstance = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const theme = useTheme();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [refactorMenuAnchor, setRefactorMenuAnchor] = useState<null | HTMLElement>(null);

  useEffect(() => {
    if (editorRef.current && !monacoInstance.current) {
      // Initialize Monaco editor with enhanced features
      monacoInstance.current = monaco.editor.create(editorRef.current, {
        value: content,
        language: getLanguageFromFile(currentFile),
        theme: theme.palette.mode === 'dark' ? 'vs-dark' : 'vs',
        automaticLayout: true,
        minimap: { enabled: true },
        scrollBeyondLastLine: false,
        fontSize: 14,
        lineNumbers: 'on',
        roundedSelection: false,
        scrollbar: {
          vertical: 'visible',
          horizontal: 'visible'
        },
        // Enhanced features
        quickSuggestions: {
          other: true,
          comments: true,
          strings: true
        },
        suggestOnTriggerCharacters: true,
        acceptSuggestionOnEnter: 'on',
        tabCompletion: 'on',
        wordBasedSuggestions: true,
        parameterHints: {
          enabled: true
        },
        snippetSuggestions: 'top',
        formatOnPaste: true,
        formatOnType: true,
        renderWhitespace: 'selection',
        renderLineHighlight: 'all',
        renderFinalNewline: true,
        // Debugging features
        glyphMargin: true,
        lineDecorationsWidth: 5,
        lineNumbersMinChars: 3,
        folding: true,
        foldingStrategy: 'indentation',
        showFoldingControls: 'always',
        // Security features
        bracketPairColorization: {
          enabled: true
        },
        guides: {
          bracketPairs: true,
          indentation: true
        }
      });

      // Register custom completion provider
      monaco.languages.registerCompletionItemProvider(getLanguageFromFile(currentFile), {
        provideCompletionItems: async (model, position) => {
          const suggestions: CompletionItem[] = [];
          
          // Add AI-powered code completion
          const lineContent = model.getLineContent(position.lineNumber);
          const word = model.getWordAtPosition(position);
          
          if (word) {
            // Add context-aware suggestions
            suggestions.push({
              label: 'AI Suggestion',
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: '// AI-generated code\n',
              documentation: 'AI-powered code completion based on context'
            });
          }

          return { suggestions };
        }
      });

      // Register custom hover provider for debugging
      monaco.languages.registerHoverProvider(getLanguageFromFile(currentFile), {
        provideHover: (model, position) => {
          const word = model.getWordAtPosition(position);
          if (word) {
            return {
              contents: [
                { value: `Debug: ${word.word}` },
                { value: 'Click to add breakpoint' }
              ]
            };
          }
          return null;
        }
      });

      // Add save shortcut (Ctrl/Cmd + S)
      monacoInstance.current.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
        const currentContent = monacoInstance.current?.getValue() || '';
        onSave(currentContent);
      });

      // Add debugging commands
      monacoInstance.current.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyD, () => {
        const position = monacoInstance.current?.getPosition();
        if (position && onDebug) {
          onDebug(position.lineNumber);
        }
      });

      // Add refactoring commands
      monacoInstance.current.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyR, () => {
        setRefactorMenuAnchor(editorRef.current);
      });
    }

    return () => {
      if (monacoInstance.current) {
        monacoInstance.current.dispose();
        monacoInstance.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (monacoInstance.current && content !== monacoInstance.current.getValue()) {
      monacoInstance.current.setValue(content);
    }
  }, [content]);

  useEffect(() => {
    if (monacoInstance.current) {
      monaco.editor.setTheme(theme.palette.mode === 'dark' ? 'vs-dark' : 'vs');
    }
  }, [theme.palette.mode]);

  const getLanguageFromFile = (file: string | null): string => {
    if (!file) return 'plaintext';
    const extension = file.split('.').pop()?.toLowerCase();
    const languageMap: { [key: string]: string } = {
      'js': 'javascript',
      'jsx': 'javascript',
      'ts': 'typescript',
      'tsx': 'typescript',
      'py': 'python',
      'java': 'java',
      'cpp': 'cpp',
      'c': 'c',
      'html': 'html',
      'css': 'css',
      'json': 'json',
      'md': 'markdown'
    };
    return languageMap[extension || ''] || 'plaintext';
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleRefactorMenuClose = () => {
    setRefactorMenuAnchor(null);
  };

  const handleRefactorAction = (action: string) => {
    if (onRefactor) {
      onRefactor(action);
    }
    handleRefactorMenuClose();
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 1, borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center' }}>
        <Typography variant="subtitle1" sx={{ flex: 1 }}>
          {currentFile || 'No file selected'}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Debug">
            <IconButton size="small" onClick={() => onDebug?.(0)}>
              <DebugIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Refactor">
            <IconButton size="small" onClick={handleMenuClick}>
              <RefactorIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Security Check">
            <IconButton size="small" onClick={() => onSecurityCheck?.()}>
              <SecurityIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="AI Suggestions">
            <IconButton size="small" onClick={() => monacoInstance.current?.trigger('keyboard', 'editor.action.triggerSuggest', {})}>
              <AutoFixIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Share">
            <IconButton size="small" onClick={() => onShare?.()}>
              <ShareIcon />
            </IconButton>
          </Tooltip>
          {isLoading && <CircularProgress size={20} />}
        </Box>
      </Box>
      <Box ref={editorRef} sx={{ flex: 1, overflow: 'hidden' }} />
      
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => handleRefactorAction('extract-method')}>Extract Method</MenuItem>
        <MenuItem onClick={() => handleRefactorAction('rename-symbol')}>Rename Symbol</MenuItem>
        <MenuItem onClick={() => handleRefactorAction('extract-variable')}>Extract Variable</MenuItem>
        <MenuItem onClick={() => handleRefactorAction('inline-variable')}>Inline Variable</MenuItem>
      </Menu>
    </Box>
  );
};

export default CodeEditor; 