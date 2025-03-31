import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaBell, FaExclamationCircle, FaCheckCircle, FaInfoCircle, FaTimes } from 'react-icons/fa';
import axios from 'axios';

const Container = styled.div`
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
`;

const Header = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const Title = styled.h1`
  margin: 0;
  color: #333;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const NotificationList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const NotificationItem = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  align-items: flex-start;
  gap: 15px;
  position: relative;
  border-left: 4px solid ${props => {
    switch (props.type) {
      case 'error': return '#dc3545';
      case 'success': return '#28a745';
      case 'warning': return '#ffc107';
      default: return '#007bff';
    }
  }};
`;

const NotificationIcon = styled.div`
  font-size: 24px;
  color: ${props => {
    switch (props.type) {
      case 'error': return '#dc3545';
      case 'success': return '#28a745';
      case 'warning': return '#ffc107';
      default: return '#007bff';
    }
  }};
`;

const NotificationContent = styled.div`
  flex: 1;
`;

const NotificationTitle = styled.h3`
  margin: 0 0 5px 0;
  color: #333;
  font-size: 16px;
`;

const NotificationMessage = styled.p`
  margin: 0;
  color: #666;
  font-size: 14px;
`;

const NotificationTime = styled.div`
  font-size: 12px;
  color: #999;
  margin-top: 5px;
`;

const DeleteButton = styled.button`
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 5px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    color: #dc3545;
  }
`;

const FilterContainer = styled.div`
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
`;

const FilterButton = styled.button`
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  background: ${props => props.active ? '#007bff' : 'white'};
  color: ${props => props.active ? 'white' : '#666'};
  border: 1px solid ${props => props.active ? '#007bff' : '#ddd'};
  
  &:hover {
    background: ${props => props.active ? '#0056b3' : '#f5f5f5'};
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const EmptyStateIcon = styled.div`
  font-size: 48px;
  color: #999;
  margin-bottom: 20px;
`;

const EmptyStateText = styled.p`
  color: #666;
  font-size: 16px;
  margin: 0;
`;

const ProjectNotifications = ({ projectId }) => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  
  useEffect(() => {
    fetchNotifications();
  }, [projectId]);
  
  const fetchNotifications = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}/notifications`);
      setNotifications(response.data);
    } catch (err) {
      setError('Failed to fetch notifications');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const deleteNotification = async (notificationId) => {
    try {
      await axios.delete(`/api/projects/${projectId}/notifications/${notificationId}`);
      setNotifications(notifications.filter(n => n.id !== notificationId));
    } catch (err) {
      console.error('Failed to delete notification:', err);
    }
  };
  
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'error':
        return <FaExclamationCircle />;
      case 'success':
        return <FaCheckCircle />;
      case 'warning':
        return <FaExclamationCircle />;
      default:
        return <FaInfoCircle />;
    }
  };
  
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };
  
  const filteredNotifications = notifications.filter(notification => {
    if (filter === 'all') return true;
    return notification.type === filter;
  });
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <Container>
      <Header>
        <Title>
          <FaBell />
          Project Notifications
        </Title>
      </Header>
      
      {error && (
        <div style={{ color: 'red', marginBottom: '20px' }}>
          {error}
        </div>
      )}
      
      <FilterContainer>
        <FilterButton
          active={filter === 'all'}
          onClick={() => setFilter('all')}
        >
          All
        </FilterButton>
        <FilterButton
          active={filter === 'info'}
          onClick={() => setFilter('info')}
        >
          Info
        </FilterButton>
        <FilterButton
          active={filter === 'success'}
          onClick={() => setFilter('success')}
        >
          Success
        </FilterButton>
        <FilterButton
          active={filter === 'warning'}
          onClick={() => setFilter('warning')}
        >
          Warning
        </FilterButton>
        <FilterButton
          active={filter === 'error'}
          onClick={() => setFilter('error')}
        >
          Error
        </FilterButton>
      </FilterContainer>
      
      {filteredNotifications.length === 0 ? (
        <EmptyState>
          <EmptyStateIcon>
            <FaBell />
          </EmptyStateIcon>
          <EmptyStateText>
            No notifications to display
          </EmptyStateText>
        </EmptyState>
      ) : (
        <NotificationList>
          {filteredNotifications.map(notification => (
            <NotificationItem key={notification.id} type={notification.type}>
              <NotificationIcon type={notification.type}>
                {getNotificationIcon(notification.type)}
              </NotificationIcon>
              <NotificationContent>
                <NotificationTitle>{notification.title}</NotificationTitle>
                <NotificationMessage>{notification.message}</NotificationMessage>
                <NotificationTime>
                  {formatTime(notification.timestamp)}
                </NotificationTime>
              </NotificationContent>
              <DeleteButton onClick={() => deleteNotification(notification.id)}>
                <FaTimes />
              </DeleteButton>
            </NotificationItem>
          ))}
        </NotificationList>
      )}
    </Container>
  );
};

export default ProjectNotifications; 