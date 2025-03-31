import { DesignSpec, DesignComponent } from '../../../frontend/src/services/DesignAgentService';

interface ImplementationResult {
  componentCode: string;
  styles: string;
  dependencies: string[];
}

export class DesignRenderer {
  public async generateImplementation(design: DesignSpec): Promise<ImplementationResult> {
    const { components } = design;
    const dependencies = new Set<string>();
    const componentCode = this.generateComponentCode(components, dependencies);
    const styles = this.generateStyles(components);

    return {
      componentCode,
      styles,
      dependencies: Array.from(dependencies)
    };
  }

  private generateComponentCode(components: DesignComponent[], dependencies: Set<string>): string {
    dependencies.add('react');
    dependencies.add('@mui/material');
    dependencies.add('@emotion/react');
    dependencies.add('@emotion/styled');

    const componentCode = components.map(comp => this.generateComponent(comp)).join('\n\n');

    return `
import React from 'react';
import { styled } from '@mui/material/styles';
${Array.from(dependencies).map(dep => `import ${dep} from '${dep}';`).join('\n')}

${componentCode}

export const Design: React.FC = () => {
  return (
    <DesignContainer>
      ${components.map(comp => `<${comp.type}Component key="${comp.id}" {...${comp.id}Props} />`).join('\n      ')}
    </DesignContainer>
  );
};

export default Design;
    `.trim();
  }

  private generateComponent(component: DesignComponent): string {
    const { id, type, content, style, position, size } = component;

    const props = {
      ...style,
      position: 'absolute',
      left: `${position.x}px`,
      top: `${position.y}px`,
      width: `${size.width}px`,
      height: `${size.height}px`
    };

    const propsString = Object.entries(props)
      .map(([key, value]) => `${key}={${JSON.stringify(value)}}`)
      .join('\n    ');

    const componentProps = `const ${id}Props = {\n  ${propsString}\n};`;

    let componentCode = '';
    switch (type) {
      case 'container':
        componentCode = this.generateContainerComponent(id, component);
        break;
      case 'button':
        componentCode = this.generateButtonComponent(id, content);
        break;
      case 'input':
        componentCode = this.generateInputComponent(id, content);
        break;
      case 'text':
        componentCode = this.generateTextComponent(id, content);
        break;
      case 'image':
        componentCode = this.generateImageComponent(id, content);
        break;
      case 'card':
        componentCode = this.generateCardComponent(id, content);
        break;
    }

    return `${componentProps}\n\n${componentCode}`;
  }

  private generateContainerComponent(id: string, component: DesignComponent): string {
    return `
const ${id}Component = styled('div')({
  display: 'flex',
  flexDirection: 'column',
  position: 'relative'
});

${component.children?.map(child => this.generateComponent(child)).join('\n\n') || ''}
    `.trim();
  }

  private generateButtonComponent(id: string, content: string): string {
    return `
const ${id}Component = styled('button')({
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: '8px 16px',
  background: '#1976d2',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
  '&:hover': {
    background: '#1565c0'
  }
});
    `.trim();
  }

  private generateInputComponent(id: string, content: string): string {
    return `
const ${id}Component = styled('input')({
  padding: '8px',
  border: '1px solid #ccc',
  borderRadius: '4px',
  width: '100%',
  boxSizing: 'border-box'
});
    `.trim();
  }

  private generateTextComponent(id: string, content: string): string {
    return `
const ${id}Component = styled('div')({
  padding: '8px'
});
    `.trim();
  }

  private generateImageComponent(id: string, content: string): string {
    return `
const ${id}Component = styled('img')({
  width: '100%',
  height: '100%',
  objectFit: 'cover'
});
    `.trim();
  }

  private generateCardComponent(id: string, content: string): string {
    return `
const ${id}Component = styled('div')({
  padding: '16px',
  background: 'white',
  borderRadius: '8px',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
});
    `.trim();
  }

  private generateStyles(components: DesignComponent[]): string {
    const styles = components.map(comp => this.generateComponentStyles(comp)).join('\n\n');
    
    return `
/* Design Styles */
${styles}

/* Global Styles */
.DesignContainer {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background: #f5f5f5;
}
    `.trim();
  }

  private generateComponentStyles(component: DesignComponent): string {
    const { id, type, style } = component;
    const styleString = Object.entries(style)
      .map(([key, value]) => `  ${key}: ${value};`)
      .join('\n');

    return `
.${id} {
${styleString}
}
    `.trim();
  }
} 