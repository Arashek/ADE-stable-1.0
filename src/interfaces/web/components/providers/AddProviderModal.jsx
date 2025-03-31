import React, { useState } from 'react';
import styled from 'styled-components';
import { FaTimes, FaExclamationTriangle } from 'react-icons/fa';
import PropTypes from 'prop-types';
import { providerService } from '../../services/providerService';

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  position: relative;
`;

const ModalHeader = styled.div`
  padding: 24px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h2`
  font-size: 20px;
  color: #1e293b;
  margin: 0;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    color: #1e293b;
  }
`;

const ModalBody = styled.div`
  padding: 24px;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  font-size: 14px;
  color: #64748b;
  margin-bottom: 8px;
`;

const Input = styled.input`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;

  &:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  background: white;

  &:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
`;

const Button = styled.button`
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const CancelButton = styled(Button)`
  background: none;
  border: 1px solid #e2e8f0;
  color: #64748b;

  &:hover:not(:disabled) {
    background: #f8fafc;
  }
`;

const SubmitButton = styled(Button)`
  background: #3b82f6;
  border: none;
  color: white;

  &:hover:not(:disabled) {
    background: #2563eb;
  }
`;

const ErrorMessage = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fee2e2;
  color: #991b1b;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
`;

const AddProviderModal = ({ onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    type: 'openai',
    baseUrl: '',
    models: '',
    settings: {
      maxTokens: 2048,
      temperature: 0.7,
      timeout: 30000,
      retryAttempts: 3,
    },
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (name.startsWith('settings.')) {
      const settingName = name.split('.')[1];
      setFormData(prev => ({
        ...prev,
        settings: {
          ...prev.settings,
          [settingName]: value,
        },
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value,
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);

      // Convert models string to array
      const providerData = {
        ...formData,
        models: formData.models.split(',').map(model => model.trim()),
      };

      await providerService.createProvider(providerData);
      onSuccess();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ModalOverlay onClick={onClose}>
      <ModalContent onClick={e => e.stopPropagation()}>
        <ModalHeader>
          <Title>Add New Provider</Title>
          <CloseButton onClick={onClose}>
            <FaTimes />
          </CloseButton>
        </ModalHeader>

        <ModalBody>
          {error && (
            <ErrorMessage>
              <FaExclamationTriangle />
              {error}
            </ErrorMessage>
          )}

          <form onSubmit={handleSubmit}>
            <FormGroup>
              <Label>Name</Label>
              <Input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                placeholder="e.g., OpenAI Production"
              />
            </FormGroup>

            <FormGroup>
              <Label>Type</Label>
              <Select
                name="type"
                value={formData.type}
                onChange={handleInputChange}
                required
              >
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="google">Google</option>
                <option value="azure">Azure</option>
              </Select>
            </FormGroup>

            <FormGroup>
              <Label>Base URL</Label>
              <Input
                type="url"
                name="baseUrl"
                value={formData.baseUrl}
                onChange={handleInputChange}
                required
                placeholder="e.g., https://api.openai.com/v1"
              />
            </FormGroup>

            <FormGroup>
              <Label>Models (comma-separated)</Label>
              <Input
                type="text"
                name="models"
                value={formData.models}
                onChange={handleInputChange}
                required
                placeholder="e.g., gpt-4, gpt-3.5-turbo"
              />
            </FormGroup>

            <FormGroup>
              <Label>Max Tokens</Label>
              <Input
                type="number"
                name="settings.maxTokens"
                value={formData.settings.maxTokens}
                onChange={handleInputChange}
                min="1"
                max="8192"
              />
            </FormGroup>

            <FormGroup>
              <Label>Temperature</Label>
              <Input
                type="number"
                name="settings.temperature"
                value={formData.settings.temperature}
                onChange={handleInputChange}
                min="0"
                max="1"
                step="0.1"
              />
            </FormGroup>

            <FormGroup>
              <Label>Timeout (ms)</Label>
              <Input
                type="number"
                name="settings.timeout"
                value={formData.settings.timeout}
                onChange={handleInputChange}
                min="1000"
                step="1000"
              />
            </FormGroup>

            <FormGroup>
              <Label>Retry Attempts</Label>
              <Input
                type="number"
                name="settings.retryAttempts"
                value={formData.settings.retryAttempts}
                onChange={handleInputChange}
                min="0"
                max="5"
              />
            </FormGroup>

            <ButtonGroup>
              <CancelButton type="button" onClick={onClose} disabled={loading}>
                Cancel
              </CancelButton>
              <SubmitButton type="submit" disabled={loading}>
                Add Provider
              </SubmitButton>
            </ButtonGroup>
          </form>
        </ModalBody>
      </ModalContent>
    </ModalOverlay>
  );
};

AddProviderModal.propTypes = {
  onClose: PropTypes.func.isRequired,
  onSuccess: PropTypes.func.isRequired,
};

export default AddProviderModal; 