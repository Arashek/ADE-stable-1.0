import { ArchitectureSpec, ArchitectureComponent, ArchitectureConnection } from '../../../frontend/src/services/ArchitectureService';

interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

export class ArchitectureValidator {
  async validateArchitecture(architecture: ArchitectureSpec): Promise<ValidationResult> {
    const errors: string[] = [];

    // Validate required fields
    if (!architecture.id) errors.push('Architecture ID is required');
    if (!architecture.projectId) errors.push('Project ID is required');
    if (!architecture.name) errors.push('Name is required');
    if (!architecture.description) errors.push('Description is required');

    // Validate components array
    if (!Array.isArray(architecture.components)) {
      errors.push('Components must be an array');
    } else {
      // Validate each component
      architecture.components.forEach((component, index) => {
        const componentErrors = this.validateComponent(component);
        componentErrors.forEach(error => {
          errors.push(`Component ${index}: ${error}`);
        });
      });

      // Check for duplicate component IDs
      const componentIds = new Set<string>();
      architecture.components.forEach(component => {
        if (componentIds.has(component.id)) {
          errors.push(`Duplicate component ID: ${component.id}`);
        }
        componentIds.add(component.id);
      });
    }

    // Validate connections array
    if (!Array.isArray(architecture.connections)) {
      errors.push('Connections must be an array');
    } else {
      // Validate each connection
      architecture.connections.forEach((connection, index) => {
        const connectionErrors = this.validateConnection(connection, architecture.components);
        connectionErrors.forEach(error => {
          errors.push(`Connection ${index}: ${error}`);
        });
      });

      // Check for duplicate connection IDs
      const connectionIds = new Set<string>();
      architecture.connections.forEach(connection => {
        if (connectionIds.has(connection.id)) {
          errors.push(`Duplicate connection ID: ${connection.id}`);
        }
        connectionIds.add(connection.id);
      });
    }

    // Validate timestamps
    if (!(architecture.createdAt instanceof Date)) {
      errors.push('CreatedAt must be a valid Date');
    }
    if (!(architecture.updatedAt instanceof Date)) {
      errors.push('UpdatedAt must be a valid Date');
    }

    // Validate status
    const validStatuses = ['draft', 'review', 'approved', 'implemented'];
    if (!validStatuses.includes(architecture.status)) {
      errors.push(`Status must be one of: ${validStatuses.join(', ')}`);
    }

    // Validate feedback if present
    if (architecture.feedback) {
      if (!Array.isArray(architecture.feedback)) {
        errors.push('Feedback must be an array');
      } else {
        architecture.feedback.forEach((feedback, index) => {
          const feedbackErrors = this.validateFeedback(feedback);
          feedbackErrors.forEach(error => {
            errors.push(`Feedback ${index}: ${error}`);
          });
        });
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  private validateComponent(component: ArchitectureComponent): string[] {
    const errors: string[] = [];

    // Validate required fields
    if (!component.id) errors.push('ID is required');
    if (!component.name) errors.push('Name is required');
    if (!component.type) errors.push('Type is required');
    if (!component.description) errors.push('Description is required');

    // Validate position
    if (!this.isValidPosition(component.position)) {
      errors.push('Invalid position coordinates');
    }

    // Validate size
    if (!this.isValidSize(component.size)) {
      errors.push('Invalid size dimensions');
    }

    // Validate style
    if (component.style) {
      const styleErrors = this.validateStyle(component.style);
      styleErrors.forEach(error => {
        errors.push(`Style: ${error}`);
      });
    }

    // Validate properties
    if (component.properties) {
      const propertyErrors = this.validateProperties(component.properties);
      propertyErrors.forEach(error => {
        errors.push(`Properties: ${error}`);
      });
    }

    return errors;
  }

  private validateConnection(
    connection: ArchitectureConnection,
    components: ArchitectureComponent[]
  ): string[] {
    const errors: string[] = [];

    // Validate required fields
    if (!connection.id) errors.push('ID is required');
    if (!connection.sourceId) errors.push('Source ID is required');
    if (!connection.targetId) errors.push('Target ID is required');
    if (!connection.type) errors.push('Type is required');

    // Validate component references
    const sourceComponent = components.find(c => c.id === connection.sourceId);
    const targetComponent = components.find(c => c.id === connection.targetId);

    if (!sourceComponent) {
      errors.push(`Source component not found: ${connection.sourceId}`);
    }
    if (!targetComponent) {
      errors.push(`Target component not found: ${connection.targetId}`);
    }

    // Validate connection type
    const validTypes = ['dependency', 'composition', 'aggregation', 'inheritance'];
    if (!validTypes.includes(connection.type)) {
      errors.push(`Type must be one of: ${validTypes.join(', ')}`);
    }

    // Validate style if present
    if (connection.style) {
      const styleErrors = this.validateStyle(connection.style);
      styleErrors.forEach(error => {
        errors.push(`Style: ${error}`);
      });
    }

    return errors;
  }

  private validateFeedback(feedback: any): string[] {
    const errors: string[] = [];

    // Validate required fields
    if (!feedback.id) errors.push('ID is required');
    if (!feedback.from) errors.push('From is required');
    if (!feedback.comment) errors.push('Comment is required');
    if (!(feedback.timestamp instanceof Date)) {
      errors.push('Timestamp must be a valid Date');
    }

    // Validate status
    const validStatuses = ['pending', 'resolved', 'rejected'];
    if (!validStatuses.includes(feedback.status)) {
      errors.push(`Status must be one of: ${validStatuses.join(', ')}`);
    }

    return errors;
  }

  private isValidPosition(position: { x: number; y: number }): boolean {
    return (
      typeof position === 'object' &&
      typeof position.x === 'number' &&
      typeof position.y === 'number' &&
      position.x >= 0 &&
      position.y >= 0
    );
  }

  private isValidSize(size: { width: number; height: number }): boolean {
    return (
      typeof size === 'object' &&
      typeof size.width === 'number' &&
      typeof size.height === 'number' &&
      size.width > 0 &&
      size.height > 0
    );
  }

  private validateStyle(style: Record<string, any>): string[] {
    const errors: string[] = [];

    // Validate color values
    if (style.color && !this.isValidColor(style.color)) {
      errors.push('Invalid color value');
    }

    // Validate numeric values
    if (style.opacity !== undefined && !this.isValidOpacity(style.opacity)) {
      errors.push('Invalid opacity value');
    }

    // Validate border values
    if (style.borderWidth !== undefined && !this.isValidBorderWidth(style.borderWidth)) {
      errors.push('Invalid border width');
    }

    return errors;
  }

  private validateProperties(properties: Record<string, any>): string[] {
    const errors: string[] = [];

    // Validate required properties based on component type
    if (properties.required !== undefined && !Array.isArray(properties.required)) {
      errors.push('Required properties must be an array');
    }

    // Validate property types
    if (properties.types) {
      Object.entries(properties.types).forEach(([key, value]) => {
        if (!this.isValidPropertyType(value)) {
          errors.push(`Invalid property type for ${key}`);
        }
      });
    }

    return errors;
  }

  private isValidColor(color: string): boolean {
    // Basic color validation
    const colorRegex = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/;
    const namedColors = [
      'black', 'white', 'red', 'green', 'blue', 'yellow', 'purple', 'orange',
      'gray', 'brown', 'pink', 'cyan', 'magenta', 'lime', 'maroon', 'navy',
      'olive', 'teal', 'aqua', 'fuchsia', 'silver'
    ];

    return colorRegex.test(color) || namedColors.includes(color.toLowerCase());
  }

  private isValidOpacity(opacity: number): boolean {
    return typeof opacity === 'number' && opacity >= 0 && opacity <= 1;
  }

  private isValidBorderWidth(width: number): boolean {
    return typeof width === 'number' && width >= 0;
  }

  private isValidPropertyType(type: string): boolean {
    const validTypes = ['string', 'number', 'boolean', 'object', 'array', 'function'];
    return validTypes.includes(type);
  }
} 