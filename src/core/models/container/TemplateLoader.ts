import { ContainerTemplate, ProjectType } from './types';
import { Logger } from '../logging/Logger';
import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';

export class TemplateLoader {
  private logger: Logger;
  private templateDir: string;
  private templates: Map<ProjectType, ContainerTemplate>;

  constructor(templateDir: string = path.join(__dirname, 'templates')) {
    this.logger = new Logger('TemplateLoader');
    this.templateDir = templateDir;
    this.templates = new Map();
  }

  async loadTemplates(): Promise<ContainerTemplate[]> {
    try {
      this.logger.info(`Loading templates from ${this.templateDir}`);
      
      // Read all YAML files from the template directory
      const files = await fs.promises.readdir(this.templateDir);
      const yamlFiles = files.filter(file => file.endsWith('.yaml'));
      
      const templates: ContainerTemplate[] = [];
      
      for (const file of yamlFiles) {
        try {
          const template = await this.loadTemplateFile(file);
          templates.push(template);
          this.templates.set(template.projectType, template);
          this.logger.info(`Loaded template: ${template.name}`);
        } catch (error) {
          this.logger.error(`Failed to load template from ${file}`, error);
        }
      }
      
      return templates;
    } catch (error) {
      this.logger.error('Failed to load templates', error);
      throw error;
    }
  }

  private async loadTemplateFile(filename: string): Promise<ContainerTemplate> {
    const filePath = path.join(this.templateDir, filename);
    const content = await fs.promises.readFile(filePath, 'utf8');
    const template = yaml.load(content) as ContainerTemplate;
    
    // Validate template
    this.validateTemplate(template);
    
    return template;
  }

  private validateTemplate(template: ContainerTemplate): void {
    const requiredFields = [
      'id',
      'name',
      'projectType',
      'baseImage',
      'defaultResources',
      'description',
      'tags'
    ];

    for (const field of requiredFields) {
      if (!(field in template)) {
        throw new Error(`Template is missing required field: ${field}`);
      }
    }

    // Validate resource limits
    if (template.defaultResources) {
      this.validateResources(template.defaultResources);
    }

    // Validate environment variables
    if (template.defaultEnvironment) {
      this.validateEnvironmentVariables(template.defaultEnvironment);
    }

    // Validate ports
    if (template.defaultPorts) {
      this.validatePorts(template.defaultPorts);
    }

    // Validate volumes
    if (template.defaultVolumes) {
      this.validateVolumes(template.defaultVolumes);
    }

    // Validate networks
    if (template.defaultNetworks) {
      this.validateNetworks(template.defaultNetworks);
    }
  }

  private validateResources(resources: any): void {
    const requiredResourceFields = ['cpu', 'memory', 'disk'];
    
    for (const field of requiredResourceFields) {
      if (!(field in resources)) {
        throw new Error(`Resources missing required field: ${field}`);
      }
    }

    // Validate CPU limits
    if (resources.cpu.limit <= 0 || resources.cpu.reservation <= 0) {
      throw new Error('CPU limits and reservations must be positive numbers');
    }

    // Validate memory format
    if (!this.isValidMemoryString(resources.memory.limit) || 
        !this.isValidMemoryString(resources.memory.reservation)) {
      throw new Error('Invalid memory format. Use format: <number><unit> (e.g., 4g)');
    }

    // Validate disk format
    if (!this.isValidMemoryString(resources.disk.limit) || 
        !this.isValidMemoryString(resources.disk.reservation)) {
      throw new Error('Invalid disk format. Use format: <number><unit> (e.g., 20g)');
    }
  }

  private validateEnvironmentVariables(env: any[]): void {
    for (const variable of env) {
      if (!variable.name || !variable.value) {
        throw new Error('Environment variables must have name and value');
      }
    }
  }

  private validatePorts(ports: any[]): void {
    for (const port of ports) {
      if (!port.hostPort || !port.containerPort || !port.protocol) {
        throw new Error('Ports must have hostPort, containerPort, and protocol');
      }
      if (!['tcp', 'udp'].includes(port.protocol)) {
        throw new Error('Port protocol must be either tcp or udp');
      }
    }
  }

  private validateVolumes(volumes: any[]): void {
    for (const volume of volumes) {
      if (!volume.source || !volume.target || !volume.type) {
        throw new Error('Volumes must have source, target, and type');
      }
      if (!['bind', 'volume', 'tmpfs'].includes(volume.type)) {
        throw new Error('Volume type must be either bind, volume, or tmpfs');
      }
    }
  }

  private validateNetworks(networks: any[]): void {
    for (const network of networks) {
      if (!network.name || !network.driver) {
        throw new Error('Networks must have name and driver');
      }
    }
  }

  private isValidMemoryString(memory: string): boolean {
    return /^\d+[bkmg]$/i.test(memory);
  }

  getTemplate(projectType: ProjectType): ContainerTemplate | undefined {
    return this.templates.get(projectType);
  }

  getAllTemplates(): ContainerTemplate[] {
    return Array.from(this.templates.values());
  }

  async saveTemplate(template: ContainerTemplate): Promise<void> {
    try {
      const filename = `${template.id}.yaml`;
      const filePath = path.join(this.templateDir, filename);
      const content = yaml.dump(template);
      await fs.promises.writeFile(filePath, content);
      this.templates.set(template.projectType, template);
      this.logger.info(`Saved template: ${template.name}`);
    } catch (error) {
      this.logger.error(`Failed to save template ${template.name}`, error);
      throw error;
    }
  }

  async deleteTemplate(projectType: ProjectType): Promise<void> {
    const template = this.templates.get(projectType);
    if (template) {
      try {
        const filename = `${template.id}.yaml`;
        const filePath = path.join(this.templateDir, filename);
        await fs.promises.unlink(filePath);
        this.templates.delete(projectType);
        this.logger.info(`Deleted template: ${template.name}`);
      } catch (error) {
        this.logger.error(`Failed to delete template ${template.name}`, error);
        throw error;
      }
    }
  }
} 