import React, { useState, useEffect } from 'react';
import { FaKey, FaShieldAlt, FaQrcode } from 'react-icons/fa';
import styled from 'styled-components';
import axios from 'axios';

const SecurityGroup = styled.div`
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const SecurityHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  
  svg {
    margin-right: 10px;
    color: #4a90e2;
  }
`;

const SecurityTitle = styled.h3`
  margin: 0;
  color: #333;
`;

const SecurityDescription = styled.p`
  color: #666;
  margin-bottom: 20px;
`;

const FormGroup = styled.div`
  margin-bottom: 15px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 5px;
  color: #333;
`;

const Input = styled.input`
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 10px;
`;

const Button = styled.button`
  background: #4a90e2;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  
  &:hover {
    background: #357abd;
  }
  
  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`;

const QRCodeContainer = styled.div`
  text-align: center;
  margin: 20px 0;
  
  img {
    max-width: 200px;
    margin-bottom: 10px;
  }
`;

const SecuritySettings = () => {
  const [formData, setFormData] = useState({
    twoFactor: {
      enabled: false,
      method: 'authenticator',
      phoneNumber: '',
      email: ''
    }
  });
  const [loading, setLoading] = useState(false);
  const [qrCode, setQrCode] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    check2FAStatus();
  }, []);

  const check2FAStatus = async () => {
    try {
      const response = await axios.get('/api/2fa/status');
      setFormData(prev => ({
        ...prev,
        twoFactor: {
          ...prev.twoFactor,
          enabled: response.data.enabled
        }
      }));
    } catch (error) {
      console.error('Failed to check 2FA status:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      twoFactor: {
        ...prev.twoFactor,
        [name.split('.')[1]]: type === 'checkbox' ? checked : value
      }
    }));
  };

  const handleSetup2FA = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await axios.post('/api/2fa/setup', {
        method: formData.twoFactor.method,
        phone_number: formData.twoFactor.phoneNumber,
        email: formData.twoFactor.email
      });

      if (formData.twoFactor.method === 'authenticator') {
        setQrCode(response.data.qr_code);
      } else {
        setSuccess('Verification code sent successfully');
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to setup 2FA');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify2FA = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await axios.post('/api/2fa/verify', {
        code: verificationCode,
        method: formData.twoFactor.method
      });
      setSuccess('2FA verified successfully');
      check2FAStatus();
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to verify 2FA');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SecurityGroup>
      <SecurityHeader>
        <FaShieldAlt />
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
        <>
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

          {formData.twoFactor.method === 'sms' && (
            <FormGroup>
              <Label>Phone Number</Label>
              <Input
                type="tel"
                name="twoFactor.phoneNumber"
                value={formData.twoFactor.phoneNumber}
                onChange={handleInputChange}
                disabled={loading}
                placeholder="Enter your phone number"
              />
            </FormGroup>
          )}

          {formData.twoFactor.method === 'email' && (
            <FormGroup>
              <Label>Email Address</Label>
              <Input
                type="email"
                name="twoFactor.email"
                value={formData.twoFactor.email}
                onChange={handleInputChange}
                disabled={loading}
                placeholder="Enter your email address"
              />
            </FormGroup>
          )}

          <Button
            onClick={handleSetup2FA}
            disabled={loading}
          >
            Setup 2FA
          </Button>

          {qrCode && (
            <QRCodeContainer>
              <img src={`data:image/png;base64,${qrCode}`} alt="2FA QR Code" />
              <p>Scan this QR code with your authenticator app</p>
            </QRCodeContainer>
          )}

          {(qrCode || formData.twoFactor.method !== 'authenticator') && (
            <FormGroup>
              <Label>Verification Code</Label>
              <Input
                type="text"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                disabled={loading}
                placeholder="Enter verification code"
              />
              <Button
                onClick={handleVerify2FA}
                disabled={loading || !verificationCode}
              >
                Verify Code
              </Button>
            </FormGroup>
          )}

          {error && <p style={{ color: 'red' }}>{error}</p>}
          {success && <p style={{ color: 'green' }}>{success}</p>}
        </>
      )}
    </SecurityGroup>
  );
};

export default SecuritySettings; 