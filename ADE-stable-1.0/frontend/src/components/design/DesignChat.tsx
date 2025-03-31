import React, { useState, useRef, useEffect } from 'react';
import { DesignSystem, DesignComponent, DesignStyle, DesignModification } from '../../types/design';
import { DesignAgent } from '../../services/DesignAgent';

interface DesignChatProps {
  designAgent: DesignAgent;
  currentDesign: Partial<DesignSystem>;
  onDesignUpdate: (design: Partial<DesignSystem>) => void;
  modificationMode: 'natural' | 'tools' | 'hybrid';
  onModeChange: (mode: 'natural' | 'tools' | 'hybrid') => void;
}

interface ChatMessage {
  id: string;
  type: 'user' | 'agent' | 'system' | 'tool';
  content: string;
  timestamp: Date;
  metadata?: {
    component?: DesignComponent;
    style?: DesignStyle;
    preview?: string;
    modification?: DesignModification;
    toolAction?: {
      type: string;
      target: string;
      value: any;
    };
  };
}

export const DesignChat: React.FC<DesignChatProps> = ({
  designAgent,
  currentDesign,
  onDesignUpdate,
  modificationMode,
  onModeChange,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeTool, setActiveTool] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isProcessing) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsProcessing(true);

    try {
      // Process the message through the design agent
      const response = await designAgent.processMessage(input, currentDesign);
      
      const agentMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: response.message,
        timestamp: new Date(),
        metadata: response.metadata,
      };

      setMessages(prev => [...prev, agentMessage]);

      // If the response includes design updates, apply them
      if (response.designUpdate) {
        onDesignUpdate(response.designUpdate);
      }

      // If in hybrid mode and the response suggests a tool action
      if (modificationMode === 'hybrid' && response.suggestedTool) {
        const toolMessage: ChatMessage = {
          id: (Date.now() + 2).toString(),
          type: 'tool',
          content: `Suggested tool: ${response.suggestedTool.name}`,
          timestamp: new Date(),
          metadata: {
            toolAction: {
              type: response.suggestedTool.type,
              target: response.suggestedTool.target,
              value: response.suggestedTool.value,
            },
          },
        };
        setMessages(prev => [...prev, toolMessage]);
        setActiveTool(response.suggestedTool.name);
      }
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'system',
        content: 'An error occurred while processing your request.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleToolAction = async (action: ChatMessage['metadata']['toolAction']) => {
    if (!action) return;

    try {
      const toolMessage: ChatMessage = {
        id: Date.now().toString(),
        type: 'tool',
        content: `Applying ${action.type} to ${action.target}`,
        timestamp: new Date(),
        metadata: { toolAction: action },
      };
      setMessages(prev => [...prev, toolMessage]);

      // Apply the tool action
      const result = await designAgent.applyToolAction(action);
      
      // Update the design if the tool action was successful
      if (result.success && result.designUpdate) {
        onDesignUpdate(result.designUpdate);
      }
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'system',
        content: 'Failed to apply tool action.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const renderMessage = (message: ChatMessage) => {
    const messageClasses = {
      user: 'bg-blue-100 ml-auto',
      agent: 'bg-gray-100',
      system: 'bg-yellow-100 text-yellow-800',
      tool: 'bg-green-100',
    };

    return (
      <div
        key={message.id}
        className={`p-3 rounded-lg max-w-[80%] mb-2 ${messageClasses[message.type]}`}
      >
        <div className="text-sm font-medium mb-1">
          {message.type === 'user' ? 'You' : 
           message.type === 'agent' ? 'Design Agent' : 
           message.type === 'tool' ? 'Design Tool' : 'System'}
        </div>
        <div className="text-sm">{message.content}</div>
        
        {message.metadata?.preview && (
          <div className="mt-2 p-2 bg-white rounded border">
            <img src={message.metadata.preview} alt="Preview" className="max-w-full h-auto" />
          </div>
        )}

        {message.metadata?.component && (
          <div className="mt-2 p-2 bg-white rounded border">
            <h4 className="font-medium">Component Preview</h4>
            <pre className="text-xs mt-1">
              {JSON.stringify(message.metadata.component, null, 2)}
            </pre>
          </div>
        )}

        {message.metadata?.style && (
          <div className="mt-2 p-2 bg-white rounded border">
            <h4 className="font-medium">Style Preview</h4>
            <pre className="text-xs mt-1">
              {JSON.stringify(message.metadata.style, null, 2)}
            </pre>
          </div>
        )}

        {message.metadata?.toolAction && (
          <div className="mt-2 p-2 bg-white rounded border">
            <h4 className="font-medium">Tool Action</h4>
            <div className="flex justify-between items-center mt-1">
              <pre className="text-xs">
                {JSON.stringify(message.metadata.toolAction, null, 2)}
              </pre>
              <button
                onClick={() => handleToolAction(message.metadata.toolAction)}
                className="px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Apply
              </button>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full">
      {/* Mode Selector */}
      <div className="flex items-center gap-2 p-2 border-b">
        <span className="text-sm font-medium">Interaction Mode:</span>
        <select
          value={modificationMode}
          onChange={(e) => onModeChange(e.target.value as 'natural' | 'tools' | 'hybrid')}
          className="px-2 py-1 border rounded"
        >
          <option value="natural">Natural Language</option>
          <option value="tools">Design Tools</option>
          <option value="hybrid">Hybrid Mode</option>
        </select>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(renderMessage)}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder={
              modificationMode === 'natural'
                ? "Describe your design changes or ask for suggestions..."
                : modificationMode === 'tools'
                ? "Select a tool to modify the design..."
                : "Describe changes or use tools to modify the design..."
            }
            className="flex-1 px-3 py-2 border rounded"
            disabled={isProcessing}
          />
          <button
            onClick={handleSend}
            disabled={isProcessing || !input.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {isProcessing ? 'Processing...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
}; 