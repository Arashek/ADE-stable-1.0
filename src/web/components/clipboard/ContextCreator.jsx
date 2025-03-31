import React, { useState } from 'react';
import styled from 'styled-components';
import useClipboardManagerStore from '../../utils/clipboard-manager';

const CreatorContainer = styled.div`
  padding: 16px;
  background: ${props => props.theme.background};
  border-radius: 8px;
  margin-bottom: 16px;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const InputGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const Label = styled.label`
  font-size: 14px;
  color: ${props => props.theme.text};
  font-weight: 500;
`;

const TextArea = styled.textarea`
  padding: 8px 12px;
  border: 1px solid ${props => props.theme.border};
  border-radius: 4px;
  background: ${props => props.theme.inputBackground};
  color: ${props => props.theme.text};
  font-size: 14px;
  min-height: 100px;
  resize: vertical;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.primary};
  }
`;

const Select = styled.select`
  padding: 8px 12px;
  border: 1px solid ${props => props.theme.border};
  border-radius: 4px;
  background: ${props => props.theme.inputBackground};
  color: ${props => props.theme.text};
  font-size: 14px;
`;

const Button = styled.button`
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background: ${props => props.theme.primary};
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.primaryHover};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  color: ${props => props.theme.error};
  font-size: 12px;
  margin-top: 4px;
`;

const ContextCreator = () => {
  const [content, setContent] = useState('');
  const [type, setType] = useState('text');
  const [priority, setPriority] = useState(5);
  const [error, setError] = useState('');
  const {
    createContextReference,
    activateContext
  } = useClipboardManagerStore();

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!content.trim()) {
      setError('Content is required');
      return;
    }

    try {
      const contextId = createContextReference(content, {
        type,
        priority
      });
      activateContext(contextId);
      setContent('');
      setType('text');
      setPriority(5);
    } catch (err) {
      setError('Failed to create context');
    }
  };

  return (
    <CreatorContainer>
      <Form onSubmit={handleSubmit}>
        <InputGroup>
          <Label>Content</Label>
          <TextArea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Enter context content..."
          />
          {error && <ErrorMessage>{error}</ErrorMessage>}
        </InputGroup>

        <InputGroup>
          <Label>Type</Label>
          <Select value={type} onChange={(e) => setType(e.target.value)}>
            <option value="text">Text</option>
            <option value="code">Code</option>
            <option value="url">URL</option>
            <option value="filepath">File Path</option>
          </Select>
        </InputGroup>

        <InputGroup>
          <Label>Priority (0-10)</Label>
          <input
            type="range"
            min="0"
            max="10"
            value={priority}
            onChange={(e) => setPriority(parseInt(e.target.value))}
          />
          <span>{priority}</span>
        </InputGroup>

        <Button type="submit" disabled={!content.trim()}>
          Create Context
        </Button>
      </Form>
    </CreatorContainer>
  );
};

export default ContextCreator; 