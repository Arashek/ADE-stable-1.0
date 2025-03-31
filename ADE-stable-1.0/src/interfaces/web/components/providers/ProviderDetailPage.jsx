import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaArrowLeft, FaExclamationTriangle, FaServer, FaKey, FaCog, FaChartLine } from 'react-icons/fa';
import PropTypes from 'prop-types';
import { providerService } from '../../services/providerService';
import ApiKeyManager from './ApiKeyManager';
import ProviderUsageStats from './ProviderUsageStats';
import ProviderPerformanceChart from './ProviderPerformanceChart';

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
  max-width: 1200px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
`;

const ModalHeader = styled.div`
  padding: 24px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 16px;
`;

const BackButton = styled.button`
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;

  &:hover {
    color: #1e293b;
  }
`;

const HeaderTitle = styled.h2`
  font-size: 20px;
  color: #1e293b;
  margin: 0;
`;

const ModalBody = styled.div`
  padding: 24px;
`;

const Section = styled.div`
  margin-bottom: 32px;
`;

const SectionHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
`;

const SectionTitle = styled.h3`
  font-size: 18px;
  color: #1e293b;
  margin: 0;
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
`;

const Card = styled.div`
  background: #f8fafc;
  border-radius: 8px;
  padding: 20px;
`;

const FormGroup = styled.div`
  margin-bottom: 16px;
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

const Button = styled.button`
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #2563eb;
  }

  &:disabled {
    background: #94a3b8;
    cursor: not-allowed;
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

const ProviderDetailPage = ({ provider, onClose, onUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    name: provider.name,
    type: provider.type,
    baseUrl: provider.baseUrl,
    models: provider.models,
    settings: provider.settings,
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      await providerService.updateProvider(provider.id, formData);
      onUpdate();
      onClose();
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
          <BackButton onClick={onClose}>
            <FaArrowLeft />
            Back
          </BackButton>
          <HeaderTitle>{provider.name}</HeaderTitle>
        </ModalHeader>

        <ModalBody>
          {error && (
            <ErrorMessage>
              <FaExclamationTriangle />
              {error}
            </ErrorMessage>
          )}

          <form onSubmit={handleSubmit}>
            <Section>
              <SectionHeader>
                <FaServer />
                <SectionTitle>Provider Details</SectionTitle>
              </SectionHeader>
              <Grid>
                <Card>
                  <FormGroup>
                    <Label>Name</Label>
                    <Input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      required
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
                </Card>
                <Card>
                  <FormGroup>
                    <Label>Base URL</Label>
                    <Input
                      type="url"
                      name="baseUrl"
                      value={formData.baseUrl}
                      onChange={handleInputChange}
                      required
                    />
                  </FormGroup>
                  <FormGroup>
                    <Label>Models</Label>
                    <Input
                      type="text"
                      name="models"
                      value={formData.models.join(', ')}
                      onChange={handleInputChange}
                      placeholder="Comma-separated list of models"
                    />
                  </FormGroup>
                </Card>
              </Grid>
            </Section>

            <Section>
              <SectionHeader>
                <FaKey />
                <SectionTitle>API Keys</SectionTitle>
              </SectionHeader>
              <ApiKeyManager providerId={provider.id} />
            </Section>

            <Section>
              <SectionHeader>
                <FaCog />
                <SectionTitle>Settings</SectionTitle>
              </SectionHeader>
              <Grid>
                <Card>
                  <FormGroup>
                    <Label>Max Tokens</Label>
                    <Input
                      type="number"
                      name="maxTokens"
                      value={formData.settings.maxTokens}
                      onChange={handleInputChange}
                    />
                  </FormGroup>
                  <FormGroup>
                    <Label>Temperature</Label>
                    <Input
                      type="number"
                      name="temperature"
                      value={formData.settings.temperature}
                      onChange={handleInputChange}
                      min="0"
                      max="1"
                      step="0.1"
                    />
                  </FormGroup>
                </Card>
                <Card>
                  <FormGroup>
                    <Label>Timeout (ms)</Label>
                    <Input
                      type="number"
                      name="timeout"
                      value={formData.settings.timeout}
                      onChange={handleInputChange}
                    />
                  </FormGroup>
                  <FormGroup>
                    <Label>Retry Attempts</Label>
                    <Input
                      type="number"
                      name="retryAttempts"
                      value={formData.settings.retryAttempts}
                      onChange={handleInputChange}
                    />
                  </FormGroup>
                </Card>
              </Grid>
            </Section>

            <Section>
              <SectionHeader>
                <FaChartLine />
                <SectionTitle>Usage & Performance</SectionTitle>
              </SectionHeader>
              <ProviderUsageStats providers={[provider]} />
              <ProviderPerformanceChart providers={[provider]} />
            </Section>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
              <Button type="button" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                Save Changes
              </Button>
            </div>
          </form>
        </ModalBody>
      </ModalContent>
    </ModalOverlay>
  );
};

ProviderDetailPage.propTypes = {
  provider: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    type: PropTypes.string.isRequired,
    baseUrl: PropTypes.string.isRequired,
    models: PropTypes.arrayOf(PropTypes.string).isRequired,
    settings: PropTypes.shape({
      maxTokens: PropTypes.number,
      temperature: PropTypes.number,
      timeout: PropTypes.number,
      retryAttempts: PropTypes.number,
    }).isRequired,
  }).isRequired,
  onClose: PropTypes.func.isRequired,
  onUpdate: PropTypes.func.isRequired,
};

export default ProviderDetailPage; 