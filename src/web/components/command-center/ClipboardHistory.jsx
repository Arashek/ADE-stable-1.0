import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { 
  FaClipboard, FaHistory, FaSearch, FaFilter, FaTimes,
  FaCode, FaFileAlt, FaImage, FaLink, FaComments,
  FaArrowRight, FaBookmark, FaCopy
} from 'react-icons/fa';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';

const Container = styled.div`
  background: ${props => props.theme.cardBackground};
  border-radius: 8px;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h3`
  color: ${props => props.theme.text};
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const Controls = styled.div`
  display: flex;
  gap: 8px;
`;

const ControlButton = styled.button`
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  background: ${props => props.theme.buttonBackground};
  color: ${props => props.theme.text};
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.buttonHoverBackground};
  }
`;

const SearchBar = styled.div`
  display: flex;
  gap: 8px;
  align-items: center;
`;

const SearchInput = styled.input`
  flex: 1;
  padding: 8px 12px;
  border: 1px solid ${props => props.theme.border};
  border-radius: 4px;
  background: ${props => props.theme.background};
  color: ${props => props.theme.text};

  &:focus {
    outline: none;
    border-color: ${props => props.theme.primary};
  }
`;

const FilterSelect = styled.select`
  padding: 8px 12px;
  border: 1px solid ${props => props.theme.border};
  border-radius: 4px;
  background: ${props => props.theme.background};
  color: ${props => props.theme.text};
`;

const Content = styled.div`
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 20px;
  flex: 1;
  overflow: hidden;
`;

const ClipboardList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  flex: 1;
`;

const ClipboardItem = styled.div`
  background: ${props => props.theme.cardBackground};
  border-radius: 6px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  cursor: pointer;
  border: 1px solid ${props => props.theme.border};

  &:hover {
    border-color: ${props => props.theme.primary};
  }
`;

const ItemHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ItemTitle = styled.div`
  font-weight: 500;
  color: ${props => props.theme.text};
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ItemMeta = styled.div`
  font-size: 12px;
  color: ${props => props.theme.metaText};
`;

const ItemPreview = styled.div`
  font-size: 14px;
  color: ${props => props.theme.metaText};
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
`;

const PreviewPanel = styled.div`
  background: ${props => props.theme.background};
  border-radius: 6px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const PreviewHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const PreviewTitle = styled.h4`
  color: ${props => props.theme.text};
  margin: 0;
`;

const PreviewContent = styled.div`
  flex: 1;
  overflow-y: auto;
  font-size: 14px;
  line-height: 1.5;
  color: ${props => props.theme.text};
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 8px;
`;

const ActionButton = styled.button`
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  background: ${props => props.theme.buttonBackground};
  color: ${props => props.theme.text};
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.buttonHoverBackground};
  }
`;

const ClipboardHistory = () => {
  const [clipboardItems, setClipboardItems] = useState([
    {
      id: '1',
      type: 'code',
      title: 'API Endpoint',
      content: 'def handle_request(request):\n    return {"status": "success"}',
      timestamp: new Date(),
      source: 'src/api/main.py'
    },
    {
      id: '2',
      type: 'doc',
      title: 'Architecture Notes',
      content: 'The system follows a microservices architecture...',
      timestamp: new Date(),
      source: 'docs/architecture.md'
    },
    {
      id: '3',
      type: 'image',
      title: 'System Diagram',
      content: 'Base64 encoded image data...',
      timestamp: new Date(),
      source: 'assets/diagram.png'
    }
  ]);

  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [selectedItem, setSelectedItem] = useState(null);

  const filteredItems = clipboardItems.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterType === 'all' || item.type === filterType;
    return matchesSearch && matchesFilter;
  });

  const renderPreview = (item) => {
    if (!item) return null;

    switch (item.type) {
      case 'code':
        return (
          <SyntaxHighlighter language="python" style={docco}>
            {item.content}
          </SyntaxHighlighter>
        );
      case 'doc':
        return <div>{item.content}</div>;
      case 'image':
        return <div>Image preview would go here</div>;
      default:
        return <div>{item.content}</div>;
    }
  };

  const copyToClipboard = (content) => {
    navigator.clipboard.writeText(content);
  };

  const convertToContext = (item) => {
    // Implementation for converting clipboard item to context reference
    console.log('Converting to context:', item);
  };

  return (
    <Container>
      <Header>
        <Title>
          <FaClipboard />
          Clipboard History
        </Title>
        <Controls>
          <ControlButton>
            <FaHistory /> History
          </ControlButton>
        </Controls>
      </Header>

      <SearchBar>
        <FaSearch />
        <SearchInput
          placeholder="Search clipboard items..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <FilterSelect
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
        >
          <option value="all">All Types</option>
          <option value="code">Code</option>
          <option value="doc">Documentation</option>
          <option value="image">Images</option>
          <option value="url">URLs</option>
        </FilterSelect>
      </SearchBar>

      <Content>
        <ClipboardList>
          {filteredItems.map(item => (
            <ClipboardItem
              key={item.id}
              onClick={() => setSelectedItem(item)}
            >
              <ItemHeader>
                <ItemTitle>
                  {item.type === 'code' && <FaCode />}
                  {item.type === 'doc' && <FaFileAlt />}
                  {item.type === 'image' && <FaImage />}
                  {item.type === 'url' && <FaLink />}
                  {item.title}
                </ItemTitle>
                <ItemMeta>
                  {item.timestamp.toLocaleTimeString()}
                </ItemMeta>
              </ItemHeader>
              <ItemPreview>
                {item.content.substring(0, 100)}...
              </ItemPreview>
              <ItemMeta>
                Source: {item.source}
              </ItemMeta>
            </ClipboardItem>
          ))}
        </ClipboardList>

        <PreviewPanel>
          <PreviewHeader>
            <PreviewTitle>
              {selectedItem ? selectedItem.title : 'Select an item to preview'}
            </PreviewTitle>
            {selectedItem && (
              <ControlButton>
                <FaTimes />
              </ControlButton>
            )}
          </PreviewHeader>
          <PreviewContent>
            {renderPreview(selectedItem)}
          </PreviewContent>
          {selectedItem && (
            <ActionButtons>
              <ActionButton onClick={() => copyToClipboard(selectedItem.content)}>
                <FaCopy /> Copy
              </ActionButton>
              <ActionButton onClick={() => convertToContext(selectedItem)}>
                <FaBookmark /> Convert to Context
              </ActionButton>
            </ActionButtons>
          )}
        </PreviewPanel>
      </Content>
    </Container>
  );
};

export default ClipboardHistory; 