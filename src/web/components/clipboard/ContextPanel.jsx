import React, { useState } from 'react';
import styled from 'styled-components';
import useClipboardManagerStore from '../../utils/clipboard-manager';

const PanelContainer = styled.div`
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

const ContextList = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 8px;
`;

const ContextItem = styled.div`
  display: flex;
  flex-direction: column;
  padding: 12px;
  margin-bottom: 8px;
  background: ${props => props.theme.itemBackground};
  border-radius: 6px;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.itemHoverBackground};
  }
`;

const ContextHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
`;

const ContextContent = styled.div`
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 8px;
  max-height: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
`;

const ContextMeta = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: ${props => props.theme.metaText};
`;

const PrioritySlider = styled.input`
  width: 100px;
  margin: 0 8px;
`;

const ActionButton = styled.button`
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  background: ${props => props.theme.buttonBackground};
  color: ${props => props.theme.buttonText};
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.buttonHoverBackground};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
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

const ContextPanel = () => {
  const {
    getActiveContexts,
    updateContextPriority,
    removeContext,
    deactivateContext,
    clearContexts
  } = useClipboardManagerStore();

  const activeContexts = getActiveContexts();

  const handlePriorityChange = (contextId, value) => {
    updateContextPriority(contextId, parseInt(value));
  };

  const handleRemoveContext = (contextId) => {
    removeContext(contextId);
    deactivateContext(contextId);
  };

  return (
    <PanelContainer>
      <Header>
        <h3>Active Contexts</h3>
        <ActionButton onClick={clearContexts}>Clear All</ActionButton>
      </Header>

      <ContextList>
        {activeContexts.length === 0 ? (
          <EmptyState>
            <p>No active contexts</p>
            <p>Create a context to see it here</p>
          </EmptyState>
        ) : (
          activeContexts.map((context) => (
            <ContextItem key={context.id}>
              <ContextHeader>
                <span>Context #{context.id}</span>
                <ActionButton onClick={() => handleRemoveContext(context.id)}>
                  Remove
                </ActionButton>
              </ContextHeader>
              <ContextContent>{context.content}</ContextContent>
              <ContextMeta>
                <span>Type: {context.type}</span>
                <div>
                  <span>Priority:</span>
                  <PrioritySlider
                    type="range"
                    min="0"
                    max="10"
                    value={context.priority}
                    onChange={(e) => handlePriorityChange(context.id, e.target.value)}
                  />
                  <span>{context.priority}</span>
                </div>
              </ContextMeta>
            </ContextItem>
          ))
        )}
      </ContextList>
    </PanelContainer>
  );
};

export default ContextPanel; 