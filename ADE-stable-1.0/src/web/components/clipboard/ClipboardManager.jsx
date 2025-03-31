import React, { useState } from 'react';
import styled from 'styled-components';
import ClipboardHistory from './ClipboardHistory';
import ContextPanel from './ContextPanel';
import ContextCreator from './ContextCreator';
import ClipboardStats from './ClipboardStats';

const ManagerContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 16px;
  padding: 16px;
  background: ${props => props.theme.background};
`;

const MainContent = styled.div`
  display: flex;
  gap: 16px;
  flex: 1;
  min-height: 0;
`;

const LeftPanel = styled.div`
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
`;

const RightPanel = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
`;

const TabContainer = styled.div`
  display: flex;
  border-bottom: 1px solid ${props => props.theme.border};
`;

const Tab = styled.button`
  padding: 12px 24px;
  border: none;
  background: none;
  color: ${props => props.theme.text};
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  position: relative;
  transition: all 0.2s ease;

  &:hover {
    color: ${props => props.theme.primary};
  }

  ${props => props.active && `
    color: ${props.theme.primary};
    
    &:after {
      content: '';
      position: absolute;
      bottom: -1px;
      left: 0;
      right: 0;
      height: 2px;
      background: ${props.theme.primary};
    }
  `}
`;

const PanelContent = styled.div`
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const ScrollableContent = styled.div`
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;

  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: ${props => props.theme.scrollbarTrack};
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb {
    background: ${props => props.theme.scrollbarThumb};
    border-radius: 4px;

    &:hover {
      background: ${props => props.theme.scrollbarThumbHover};
    }
  }
`;

const ClipboardManager = () => {
  const [activeTab, setActiveTab] = useState('history');

  return (
    <ManagerContainer>
      <ClipboardStats />
      <MainContent>
        <LeftPanel>
          <TabContainer>
            <Tab
              active={activeTab === 'history'}
              onClick={() => setActiveTab('history')}
            >
              Clipboard History
            </Tab>
            <Tab
              active={activeTab === 'contexts'}
              onClick={() => setActiveTab('contexts')}
            >
              Active Contexts
            </Tab>
          </TabContainer>
          <PanelContent>
            <ScrollableContent>
              {activeTab === 'history' ? <ClipboardHistory /> : <ContextPanel />}
            </ScrollableContent>
          </PanelContent>
        </LeftPanel>
        <RightPanel>
          <ContextCreator />
        </RightPanel>
      </MainContent>
    </ManagerContainer>
  );
};

export default ClipboardManager; 