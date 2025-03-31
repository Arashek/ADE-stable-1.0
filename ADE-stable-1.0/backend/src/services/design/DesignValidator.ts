import { DesignSpec, DesignComponent } from '../../../frontend/src/services/DesignAgentService';

interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

export class DesignValidator {
  public async validateDesign(design: DesignSpec): Promise<ValidationResult> {
    const errors: string[] = [];

    // Validate basic design properties
    if (!design.id) errors.push('Design ID is required');
    if (!design.projectId) errors.push('Project ID is required');
    if (!design.name) errors.push('Design name is required');
    if (!design.description) errors.push('Design description is required');

    // Validate components
    if (!Array.isArray(design.components)) {
      errors.push('Components must be an array');
    } else {
      // Validate each component
      design.components.forEach((component, index) => {
        const componentErrors = this.validateComponent(component, index);
        errors.push(...componentErrors);
      });
    }

    // Validate dates
    if (!(design.createdAt instanceof Date)) {
      errors.push('Created date must be a valid Date object');
    }
    if (!(design.updatedAt instanceof Date)) {
      errors.push('Updated date must be a valid Date object');
    }

    // Validate status
    const validStatuses = ['draft', 'review', 'approved', 'implemented'];
    if (!validStatuses.includes(design.status)) {
      errors.push(`Invalid status. Must be one of: ${validStatuses.join(', ')}`);
    }

    // Validate feedback if present
    if (design.feedback) {
      if (!Array.isArray(design.feedback)) {
        errors.push('Feedback must be an array');
      } else {
        design.feedback.forEach((feedback, index) => {
          const feedbackErrors = this.validateFeedback(feedback, index);
          errors.push(...feedbackErrors);
        });
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  private validateComponent(component: DesignComponent, index: number): string[] {
    const errors: string[] = [];

    // Validate required properties
    if (!component.id) errors.push(`Component ${index}: ID is required`);
    if (!component.type) errors.push(`Component ${index}: Type is required`);
    if (!component.position) errors.push(`Component ${index}: Position is required`);
    if (!component.size) errors.push(`Component ${index}: Size is required`);

    // Validate type
    const validTypes = ['container', 'button', 'input', 'text', 'image', 'card'];
    if (!validTypes.includes(component.type)) {
      errors.push(`Component ${index}: Invalid type. Must be one of: ${validTypes.join(', ')}`);
    }

    // Validate position
    if (component.position) {
      if (typeof component.position.x !== 'number') {
        errors.push(`Component ${index}: Position X must be a number`);
      }
      if (typeof component.position.y !== 'number') {
        errors.push(`Component ${index}: Position Y must be a number`);
      }
    }

    // Validate size
    if (component.size) {
      if (typeof component.size.width !== 'number' || component.size.width <= 0) {
        errors.push(`Component ${index}: Width must be a positive number`);
      }
      if (typeof component.size.height !== 'number' || component.size.height <= 0) {
        errors.push(`Component ${index}: Height must be a positive number`);
      }
    }

    // Validate style
    if (component.style) {
      const styleErrors = this.validateStyle(component.style, index);
      errors.push(...styleErrors);
    }

    // Validate children for container type
    if (component.type === 'container' && component.children) {
      if (!Array.isArray(component.children)) {
        errors.push(`Component ${index}: Children must be an array for container type`);
      } else {
        component.children.forEach((child, childIndex) => {
          const childErrors = this.validateComponent(child, childIndex);
          errors.push(...childErrors.map(error => `Component ${index} child ${childIndex}: ${error}`));
        });
      }
    }

    return errors;
  }

  private validateStyle(style: React.CSSProperties, componentIndex: number): string[] {
    const errors: string[] = [];

    // Validate numeric values
    Object.entries(style).forEach(([key, value]) => {
      if (typeof value === 'number' && isNaN(value)) {
        errors.push(`Component ${componentIndex}: Invalid style value for ${key}`);
      }
    });

    // Validate color values
    const colorProperties = ['color', 'backgroundColor', 'borderColor'];
    colorProperties.forEach(prop => {
      if (style[prop] && !this.isValidColor(style[prop])) {
        errors.push(`Component ${componentIndex}: Invalid color value for ${prop}`);
      }
    });

    return errors;
  }

  private validateFeedback(feedback: any, index: number): string[] {
    const errors: string[] = [];

    if (!feedback.id) errors.push(`Feedback ${index}: ID is required`);
    if (!feedback.from) errors.push(`Feedback ${index}: From is required`);
    if (!feedback.comment) errors.push(`Feedback ${index}: Comment is required`);
    if (!(feedback.timestamp instanceof Date)) {
      errors.push(`Feedback ${index}: Timestamp must be a valid Date object`);
    }

    const validStatuses = ['pending', 'resolved'];
    if (!validStatuses.includes(feedback.status)) {
      errors.push(`Feedback ${index}: Invalid status. Must be one of: ${validStatuses.join(', ')}`);
    }

    return errors;
  }

  private isValidColor(color: string): boolean {
    // Basic color validation
    const colorRegex = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/;
    const rgbRegex = /^rgb\(\d{1,3},\s*\d{1,3},\s*\d{1,3}\)$/;
    const rgbaRegex = /^rgba\(\d{1,3},\s*\d{1,3},\s*\d{1,3},\s*[0-1](\.[0-9]+)?\)$/;
    const namedColors = [
      'black', 'white', 'red', 'green', 'blue', 'yellow', 'purple', 'orange',
      'gray', 'grey', 'pink', 'brown', 'cyan', 'magenta', 'lime', 'maroon',
      'navy', 'olive', 'teal', 'aqua', 'fuchsia', 'silver'
    ];

    return (
      colorRegex.test(color) ||
      rgbRegex.test(color) ||
      rgbaRegex.test(color) ||
      namedColors.includes(color.toLowerCase())
    );
  }
} 