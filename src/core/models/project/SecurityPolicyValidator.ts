import { SecurityPolicy } from './SecurityManager';
import { Logger } from '../logging/Logger';

export interface ComplianceRule {
  id: string;
  name: string;
  description: string;
  check: (policy: SecurityPolicy) => boolean;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface ComplianceResult {
  ruleId: string;
  passed: boolean;
  details: string;
  severity: ComplianceRule['severity'];
}

export class SecurityPolicyValidator {
  private logger: Logger;
  private complianceRules: ComplianceRule[];

  constructor() {
    this.logger = new Logger('SecurityPolicyValidator');
    this.complianceRules = this.initializeComplianceRules();
  }

  validatePolicy(policy: SecurityPolicy): ComplianceResult[] {
    return this.complianceRules.map(rule => {
      const passed = rule.check(policy);
      return {
        ruleId: rule.id,
        passed,
        details: this.generateComplianceDetails(rule, policy),
        severity: rule.severity,
      };
    });
  }

  private initializeComplianceRules(): ComplianceRule[] {
    return [
      {
        id: 'PRIVILEGED_MODE',
        name: 'Privileged Mode Check',
        description: 'Container should not run in privileged mode',
        check: (policy) => !policy.privileged,
        severity: 'critical',
      },
      {
        id: 'USER_NAMESPACE',
        name: 'User Namespace Check',
        description: 'Container should use user namespace mapping',
        check: (policy) => policy.userNamespace,
        severity: 'high',
      },
      {
        id: 'READ_ONLY_ROOT',
        name: 'Read-only Root Filesystem',
        description: 'Container root filesystem should be read-only',
        check: (policy) => policy.readOnlyRootfs,
        severity: 'high',
      },
      {
        id: 'NO_NEW_PRIVILEGES',
        name: 'No New Privileges',
        description: 'Container should not be able to gain new privileges',
        check: (policy) => policy.noNewPrivileges,
        severity: 'high',
      },
      {
        id: 'CAPABILITY_DROP',
        name: 'Capability Drop',
        description: 'Container should drop unnecessary capabilities',
        check: (policy) => policy.capabilities.drop.includes('ALL'),
        severity: 'high',
      },
      {
        id: 'NETWORK_MODE',
        name: 'Network Mode Check',
        description: 'Container should not use host network mode',
        check: (policy) => policy.networkMode !== 'host',
        severity: 'high',
      },
      {
        id: 'SECURITY_OPTS',
        name: 'Security Options',
        description: 'Container should have appropriate security options',
        check: (policy) => 
          policy.securityOpts.includes('no-new-privileges:true') &&
          policy.securityOpts.includes('seccomp=unconfined'),
        severity: 'medium',
      },
      {
        id: 'RESOURCE_LIMITS',
        name: 'Resource Limits',
        description: 'Container should have appropriate resource limits',
        check: (policy) => 
          policy.ulimits.nofile > 0 &&
          policy.ulimits.nproc > 0,
        severity: 'medium',
      },
      {
        id: 'EXPOSED_PORTS',
        name: 'Exposed Ports',
        description: 'Container should not expose unnecessary ports',
        check: (policy) => policy.exposedPorts.length === 0,
        severity: 'medium',
      },
      {
        id: 'ALLOWED_IPS',
        name: 'IP Filtering',
        description: 'Container should have IP filtering configured',
        check: (policy) => policy.allowedIPs.length > 0,
        severity: 'medium',
      },
    ];
  }

  private generateComplianceDetails(rule: ComplianceRule, policy: SecurityPolicy): string {
    switch (rule.id) {
      case 'PRIVILEGED_MODE':
        return policy.privileged 
          ? 'Container is running in privileged mode, which is a security risk'
          : 'Container is not running in privileged mode';
      case 'USER_NAMESPACE':
        return policy.userNamespace
          ? 'Container is using user namespace mapping'
          : 'Container is not using user namespace mapping';
      case 'READ_ONLY_ROOT':
        return policy.readOnlyRootfs
          ? 'Container root filesystem is read-only'
          : 'Container root filesystem is writable';
      case 'NO_NEW_PRIVILEGES':
        return policy.noNewPrivileges
          ? 'Container cannot gain new privileges'
          : 'Container can gain new privileges';
      case 'CAPABILITY_DROP':
        return policy.capabilities.drop.includes('ALL')
          ? 'Container drops all capabilities by default'
          : 'Container does not drop all capabilities by default';
      case 'NETWORK_MODE':
        return policy.networkMode !== 'host'
          ? 'Container is not using host network mode'
          : 'Container is using host network mode';
      case 'SECURITY_OPTS':
        return policy.securityOpts.includes('no-new-privileges:true')
          ? 'Container has appropriate security options'
          : 'Container is missing required security options';
      case 'RESOURCE_LIMITS':
        return policy.ulimits.nofile > 0 && policy.ulimits.nproc > 0
          ? 'Container has appropriate resource limits'
          : 'Container is missing resource limits';
      case 'EXPOSED_PORTS':
        return policy.exposedPorts.length === 0
          ? 'Container does not expose any ports'
          : `Container exposes ${policy.exposedPorts.length} ports`;
      case 'ALLOWED_IPS':
        return policy.allowedIPs.length > 0
          ? 'Container has IP filtering configured'
          : 'Container does not have IP filtering configured';
      default:
        return 'Unknown compliance rule';
    }
  }
} 