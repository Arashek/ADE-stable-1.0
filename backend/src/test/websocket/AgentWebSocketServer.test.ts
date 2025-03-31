import { createServer } from 'http';
import { Server } from 'socket.io';
import { Client } from 'socket.io-client';
import { container } from 'tsyringe';
import { AgentWebSocketServer } from '../../services/websocket/AgentWebSocketServer';
import { AgentRegistry } from '../../services/agent/AgentRegistry';
import { Logger } from '../../services/logger/Logger';
import { ConfigService } from '../../services/config/ConfigService';

describe('AgentWebSocketServer', () => {
  let httpServer: any;
  let io: Server;
  let serverSocket: any;
  let clientSocket: Client;
  let agentWebSocketServer: AgentWebSocketServer;
  let agentRegistry: AgentRegistry;
  let logger: Logger;
  let config: ConfigService;

  beforeAll((done) => {
    httpServer = createServer();
    io = new Server(httpServer);
    
    agentRegistry = container.resolve(AgentRegistry);
    logger = container.resolve(Logger);
    config = container.resolve(ConfigService);
    
    agentWebSocketServer = new AgentWebSocketServer(httpServer, agentRegistry, logger, config);
    httpServer.listen();
    
    const port = (httpServer.address() as any).port;
    clientSocket = new Client(`http://localhost:${port}`);
    
    io.on('connection', (socket) => {
      serverSocket = socket;
    });
    
    clientSocket.on('connect', done);
  });

  afterAll(() => {
    io.close();
    clientSocket.close();
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('agent preview subscription', () => {
    it('should handle successful preview subscription', (done) => {
      const agentId = 'test-agent';
      const mockRegistration = {
        id: agentId,
        status: 'active',
        lastActivity: new Date(),
        collaborators: []
      };

      jest.spyOn(agentRegistry, 'getRegistration').mockReturnValue(mockRegistration);
      jest.spyOn(agentRegistry, 'registerPreviewSocket').mockImplementation();

      clientSocket.emit('subscribe:agent-preview', agentId);

      clientSocket.on('agent-preview:state', (data) => {
        expect(data).toEqual({
          agentId,
          status: mockRegistration.status,
          lastActivity: mockRegistration.lastActivity,
          collaborators: mockRegistration.collaborators
        });
        done();
      });
    });

    it('should handle failed preview subscription', (done) => {
      const agentId = 'non-existent-agent';
      
      jest.spyOn(agentRegistry, 'getRegistration').mockReturnValue(null);

      clientSocket.emit('subscribe:agent-preview', agentId);

      clientSocket.on('error', (data) => {
        expect(data.message).toBe(`Agent ${agentId} not found`);
        done();
      });
    });
  });

  describe('agent collaboration', () => {
    it('should handle collaboration request', (done) => {
      const collaborationData = {
        sourceAgentId: 'agent1',
        targetAgentId: 'agent2',
        action: 'start' as const,
        context: { task: 'test' }
      };

      jest.spyOn(agentRegistry, 'startCollaboration').mockResolvedValue(undefined);

      clientSocket.emit('collaboration:request', collaborationData);

      clientSocket.on('collaboration:update', (data) => {
        expect(data).toEqual({
          ...collaborationData,
          timestamp: expect.any(Date)
        });
        done();
      });
    });
  });

  describe('broadcasting updates', () => {
    it('should broadcast agent updates', (done) => {
      const agentId = 'test-agent';
      const updateData = { status: 'updated' };

      clientSocket.join(`agent:${agentId}`);
      agentWebSocketServer.broadcastAgentUpdate(agentId, updateData);

      clientSocket.on('agent:update', (data) => {
        expect(data).toEqual({
          agentId,
          data: updateData,
          timestamp: expect.any(Date)
        });
        done();
      });
    });

    it('should broadcast capability updates', (done) => {
      const agentId = 'test-agent';
      const capabilityId = 'code-awareness';
      const updateData = { status: 'active' };

      clientSocket.join(`agent:${agentId}`);
      agentWebSocketServer.broadcastCapabilityUpdate(agentId, capabilityId, updateData);

      clientSocket.on('capability:update', (data) => {
        expect(data).toEqual({
          agentId,
          capabilityId,
          data: updateData,
          timestamp: expect.any(Date)
        });
        done();
      });
    });

    it('should broadcast LLM updates', (done) => {
      const llmId = 'claude-3-opus';
      const updateData = { status: 'available' };

      agentWebSocketServer.broadcastLLMUpdate(llmId, updateData);

      clientSocket.on('llm:update', (data) => {
        expect(data).toEqual({
          llmId,
          data: updateData,
          timestamp: expect.any(Date)
        });
        done();
      });
    });
  });
}); 