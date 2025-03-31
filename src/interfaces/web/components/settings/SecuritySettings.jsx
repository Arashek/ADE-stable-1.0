import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaShieldAlt, FaLock, FaKey, FaUserShield, FaExclamationTriangle } from 'react-icons/fa';
import PropTypes from 'prop-types';
import { settingsService } from '../../services/settingsService';

const Section = styled.div`
  margin-bottom: 32px;
`;

const SectionHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
`;

const SectionTitle = styled.h2`
  font-size: 18px;
  color: #1e293b;
  margin: 0;
`;

const SectionDescription = styled.p`
  color: #64748b;
  margin: 4px 0 0 0;
  font-size: 14px;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const Label = styled.label`
  font-size: 14px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const Input = styled.input`
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s;

  &:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
  }

  &:disabled {
    background: #f1f5f9;
    cursor: not-allowed;
  }
`;

const Button = styled.button`
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  align-self: flex-start;

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
`;

const SecurityGroup = styled.div`
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
`;

const SecurityHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
`;

const SecurityTitle = styled.h3`
  font-size: 16px;
  color: #1e293b;
  margin: 0;
`;

const SecurityDescription = styled.p`
  font-size: 14px;
  color: #64748b;
  margin: 0 0 12px 0;
`;

const SecuritySettings = ({ onSettingChange }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    password: {
      current: '',
      new: '',
      confirm: '',
    },
    twoFactor: {
      enabled: false,
      method: 'authenticator',
    },
    sessionManagement: {
      maxSessions: 5,
      autoLogout: 30,
    },
    securityQuestions: {
      enabled: false,
      questions: [
        { id: 1, question: '', answer: '' },
        { id: 2, question: '', answer: '' },
        { id: 3, question: '', answer: '' },
      ],
    },
    loginHistory: {
      enabled: true,
      retentionDays: 90,
    },
  });

  useEffect(() => {
    fetchSecuritySettings();
  }, []);

  const fetchSecuritySettings = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await settingsService.getSecuritySettings();
      setFormData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    const [category, setting] = name.split('.');
    
    if (type === 'checkbox') {
      setFormData(prev => ({
        ...prev,
        [category]: {
          ...prev[category],
          [setting]: checked,
        },
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [category]: {
          ...prev[category],
          [setting]: value,
        },
      }));
    }
  };

  const handleQuestionChange = (e, questionId) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      securityQuestions: {
        ...prev.securityQuestions,
        questions: prev.securityQuestions.questions.map(q =>
          q.id === questionId ? { ...q, [name]: value } : q
        ),
      },
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      await settingsService.updateSecuritySettings(formData);
      onSettingChange('Security settings updated successfully');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Section>
      <SectionHeader>
        <FaShieldAlt />
        <div>
          <SectionTitle>Security Settings</SectionTitle>
          <SectionDescription>Manage your account security and privacy settings</SectionDescription>
        </div>
      </SectionHeader>

      {error && (
        <ErrorMessage>
          <FaExclamationTriangle />
          {error}
        </ErrorMessage>
      )}

      <Form onSubmit={handleSubmit}>
        <SecurityGroup>
          <SecurityHeader>
            <FaLock />
            <SecurityTitle>Password</SecurityTitle>
          </SecurityHeader>
          <SecurityDescription>
            Change your account password
          </SecurityDescription>
          <FormGroup>
            <Label>Current Password</Label>
            <Input
              type="password"
              name="password.current"
              value={formData.password.current}
              onChange={handleInputChange}
              disabled={loading}
            />
          </FormGroup>
          <FormGroup>
            <Label>New Password</Label>
            <Input
              type="password"
              name="password.new"
              value={formData.password.new}
              onChange={handleInputChange}
              disabled={loading}
            />
          </FormGroup>
          <FormGroup>
            <Label>Confirm New Password</Label>
            <Input
              type="password"
              name="password.confirm"
              value={formData.password.confirm}
              onChange={handleInputChange}
              disabled={loading}
            />
          </FormGroup>
        </SecurityGroup>

        <SecurityGroup>
          <SecurityHeader>
            <FaKey />
            <SecurityTitle>Two-Factor Authentication</SecurityTitle>
          </SecurityHeader>
          <SecurityDescription>
            Add an extra layer of security to your account
          </SecurityDescription>
          <FormGroup>
            <Label>
              <input
                type="checkbox"
                name="twoFactor.enabled"
                checked={formData.twoFactor.enabled}
                onChange={handleInputChange}
                disabled={loading}
              />
              Enable Two-Factor Authentication
            </Label>
          </FormGroup>
          {formData.twoFactor.enabled && (
            <FormGroup>
              <Label>Authentication Method</Label>
              <select
                name="twoFactor.method"
                value={formData.twoFactor.method}
                onChange={handleInputChange}
                disabled={loading}
              >
                <option value="authenticator">Authenticator App</option>
                <option value="sms">SMS</option>
                <option value="email">Email</option>
              </select>
            </FormGroup>
          )}
        </SecurityGroup>

        <SecurityGroup>
          <SecurityHeader>
            <FaUserShield />
            <SecurityTitle>Session Management</SecurityTitle>
          </SecurityHeader>
          <SecurityDescription>
            Control your active sessions and automatic logout
          </SecurityDescription>
          <FormGroup>
            <Label>Maximum Active Sessions</Label>
            <Input
              type="number"
              name="sessionManagement.maxSessions"
              value={formData.sessionManagement.maxSessions}
              onChange={handleInputChange}
              min="1"
              max="10"
              disabled={loading}
            />
          </FormGroup>
          <FormGroup>
            <Label>Auto Logout (minutes)</Label>
            <Input
              type="number"
              name="sessionManagement.autoLogout"
              value={formData.sessionManagement.autoLogout}
              onChange={handleInputChange}
              min="5"
              max="120"
              disabled={loading}
            />
          </FormGroup>
        </SecurityGroup>

        <SecurityGroup>
          <SecurityHeader>
            <FaShieldAlt />
            <SecurityTitle>Security Questions</SecurityTitle>
          </SecurityHeader>
          <SecurityDescription>
            Set up security questions for account recovery
          </SecurityDescription>
          <FormGroup>
            <Label>
              <input
                type="checkbox"
                name="securityQuestions.enabled"
                checked={formData.securityQuestions.enabled}
                onChange={handleInputChange}
                disabled={loading}
              />
              Enable Security Questions
            </Label>
          </FormGroup>
          {formData.securityQuestions.enabled && (
            <>
              {formData.securityQuestions.questions.map(question => (
                <div key={question.id}>
                  <FormGroup>
                    <Label>Question {question.id}</Label>
                    <Input
                      type="text"
                      name="question"
                      value={question.question}
                      onChange={(e) => handleQuestionChange(e, question.id)}
                      disabled={loading}
                    />
                  </FormGroup>
                  <FormGroup>
                    <Label>Answer</Label>
                    <Input
                      type="text"
                      name="answer"
                      value={question.answer}
                      onChange={(e) => handleQuestionChange(e, question.id)}
                      disabled={loading}
                    />
                  </FormGroup>
                </div>
              ))}
            </>
          )}
        </SecurityGroup>

        <SecurityGroup>
          <SecurityHeader>
            <FaUserShield />
            <SecurityTitle>Login History</SecurityTitle>
          </SecurityHeader>
          <SecurityDescription>
            Manage your login history and retention settings
          </SecurityDescription>
          <FormGroup>
            <Label>
              <input
                type="checkbox"
                name="loginHistory.enabled"
                checked={formData.loginHistory.enabled}
                onChange={handleInputChange}
                disabled={loading}
              />
              Enable Login History
            </Label>
          </FormGroup>
          {formData.loginHistory.enabled && (
            <FormGroup>
              <Label>Retention Period (days)</Label>
              <Input
                type="number"
                name="loginHistory.retentionDays"
                value={formData.loginHistory.retentionDays}
                onChange={handleInputChange}
                min="30"
                max="365"
                disabled={loading}
              />
            </FormGroup>
          )}
        </SecurityGroup>

        <Button type="submit" disabled={loading}>
          Save Changes
        </Button>
      </Form>
    </Section>
  );
};

SecuritySettings.propTypes = {
  onSettingChange: PropTypes.func.isRequired,
};

export default SecuritySettings; 