import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaLink, FaPlus, FaTrash, FaEdit, FaSave, FaTimes, FaCheckCircle, FaTimesCircle } from 'react-icons/fa';
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

const WebhooksGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
`;

const WebhookCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const WebhookHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
`;

const WebhookInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const WebhookName = styled.h3`
  margin: 0;
  color: #333;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const WebhookMeta = styled.div`
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #999;
`;

const MetaItem = styled.div`
  display: flex;
  align-items: center;
  gap: 5px;
`;

const WebhookStatus = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  background: ${props => props.active ? '#d4edda' : '#f8d7da'};
  color: ${props => props.active ? '#155724' : '#721c24'};
`;

const WebhookActions = styled.div`
  display: flex;
  gap: 10px;
`;

const Button = styled.button`
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  background: ${props => props.variant === 'danger' ? '#dc3545' : '#007bff'};
  color: white;
  border: none;
  
  &:hover {
    background: ${props => props.variant === 'danger' ? '#c82333' : '#0056b3'};
  }
  
  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`;

const WebhookDetails = styled.div`
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
`;

const DetailRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
`;

const DetailLabel = styled.span`
  color: #666;
`;

const DetailValue = styled.span`
  color: #333;
  font-weight: 500;
`;

const WebhookEvents = styled.div`
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
`;

const EventsTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
`;

const EventsList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const EventTag = styled.span`
  padding: 4px 8px;
  background: #e9ecef;
  border-radius: 4px;
  font-size: 12px;
  color: #495057;
`;

const WebhookHistory = styled.div`
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
`;

const HistoryTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
`;

const HistoryList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const HistoryItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 12px;
`;

const HistoryInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const HistoryMeta = styled.div`
  display: flex;
  gap: 10px;
  color: #999;
`;

const Alert = styled.div`
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  background: ${props => props.type === 'success' ? '#d4edda' : '#f8d7da'};
  color: ${props => props.type === 'success' ? '#155724' : '#721c24'};
  border: 1px solid ${props => props.type === 'success' ? '#c3e6cb' : '#f5c6cb'};
`;

const Modal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const ModalTitle = styled.h2`
  margin: 0;
  color: #333;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
  
  &:hover {
    color: #333;
  }
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const Label = styled.label`
  color: #666;
  font-size: 14px;
`;

const Input = styled.input`
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const Select = styled.select`
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const CheckboxGroup = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: #666;
`;

const ProjectWebhooks = ({ projectId }) => {
  const [webhooks, setWebhooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingWebhook, setEditingWebhook] = useState(null);
  const [newWebhook, setNewWebhook] = useState({
    name: '',
    url: '',
    secret: '',
    events: [],
    active: true
  });
  
  const availableEvents = [
    'push',
    'pull_request',
    'issue',
    'release',
    'deployment',
    'build',
    'test',
    'comment'
  ];
  
  useEffect(() => {
    fetchWebhooks();
  }, [projectId]);
  
  const fetchWebhooks = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}/webhooks`);
      setWebhooks(response.data);
    } catch (err) {
      setError('Failed to fetch webhooks');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleAddWebhook = async (e) => {
    e.preventDefault();
    
    try {
      await axios.post(`/api/projects/${projectId}/webhooks`, newWebhook);
      setSuccess(true);
      setShowAddModal(false);
      setNewWebhook({
        name: '',
        url: '',
        secret: '',
        events: [],
        active: true
      });
      fetchWebhooks();
    } catch (err) {
      setError('Failed to add webhook');
      console.error(err);
    }
  };
  
  const handleUpdateWebhook = async (e) => {
    e.preventDefault();
    
    try {
      await axios.put(`/api/projects/${projectId}/webhooks/${editingWebhook.id}`, editingWebhook);
      setSuccess(true);
      setEditingWebhook(null);
      fetchWebhooks();
    } catch (err) {
      setError('Failed to update webhook');
      console.error(err);
    }
  };
  
  const handleDeleteWebhook = async (webhookId) => {
    if (!window.confirm('Are you sure you want to delete this webhook?')) {
      return;
    }
    
    try {
      await axios.delete(`/api/projects/${projectId}/webhooks/${webhookId}`);
      setSuccess(true);
      fetchWebhooks();
    } catch (err) {
      setError('Failed to delete webhook');
      console.error(err);
    }
  };
  
  const toggleEvent = (event, webhook) => {
    const events = webhook.events.includes(event)
      ? webhook.events.filter(e => e !== event)
      : [...webhook.events, event];
    
    if (webhook === newWebhook) {
      setNewWebhook(prev => ({ ...prev, events }));
    } else {
      setEditingWebhook(prev => ({ ...prev, events }));
    }
  };
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <Container>
      <Header>
        <Title>
          <FaLink />
          Project Webhooks
        </Title>
      </Header>
      
      {error && (
        <Alert type="error">
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert type="success">
          Operation completed successfully
        </Alert>
      )}
      
      <Button onClick={() => setShowAddModal(true)} style={{ marginBottom: '20px' }}>
        <FaPlus />
        Add Webhook
      </Button>
      
      <WebhooksGrid>
        {webhooks.map(webhook => (
          <WebhookCard key={webhook.id}>
            <WebhookHeader>
              <WebhookInfo>
                <WebhookName>
                  {webhook.name}
                  <WebhookStatus active={webhook.active}>
                    {webhook.active ? <FaCheckCircle /> : <FaTimesCircle />}
                    {webhook.active ? 'Active' : 'Inactive'}
                  </WebhookStatus>
                </WebhookName>
                <WebhookMeta>
                  <MetaItem>
                    URL: {webhook.url}
                  </MetaItem>
                  <MetaItem>
                    Last Triggered: {webhook.lastTriggeredAt ? new Date(webhook.lastTriggeredAt).toLocaleString() : 'Never'}
                  </MetaItem>
                </WebhookMeta>
              </WebhookInfo>
              <WebhookActions>
                <Button onClick={() => setEditingWebhook(webhook)}>
                  <FaEdit />
                  Edit
                </Button>
                <Button
                  variant="danger"
                  onClick={() => handleDeleteWebhook(webhook.id)}
                >
                  <FaTrash />
                  Delete
                </Button>
              </WebhookActions>
            </WebhookHeader>
            
            <WebhookDetails>
              <DetailRow>
                <DetailLabel>Secret</DetailLabel>
                <DetailValue>
                  {webhook.secret ? '••••••••' : 'None'}
                </DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>Created</DetailLabel>
                <DetailValue>
                  {new Date(webhook.createdAt).toLocaleString()}
                </DetailValue>
              </DetailRow>
            </WebhookDetails>
            
            <WebhookEvents>
              <EventsTitle>Events</EventsTitle>
              <EventsList>
                {availableEvents.map(event => (
                  <EventTag
                    key={event}
                    style={{
                      background: webhook.events.includes(event) ? '#cce5ff' : '#e9ecef',
                      color: webhook.events.includes(event) ? '#004085' : '#495057'
                    }}
                  >
                    {event}
                  </EventTag>
                ))}
              </EventsList>
            </WebhookEvents>
            
            <WebhookHistory>
              <HistoryTitle>Recent Deliveries</HistoryTitle>
              <HistoryList>
                {webhook.deliveries?.map(delivery => (
                  <HistoryItem key={delivery.id}>
                    <HistoryInfo>
                      <div>Delivery #{delivery.number}</div>
                      <HistoryMeta>
                        <span>{new Date(delivery.startedAt).toLocaleString()}</span>
                        <span>{delivery.status}</span>
                      </HistoryMeta>
                    </HistoryInfo>
                  </HistoryItem>
                ))}
              </HistoryList>
            </WebhookHistory>
          </WebhookCard>
        ))}
      </WebhooksGrid>
      
      {showAddModal && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Add New Webhook</ModalTitle>
              <CloseButton onClick={() => setShowAddModal(false)}>
                ×
              </CloseButton>
            </ModalHeader>
            
            <Form onSubmit={handleAddWebhook}>
              <FormGroup>
                <Label>Webhook Name</Label>
                <Input
                  type="text"
                  value={newWebhook.name}
                  onChange={(e) => setNewWebhook(prev => ({
                    ...prev,
                    name: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Webhook URL</Label>
                <Input
                  type="url"
                  value={newWebhook.url}
                  onChange={(e) => setNewWebhook(prev => ({
                    ...prev,
                    url: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Secret (Optional)</Label>
                <Input
                  type="password"
                  value={newWebhook.secret}
                  onChange={(e) => setNewWebhook(prev => ({
                    ...prev,
                    secret: e.target.value
                  }))}
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Events</Label>
                <CheckboxGroup>
                  {availableEvents.map(event => (
                    <CheckboxLabel key={event}>
                      <input
                        type="checkbox"
                        checked={newWebhook.events.includes(event)}
                        onChange={() => toggleEvent(event, newWebhook)}
                      />
                      {event}
                    </CheckboxLabel>
                  ))}
                </CheckboxGroup>
              </FormGroup>
              
              <FormGroup>
                <Label>
                  <input
                    type="checkbox"
                    checked={newWebhook.active}
                    onChange={(e) => setNewWebhook(prev => ({
                      ...prev,
                      active: e.target.checked
                    }))}
                  />
                  Active
                </Label>
              </FormGroup>
              
              <Button type="submit">
                <FaPlus />
                Add Webhook
              </Button>
            </Form>
          </ModalContent>
        </Modal>
      )}
      
      {editingWebhook && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Edit Webhook</ModalTitle>
              <CloseButton onClick={() => setEditingWebhook(null)}>
                ×
              </CloseButton>
            </ModalHeader>
            
            <Form onSubmit={handleUpdateWebhook}>
              <FormGroup>
                <Label>Webhook Name</Label>
                <Input
                  type="text"
                  value={editingWebhook.name}
                  onChange={(e) => setEditingWebhook(prev => ({
                    ...prev,
                    name: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Webhook URL</Label>
                <Input
                  type="url"
                  value={editingWebhook.url}
                  onChange={(e) => setEditingWebhook(prev => ({
                    ...prev,
                    url: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Secret (Optional)</Label>
                <Input
                  type="password"
                  value={editingWebhook.secret}
                  onChange={(e) => setEditingWebhook(prev => ({
                    ...prev,
                    secret: e.target.value
                  }))}
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Events</Label>
                <CheckboxGroup>
                  {availableEvents.map(event => (
                    <CheckboxLabel key={event}>
                      <input
                        type="checkbox"
                        checked={editingWebhook.events.includes(event)}
                        onChange={() => toggleEvent(event, editingWebhook)}
                      />
                      {event}
                    </CheckboxLabel>
                  ))}
                </CheckboxGroup>
              </FormGroup>
              
              <FormGroup>
                <Label>
                  <input
                    type="checkbox"
                    checked={editingWebhook.active}
                    onChange={(e) => setEditingWebhook(prev => ({
                      ...prev,
                      active: e.target.checked
                    }))}
                  />
                  Active
                </Label>
              </FormGroup>
              
              <Button type="submit">
                <FaSave />
                Save Changes
              </Button>
            </Form>
          </ModalContent>
        </Modal>
      )}
    </Container>
  );
};

export default ProjectWebhooks; 