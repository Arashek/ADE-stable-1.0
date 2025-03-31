import React, { useState } from 'react';
import styled from 'styled-components';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { 
  FaUserRobot, FaUsers, FaPlus, FaSave, FaFolderOpen, 
  FaSlidersH, FaUserShield, FaUserCog, FaUserGraduate 
} from 'react-icons/fa';

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

const Content = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  flex: 1;
  overflow: hidden;
`;

const Panel = styled.div`
  background: ${props => props.theme.background};
  border-radius: 6px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const PanelTitle = styled.h4`
  color: ${props => props.theme.text};
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const RoleList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  flex: 1;
`;

const RoleCard = styled.div`
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

const RoleHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const RoleTitle = styled.div`
  font-weight: 500;
  color: ${props => props.theme.text};
  display: flex;
  align-items: center;
  gap: 8px;
`;

const RoleDescription = styled.div`
  color: ${props => props.theme.metaText};
  font-size: 14px;
  line-height: 1.5;
`;

const CapabilityList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const CapabilityTag = styled.div`
  background: ${props => props.theme.tagBackground};
  color: ${props => props.theme.tagText};
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
`;

const TeamComposition = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const TeamMember = styled.div`
  background: ${props => props.theme.cardBackground};
  border-radius: 6px;
  padding: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid ${props => props.theme.border};
`;

const MemberInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const MemberAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: ${props => props.theme.primary};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500;
`;

const MemberDetails = styled.div`
  display: flex;
  flex-direction: column;
`;

const MemberName = styled.div`
  font-weight: 500;
  color: ${props => props.theme.text};
`;

const MemberRole = styled.div`
  font-size: 12px;
  color: ${props => props.theme.metaText};
`;

const AutonomySlider = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const Slider = styled.input`
  flex: 1;
  height: 4px;
  -webkit-appearance: none;
  background: ${props => props.theme.border};
  border-radius: 2px;
  outline: none;

  &::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 16px;
    height: 16px;
    background: ${props => props.theme.primary};
    border-radius: 50%;
    cursor: pointer;
  }
`;

const AgentDirectory = () => {
  const [roles] = useState([
    {
      id: 'architect',
      title: 'Architect',
      icon: <FaUserShield />,
      description: 'System architecture design and technical decision making',
      capabilities: ['Architecture Design', 'Technical Leadership', 'System Integration'],
      autonomy: 80
    },
    {
      id: 'developer',
      title: 'Developer',
      icon: <FaUserCog />,
      description: 'Implementation and development of system components',
      capabilities: ['Coding', 'Testing', 'Documentation'],
      autonomy: 60
    },
    {
      id: 'researcher',
      title: 'Researcher',
      icon: <FaUserGraduate />,
      description: 'Technology research and innovation',
      capabilities: ['Research', 'Innovation', 'Prototyping'],
      autonomy: 90
    }
  ]);

  const [team, setTeam] = useState([]);

  const onDragEnd = (result) => {
    if (!result.destination) return;

    const { source, destination } = result;

    if (source.droppableId === 'roles' && destination.droppableId === 'team') {
      const role = roles.find(r => r.id === result.draggableId);
      setTeam([...team, { ...role, id: `${role.id}-${Date.now()}` }]);
    } else if (source.droppableId === 'team' && destination.droppableId === 'team') {
      const newTeam = Array.from(team);
      const [removed] = newTeam.splice(source.index, 1);
      newTeam.splice(destination.index, 0, removed);
      setTeam(newTeam);
    }
  };

  return (
    <Container>
      <Header>
        <Title>
          <FaUserRobot />
          Agent Directory
        </Title>
        <Controls>
          <ControlButton>
            <FaPlus /> New Role
          </ControlButton>
          <ControlButton>
            <FaSave /> Save Team
          </ControlButton>
          <ControlButton>
            <FaFolderOpen /> Load Team
          </ControlButton>
        </Controls>
      </Header>

      <DragDropContext onDragEnd={onDragEnd}>
        <Content>
          <Panel>
            <PanelTitle>
              <FaUsers />
              Available Roles
            </PanelTitle>
            <Droppable droppableId="roles">
              {(provided) => (
                <RoleList ref={provided.innerRef} {...provided.droppableProps}>
                  {roles.map((role, index) => (
                    <Draggable key={role.id} draggableId={role.id} index={index}>
                      {(provided) => (
                        <RoleCard
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                        >
                          <RoleHeader>
                            <RoleTitle>
                              {role.icon}
                              {role.title}
                            </RoleTitle>
                            <AutonomySlider>
                              <Slider
                                type="range"
                                min="0"
                                max="100"
                                value={role.autonomy}
                                readOnly
                              />
                              <span>{role.autonomy}%</span>
                            </AutonomySlider>
                          </RoleHeader>
                          <RoleDescription>
                            {role.description}
                          </RoleDescription>
                          <CapabilityList>
                            {role.capabilities.map(capability => (
                              <CapabilityTag key={capability}>
                                {capability}
                              </CapabilityTag>
                            ))}
                          </CapabilityList>
                        </RoleCard>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </RoleList>
              )}
            </Droppable>
          </Panel>

          <Panel>
            <PanelTitle>
              <FaUsers />
              Team Composition
            </PanelTitle>
            <Droppable droppableId="team">
              {(provided) => (
                <TeamComposition ref={provided.innerRef} {...provided.droppableProps}>
                  {team.map((member, index) => (
                    <Draggable key={member.id} draggableId={member.id} index={index}>
                      {(provided) => (
                        <TeamMember
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                        >
                          <MemberInfo>
                            <MemberAvatar>
                              {member.title[0]}
                            </MemberAvatar>
                            <MemberDetails>
                              <MemberName>{member.title}</MemberName>
                              <MemberRole>{member.description}</MemberRole>
                            </MemberDetails>
                          </MemberInfo>
                          <AutonomySlider>
                            <Slider
                              type="range"
                              min="0"
                              max="100"
                              value={member.autonomy}
                              onChange={(e) => {
                                const newTeam = [...team];
                                newTeam[index] = {
                                  ...newTeam[index],
                                  autonomy: parseInt(e.target.value)
                                };
                                setTeam(newTeam);
                              }}
                            />
                            <span>{member.autonomy}%</span>
                          </AutonomySlider>
                        </TeamMember>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </TeamComposition>
              )}
            </Droppable>
          </Panel>
        </Content>
      </DragDropContext>
    </Container>
  );
};

export default AgentDirectory; 