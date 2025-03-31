import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { subscribeToEvents } from '../../services/websocket';
import { colors, spacing, shadows } from '../styles';

const ProgressContainer = styled.div`
  background: white;
  border-radius: 8px;
  box-shadow: ${shadows.md};
  padding: ${spacing.md};
  height: 100%;
  display: flex;
  flex-direction: column;
`;

const TimelineContainer = styled.div`
  position: relative;
  height: 100px;
  background: ${colors.background};
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: ${spacing.md};
`;

const TimelineGrid = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  border-right: 1px solid ${colors.border};
  
  > div {
    border-right: 1px solid ${colors.border};
  }
`;

const TaskBar = styled.div`
  position: absolute;
  height: 20px;
  background: ${props => props.color};
  border-radius: 4px;
  transition: all 0.3s ease;
  cursor: pointer;
  
  &:hover {
    transform: scaleY(1.2);
    z-index: 1;
  }
`;

const TaskList = styled.div`
  flex: 1;
  overflow-y: auto;
`;

const TaskItem = styled.div`
  display: flex;
  align-items: center;
  padding: ${spacing.sm};
  border-radius: 4px;
  margin-bottom: ${spacing.sm};
  background: ${colors.background};
  transition: all 0.2s ease;
  
  &:hover {
    background: ${colors.primary + '10'};
  }
`;

const ProgressBar = styled.div`
  width: 100px;
  height: 4px;
  background: ${colors.border};
  border-radius: 2px;
  overflow: hidden;
  margin-left: auto;
`;

const Progress = styled.div`
  height: 100%;
  background: ${props => props.color};
  width: ${props => props.progress}%;
  transition: width 0.3s ease;
`;

const ProgressVisualization = () => {
  const [tasks, setTasks] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);

  useEffect(() => {
    // Subscribe to task updates
    const unsubscribe = subscribeToEvents((event) => {
      if (event.type === 'task_update') {
        setTasks(prevTasks => {
          const updatedTasks = prevTasks.map(task => 
            task.id === event.data.id ? { ...task, ...event.data } : task
          );
          return updatedTasks;
        });
      }
    });

    return () => unsubscribe();
  }, []);

  const getTaskColor = (status) => {
    switch (status) {
      case 'completed': return colors.success;
      case 'in_progress': return colors.primary;
      case 'blocked': return colors.error;
      default: return colors.textLight;
    }
  };

  const calculateTaskPosition = (task) => {
    const start = (task.startDate - Date.now()) / (24 * 60 * 60 * 1000);
    const duration = task.duration / (24 * 60 * 60 * 1000);
    return {
      left: `${(start / 10) * 100}%`,
      width: `${(duration / 10) * 100}%`,
    };
  };

  return (
    <ProgressContainer>
      <TimelineContainer>
        <TimelineGrid>
          {[...Array(10)].map((_, i) => (
            <div key={i} />
          ))}
        </TimelineGrid>
        {tasks.map(task => (
          <TaskBar
            key={task.id}
            color={getTaskColor(task.status)}
            style={calculateTaskPosition(task)}
            onClick={() => setSelectedTask(task)}
          />
        ))}
      </TimelineContainer>

      <TaskList>
        {tasks.map(task => (
          <TaskItem key={task.id}>
            <div>
              <div>{task.title}</div>
              <div style={{ fontSize: '12px', color: colors.textLight }}>
                {task.assignedTo}
              </div>
            </div>
            <ProgressBar>
              <Progress
                color={getTaskColor(task.status)}
                progress={task.progress}
              />
            </ProgressBar>
          </TaskItem>
        ))}
      </TaskList>
    </ProgressContainer>
  );
};

export default ProgressVisualization; 