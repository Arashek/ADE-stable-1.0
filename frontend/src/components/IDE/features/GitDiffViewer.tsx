import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Remove as RemoveIcon,
  SwapHoriz as SwapIcon,
  ContentCopy as CopyIcon,
  Check as CheckIcon,
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface DiffLine {
  type: 'add' | 'remove' | 'context';
  content: string;
  oldLineNumber?: number;
  newLineNumber?: number;
}

interface FileDiff {
  oldPath: string;
  newPath: string;
  hunks: Array<{
    header: string;
    lines: DiffLine[];
  }>;
  language: string;
}

interface GitDiffViewerProps {
  diffs: FileDiff[];
  onStageHunk?: (filePath: string, hunkIndex: number) => void;
  onStageFile?: (filePath: string) => void;
  onDiscardChanges?: (filePath: string) => void;
}

export const GitDiffViewer: React.FC<GitDiffViewerProps> = ({
  diffs,
  onStageHunk,
  onStageFile,
  onDiscardChanges,
}) => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [copiedLines, setCopiedLines] = useState<string[]>([]);

  const handleCopyLine = (content: string) => {
    navigator.clipboard.writeText(content);
    setCopiedLines([...copiedLines, content]);
    setTimeout(() => {
      setCopiedLines(prev => prev.filter(line => line !== content));
    }, 2000);
  };

  const getLineColor = (type: DiffLine['type']) => {
    switch (type) {
      case 'add':
        return theme.palette.success.main;
      case 'remove':
        return theme.palette.error.main;
      default:
        return theme.palette.text.primary;
    }
  };

  const getLineBackground = (type: DiffLine['type']) => {
    switch (type) {
      case 'add':
        return theme.palette.success.light + '20';
      case 'remove':
        return theme.palette.error.light + '20';
      default:
        return 'transparent';
    }
  };

  const renderLineNumber = (number?: number) => (
    <Box
      sx={{
        width: 40,
        textAlign: 'right',
        color: theme.palette.text.secondary,
        userSelect: 'none',
        pr: 1,
      }}
    >
      {number || ' '}
    </Box>
  );

  const renderDiffLine = (line: DiffLine) => (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        backgroundColor: getLineBackground(line.type),
        '&:hover': {
          '& .actions': {
            opacity: 1,
          },
        },
      }}
    >
      <Box sx={{ display: 'flex', width: 80 }}>
        {renderLineNumber(line.oldLineNumber)}
        {renderLineNumber(line.newLineNumber)}
      </Box>
      <Box
        sx={{
          width: 20,
          color: getLineColor(line.type),
          userSelect: 'none',
        }}
      >
        {line.type === 'add' ? '+' : line.type === 'remove' ? '-' : ' '}
      </Box>
      <Box
        sx={{
          flex: 1,
          fontFamily: 'monospace',
          whiteSpace: 'pre',
          color: getLineColor(line.type),
        }}
      >
        {line.content}
      </Box>
      <Box
        className="actions"
        sx={{
          opacity: 0,
          transition: 'opacity 0.2s',
          display: 'flex',
          gap: 0.5,
          pr: 1,
        }}
      >
        <Tooltip title="Copy line">
          <IconButton
            size="small"
            onClick={() => handleCopyLine(line.content)}
          >
            {copiedLines.includes(line.content) ? (
              <CheckIcon fontSize="small" />
            ) : (
              <CopyIcon fontSize="small" />
            )}
          </IconButton>
        </Tooltip>
      </Box>
    </Box>
  );

  const renderHunk = (hunk: FileDiff['hunks'][0], fileIndex: number, hunkIndex: number) => (
    <Box key={hunkIndex} sx={{ mb: 2 }}>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          p: 1,
          backgroundColor: theme.palette.action.hover,
        }}
      >
        <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
          {hunk.header}
        </Typography>
        {onStageHunk && (
          <Tooltip title="Stage hunk">
            <IconButton
              size="small"
              onClick={() => onStageHunk(diffs[fileIndex].newPath, hunkIndex)}
            >
              <AddIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        )}
      </Box>
      {hunk.lines.map((line, lineIndex) => (
        <Box key={lineIndex}>
          {renderDiffLine(line)}
        </Box>
      ))}
    </Box>
  );

  return (
    <Paper
      elevation={0}
      sx={{
        height: '100%',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        border: `1px solid ${theme.palette.divider}`,
      }}
    >
      <Tabs
        value={activeTab}
        onChange={(_, value) => setActiveTab(value)}
        sx={{ borderBottom: `1px solid ${theme.palette.divider}` }}
      >
        {diffs.map((diff, index) => (
          <Tab
            key={index}
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="body2" noWrap>
                  {diff.newPath}
                </Typography>
              </Box>
            }
          />
        ))}
      </Tabs>
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {diffs[activeTab] && (
          <>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                mb: 2,
              }}
            >
              <Typography variant="subtitle2">
                {diffs[activeTab].oldPath === diffs[activeTab].newPath ? (
                  diffs[activeTab].newPath
                ) : (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {diffs[activeTab].oldPath}
                    <SwapIcon fontSize="small" />
                    {diffs[activeTab].newPath}
                  </Box>
                )}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                {onStageFile && (
                  <Tooltip title="Stage file">
                    <IconButton
                      size="small"
                      onClick={() => onStageFile(diffs[activeTab].newPath)}
                    >
                      <AddIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                )}
                {onDiscardChanges && (
                  <Tooltip title="Discard changes">
                    <IconButton
                      size="small"
                      onClick={() => onDiscardChanges(diffs[activeTab].newPath)}
                    >
                      <RemoveIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                )}
              </Box>
            </Box>
            {diffs[activeTab].hunks.map((hunk, hunkIndex) =>
              renderHunk(hunk, activeTab, hunkIndex)
            )}
          </>
        )}
      </Box>
    </Paper>
  );
};
