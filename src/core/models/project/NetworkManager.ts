import { Logger } from '../logging/Logger';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export interface PortMapping {
  containerPort: number;
  hostPort: number;
  protocol: 'tcp' | 'udp';
  description?: string;
}

export interface NetworkOptions {
  'com.docker.network.bridge.name'?: string;
  'com.docker.network.bridge.enable_icc'?: boolean;
  'com.docker.network.bridge.enable_ip_masquerade'?: boolean;
  'com.docker.network.bridge.host_binding_ipv4'?: string;
  'com.docker.network.bridge.mtu'?: number;
}

export interface NetworkConfig {
  name: string;
  driver: 'bridge' | 'host' | 'none';
  subnet?: string;
  gateway?: string;
  ipRange?: string;
  options?: NetworkOptions;
}

export interface SecurityRule {
  type: 'allow' | 'deny';
  protocol: 'tcp' | 'udp' | 'icmp';
  source: string;
  destination: string;
  port?: number;
  description?: string;
}

export interface ProxyConfig {
  target: string;
  port: number;
  path?: string;
  rewrite?: boolean;
  headers?: Record<string, string>;
  ssl?: {
    enabled: boolean;
    cert?: string;
    key?: string;
  };
}

export class NetworkManager {
  private logger: Logger;
  private networkConfig: NetworkConfig;
  private portMappings: PortMapping[];
  private securityRules: SecurityRule[];
  private proxyConfigs: ProxyConfig[];

  constructor() {
    this.logger = new Logger('NetworkManager');
    this.networkConfig = this.getDefaultNetworkConfig();
    this.portMappings = [];
    this.securityRules = [];
    this.proxyConfigs = [];
  }

  private getDefaultNetworkConfig(): NetworkConfig {
    return {
      name: 'ade-network',
      driver: 'bridge',
      subnet: '172.20.0.0/16',
      gateway: '172.20.0.1',
      ipRange: '172.20.0.2/16',
      options: {
        'com.docker.network.bridge.enable_icc': true,
        'com.docker.network.bridge.enable_ip_masquerade': true,
        'com.docker.network.bridge.mtu': 1500
      }
    };
  }

  async createNetwork(): Promise<void> {
    try {
      // Check if network already exists
      const networks = await this.listNetworks();
      if (networks.includes(this.networkConfig.name)) {
        this.logger.info(`Network ${this.networkConfig.name} already exists`);
        return;
      }

      // Build network creation command
      const command = this.buildNetworkCreateCommand();
      await execAsync(command);
      this.logger.info(`Created network: ${this.networkConfig.name}`);
    } catch (error) {
      this.logger.error(`Failed to create network: ${this.networkConfig.name}`, error);
      throw error;
    }
  }

  private buildNetworkCreateCommand(): string {
    const { name, driver, subnet, gateway, ipRange, options } = this.networkConfig;
    let command = `docker network create --driver ${driver}`;

    if (subnet) command += ` --subnet ${subnet}`;
    if (gateway) command += ` --gateway ${gateway}`;
    if (ipRange) command += ` --ip-range ${ipRange}`;

    // Add network options
    if (options) {
      Object.entries(options).forEach(([key, value]) => {
        command += ` --opt ${key}=${value}`;
      });
    }

    command += ` ${name}`;
    return command;
  }

  async configurePortMappings(containerId: string): Promise<void> {
    try {
      for (const mapping of this.portMappings) {
        const command = `docker container update --publish ${mapping.hostPort}:${mapping.containerPort}/${mapping.protocol} ${containerId}`;
        await execAsync(command);
        this.logger.info(`Configured port mapping: ${mapping.hostPort}:${mapping.containerPort}`);
      }
    } catch (error) {
      this.logger.error('Failed to configure port mappings', error);
      throw error;
    }
  }

  async setupSecurityRules(): Promise<void> {
    try {
      // In a real implementation, this would configure iptables rules
      // or use Docker's built-in network security features
      for (const rule of this.securityRules) {
        const command = this.buildSecurityRuleCommand(rule);
        await execAsync(command);
        this.logger.info(`Applied security rule: ${rule.description || 'unnamed rule'}`);
      }
    } catch (error) {
      this.logger.error('Failed to setup security rules', error);
      throw error;
    }
  }

  private buildSecurityRuleCommand(rule: SecurityRule): string {
    // This is a simplified example. In a real implementation,
    // you would use proper iptables commands or Docker's security features
    return `iptables -A ${rule.type.toUpperCase()} -p ${rule.protocol} -s ${rule.source} -d ${rule.destination} ${
      rule.port ? `--dport ${rule.port}` : ''
    } -j ${rule.type.toUpperCase()}`;
  }

  async setupProxy(proxyConfig: ProxyConfig): Promise<void> {
    try {
      // In a real implementation, this would configure a reverse proxy
      // like Nginx or Traefik
      const command = this.buildProxyCommand(proxyConfig);
      await execAsync(command);
      this.logger.info(`Configured proxy for ${proxyConfig.target}`);
    } catch (error) {
      this.logger.error('Failed to setup proxy', error);
      throw error;
    }
  }

  private buildProxyCommand(config: ProxyConfig): string {
    // This is a simplified example. In a real implementation,
    // you would generate proper Nginx or Traefik configuration
    return `docker service create --name proxy-${config.target} --network ${this.networkConfig.name} --publish ${config.port}:80 nginx`;
  }

  async addPortMapping(mapping: PortMapping): Promise<void> {
    try {
      this.validatePortMapping(mapping);
      this.portMappings.push(mapping);
      this.logger.info(`Added port mapping: ${mapping.hostPort}:${mapping.containerPort}`);
    } catch (error) {
      this.logger.error('Failed to add port mapping', error);
      throw error;
    }
  }

  private validatePortMapping(mapping: PortMapping): void {
    if (mapping.containerPort < 1 || mapping.containerPort > 65535) {
      throw new Error('Invalid container port');
    }
    if (mapping.hostPort < 1 || mapping.hostPort > 65535) {
      throw new Error('Invalid host port');
    }
    if (!['tcp', 'udp'].includes(mapping.protocol)) {
      throw new Error('Invalid protocol');
    }
  }

  async addSecurityRule(rule: SecurityRule): Promise<void> {
    try {
      this.validateSecurityRule(rule);
      this.securityRules.push(rule);
      this.logger.info(`Added security rule: ${rule.description || 'unnamed rule'}`);
    } catch (error) {
      this.logger.error('Failed to add security rule', error);
      throw error;
    }
  }

  private validateSecurityRule(rule: SecurityRule): void {
    if (!['allow', 'deny'].includes(rule.type)) {
      throw new Error('Invalid rule type');
    }
    if (!['tcp', 'udp', 'icmp'].includes(rule.protocol)) {
      throw new Error('Invalid protocol');
    }
    if (!this.isValidIPRange(rule.source)) {
      throw new Error('Invalid source IP range');
    }
    if (!this.isValidIPRange(rule.destination)) {
      throw new Error('Invalid destination IP range');
    }
    if (rule.port && (rule.port < 1 || rule.port > 65535)) {
      throw new Error('Invalid port number');
    }
  }

  private isValidIPRange(ipRange: string): boolean {
    // Basic IP range validation
    const ipRangeRegex = /^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$/;
    return ipRangeRegex.test(ipRange);
  }

  async addProxyConfig(config: ProxyConfig): Promise<void> {
    try {
      this.validateProxyConfig(config);
      this.proxyConfigs.push(config);
      this.logger.info(`Added proxy config for ${config.target}`);
    } catch (error) {
      this.logger.error('Failed to add proxy config', error);
      throw error;
    }
  }

  private validateProxyConfig(config: ProxyConfig): void {
    if (!config.target) {
      throw new Error('Target is required');
    }
    if (config.port < 1 || config.port > 65535) {
      throw new Error('Invalid port number');
    }
    if (config.ssl?.enabled && (!config.ssl.cert || !config.ssl.key)) {
      throw new Error('SSL certificate and key are required when SSL is enabled');
    }
  }

  async cleanup(): Promise<void> {
    try {
      // Remove security rules
      for (const rule of this.securityRules) {
        const command = this.buildSecurityRuleCommand(rule).replace('-A', '-D');
        await execAsync(command);
      }

      // Remove proxy configurations
      for (const config of this.proxyConfigs) {
        await execAsync(`docker service rm proxy-${config.target}`);
      }

      // Remove network
      await execAsync(`docker network rm ${this.networkConfig.name}`);

      this.logger.info('Network cleanup completed');
    } catch (error) {
      this.logger.error('Failed to cleanup network', error);
      throw error;
    }
  }

  private async listNetworks(): Promise<string[]> {
    try {
      const { stdout } = await execAsync('docker network ls --format "{{.Name}}"');
      return stdout.split('\n').filter(Boolean);
    } catch (error) {
      this.logger.error('Failed to list networks', error);
      throw error;
    }
  }
} 