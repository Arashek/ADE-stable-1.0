import React from 'react';
import styled from 'styled-components';
import { FaCode, FaTable, FaFileAlt, FaChartBar } from 'react-icons/fa';
import PropTypes from 'prop-types';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { atomOneDark } from 'react-syntax-highlighter/dist/esm/styles/hljs';

const OutputContainer = styled.div`
  background: white;
  border-radius: 8px;
  overflow: hidden;
  margin: 8px 0;
`;

const OutputHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
`;

const OutputIcon = styled.div`
  color: ${props => {
    switch (props.type) {
      case 'code':
        return '#3b82f6';
      case 'data':
        return '#10b981';
      case 'document':
        return '#f59e0b';
      case 'chart':
        return '#8b5cf6';
      default:
        return '#64748b';
    }
  }};
`;

const OutputTitle = styled.span`
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
`;

const OutputContent = styled.div`
  padding: 16px;
  font-size: 14px;
  line-height: 1.5;
  color: #1e293b;
  overflow-x: auto;

  pre {
    margin: 0;
    padding: 12px;
    background: #1e293b;
    border-radius: 6px;
    overflow-x: auto;
  }

  code {
    font-family: 'Fira Code', monospace;
    font-size: 13px;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0;
  }

  th, td {
    padding: 8px 12px;
    text-align: left;
    border-bottom: 1px solid #e2e8f0;
  }

  th {
    background: #f8fafc;
    font-weight: 500;
  }

  tr:hover {
    background: #f8fafc;
  }

  img {
    max-width: 100%;
    height: auto;
    border-radius: 6px;
  }
`;

const getOutputIcon = (type) => {
  switch (type) {
    case 'code':
      return <FaCode />;
    case 'data':
      return <FaTable />;
    case 'document':
      return <FaFileAlt />;
    case 'chart':
      return <FaChartBar />;
    default:
      return null;
  }
};

const renderContent = (content, type) => {
  switch (type) {
    case 'code':
      return (
        <SyntaxHighlighter
          language={content.language || 'javascript'}
          style={atomOneDark}
          customStyle={{
            margin: 0,
            padding: '12px',
            borderRadius: '6px',
          }}
        >
          {content.code}
        </SyntaxHighlighter>
      );
    case 'data':
      return (
        <table>
          <thead>
            <tr>
              {content.headers.map((header, index) => (
                <th key={index}>{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {content.rows.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {row.map((cell, cellIndex) => (
                  <td key={cellIndex}>{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      );
    case 'chart':
      return (
        <div>
          {/* Chart rendering logic would go here */}
          <img src={content.imageUrl} alt={content.title} />
        </div>
      );
    default:
      return <div>{content}</div>;
  }
};

const AgentOutputDisplay = ({ output }) => {
  const { type, content, title } = output;

  return (
    <OutputContainer>
      <OutputHeader>
        <OutputIcon type={type}>
          {getOutputIcon(type)}
        </OutputIcon>
        <OutputTitle>{title}</OutputTitle>
      </OutputHeader>
      <OutputContent>
        {renderContent(content, type)}
      </OutputContent>
    </OutputContainer>
  );
};

AgentOutputDisplay.propTypes = {
  output: PropTypes.shape({
    type: PropTypes.oneOf(['text', 'code', 'data', 'document', 'chart']).isRequired,
    content: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.shape({
        language: PropTypes.string,
        code: PropTypes.string,
      }),
      PropTypes.shape({
        headers: PropTypes.arrayOf(PropTypes.string),
        rows: PropTypes.arrayOf(PropTypes.array),
      }),
      PropTypes.shape({
        imageUrl: PropTypes.string,
        title: PropTypes.string,
      }),
    ]).isRequired,
    title: PropTypes.string.isRequired,
  }).isRequired,
};

export default AgentOutputDisplay; 