import React, { useState } from 'react';
import styled, { keyframes } from 'styled-components';
import { colors, spacing, shadows } from './styles';

// Animations
const pulse = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
`;

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const slideIn = keyframes`
  from { transform: translateX(-20px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
`;

const MockupContainer = styled.div`
  width: 100%;
  height: 100vh;
  background: #1a1b1e;
  padding: ${spacing.md};
  overflow: hidden;
  animation: ${fadeIn} 0.5s ease-out;
`;

const TopBar = styled.div`
  height: 48px;
  background: #2d2e32;
  border-radius: ${spacing.sm};
  margin-bottom: ${spacing.md};
  display: flex;
  align-items: center;
  padding: 0 ${spacing.md};
  box-shadow: ${shadows.md};
  position: relative;
  overflow: hidden;

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, #3b82f6, #22c55e);
    opacity: 0.5;
  }
`;

const MainLayout = styled.div`
  display: grid;
  grid-template-columns: 300px 1fr 300px;
  grid-template-rows: 1fr 200px;
  gap: ${spacing.md};
  height: calc(100vh - 64px);
`;

const SidePanel = styled.div`
  background: #2d2e32;
  border-radius: ${spacing.sm};
  padding: ${spacing.md};
  box-shadow: ${shadows.md};
  transition: transform 0.2s ease;
  animation: ${slideIn} 0.5s ease-out;

  &:hover {
    transform: translateY(-2px);
  }
`;

const MainPanel = styled.div`
  background: #2d2e32;
  border-radius: ${spacing.sm};
  padding: ${spacing.md};
  box-shadow: ${shadows.md};
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(45deg, rgba(59, 130, 246, 0.1), rgba(34, 197, 94, 0.1));
    pointer-events: none;
  }
`;

const TerminalPanel = styled.div`
  grid-column: 1 / -1;
  background: #2d2e32;
  border-radius: ${spacing.sm};
  padding: ${spacing.md};
  box-shadow: ${shadows.md};
  position: relative;
  overflow: hidden;

  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, #3b82f6, #22c55e);
    opacity: 0.5;
  }
`;

const AgentAvatar = styled.g`
  cursor: pointer;
  transition: transform 0.2s ease;

  &:hover {
    transform: scale(1.1);
  }

  .status-indicator {
    transition: all 0.2s ease;
  }

  &:hover .status-indicator {
    transform: scale(1.2);
    filter: brightness(1.2);
  }
`;

const TaskBar = styled.rect`
  transition: all 0.2s ease;
  cursor: pointer;

  &:hover {
    height: 24px;
    y: ${props => props.y - 2};
    filter: brightness(1.2);
  }
`;

const ResourceMeter = styled.rect`
  transition: width 0.3s ease;
`;

const CommandCenterMockup = () => {
  const [activeAgent, setActiveAgent] = useState(null);
  const [hoveredTask, setHoveredTask] = useState(null);

  return (
    <MockupContainer>
      <TopBar>
        <svg width="100%" height="48" viewBox="0 0 1200 48">
          <g>
            {/* Project selector */}
            <rect x="20" y="8" width="200" height="32" fill="#1a1b1e" rx="4" />
            <text x="40" y="30" fill="white" fontSize="14">Project: ADE Platform</text>
            
            {/* Search bar */}
            <rect x="240" y="8" width="400" height="32" fill="#1a1b1e" rx="4" />
            <text x="260" y="30" fill="#64748b" fontSize="14">Search...</text>
            
            {/* Notifications */}
            <circle cx="1100" cy="24" r="12" fill="#1a1b1e" />
            <text x="1095" y="30" textAnchor="middle" fill="#3b82f6" fontSize="12">3</text>
            
            {/* User profile */}
            <circle cx="1150" cy="24" r="12" fill="#1a1b1e" />
            <text x="1145" y="30" textAnchor="middle" fill="white" fontSize="12">U</text>
          </g>
        </svg>
      </TopBar>
      <MainLayout>
        <SidePanel>
          <svg width="100%" height="100%" viewBox="0 0 300 800">
            <g>
              {/* Agent avatars with enhanced interactivity */}
              <AgentAvatar onClick={() => setActiveAgent('pm')}>
                <circle cx="40" cy="40" r="20" fill="#3b82f6" />
                <circle cx="40" cy="40" r="18" fill="#2d2e32" />
                <text x="40" y="45" textAnchor="middle" fill="white" fontSize="12">PM</text>
                <circle className="status-indicator" cx="70" cy="40" r="4" fill="#22c55e" />
                {activeAgent === 'pm' && (
                  <rect x="10" y="60" width="260" height="40" fill="#1a1b1e" rx="4" />
                )}
              </AgentAvatar>
              
              <AgentAvatar onClick={() => setActiveAgent('ar')}>
                <circle cx="40" cy="100" r="20" fill="#3b82f6" />
                <circle cx="40" cy="100" r="18" fill="#2d2e32" />
                <text x="40" y="105" textAnchor="middle" fill="white" fontSize="12">AR</text>
                <circle className="status-indicator" cx="70" cy="100" r="4" fill="#f59e0b" />
                {activeAgent === 'ar' && (
                  <rect x="10" y="120" width="260" height="40" fill="#1a1b1e" rx="4" />
                )}
              </AgentAvatar>
              
              {/* Add similar AgentAvatar components for DEV, QA, and OPS */}
            </g>
          </svg>
        </SidePanel>
        
        <MainPanel>
          <svg width="100%" height="100%" viewBox="0 0 800 800">
            <g>
              {/* Enhanced timeline grid */}
              <rect x="0" y="0" width="800" height="800" fill="#1a1b1e" />
              {[...Array(10)].map((_, i) => (
                <line
                  key={i}
                  x1={i * 80}
                  y1="0"
                  x2={i * 80}
                  y2="800"
                  stroke="#3b82f6"
                  strokeWidth="1"
                  opacity="0.2"
                />
              ))}
              
              {/* Interactive task bars */}
              <TaskBar
                x="50"
                y="50"
                width="100"
                height="20"
                fill="#3b82f6"
                rx="4"
                onMouseEnter={() => setHoveredTask('task1')}
                onMouseLeave={() => setHoveredTask(null)}
              />
              <TaskBar
                x="200"
                y="50"
                width="150"
                height="20"
                fill="#f59e0b"
                rx="4"
                onMouseEnter={() => setHoveredTask('task2')}
                onMouseLeave={() => setHoveredTask(null)}
              />
              <TaskBar
                x="400"
                y="50"
                width="120"
                height="20"
                fill="#22c55e"
                rx="4"
                onMouseEnter={() => setHoveredTask('task3')}
                onMouseLeave={() => setHoveredTask(null)}
              />
              
              {/* Enhanced dependencies with animations */}
              <line
                x1="150"
                y1="60"
                x2="200"
                y2="60"
                stroke="#3b82f6"
                strokeWidth="2"
                strokeDasharray="4 4"
                style={{ animation: `${pulse} 2s infinite` }}
              />
              
              {/* Task labels */}
              {hoveredTask && (
                <g>
                  <rect
                    x={hoveredTask === 'task1' ? 50 : hoveredTask === 'task2' ? 200 : 400}
                    y="30"
                    width="100"
                    height="20"
                    fill="#1a1b1e"
                    rx="4"
                  />
                  <text
                    x={hoveredTask === 'task1' ? 100 : hoveredTask === 'task2' ? 275 : 460}
                    y="45"
                    textAnchor="middle"
                    fill="white"
                    fontSize="12"
                  >
                    {hoveredTask === 'task1' ? 'Setup Project' : 
                     hoveredTask === 'task2' ? 'Design Architecture' : 'Implement Core'}
                  </text>
                </g>
              )}
            </g>
          </svg>
        </MainPanel>
        
        <SidePanel>
          <svg width="100%" height="100%" viewBox="0 0 300 800">
            <g>
              {/* Animated resource meters */}
              <ResourceMeter
                x="20"
                y="20"
                width="180"
                height="10"
                fill="#3b82f6"
                rx="5"
                style={{ animation: `${pulse} 2s infinite` }}
              />
              <ResourceMeter
                x="20"
                y="40"
                width="200"
                height="10"
                fill="#22c55e"
                rx="5"
                style={{ animation: `${pulse} 2s infinite` }}
              />
              
              {/* Enhanced context items */}
              <g>
                <rect x="20" y="80" width="260" height="60" fill="#1a1b1e" rx="4" />
                <text x="40" y="110" fill="white" fontSize="12">Current File: src/components/CommandCenter.jsx</text>
                <circle cx="250" cy="110" r="4" fill="#3b82f6" />
              </g>
              
              {/* Additional context items */}
              <g style={{ animation: `${fadeIn} 0.5s ease-out` }}>
                <rect x="20" y="160" width="260" height="60" fill="#1a1b1e" rx="4" />
                <text x="40" y="190" fill="white" fontSize="12">GitHub Issue #123</text>
                <circle cx="250" cy="190" r="4" fill="#f59e0b" />
              </g>
            </g>
          </svg>
        </SidePanel>
        
        <TerminalPanel>
          <svg width="100%" height="100%" viewBox="0 0 1200 200">
            <g>
              {/* Enhanced terminal output */}
              <rect x="0" y="0" width="1200" height="150" fill="#1a1b1e" rx="4" />
              <text x="20" y="30" fill="#3b82f6" fontSize="12">$ npm start</text>
              <text x="20" y="50" fill="#22c55e" fontSize="12">Starting the development server...</text>
              
              {/* Interactive input area */}
              <rect x="0" y="160" width="1200" height="40" fill="#2d2e32" rx="4" />
              <rect
                x="20"
                y="170"
                width="1000"
                height="20"
                fill="#1a1b1e"
                rx="4"
                style={{ transition: 'all 0.2s ease' }}
              />
              <circle
                cx="1150"
                cy="180"
                r="10"
                fill="#3b82f6"
                style={{ cursor: 'pointer', transition: 'all 0.2s ease' }}
              />
              
              {/* Voice input indicator */}
              <circle cx="1100" cy="180" r="8" fill="#f59e0b" />
              <path
                d="M1095 180 L1105 180 M1100 175 L1100 185"
                stroke="#1a1b1e"
                strokeWidth="2"
              />
            </g>
          </svg>
        </TerminalPanel>
      </MainLayout>
    </MockupContainer>
  );
};

export default CommandCenterMockup; 