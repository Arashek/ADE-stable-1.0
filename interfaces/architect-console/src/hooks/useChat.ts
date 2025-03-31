import { useState, useEffect } from 'react';
import useStore from '../store';
import { chatApi } from '../services/api';
import { Message } from '../types';

export const useChat = () => {
  const { messages, addMessage, clearMessages } = useStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadMessages = async () => {
      try {
        setIsLoading(true);
        const fetchedMessages = await chatApi.getMessages();
        clearMessages();
        fetchedMessages.forEach(addMessage);
      } catch (err) {
        setError('Failed to load messages');
        console.error('Error loading messages:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadMessages();
  }, [clearMessages, addMessage]);

  const sendMessage = async (message: string) => {
    try {
      setIsLoading(true);
      const response = await chatApi.sendMessage(message);
      addMessage(response);
    } catch (err) {
      setError('Failed to send message');
      console.error('Error sending message:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    messages,
    isLoading,
    error,
    sendMessage,
  };
}; 