import React from 'react';
import { Box, useTheme } from '@mui/material';
import { styled } from '@mui/material/styles';

// Create a styled component for the code display
const CodeContainer = styled(Box)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1E1E1E' : '#f5f5f5', // VS Code-like dark background or light background
  color: theme.palette.mode === 'dark' ? '#D4D4D4' : '#333333',  // Appropriate text color
  padding: theme.spacing(2),
  borderRadius: theme.shape.borderRadius,
  fontFamily: 'Consolas, Monaco, "Andale Mono", "Ubuntu Mono", monospace',
  fontSize: '0.875rem',
  overflow: 'auto',
  marginBottom: theme.spacing(2),
  position: 'relative',
  border: `1px solid ${theme.palette.divider}`,
  minHeight: '2.5rem',
  maxHeight: '400px',
  whiteSpace: 'pre',
  '&::-webkit-scrollbar': {
    width: '8px',
    height: '8px',
  },
  '&::-webkit-scrollbar-thumb': {
    backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)',
    borderRadius: '4px',
  },
  '&::-webkit-scrollbar-track': {
    backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)',
  },
}));

const LanguageLabel = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: 0,
  right: 0,
  padding: theme.spacing(0.5, 1),
  backgroundColor: theme.palette.mode === 'dark' ? 'rgba(30, 30, 30, 0.8)' : 'rgba(245, 245, 245, 0.8)',
  borderBottomLeftRadius: theme.shape.borderRadius,
  fontSize: '0.7rem',
  color: theme.palette.text.secondary,
}));

// Define basic syntax highlighting for common languages
const applyHighlighting = (code: string, language: string): string => {
  let highlightedCode = code;
  
  switch (language.toLowerCase()) {
    case 'javascript':
    case 'js':
    case 'typescript':
    case 'ts':
      // Highlight keywords
      highlightedCode = highlightedCode.replace(
        /(const|let|var|function|return|if|else|for|while|class|import|export|from|async|await|try|catch|throw|new|this|super|extends|implements|interface|type|enum|namespace|module|public|private|protected|static|get|set|default|break|continue|switch|case|yield|typeof|instanceof|void|delete|null|undefined|true|false)\b/g,
        '<span style="color: #569CD6;">$1</span>'
      );
      // Highlight strings
      highlightedCode = highlightedCode.replace(
        /(["'`])(?:(?=(\\?))\2.)*?\1/g,
        '<span style="color: #CE9178;">$&</span>'
      );
      // Highlight comments
      highlightedCode = highlightedCode.replace(
        /(\/\/.*|\/\*[\s\S]*?\*\/)/g,
        '<span style="color: #6A9955;">$1</span>'
      );
      // Highlight numbers
      highlightedCode = highlightedCode.replace(
        /\b(\d+(?:\.\d+)?)\b/g,
        '<span style="color: #B5CEA8;">$1</span>'
      );
      break;
      
    case 'html':
    case 'xml':
      // Highlight tags
      highlightedCode = highlightedCode.replace(
        /(&lt;[\/\!]?[a-z].*?&gt;)/gi,
        '<span style="color: #569CD6;">$1</span>'
      );
      // Highlight attributes
      highlightedCode = highlightedCode.replace(
        /(\s[a-z0-9-]+)=/gi,
        '<span style="color: #9CDCFE;">$1</span>='
      );
      // Highlight strings
      highlightedCode = highlightedCode.replace(
        /(["'])(?:(?=(\\?))\2.)*?\1/g,
        '<span style="color: #CE9178;">$&</span>'
      );
      break;
      
    case 'css':
      // Highlight selectors
      highlightedCode = highlightedCode.replace(
        /([a-z0-9\-\_\.#\*\:]+\s*\{)/gi,
        '<span style="color: #D7BA7D;">$1</span>'
      );
      // Highlight properties
      highlightedCode = highlightedCode.replace(
        /(\s[a-z\-]+\s*:)/gi,
        '<span style="color: #9CDCFE;">$1</span>'
      );
      // Highlight values
      highlightedCode = highlightedCode.replace(
        /(:.*?;)/g,
        function(match) {
          return match.replace(/(#[a-f0-9]{3,6}|rgba?\([^)]+\))/gi, '<span style="color: #CE9178;">$1</span>');
        }
      );
      break;
    
    case 'json':
      // Highlight keys
      highlightedCode = highlightedCode.replace(
        /(".*?"):/g,
        '<span style="color: #9CDCFE;">$1</span>:'
      );
      // Highlight strings
      highlightedCode = highlightedCode.replace(
        /:\s*(".*?")(,|\n|$)/g,
        ': <span style="color: #CE9178;">$1</span>$2'
      );
      // Highlight numbers
      highlightedCode = highlightedCode.replace(
        /:\s*(\d+(?:\.\d+)?)(,|\n|$)/g,
        ': <span style="color: #B5CEA8;">$1</span>$2'
      );
      // Highlight booleans and null
      highlightedCode = highlightedCode.replace(
        /:\s*(true|false|null)(,|\n|$)/g,
        ': <span style="color: #569CD6;">$1</span>$2'
      );
      break;
      
    default:
      // Default highlighting for other languages
      // Highlight strings
      highlightedCode = highlightedCode.replace(
        /(["'`])(?:(?=(\\?))\2.)*?\1/g,
        '<span style="color: #CE9178;">$&</span>'
      );
      // Highlight comments
      highlightedCode = highlightedCode.replace(
        /(\/\/.*|\/\*[\s\S]*?\*\/|#.*)/g,
        '<span style="color: #6A9955;">$1</span>'
      );
      break;
  }
  
  return highlightedCode;
};

// Define props for the SyntaxHighlighter component
interface SyntaxHighlighterProps {
  code: string;
  language: string;
  showLanguage?: boolean;
}

const SyntaxHighlighter: React.FC<SyntaxHighlighterProps> = ({ code, language, showLanguage = true }) => {
  const theme = useTheme();
  
  // Escape HTML characters for safe rendering
  const escapeHtml = (unsafe: string): string => {
    return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  };
  
  // Prepare code for syntax highlighting
  const escapedCode = escapeHtml(code);
  const highlightedCode = applyHighlighting(escapedCode, language);
  
  return (
    <CodeContainer>
      {showLanguage && <LanguageLabel>{language}</LanguageLabel>}
      <Box 
        dangerouslySetInnerHTML={{ __html: highlightedCode }} 
        sx={{ 
          pt: showLanguage ? 3 : 0,
          color: theme.palette.mode === 'dark' ? '#D4D4D4' : '#333333',
        }}
      />
    </CodeContainer>
  );
};

export default SyntaxHighlighter;
