import React, { useState } from 'react';
import styled from 'styled-components';
import { FaTimes, FaUser, FaCalendar, FaTag, FaEdit, FaCheck } from 'react-icons/fa';
import { colors, spacing, shadows } from '../styles';
import useCommandCenterStore from '../../store/commandCenterStore';

const PanelContainer = styled.div`
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: 400px;
  background: white;
  box-shadow: ${shadows.lg};
  z-index: 1100;
  display: flex;
  flex-direction: column;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${spacing.md};
  border-bottom: 1px solid ${colors.border};
`;

const Title = styled.h2`
  margin: 0;
  font-size: 1.2rem;
  color: ${colors.text};
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: ${colors.text};
  cursor: pointer;
  padding: ${spacing.sm};
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: ${colors.background};
  }
`;

const Content = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: ${spacing.md};
`;

const Section = styled.div`
  margin-bottom: ${spacing.xl};
`;

const SectionTitle = styled.h3`
  margin: 0 0 ${spacing.md};
  font-size: 1rem;
  color: ${colors.text};
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
`;

const InfoItem = styled.div`
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
  padding: ${spacing.md};
  background: ${colors.background};
  border-radius: 4px;
  margin-bottom: ${spacing.sm};
  color: ${colors.text};
`;

const Description = styled.div`
  padding: ${spacing.md};
  background: ${colors.background};
  border-radius: 4px;
  margin-bottom: ${spacing.md};
  color: ${colors.text};
  white-space: pre-wrap;
`;

const StatusBadge = styled.span`
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background: ${props => {
    switch (props.status) {
      case 'completed':
        return colors.success + '20';
      case 'in_progress':
        return colors.primary + '20';
      case 'blocked':
        return colors.error + '20';
      default:
        return colors.textLight + '20';
    }
  }};
  color: ${props => {
    switch (props.status) {
      case 'completed':
        return colors.success;
      case 'in_progress':
        return colors.primary;
      case 'blocked':
        return colors.error;
      default:
        return colors.textLight;
    }
  }};
`;

const EditButton = styled.button`
  background: none;
  border: none;
  color: ${colors.primary};
  cursor: pointer;
  padding: ${spacing.sm};
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
  margin-left: auto;

  &:hover {
    background: ${colors.primary + '10'};
  }
`;

const TaskDetailsPanel = ({ taskId, onClose }) => {
  const { getTaskById, updateTask } = useCommandCenterStore();
  const task = getTaskById(taskId);
  const [isEditing, setIsEditing] = useState(false);
  const [editedTask, setEditedTask] = useState(null);

  if (!task) return null;

  const handleEdit = () => {
    setEditedTask({ ...task });
    setIsEditing(true);
  };

  const handleSave = () => {
    updateTask(taskId, editedTask);
    setIsEditing(false);
  };

  const handleChange = (field, value) => {
    setEditedTask(prev => ({ ...prev, [field]: value }));
  };

  const displayTask = isEditing ? editedTask : task;

  return (
    <PanelContainer>
      <Header>
        <Title>Task Details</Title>
        <CloseButton onClick={onClose}>
          <FaTimes />
        </CloseButton>
      </Header>

      <Content>
        <Section>
          <SectionTitle>Status</SectionTitle>
          <InfoItem>
            <StatusBadge status={displayTask.status}>
              {displayTask.status}
            </StatusBadge>
            <EditButton onClick={isEditing ? handleSave : handleEdit}>
              {isEditing ? <FaCheck /> : <FaEdit />}
            </EditButton>
          </InfoItem>
        </Section>

        <Section>
          <SectionTitle>Description</SectionTitle>
          {isEditing ? (
            <textarea
              value={displayTask.description}
              onChange={(e) => handleChange('description', e.target.value)}
              style={{
                width: '100%',
                minHeight: '100px',
                padding: spacing.md,
                border: `1px solid ${colors.border}`,
                borderRadius: '4px',
                marginBottom: spacing.md
              }}
            />
          ) : (
            <Description>{displayTask.description}</Description>
          )}
        </Section>

        <Section>
          <SectionTitle>Details</SectionTitle>
          <InfoItem>
            <FaUser />
            <span>{displayTask.assignedTo}</span>
          </InfoItem>
          <InfoItem>
            <FaCalendar />
            <span>Due: {new Date(displayTask.dueDate).toLocaleDateString()}</span>
          </InfoItem>
          <InfoItem>
            <FaTag />
            <span>{displayTask.priority}</span>
          </InfoItem>
        </Section>
      </Content>
    </PanelContainer>
  );
};

export default TaskDetailsPanel; 