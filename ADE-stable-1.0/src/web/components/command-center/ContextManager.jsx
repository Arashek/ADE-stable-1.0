import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { 
  FaBookmark, FaSearch, FaFilter, FaHistory, FaTimes,
  FaCode, FaFileAlt, FaImage, FaLink, FaComments,
  FaArrowUp, FaArrowDown, FaStar, FaRegStar
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

const Sidebar = styled.div`
  background: ${props => props.theme.background};
  border-radius: 6px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const ContextList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  flex: 1;
`;

const ContextItem = styled.div`
  background: ${props => props.theme.cardBackground};
  border-radius: 6px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  cursor: grab;
  border: 1px solid ${props => props.theme.border};

  &:hover {
    border-color: ${props => props.theme.primary};
  }
`;

const ContextHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ContextTitle = styled.div`
  font-weight: 500;
  color: ${props => props.theme.text};
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ContextMeta = styled.div`
  font-size: 12px;
  color: ${props => props.theme.metaText};
`;

const ContextPreview = styled.div`
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

const PriorityControls = styled.div`
  display: flex;
  gap: 4px;
`;

const PriorityButton = styled.button`
  padding: 4px 8px;
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

const HistoryList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  max-height: 200px;
`;

const HistoryItem = styled.div`
  background: ${props => props.theme.cardBackground};
  border-radius: 4px;
  padding: 8px;
  font-size: 12px;
  color: ${props => props.theme.metaText};
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ContextManager = () => {
  const [contexts, setContexts] = useState([
    {
      id: '1',
      type: 'code',
      title: 'API Implementation',
      source: 'src/api/main.py',
      content: 'def handle_request(request):\n    return {"status": "success"}',
      priority: 1,
      lastAccessed: new Date(),
      isActive: true
    },
    {
      id: '2',
      type: 'doc',
      title: 'Architecture Overview',
      source: 'docs/architecture.md',
      content: 'The system follows a microservices architecture...',
      priority: 2,
      lastAccessed: new Date(),
      isActive: true
    },
    {
      id: '3',
      type: 'image',
      title: 'System Diagram',
      source: 'assets/diagram.png',
      content: 'Base64 encoded image data...',
      priority: 3,
      lastAccessed: new Date(),
      isActive: false
    }
  ]);

  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [selectedContext, setSelectedContext] = useState(null);
  const [history, setHistory] = useState([
    {
      id: '1',
      contextId: '1',
      action: 'activated',
      timestamp: new Date()
    },
    {
      id: '2',
      contextId: '2',
      action: 'deactivated',
      timestamp: new Date()
    }
  ]);

  const onDragEnd = (result) => {
    if (!result.destination) return;

    const items = Array.from(contexts);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    // Update priorities
    const updatedItems = items.map((item, index) => ({
      ...item,
      priority: index + 1
    }));

    setContexts(updatedItems);
  };

  const toggleContextActive = (contextId) => {
    setContexts(contexts.map(context => 
      context.id === contextId 
        ? { ...context, isActive: !context.isActive }
        : context
    ));
  };

  const updatePriority = (contextId, direction) => {
    const contextIndex = contexts.findIndex(c => c.id === contextId);
    if (direction === 'up' && contextIndex > 0) {
      const newContexts = [...contexts];
      [newContexts[contextIndex], newContexts[contextIndex - 1]] = 
      [newContexts[contextIndex - 1], newContexts[contextIndex]];
      setContexts(newContexts);
    } else if (direction === 'down' && contextIndex < contexts.length - 1) {
      const newContexts = [...contexts];
      [newContexts[contextIndex], newContexts[contextIndex + 1]] = 
      [newContexts[contextIndex + 1], newContexts[contextIndex]];
      setContexts(newContexts);
    }
  };

  const filteredContexts = contexts.filter(context => {
    const matchesSearch = context.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterType === 'all' || context.type === filterType;
    return matchesSearch && matchesFilter;
  });

  const renderContextPreview = (context) => {
    if (!context) return null;

    switch (context.type) {
      case 'code':
        return (
          <SyntaxHighlighter language="python" style={docco}>
            {context.content}
          </SyntaxHighlighter>
        );
      case 'doc':
        return <div>{context.content}</div>;
      case 'image':
        return <div>Image preview would go here</div>;
      default:
        return <div>{context.content}</div>;
    }
  };

  return (
    <Container>
      <Header>
        <Title>
          <FaBookmark />
          Context Manager
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
          placeholder="Search contexts..."
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
        <Sidebar>
          <DragDropContext onDragEnd={onDragEnd}>
            <Droppable droppableId="contexts">
              {(provided) => (
                <ContextList ref={provided.innerRef} {...provided.droppableProps}>
                  {filteredContexts.map((context, index) => (
                    <Draggable key={context.id} draggableId={context.id} index={index}>
                      {(provided) => (
                        <ContextItem
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          onClick={() => setSelectedContext(context)}
                        >
                          <ContextHeader>
                            <ContextTitle>
                              {context.type === 'code' && <FaCode />}
                              {context.type === 'doc' && <FaFileAlt />}
                              {context.type === 'image' && <FaImage />}
                              {context.type === 'url' && <FaLink />}
                              {context.title}
                            </ContextTitle>
                            <PriorityControls>
                              <PriorityButton onClick={() => updatePriority(context.id, 'up')}>
                                <FaArrowUp />
                              </PriorityButton>
                              <PriorityButton onClick={() => updatePriority(context.id, 'down')}>
                                <FaArrowDown />
                              </PriorityButton>
                              <PriorityButton onClick={() => toggleContextActive(context.id)}>
                                {context.isActive ? <FaStar /> : <FaRegStar />}
                              </PriorityButton>
                            </PriorityControls>
                          </ContextHeader>
                          <ContextMeta>
                            Source: {context.source}
                          </ContextMeta>
                        </ContextItem>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </ContextList>
              )}
            </Droppable>
          </DragDropContext>

          <div>
            <Title>Recent History</Title>
            <HistoryList>
              {history.map(item => (
                <HistoryItem key={item.id}>
                  <div>
                    {item.action === 'activated' ? 'Activated' : 'Deactivated'} context
                  </div>
                  <div>
                    {item.timestamp.toLocaleTimeString()}
                  </div>
                </HistoryItem>
              ))}
            </HistoryList>
          </div>
        </Sidebar>

        <ContextPreview>
          <PreviewHeader>
            <PreviewTitle>
              {selectedContext ? selectedContext.title : 'Select a context to preview'}
            </PreviewTitle>
            {selectedContext && (
              <ControlButton>
                <FaTimes />
              </ControlButton>
            )}
          </PreviewHeader>
          <PreviewContent>
            {renderContextPreview(selectedContext)}
          </PreviewContent>
        </ContextPreview>
      </Content>
    </Container>
  );
};

export default ContextManager; 