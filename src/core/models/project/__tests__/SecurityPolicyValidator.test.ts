import { SecurityPolicyValidator } from '../SecurityPolicyValidator';
import { SecurityPolicy } from '../SecurityManager';
import { Logger } from '../../../logging/Logger';

jest.mock('../../../logging/Logger');

describe('SecurityPolicyValidator', () => {
  let validator: SecurityPolicyValidator;
  let mockLogger: jest.Mocked<Logger>;

  beforeEach(() => {
    jest.clearAllMocks();
    validator = new SecurityPolicyValidator();
    mockLogger = new Logger('test') as jest.Mocked<Logger>;
  });

  describe('validatePolicy', () => {
    it('should validate a secure policy', () => {
      const securePolicy: SecurityPolicy = {
        userNamespace: true,
        readOnlyRootfs: true,
        noNewPrivileges: true,
        privileged: false,
        ulimits: {
          nofile: 1024,
          nproc: 1024,
        },
        capabilities: {
          add: [],
          drop: ['ALL', 'NET_ADMIN', 'SYS_ADMIN'],
        },
        securityOpts: [
          'no-new-privileges:true',
          'seccomp=unconfined',
          'apparmor=unconfined',
        ],
        networkMode: 'bridge',
        exposedPorts: [],
        allowedIPs: ['192.168.1.1'],
        readOnlyPaths: ['/proc', '/sys'],
        writablePaths: ['/tmp', '/var/tmp'],
        allowedCommands: [],
      };

      const results = validator.validatePolicy(securePolicy);

      expect(results.every(r => r.passed)).toBe(true);
      expect(results.some(r => r.severity === 'critical')).toBe(true);
    });

    it('should detect insecure policy settings', () => {
      const insecurePolicy: SecurityPolicy = {
        userNamespace: false,
        readOnlyRootfs: false,
        noNewPrivileges: false,
        privileged: true,
        ulimits: {
          nofile: 0,
          nproc: 0,
        },
        capabilities: {
          add: ['ALL'],
          drop: [],
        },
        securityOpts: [],
        networkMode: 'host',
        exposedPorts: ['80:80', '443:443'],
        allowedIPs: [],
        readOnlyPaths: [],
        writablePaths: ['/'],
        allowedCommands: [],
      };

      const results = validator.validatePolicy(insecurePolicy);

      expect(results.some(r => !r.passed)).toBe(true);
      expect(results.filter(r => r.severity === 'critical' && !r.passed).length).toBeGreaterThan(0);
    });

    it('should validate partial policy updates', () => {
      const partialPolicy: Partial<SecurityPolicy> = {
        privileged: false,
        networkMode: 'bridge',
      };

      const results = validator.validatePolicy(partialPolicy as SecurityPolicy);

      expect(results.some(r => r.ruleId === 'PRIVILEGED_MODE' && r.passed)).toBe(true);
      expect(results.some(r => r.ruleId === 'NETWORK_MODE' && r.passed)).toBe(true);
    });

    it('should provide detailed compliance information', () => {
      const policy: SecurityPolicy = {
        userNamespace: true,
        readOnlyRootfs: false,
        noNewPrivileges: true,
        privileged: false,
        ulimits: {
          nofile: 1024,
          nproc: 1024,
        },
        capabilities: {
          add: [],
          drop: ['ALL'],
        },
        securityOpts: ['no-new-privileges:true'],
        networkMode: 'bridge',
        exposedPorts: [],
        allowedIPs: ['192.168.1.1'],
        readOnlyPaths: ['/proc', '/sys'],
        writablePaths: ['/tmp', '/var/tmp'],
        allowedCommands: [],
      };

      const results = validator.validatePolicy(policy);

      const readOnlyRootResult = results.find(r => r.ruleId === 'READ_ONLY_ROOT');
      expect(readOnlyRootResult).toBeDefined();
      expect(readOnlyRootResult?.passed).toBe(false);
      expect(readOnlyRootResult?.details).toContain('Container root filesystem is writable');

      const userNamespaceResult = results.find(r => r.ruleId === 'USER_NAMESPACE');
      expect(userNamespaceResult).toBeDefined();
      expect(userNamespaceResult?.passed).toBe(true);
      expect(userNamespaceResult?.details).toContain('Container is using user namespace mapping');
    });

    it('should handle edge cases', () => {
      const edgeCasePolicy: SecurityPolicy = {
        userNamespace: true,
        readOnlyRootfs: true,
        noNewPrivileges: true,
        privileged: false,
        ulimits: {
          nofile: 0,
          nproc: 0,
        },
        capabilities: {
          add: [],
          drop: ['ALL'],
        },
        securityOpts: ['no-new-privileges:true'],
        networkMode: 'bridge',
        exposedPorts: [],
        allowedIPs: [],
        readOnlyPaths: [],
        writablePaths: [],
        allowedCommands: [],
      };

      const results = validator.validatePolicy(edgeCasePolicy);

      expect(results.some(r => r.ruleId === 'RESOURCE_LIMITS' && !r.passed)).toBe(true);
      expect(results.some(r => r.ruleId === 'ALLOWED_IPS' && !r.passed)).toBe(true);
    });
  });
}); 