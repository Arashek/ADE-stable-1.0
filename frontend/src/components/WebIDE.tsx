import React, { useEffect, useRef, useState } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import Editor from '@monaco-editor/react';
import { CodeEditingService } from '../services/CodeEditingService';
import { IDECommunicationService } from '../services/IDECommunicationService';
import { CollaborativeEditingService } from '../services/CollaborativeEditingService';
import { CodeNavigationService } from '../services/CodeNavigationService';
import { useWebSocket } from '../hooks/useWebSocket';

interface WebIDEProps {
  projectId: string;
  initialCode?: string;
  initialFile?: string;
}

export const WebIDE: React.FC<WebIDEProps> = ({
  projectId,
  initialCode = '',
  initialFile = 'index.ts'
}) => {
  const [code, setCode] = useState(initialCode);
  const [currentFile, setCurrentFile] = useState(initialFile);
  const editorRef = useRef<any>(null);
  const codeEditingServiceRef = useRef<CodeEditingService | null>(null);
  const ideCommunicationServiceRef = useRef<IDECommunicationService | null>(null);
  const collaborativeEditingServiceRef = useRef<CollaborativeEditingService | null>(null);
  const codeNavigationServiceRef = useRef<CodeNavigationService | null>(null);
  const socket = useWebSocket(projectId);

  useEffect(() => {
    if (!socket) return;

    // Initialize services
    const codeEditingService = new CodeEditingService({
      ws: socket,
      projectId
    });

    const ideCommunicationService = new IDECommunicationService({
      ws: socket,
      projectId,
      ideType: 'web'
    });

    const collaborativeEditingService = new CollaborativeEditingService({
      ws: socket,
      projectId,
      editor: editorRef.current
    });

    const codeNavigationService = new CodeNavigationService({
      ws: socket,
      projectId,
      editor: editorRef.current
    });

    // Store service references
    codeEditingServiceRef.current = codeEditingService;
    ideCommunicationServiceRef.current = ideCommunicationService;
    collaborativeEditingServiceRef.current = collaborativeEditingService;
    codeNavigationServiceRef.current = codeNavigationService;

    // Initialize services
    Promise.all([
      codeEditingService.initialize(editorRef.current),
      ideCommunicationService.initialize(),
      collaborativeEditingService.initialize(),
      codeNavigationService.initialize()
    ]);

    // Cleanup
    return () => {
      codeEditingService.dispose();
      ideCommunicationService.dispose();
      collaborativeEditingService.dispose();
      codeNavigationService.dispose();
    };
  }, [socket, projectId]);

  const handleEditorMount = (editor: any) => {
    editorRef.current = editor;
  };

  const handleEditorChange = (value: string | undefined) => {
    if (value) {
      setCode(value);
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Paper sx={{ p: 1, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="subtitle1">
          {currentFile}
        </Typography>
      </Paper>
      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        <Editor
          height="100%"
          defaultLanguage="typescript"
          defaultValue={code}
          onMount={handleEditorMount}
          onChange={handleEditorChange}
          options={{
            minimap: { enabled: true },
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            readOnly: false,
            cursorStyle: 'line',
            automaticLayout: true,
            hover: {
              enabled: true,
              delay: 300
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
          }}
        />
      </Box>
    </Box>
  );
}; 