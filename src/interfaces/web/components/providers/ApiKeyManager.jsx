import React, { useState } from 'react';
import styled from 'styled-components';
import { FaKey, FaEye, FaEyeSlash, FaCopy, FaCheck, FaExclamationTriangle } from 'react-icons/fa';
import PropTypes from 'prop-types';

const Container = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const Title = styled.h3`
  font-size: 18px;
  color: #1e293b;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const KeyList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const KeyItem = styled.div`
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const KeyInfo = styled.div`
  flex: 1;
`;

const KeyName = styled.div`
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 4px;
`;

const KeyValue = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: monospace;
  font-size: 14px;
  color: #64748b;
`;

const KeyActions = styled.div`
  display: flex;
  gap: 8px;
`;

const Button = styled.button`
  padding: 6px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  transition: all 0.2s;

  &:hover {
    background: #f8fafc;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const AddButton = styled(Button)`
  background: #3b82f6;
  border: none;
  color: white;

  &:hover {
    background: #2563eb;
  }
`;

const SuccessMessage = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  background: #dcfce7;
  color: #166534;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
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

const WarningMessage = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fef3c7;
  color: #92400e;
  padding: 12px 16px;
  border-radius: 6px;
  margin-top: 16px;
`;

const ApiKeyManager = ({ providerId, apiKeys, onAddKey, onDeleteKey, onRotateKey }) => {
  const [showKeys, setShowKeys] = useState({});
  const [copiedKey, setCopiedKey] = useState(null);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);

  const toggleKeyVisibility = (keyId) => {
    setShowKeys(prev => ({
      ...prev,
      [keyId]: !prev[keyId],
    }));
  };

  const copyToClipboard = async (key) => {
    try {
      await navigator.clipboard.writeText(key);
      setSuccess('API key copied to clipboard');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Failed to copy API key');
      setTimeout(() => setError(null), 3000);
    }
  };

  const handleAddKey = async () => {
    try {
      await onAddKey(providerId);
      setSuccess('New API key generated');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Failed to generate new API key');
      setTimeout(() => setError(null), 3000);
    }
  };

  const handleDeleteKey = async (keyId) => {
    try {
      await onDeleteKey(providerId, keyId);
      setSuccess('API key deleted');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Failed to delete API key');
      setTimeout(() => setError(null), 3000);
    }
  };

  const handleRotateKey = async (keyId) => {
    try {
      await onRotateKey(providerId, keyId);
      setSuccess('API key rotated');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Failed to rotate API key');
      setTimeout(() => setError(null), 3000);
    }
  };

  return (
    <Container>
      <Header>
        <Title>
          <FaKey />
          API Keys
        </Title>
        <AddButton onClick={handleAddKey}>
          Add Key
        </AddButton>
      </Header>

      {success && (
        <SuccessMessage>
          <FaCheck />
          {success}
        </SuccessMessage>
      )}

      {error && (
        <ErrorMessage>
          <FaExclamationTriangle />
          {error}
        </ErrorMessage>
      )}

      <KeyList>
        {apiKeys.map((key) => (
          <KeyItem key={key.id}>
            <KeyInfo>
              <KeyName>{key.name}</KeyName>
              <KeyValue>
                {showKeys[key.id] ? key.value : '••••••••••••••••'}
                <Button
                  onClick={() => toggleKeyVisibility(key.id)}
                  title={showKeys[key.id] ? 'Hide' : 'Show'}
                >
                  {showKeys[key.id] ? <FaEyeSlash /> : <FaEye />}
                </Button>
                <Button
                  onClick={() => copyToClipboard(key.value)}
                  title="Copy"
                >
                  {copiedKey === key.id ? <FaCheck /> : <FaCopy />}
                </Button>
              </KeyValue>
            </KeyInfo>
            <KeyActions>
              <Button
                onClick={() => handleRotateKey(key.id)}
                title="Rotate"
              >
                Rotate
              </Button>
              <Button
                onClick={() => handleDeleteKey(key.id)}
                title="Delete"
                style={{ color: '#ef4444' }}
              >
                Delete
              </Button>
            </KeyActions>
          </KeyItem>
        ))}
      </KeyList>

      {apiKeys.length === 0 && (
        <WarningMessage>
          <FaExclamationTriangle />
          No API keys configured. Add a key to start using the provider.
        </WarningMessage>
      )}
    </Container>
  );
};

ApiKeyManager.propTypes = {
  providerId: PropTypes.string.isRequired,
  apiKeys: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      value: PropTypes.string.isRequired,
      createdAt: PropTypes.string.isRequired,
      lastUsed: PropTypes.string,
    })
  ).isRequired,
  onAddKey: PropTypes.func.isRequired,
  onDeleteKey: PropTypes.func.isRequired,
  onRotateKey: PropTypes.func.isRequired,
};

export default ApiKeyManager; 