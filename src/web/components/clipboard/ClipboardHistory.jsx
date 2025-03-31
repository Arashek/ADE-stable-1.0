import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import useClipboardManagerStore from '../../utils/clipboard-manager';

const HistoryContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background: ${props => props.theme.background};
  color: ${props => props.theme.text};
  border-radius: 8px;
  overflow: hidden;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid ${props => props.theme.border};
`;

const SearchInput = styled.input`
  padding: 8px 12px;
  border: 1px solid ${props => props.theme.border};
  border-radius: 4px;
  background: ${props => props.theme.inputBackground};
  color: ${props => props.theme.text};
  width: 200px;
  font-size: 14px;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.primary};
  }
`;

const HistoryList = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 8px;
`;

const HistoryItem = styled.div`
  display: flex;
  align-items: flex-start;
  padding: 12px;
  margin-bottom: 8px;
  background: ${props => props.theme.itemBackground};
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.itemHoverBackground};
  }

  ${props => props.selected && `
    background: ${props.theme.selectedItemBackground};
    border-left: 3px solid ${props.theme.primary};
  `}
`;

const ContentPreview = styled.div`
  flex: 1;
  margin-right: 12px;
  font-size: 14px;
  line-height: 1.5;
  max-height: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
`;

const MetaInfo = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  font-size: 12px;
  color: ${props => props.theme.metaText};
`;

const TypeBadge = styled.span`
  padding: 2px 6px;
  border-radius: 4px;
  background: ${props => props.theme.badgeBackground};
  color: ${props => props.theme.badgeText};
  font-size: 12px;
  margin-bottom: 4px;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: ${props => props.theme.metaText};
  font-size: 14px;
`;

const ClipboardHistory = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedItem, setSelectedItem] = useState(null);
  const {
    history,
    getRecentHistory,
    searchHistory,
    clearHistory,
    addToHistory,
    setSelectedContent
  } = useClipboardManagerStore();

  useEffect(() => {
    // Listen for clipboard events
    const handlePaste = (event) => {
      const content = event.clipboardData.getData('text');
      if (content) {
        addToHistory(content);
      }
    };

    document.addEventListener('paste', handlePaste);
    return () => document.removeEventListener('paste', handlePaste);
  }, [addToHistory]);

  const filteredHistory = searchQuery
    ? searchHistory(searchQuery)
    : getRecentHistory();

  const handleItemClick = (item) => {
    setSelectedItem(item.id);
    setSelectedContent(item.content);
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  return (
    <HistoryContainer>
      <Header>
        <SearchInput
          type="text"
          placeholder="Search clipboard history..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <button onClick={clearHistory}>Clear History</button>
      </Header>

      <HistoryList>
        {filteredHistory.length === 0 ? (
          <EmptyState>
            <p>No clipboard history</p>
            <p>Copy something to see it here</p>
          </EmptyState>
        ) : (
          filteredHistory.map((item) => (
            <HistoryItem
              key={item.id}
              selected={selectedItem === item.id}
              onClick={() => handleItemClick(item)}
            >
              <ContentPreview>{item.content}</ContentPreview>
              <MetaInfo>
                <TypeBadge>{item.type}</TypeBadge>
                <span>{formatTimestamp(item.timestamp)}</span>
              </MetaInfo>
            </HistoryItem>
          ))
        )}
      </HistoryList>
    </HistoryContainer>
  );
};

export default ClipboardHistory; 