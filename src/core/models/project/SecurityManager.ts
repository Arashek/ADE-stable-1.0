import { exec } from 'child_process';
import { promisify } from 'util';
import { Logger } from '../logging/Logger';

const execAsync = promisify(exec);

export interface SecurityPolicy {
  // User isolation
  userNamespace: boolean;
  readOnlyRootfs: boolean;
  noNewPrivileges: boolean;
  privileged: boolean;
  
  // Resource limits
  ulimits: {
    nofile: number;
    nproc: number;
  };
  
  // Capabilities
  capabilities: {
    add: string[];
    drop: string[];
  };
  
  // Security options
  securityOpts: string[];
  
  // Network security
  networkMode: 'bridge' | 'host' | 'none';
  exposedPorts: string[];
  allowedIPs: string[];
  
  // Access control
  readOnlyPaths: string[];
  writablePaths: string[];
  allowedCommands: string[];
}

export interface UserPermissions {
  userId: number;
  groupId: number;
  additionalGroups: number[];
  capabilities: string[];
  allowedCommands: string[];
  allowedPaths: string[];
  deniedPaths: string[];
}

export class SecurityManager {
  private logger: Logger;
  private defaultPolicy: SecurityPolicy;

  constructor() {
    this.logger = new Logger('SecurityManager');
    this.defaultPolicy = {
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
        drop: [
          'ALL',
          'NET_ADMIN',
          'SYS_ADMIN',
          'MKNOD',
          'SETUID',
          'SETGID',
        ],
      },
      securityOpts: [
        'no-new-privileges:true',
        'seccomp=unconfined',
        'apparmor=unconfined',
      ],
      networkMode: 'bridge',
      exposedPorts: [],
      allowedIPs: [],
      readOnlyPaths: ['/proc', '/sys'],
      writablePaths: ['/tmp', '/var/tmp'],
      allowedCommands: [],
    };
  }

  async applySecurityPolicy(containerId: string, policy: Partial<SecurityPolicy> = {}): Promise<void> {
    try {
      const finalPolicy = { ...this.defaultPolicy, ...policy };
      const dockerArgs = this.generateDockerSecurityArgs(finalPolicy);
      
      await execAsync(`docker update ${dockerArgs.join(' ')} ${containerId}`);
      this.logger.info(`Applied security policy to container ${containerId}`);
    } catch (error) {
      this.logger.error('Failed to apply security policy', error);
      throw error;
    }
  }

  async configureUserIsolation(containerId: string, userId: number, groupId: number): Promise<void> {
    try {
      const commands = [
        `docker exec ${containerId} groupadd -g ${groupId} container_group`,
        `docker exec ${containerId} useradd -u ${userId} -g ${groupId} container_user`,
        `docker exec ${containerId} chown -R ${userId}:${groupId} /workspace`,
      ];

      for (const cmd of commands) {
        await execAsync(cmd);
      }

      this.logger.info(`Configured user isolation for container ${containerId}`);
    } catch (error) {
      this.logger.error('Failed to configure user isolation', error);
      throw error;
    }
  }

  async setupNetworkSecurity(containerId: string, config: {
    networkMode: 'bridge' | 'host' | 'none';
    exposedPorts: string[];
    allowedIPs: string[];
  }): Promise<void> {
    try {
      // Disconnect from all networks first
      await execAsync(`docker network disconnect -f $(docker network ls -q) ${containerId}`);

      // Apply network mode
      await execAsync(`docker update --network ${config.networkMode} ${containerId}`);

      // Configure iptables rules for IP filtering
      if (config.allowedIPs.length > 0) {
        const iptablesRules = config.allowedIPs.map(ip => 
          `iptables -A DOCKER-USER -s ${ip} -j ACCEPT`
        );
        await execAsync(iptablesRules.join('; '));
      }

      this.logger.info(`Configured network security for container ${containerId}`);
    } catch (error) {
      this.logger.error('Failed to setup network security', error);
      throw error;
    }
  }

  async configureAccessControl(containerId: string, permissions: UserPermissions): Promise<void> {
    try {
      // Set user and group IDs
      await execAsync(`docker exec ${containerId} usermod -u ${permissions.userId} container_user`);
      await execAsync(`docker exec ${containerId} groupmod -g ${permissions.groupId} container_group`);

      // Add user to additional groups
      if (permissions.additionalGroups.length > 0) {
        await execAsync(
          `docker exec ${containerId} usermod -a -G ${permissions.additionalGroups.join(',')} container_user`
        );
      }

      // Configure allowed paths
      for (const path of permissions.allowedPaths) {
        await execAsync(`docker exec ${containerId} chown -R ${permissions.userId}:${permissions.groupId} ${path}`);
      }

      // Configure denied paths
      for (const path of permissions.deniedPaths) {
        await execAsync(`docker exec ${containerId} chmod 000 ${path}`);
      }

      this.logger.info(`Configured access control for container ${containerId}`);
    } catch (error) {
      this.logger.error('Failed to configure access control', error);
      throw error;
    }
  }

  private generateDockerSecurityArgs(policy: SecurityPolicy): string[] {
    const args: string[] = [];

    // User namespace
    if (policy.userNamespace) {
      args.push('--userns=host');
    }

    // Read-only rootfs
    if (policy.readOnlyRootfs) {
      args.push('--read-only');
    }

    // No new privileges
    if (policy.noNewPrivileges) {
      args.push('--security-opt=no-new-privileges');
    }

    // Privileged mode
    if (policy.privileged) {
      args.push('--privileged');
    }

    // Ulimits
    args.push(
      `--ulimit=nofile=${policy.ulimits.nofile}`,
      `--ulimit=nproc=${policy.ulimits.nproc}`
    );

    // Capabilities
    if (policy.capabilities.add.length > 0) {
      args.push(`--cap-add=${policy.capabilities.add.join(',')}`);
    }
    if (policy.capabilities.drop.length > 0) {
      args.push(`--cap-drop=${policy.capabilities.drop.join(',')}`);
    }

    // Security options
    policy.securityOpts.forEach(opt => {
      args.push(`--security-opt=${opt}`);
    });

    // Network mode
    args.push(`--network=${policy.networkMode}`);

    // Exposed ports
    policy.exposedPorts.forEach(port => {
      args.push(`-p ${port}`);
    });

    return args;
  }
} 