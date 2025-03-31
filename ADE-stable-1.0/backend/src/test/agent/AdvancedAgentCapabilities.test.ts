import { container } from 'tsyringe';
import { AdvancedAgentCapabilities } from '../../services/agent/AdvancedAgentCapabilities';

describe('AdvancedAgentCapabilities', () => {
  let advancedCapabilities: AdvancedAgentCapabilities;

  beforeEach(() => {
    advancedCapabilities = container.resolve(AdvancedAgentCapabilities);
  });

  afterEach(() => {
    container.clearInstances();
  });

  describe('getCapabilities', () => {
    it('should return all advanced capabilities', () => {
      const capabilities = advancedCapabilities.getCapabilities();
      expect(capabilities).toBeInstanceOf(Array);
      expect(capabilities.length).toBeGreaterThan(0);
      expect(capabilities[0]).toHaveProperty('id');
      expect(capabilities[0]).toHaveProperty('name');
      expect(capabilities[0]).toHaveProperty('description');
      expect(capabilities[0]).toHaveProperty('requiredLLMs');
      expect(capabilities[0]).toHaveProperty('supportedActions');
      expect(capabilities[0]).toHaveProperty('parameters');
    });
  });

  describe('getCapabilityById', () => {
    it('should return capability by ID', () => {
      const capability = advancedCapabilities.getCapabilityById('code-generation');
      expect(capability).toBeDefined();
      expect(capability?.id).toBe('code-generation');
      expect(capability?.name).toBe('Code Generation');
    });

    it('should return undefined for non-existent ID', () => {
      const capability = advancedCapabilities.getCapabilityById('non-existent');
      expect(capability).toBeUndefined();
    });
  });

  describe('getCapabilitiesByLLM', () => {
    it('should return capabilities that require specific LLM', () => {
      const capabilities = advancedCapabilities.getCapabilitiesByLLM('claude-3-opus');
      expect(capabilities).toBeInstanceOf(Array);
      expect(capabilities.length).toBeGreaterThan(0);
      expect(capabilities.every(cap => 
        cap.requiredLLMs.includes('claude-3-opus')
      )).toBe(true);
    });

    it('should return empty array for non-existent LLM', () => {
      const capabilities = advancedCapabilities.getCapabilitiesByLLM('non-existent');
      expect(capabilities).toEqual([]);
    });
  });

  describe('getCapabilitiesByAction', () => {
    it('should return capabilities that support specific action', () => {
      const capabilities = advancedCapabilities.getCapabilitiesByAction('security-audit');
      expect(capabilities).toBeInstanceOf(Array);
      expect(capabilities.length).toBeGreaterThan(0);
      expect(capabilities.every(cap => 
        cap.supportedActions.includes('security-audit')
      )).toBe(true);
    });

    it('should return empty array for non-existent action', () => {
      const capabilities = advancedCapabilities.getCapabilitiesByAction('non-existent');
      expect(capabilities).toEqual([]);
    });
  });

  describe('capability parameters', () => {
    it('should have valid parameters for code generation', () => {
      const capability = advancedCapabilities.getCapabilityById('code-generation');
      expect(capability?.parameters).toMatchObject({
        maxTokens: expect.any(Number),
        temperature: expect.any(Number),
        topP: expect.any(Number),
        frequencyPenalty: expect.any(Number),
        presencePenalty: expect.any(Number)
      });
    });

    it('should have valid parameters for security analysis', () => {
      const capability = advancedCapabilities.getCapabilityById('security-analysis');
      expect(capability?.parameters).toMatchObject({
        maxTokens: expect.any(Number),
        temperature: expect.any(Number),
        topP: expect.any(Number),
        securityLevels: expect.arrayContaining(['critical', 'high', 'medium', 'low'])
      });
    });
  });

  describe('capability validation', () => {
    it('should have unique IDs', () => {
      const capabilities = advancedCapabilities.getCapabilities();
      const ids = capabilities.map(cap => cap.id);
      const uniqueIds = new Set(ids);
      expect(ids.length).toBe(uniqueIds.size);
    });

    it('should have required LLMs', () => {
      const capabilities = advancedCapabilities.getCapabilities();
      expect(capabilities.every(cap => 
        cap.requiredLLMs.length > 0
      )).toBe(true);
    });

    it('should have supported actions', () => {
      const capabilities = advancedCapabilities.getCapabilities();
      expect(capabilities.every(cap => 
        cap.supportedActions.length > 0
      )).toBe(true);
    });
  });
}); 