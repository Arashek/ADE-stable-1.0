import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaPlus, FaSearch, FaExclamationTriangle, FaServer } from 'react-icons/fa';
import PropTypes from 'prop-types';
import { providerService } from '../../services/providerService';
import AddProviderModal from './AddProviderModal';
import ProviderUsageStats from './ProviderUsageStats';
import ProviderPerformanceChart from './ProviderPerformanceChart';

const PageContainer = styled.div`
  padding: 24px;
  background: #f8fafc;
  min-height: calc(100vh - 64px);
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const Title = styled.h1`
  font-size: 24px;
  color: #1e293b;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const SearchBar = styled.div`
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 8px 12px;
  width: 300px;
`;

const SearchInput = styled.input`
  border: none;
  outline: none;
  background: none;
  width: 100%;
  margin-left: 8px;
  font-size: 14px;
`;

const AddButton = styled.button`
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #2563eb;
  }
`;

const ProvidersGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
`;

const ProviderCard = styled.div`
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
`;

const ProviderHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
`;

const ProviderIcon = styled.div`
  width: 40px;
  height: 40px;
  background: ${props => props.color};
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
`;

const ProviderName = styled.h3`
  font-size: 18px;
  color: #1e293b;
  margin: 0;
`;

const ProviderStatus = styled.span`
  font-size: 14px;
  color: ${props => {
    switch (props.status) {
      case 'active':
        return '#10b981';
      case 'inactive':
        return '#ef4444';
      case 'pending':
        return '#f59e0b';
      default:
        return '#64748b';
    }
  }};
  display: flex;
  align-items: center;
  gap: 4px;
`;

const ProviderDetails = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const DetailRow = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #64748b;
`;

const DetailLabel = styled.span`
  color: #94a3b8;
`;

const ErrorMessage = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fee2e2;
  color: #991b1b;
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 24px;
`;

const StatsSection = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const SectionTitle = styled.h2`
  font-size: 18px;
  color: #1e293b;
  margin: 0 0 16px 0;
`;

const ProvidersPage = () => {
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState(null);

  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await providerService.getProviders();
      setProviders(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredProviders = providers.filter(provider =>
    provider.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    provider.type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getProviderColor = (type) => {
    switch (type) {
      case 'openai':
        return '#10a37f';
      case 'anthropic':
        return '#2d3748';
      case 'google':
        return '#4285f4';
      case 'azure':
        return '#0078d4';
      default:
        return '#64748b';
    }
  };

  return (
    <PageContainer>
      <Header>
        <Title>
          <FaServer />
          AI Providers
        </Title>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <SearchBar>
            <FaSearch color="#64748b" />
            <SearchInput
              type="text"
              placeholder="Search providers..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </SearchBar>
          <AddButton onClick={() => setShowAddModal(true)}>
            <FaPlus />
            Add Provider
          </AddButton>
        </div>
      </Header>

      {error && (
        <ErrorMessage>
          <FaExclamationTriangle />
          {error}
        </ErrorMessage>
      )}

      <StatsSection>
        <SectionTitle>Usage Statistics</SectionTitle>
        <ProviderUsageStats providers={providers} />
      </StatsSection>

      <StatsSection>
        <SectionTitle>Performance Comparison</SectionTitle>
        <ProviderPerformanceChart providers={providers} />
      </StatsSection>

      <ProvidersGrid>
        {filteredProviders.map(provider => (
          <ProviderCard
            key={provider.id}
            onClick={() => setSelectedProvider(provider)}
          >
            <ProviderHeader>
              <ProviderIcon color={getProviderColor(provider.type)}>
                <FaServer />
              </ProviderIcon>
              <div>
                <ProviderName>{provider.name}</ProviderName>
                <ProviderStatus status={provider.status}>
                  {provider.status.charAt(0).toUpperCase() + provider.status.slice(1)}
                </ProviderStatus>
              </div>
            </ProviderHeader>
            <ProviderDetails>
              <DetailRow>
                <DetailLabel>Type:</DetailLabel>
                <span>{provider.type}</span>
              </DetailRow>
              <DetailRow>
                <DetailLabel>Models:</DetailLabel>
                <span>{provider.models.length}</span>
              </DetailRow>
              <DetailRow>
                <DetailLabel>Requests:</DetailLabel>
                <span>{provider.requests.toLocaleString()}</span>
              </DetailRow>
              <DetailRow>
                <DetailLabel>Cost:</DetailLabel>
                <span>${provider.cost.toFixed(2)}</span>
              </DetailRow>
            </ProviderDetails>
          </ProviderCard>
        ))}
      </ProvidersGrid>

      {showAddModal && (
        <AddProviderModal
          onClose={() => setShowAddModal(false)}
          onSuccess={() => {
            setShowAddModal(false);
            fetchProviders();
          }}
        />
      )}

      {selectedProvider && (
        <ProviderDetailPage
          provider={selectedProvider}
          onClose={() => setSelectedProvider(null)}
          onUpdate={fetchProviders}
        />
      )}
    </PageContainer>
  );
};

export default ProvidersPage; 