import React, { useState, useEffect } from 'react';
import { Box, Container, Grid, Paper, Typography } from '@mui/material';
import CodeEditor from './CodeEditor';
import FileExplorer from './FileExplorer';
import Terminal from './Terminal';
import { useTheme } from '@mui/material/styles';

interface CodeStudioProps {
  projectId: string;
}

const CodeStudio: React.FC<CodeStudioProps> = ({ projectId }) => {
  const theme = useTheme();
  const [currentFile, setCurrentFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const handleFileSelect = async (filePath: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/files/${projectId}/read?path=${encodeURIComponent(filePath)}`);
      if (!response.ok) throw new Error('Failed to read file');
      const content = await response.text();
      setFileContent(content);
      setCurrentFile(filePath);
    } catch (error) {
      console.error('Error reading file:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileSave = async (content: string) => {
    if (!currentFile) return;
    
    try {
      const response = await fetch(`/api/files/${projectId}/write`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          path: currentFile,
          content
        })
      });
      
      if (!response.ok) throw new Error('Failed to save file');
    } catch (error) {
      console.error('Error saving file:', error);
    }
  };

  return (
    <Container maxWidth={false} sx={{ height: '100vh', py: 2 }}>
      <Grid container spacing={2} sx={{ height: '100%' }}>
        {/* File Explorer */}
        <Grid item xs={3}>
          <Paper 
            elevation={2} 
            sx={{ 
              height: '100%',
              overflow: 'auto',
              bgcolor: theme.palette.background.default
            }}
          >
            <FileExplorer 
              projectId={projectId}
              onFileSelect={handleFileSelect}
            />
          </Paper>
        </Grid>

        {/* Code Editor */}
        <Grid item xs={6}>
          <Paper 
            elevation={2} 
            sx={{ 
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              bgcolor: theme.palette.background.default
            }}
          >
            <CodeEditor
              content={fileContent}
              currentFile={currentFile}
              onSave={handleFileSave}
              isLoading={isLoading}
            />
          </Paper>
        </Grid>

        {/* Terminal */}
        <Grid item xs={3}>
          <Paper 
            elevation={2} 
            sx={{ 
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              bgcolor: theme.palette.background.default
            }}
          >
            <Terminal projectId={projectId} />
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default CodeStudio; 