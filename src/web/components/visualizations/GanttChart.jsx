import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { FaChevronLeft, FaChevronRight, FaPlus, FaExpand } from 'react-icons/fa';

const ChartContainer = styled.div`
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: ${props => props.theme.background};
`;

const TimelineHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid ${props => props.theme.border};
`;

const TimelineControls = styled.div`
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

const TimelineGrid = styled.div`
  display: grid;
  grid-template-columns: 200px 1fr;
  height: calc(100% - 50px);
`;

const TaskList = styled.div`
  border-right: 1px solid ${props => props.theme.border};
  overflow-y: auto;
`;

const TaskItem = styled.div`
  padding: 8px 12px;
  border-bottom: 1px solid ${props => props.theme.border};
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.hoverBackground};
  }
`;

const TaskStatus = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => {
    switch (props.status) {
      case 'completed': return props.theme.success;
      case 'in_progress': return props.theme.warning;
      case 'blocked': return props.theme.error;
      default: return props.theme.metaText;
    }
  }};
`;

const TimelineContent = styled.div`
  position: relative;
  overflow: auto;
  background: ${props => props.theme.background};
`;

const TimelineGridLines = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: grid;
  grid-template-columns: repeat(${props => props.columns}, 1fr);
  pointer-events: none;
`;

const GridLine = styled.div`
  border-right: 1px solid ${props => props.theme.border};
  height: 100%;
`;

const TaskBar = styled.div`
  position: absolute;
  height: 24px;
  background: ${props => props.theme.primary};
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  padding: 0 8px;
  color: white;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;

  &:hover {
    transform: scale(1.02);
    z-index: 1;
  }
`;

const MilestoneMarker = styled.div`
  position: absolute;
  width: 12px;
  height: 12px;
  background: ${props => props.theme.warning};
  border-radius: 50%;
  transform: translate(-50%, -50%);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    transform: translate(-50%, -50%) scale(1.2);
    z-index: 1;
  }
`;

const DependencyArrow = styled.div`
  position: absolute;
  height: 2px;
  background: ${props => props.theme.metaText};
  transform-origin: left center;
  pointer-events: none;
`;

const GanttChart = () => {
  const [tasks, setTasks] = useState([
    {
      id: 1,
      title: 'Project Setup',
      start: new Date('2024-03-01'),
      end: new Date('2024-03-05'),
      progress: 100,
      status: 'completed',
      dependencies: []
    },
    {
      id: 2,
      title: 'Frontend Development',
      start: new Date('2024-03-06'),
      end: new Date('2024-03-20'),
      progress: 65,
      status: 'in_progress',
      dependencies: [1]
    },
    {
      id: 3,
      title: 'Backend Development',
      start: new Date('2024-03-06'),
      end: new Date('2024-03-20'),
      progress: 45,
      status: 'in_progress',
      dependencies: [1]
    },
    {
      id: 4,
      title: 'Integration Testing',
      start: new Date('2024-03-21'),
      end: new Date('2024-03-25'),
      progress: 0,
      status: 'blocked',
      dependencies: [2, 3]
    }
  ]);

  const [milestones, setMilestones] = useState([
    {
      id: 1,
      title: 'Project Kickoff',
      date: new Date('2024-03-01')
    },
    {
      id: 2,
      title: 'Development Complete',
      date: new Date('2024-03-20')
    },
    {
      id: 3,
      title: 'Testing Complete',
      date: new Date('2024-03-25')
    }
  ]);

  const [zoom, setZoom] = useState(1);
  const [offset, setOffset] = useState(0);
  const timelineRef = useRef(null);

  const calculateTaskPosition = (task) => {
    const startDate = new Date('2024-03-01');
    const daysDiff = Math.floor((task.start - startDate) / (1000 * 60 * 60 * 24));
    const duration = Math.ceil((task.end - task.start) / (1000 * 60 * 60 * 24));
    
    return {
      left: `${daysDiff * 100 * zoom}px`,
      width: `${duration * 100 * zoom}px`
    };
  };

  const calculateMilestonePosition = (milestone) => {
    const startDate = new Date('2024-03-01');
    const daysDiff = Math.floor((milestone.date - startDate) / (1000 * 60 * 60 * 24));
    return `${daysDiff * 100 * zoom}px`;
  };

  const renderDependencies = () => {
    return tasks.map(task => {
      if (!task.dependencies.length) return null;

      return task.dependencies.map(depId => {
        const dependency = tasks.find(t => t.id === depId);
        if (!dependency) return null;

        const depPos = calculateTaskPosition(dependency);
        const taskPos = calculateTaskPosition(task);

        return (
          <DependencyArrow
            key={`${task.id}-${depId}`}
            style={{
              left: `${parseFloat(depPos.left) + parseFloat(depPos.width)}px`,
              top: '50%',
              width: `${parseFloat(taskPos.left) - (parseFloat(depPos.left) + parseFloat(depPos.width))}px`
            }}
          />
        );
      });
    });
  };

  return (
    <ChartContainer>
      <TimelineHeader>
        <TimelineControls>
          <ControlButton onClick={() => setZoom(prev => Math.max(0.5, prev - 0.1))}>
            <FaChevronLeft /> Zoom Out
          </ControlButton>
          <ControlButton onClick={() => setZoom(prev => Math.min(2, prev + 0.1))}>
            <FaChevronRight /> Zoom In
          </ControlButton>
          <ControlButton>
            <FaPlus /> Add Task
          </ControlButton>
          <ControlButton>
            <FaExpand /> Fullscreen
          </ControlButton>
        </TimelineControls>
      </TimelineHeader>

      <TimelineGrid>
        <TaskList>
          {tasks.map(task => (
            <TaskItem key={task.id}>
              <TaskStatus status={task.status} />
              {task.title}
            </TaskItem>
          ))}
        </TaskList>

        <TimelineContent ref={timelineRef}>
          <TimelineGridLines columns={31}>
            {Array.from({ length: 31 }).map((_, i) => (
              <GridLine key={i} />
            ))}
          </TimelineGridLines>

          {renderDependencies()}

          {tasks.map(task => {
            const pos = calculateTaskPosition(task);
            return (
              <TaskBar
                key={task.id}
                style={{
                  left: pos.left,
                  width: pos.width,
                  top: `${(task.id - 1) * 32}px`
                }}
              >
                {task.title}
              </TaskBar>
            );
          })}

          {milestones.map(milestone => (
            <MilestoneMarker
              key={milestone.id}
              style={{
                left: calculateMilestonePosition(milestone),
                top: '50%'
              }}
            />
          ))}
        </TimelineContent>
      </TimelineGrid>
    </ChartContainer>
  );
};

export default GanttChart; 