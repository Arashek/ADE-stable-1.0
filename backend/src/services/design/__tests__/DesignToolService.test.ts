import { DesignToolService } from '../DesignToolService';
import { DesignTool } from '../../../../frontend/src/services/InteractiveDesignService';

describe('DesignToolService', () => {
  let service: DesignToolService;

  beforeEach(() => {
    service = new DesignToolService();
  });

  describe('getTool', () => {
    it('should return a tool by id', () => {
      const tool = service.getTool('rectangle');
      expect(tool).toBeDefined();
      expect(tool?.id).toBe('rectangle');
    });

    it('should return undefined for non-existent tool', () => {
      const tool = service.getTool('non-existent');
      expect(tool).toBeUndefined();
    });
  });

  describe('getAllTools', () => {
    it('should return all tools', () => {
      const tools = service.getAllTools();
      expect(tools.length).toBeGreaterThan(0);
      expect(tools.every(tool => tool.id)).toBe(true);
    });
  });

  describe('getToolsByType', () => {
    it('should return tools of a specific type', () => {
      const shapeTools = service.getToolsByType('shape');
      expect(shapeTools.length).toBeGreaterThan(0);
      expect(shapeTools.every(tool => tool.type === 'shape')).toBe(true);
    });
  });

  describe('addTool', () => {
    it('should add a new tool', () => {
      const newTool: DesignTool = {
        id: 'custom-tool',
        name: 'Custom Tool',
        type: 'shape',
        icon: 'custom',
        description: 'A custom tool',
        properties: [],
      };

      service.addTool(newTool);
      const tool = service.getTool('custom-tool');
      expect(tool).toBeDefined();
      expect(tool?.id).toBe('custom-tool');
    });
  });

  describe('updateTool', () => {
    it('should update an existing tool', () => {
      const updates = {
        name: 'Updated Rectangle',
        description: 'Updated description',
      };

      service.updateTool('rectangle', updates);
      const tool = service.getTool('rectangle');
      expect(tool?.name).toBe('Updated Rectangle');
      expect(tool?.description).toBe('Updated description');
    });

    it('should not update non-existent tool', () => {
      const updates = {
        name: 'Updated Tool',
      };

      service.updateTool('non-existent', updates);
      const tool = service.getTool('non-existent');
      expect(tool).toBeUndefined();
    });
  });

  describe('removeTool', () => {
    it('should remove an existing tool', () => {
      service.removeTool('rectangle');
      const tool = service.getTool('rectangle');
      expect(tool).toBeUndefined();
    });
  });

  describe('validateToolProperties', () => {
    it('should validate color properties', () => {
      const properties = {
        fill: '#FF0000',
        stroke: '#00FF00',
      };

      expect(service.validateToolProperties('rectangle', properties)).toBe(true);
    });

    it('should reject invalid color properties', () => {
      const properties = {
        fill: 'invalid-color',
        stroke: '#00FF00',
      };

      expect(service.validateToolProperties('rectangle', properties)).toBe(false);
    });

    it('should validate number properties', () => {
      const properties = {
        strokeWidth: 5,
        cornerRadius: 10,
      };

      expect(service.validateToolProperties('rectangle', properties)).toBe(true);
    });

    it('should reject invalid number properties', () => {
      const properties = {
        strokeWidth: -1,
        cornerRadius: 100,
      };

      expect(service.validateToolProperties('rectangle', properties)).toBe(false);
    });

    it('should validate select properties', () => {
      const properties = {
        fontFamily: 'Arial',
        fontWeight: 'bold',
      };

      expect(service.validateToolProperties('text', properties)).toBe(true);
    });

    it('should reject invalid select properties', () => {
      const properties = {
        fontFamily: 'Invalid Font',
        fontWeight: 'invalid-weight',
      };

      expect(service.validateToolProperties('text', properties)).toBe(false);
    });

    it('should validate boolean properties', () => {
      const properties = {
        shadow: true,
      };

      expect(service.validateToolProperties('style', properties)).toBe(true);
    });

    it('should reject invalid boolean properties', () => {
      const properties = {
        shadow: 'not-a-boolean',
      };

      expect(service.validateToolProperties('style', properties)).toBe(false);
    });

    it('should validate slider properties', () => {
      const properties = {
        opacity: 0.5,
      };

      expect(service.validateToolProperties('style', properties)).toBe(true);
    });

    it('should reject invalid slider properties', () => {
      const properties = {
        opacity: 2,
      };

      expect(service.validateToolProperties('style', properties)).toBe(false);
    });
  });

  describe('getDefaultProperties', () => {
    it('should return default properties for a tool', () => {
      const defaults = service.getDefaultProperties('rectangle');
      expect(defaults).toBeDefined();
      expect(defaults.fill).toBe('#ffffff');
      expect(defaults.stroke).toBe('#000000');
      expect(defaults.strokeWidth).toBe(2);
      expect(defaults.cornerRadius).toBe(0);
    });

    it('should return empty object for non-existent tool', () => {
      const defaults = service.getDefaultProperties('non-existent');
      expect(defaults).toEqual({});
    });
  });
}); 