import 'reflect-metadata';

// Extend Reflect type to include getMetadata
declare global {
  interface Reflect {
    getMetadata(metadataKey: string, target: any, propertyKey?: string | symbol): any;
  }
}

interface ApiEndpoint {
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  description: string;
  parameters?: {
    name: string;
    type: string;
    required: boolean;
    description: string;
  }[];
  responses?: {
    status: number;
    description: string;
    schema?: Record<string, any>;
  }[];
  examples?: {
    request?: Record<string, any>;
    response?: Record<string, any>;
  }[];
}

interface ComponentDoc {
  name: string;
  description: string;
  props: {
    name: string;
    type: string;
    required: boolean;
    description: string;
    defaultValue?: any;
  }[];
  examples?: {
    title: string;
    code: string;
    description: string;
  }[];
  usage?: string;
}

class Documentation {
  private static instance: Documentation;
  private apiEndpoints: Map<string, ApiEndpoint> = new Map();
  private components: Map<string, ComponentDoc> = new Map();
  private readonly DOCS_PATH = '/docs';

  private constructor() {}

  static getInstance(): Documentation {
    if (!Documentation.instance) {
      Documentation.instance = new Documentation();
    }
    return Documentation.instance;
  }

  // API Documentation
  registerApiEndpoint(endpoint: ApiEndpoint): void {
    const key = `${endpoint.method}:${endpoint.path}`;
    this.apiEndpoints.set(key, endpoint);
  }

  getApiEndpoint(method: string, path: string): ApiEndpoint | undefined {
    return this.apiEndpoints.get(`${method}:${path}`);
  }

  getAllApiEndpoints(): ApiEndpoint[] {
    return Array.from(this.apiEndpoints.values());
  }

  // Component Documentation
  registerComponent(component: ComponentDoc): void {
    this.components.set(component.name, component);
  }

  getComponent(name: string): ComponentDoc | undefined {
    return this.components.get(name);
  }

  getAllComponents(): ComponentDoc[] {
    return Array.from(this.components.values());
  }

  // Documentation Decorator
  static doc(description: string) {
    return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
      const originalMethod = descriptor.value;
      const docs = Documentation.getInstance();

      // Get parameter types from metadata or function signature
      const paramTypes = Reflect.getMetadata('design:paramtypes', target, propertyKey) || [];
      const paramNames = originalMethod.toString()
        .match(/\(([^)]*)\)/)?.[1]
        .split(',')
        .map((param: string) => param.trim())
        .filter(Boolean) || [];

      // Create parameter documentation
      const parameters = paramTypes.map((type: any, index: number) => ({
        name: paramNames[index] || `param${index + 1}`,
        type: type.name || 'any',
        required: true,
        description: `Parameter of type ${type.name || 'any'}`,
      }));

      // Register the documentation
      docs.registerApiEndpoint({
        path: `/${propertyKey.toLowerCase()}`,
        method: 'POST',
        description,
        parameters,
      });

      return descriptor;
    };
  }

  // Generate Markdown Documentation
  generateMarkdown(): string {
    let markdown = '# ADE Platform Documentation\n\n';

    // API Documentation
    markdown += '## API Endpoints\n\n';
    this.getAllApiEndpoints().forEach(endpoint => {
      markdown += `### ${endpoint.method} ${endpoint.path}\n\n`;
      markdown += `${endpoint.description}\n\n`;

      if (endpoint.parameters?.length) {
        markdown += '#### Parameters\n\n';
        markdown += '| Name | Type | Required | Description |\n';
        markdown += '|------|------|----------|-------------|\n';
        endpoint.parameters.forEach(param => {
          markdown += `| ${param.name} | ${param.type} | ${param.required} | ${param.description} |\n`;
        });
        markdown += '\n';
      }

      if (endpoint.examples?.length) {
        markdown += '#### Examples\n\n';
        endpoint.examples.forEach(example => {
          if (example.request) {
            markdown += 'Request:\n```json\n';
            markdown += JSON.stringify(example.request, null, 2);
            markdown += '\n```\n\n';
          }
          if (example.response) {
            markdown += 'Response:\n```json\n';
            markdown += JSON.stringify(example.response, null, 2);
            markdown += '\n```\n\n';
          }
        });
      }
    });

    // Component Documentation
    markdown += '## Components\n\n';
    this.getAllComponents().forEach(component => {
      markdown += `### ${component.name}\n\n`;
      markdown += `${component.description}\n\n`;

      if (component.props?.length) {
        markdown += '#### Props\n\n';
        markdown += '| Name | Type | Required | Default | Description |\n';
        markdown += '|------|------|----------|---------|-------------|\n';
        component.props.forEach(prop => {
          markdown += `| ${prop.name} | ${prop.type} | ${prop.required} | ${prop.defaultValue || '-'} | ${prop.description} |\n`;
        });
        markdown += '\n';
      }

      if (component.examples?.length) {
        markdown += '#### Examples\n\n';
        component.examples.forEach(example => {
          markdown += `##### ${example.title}\n\n`;
          markdown += `${example.description}\n\n`;
          markdown += '```tsx\n';
          markdown += example.code;
          markdown += '\n```\n\n';
        });
      }
    });

    return markdown;
  }

  // Save documentation to file
  async saveDocumentation(): Promise<void> {
    try {
      const markdown = this.generateMarkdown();
      await fetch(`${this.DOCS_PATH}/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ markdown }),
      });
    } catch (error) {
      console.error('Failed to save documentation:', error);
    }
  }
}

// Create a singleton instance
export const documentation = Documentation.getInstance();

// Example usage:
/*
// API Documentation
@Documentation.doc('Generate code from design')
async generateCode(design: Design): Promise<Code> {
  // Implementation
}

// Component Documentation
documentation.registerComponent({
  name: 'CommandHub',
  description: 'Main component for handling user commands and interactions',
  props: [
    {
      name: 'onSave',
      type: '(design: Design) => void',
      required: true,
      description: 'Callback function when design is saved',
    },
    // ... more props
  ],
  examples: [
    {
      title: 'Basic Usage',
      description: 'Using CommandHub with basic props',
      code: `
        <CommandHub
          onSave={handleSave}
          onGenerateCode={handleGenerateCode}
        />
      `,
    },
    // ... more examples
  ],
});
*/ 