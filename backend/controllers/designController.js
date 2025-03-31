const Design = require('../models/Design');
const Project = require('../models/Project');
const ValidationAgent = require('../services/agents/specialized/validation_agent');
const DesignAgent = require('../services/agents/specialized/design_agent');
const CodeAgent = require('../services/agents/specialized/code_agent');
const logger = require('../utils/logger');

/**
 * Get all designs for a project
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.getDesigns = async (req, res) => {
  try {
    const { projectId } = req.query;
    
    // Check if project exists and user has access
    const project = await Project.findById(projectId);
    if (!project) {
      return res.status(404).json({ message: 'Project not found' });
    }
    
    // Verify user has access to this project
    if (!project.members.includes(req.user.id) && project.owner !== req.user.id) {
      return res.status(403).json({ message: 'Access denied' });
    }
    
    const designs = await Design.find({ projectId });
    res.json(designs);
  } catch (error) {
    logger.error('Error getting designs:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

/**
 * Get a design by ID
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.getDesignById = async (req, res) => {
  try {
    const design = await Design.findById(req.params.id);
    
    if (!design) {
      return res.status(404).json({ message: 'Design not found' });
    }
    
    // Check if project exists and user has access
    const project = await Project.findById(design.projectId);
    if (!project) {
      return res.status(404).json({ message: 'Project not found' });
    }
    
    // Verify user has access to this project
    if (!project.members.includes(req.user.id) && project.owner !== req.user.id) {
      return res.status(403).json({ message: 'Access denied' });
    }
    
    res.json(design);
  } catch (error) {
    logger.error('Error getting design:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

/**
 * Create a new design
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.createDesign = async (req, res) => {
  try {
    const { projectId, name, description, components, styles, pages, theme } = req.body;
    
    // Check if project exists and user has access
    const project = await Project.findById(projectId);
    if (!project) {
      return res.status(404).json({ message: 'Project not found' });
    }
    
    // Verify user has access to this project
    if (!project.members.includes(req.user.id) && project.owner !== req.user.id) {
      return res.status(403).json({ message: 'Access denied' });
    }
    
    // Create default metadata
    const metadata = {
      name: name,
      description: description || '',
      version: '1.0.0',
      lastModified: new Date().toISOString(),
      createdBy: req.user.id,
      showGrid: true,
      snapToGrid: true,
      gridSize: 8,
      snapThreshold: 4,
      exportWithComments: true,
      exportWithStyles: true
    };
    
    // Create a new design
    const newDesign = new Design({
      projectId,
      name,
      description,
      components: components || [],
      styles: styles || [],
      pages: pages || [],
      theme: theme || {
        colors: {
          primary: '#1976d2',
          secondary: '#dc004e',
          background: '#f5f5f5',
          surface: '#ffffff',
          error: '#f44336',
          text: '#212121',
          textSecondary: '#757575'
        },
        typography: {
          fontFamily: 'Roboto, "Helvetica Neue", Arial, sans-serif',
          fontSize: 16
        },
        spacing: {
          unit: 8
        }
      },
      metadata,
      currentPage: pages && pages.length > 0 ? pages[0].id : null,
      version: '1.0.0',
      createdBy: req.user.id
    });
    
    await newDesign.save();
    res.status(201).json(newDesign);
  } catch (error) {
    logger.error('Error creating design:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

/**
 * Update a design
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.updateDesign = async (req, res) => {
  try {
    const design = await Design.findById(req.params.id);
    
    if (!design) {
      return res.status(404).json({ message: 'Design not found' });
    }
    
    // Check if project exists and user has access
    const project = await Project.findById(design.projectId);
    if (!project) {
      return res.status(404).json({ message: 'Project not found' });
    }
    
    // Verify user has access to this project
    if (!project.members.includes(req.user.id) && project.owner !== req.user.id) {
      return res.status(403).json({ message: 'Access denied' });
    }
    
    const updates = req.body;
    
    // Update metadata if present in request
    if (updates.metadata) {
      updates.metadata.lastModified = new Date().toISOString();
    } else {
      // Create metadata if not present in the design or request
      if (!design.metadata) {
        updates.metadata = {
          name: design.name,
          description: design.description || '',
          version: '1.0.0',
          lastModified: new Date().toISOString(),
          createdBy: design.createdBy || req.user.id,
          showGrid: true,
          snapToGrid: true,
          gridSize: 8,
          snapThreshold: 4,
          exportWithComments: true,
          exportWithStyles: true
        };
      } else {
        updates.metadata = {
          ...design.metadata,
          lastModified: new Date().toISOString()
        };
      }
    }
    
    // Update design with new values
    const updatedDesign = await Design.findByIdAndUpdate(
      req.params.id,
      { $set: updates },
      { new: true, runValidators: true }
    );
    
    res.json(updatedDesign);
  } catch (error) {
    logger.error('Error updating design:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

/**
 * Delete a design
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.deleteDesign = async (req, res) => {
  try {
    const design = await Design.findById(req.params.id);
    
    if (!design) {
      return res.status(404).json({ message: 'Design not found' });
    }
    
    // Check if project exists and user has access
    const project = await Project.findById(design.projectId);
    if (!project) {
      return res.status(404).json({ message: 'Project not found' });
    }
    
    // Verify user has access to this project and is either owner or admin
    if (project.owner !== req.user.id && 
        !(project.members.includes(req.user.id) && req.user.role === 'admin')) {
      return res.status(403).json({ message: 'Access denied' });
    }
    
    await Design.findByIdAndDelete(req.params.id);
    res.json({ message: 'Design deleted successfully' });
  } catch (error) {
    logger.error('Error deleting design:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

/**
 * Validate a design
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.validateDesign = async (req, res) => {
  try {
    const design = await Design.findById(req.params.id);
    
    if (!design) {
      return res.status(404).json({ message: 'Design not found' });
    }
    
    // Check if project exists and user has access
    const project = await Project.findById(design.projectId);
    if (!project) {
      return res.status(404).json({ message: 'Project not found' });
    }
    
    // Verify user has access to this project
    if (!project.members.includes(req.user.id) && project.owner !== req.user.id) {
      return res.status(403).json({ message: 'Access denied' });
    }
    
    // Use the validation agent to check the design
    const validationAgent = new ValidationAgent();
    const validationResult = await validationAgent.validateDesign(design);
    
    res.json(validationResult);
  } catch (error) {
    logger.error('Error validating design:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

/**
 * Generate code from a design
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.generateCode = async (req, res) => {
  try {
    const design = await Design.findById(req.params.id);
    
    if (!design) {
      return res.status(404).json({ message: 'Design not found' });
    }
    
    // Check if project exists and user has access
    const project = await Project.findById(design.projectId);
    if (!project) {
      return res.status(404).json({ message: 'Project not found' });
    }
    
    // Verify user has access to this project
    if (!project.members.includes(req.user.id) && project.owner !== req.user.id) {
      return res.status(403).json({ message: 'Access denied' });
    }
    
    // Use the code agent to generate code from the design
    const codeAgent = new CodeAgent();
    const format = req.body.format || 'react';
    const generatedCode = await codeAgent.generateFromDesign(design, format);
    
    res.json({ code: generatedCode });
  } catch (error) {
    logger.error('Error generating code:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

/**
 * Generate design improvement suggestions
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.generateSuggestions = async (req, res) => {
  try {
    const design = await Design.findById(req.params.id);
    
    if (!design) {
      return res.status(404).json({ message: 'Design not found' });
    }
    
    // Check if project exists and user has access
    const project = await Project.findById(design.projectId);
    if (!project) {
      return res.status(404).json({ message: 'Project not found' });
    }
    
    // Verify user has access to this project
    if (!project.members.includes(req.user.id) && project.owner !== req.user.id) {
      return res.status(403).json({ message: 'Access denied' });
    }
    
    // Use the design agent to generate suggestions
    const designAgent = new DesignAgent();
    const suggestions = await designAgent.generateSuggestions(design);
    
    res.json(suggestions);
  } catch (error) {
    logger.error('Error generating suggestions:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

/**
 * Export a design to various formats
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.exportDesign = async (req, res) => {
  try {
    const design = await Design.findById(req.params.id);
    
    if (!design) {
      return res.status(404).json({ message: 'Design not found' });
    }
    
    // Check if project exists and user has access
    const project = await Project.findById(design.projectId);
    if (!project) {
      return res.status(404).json({ message: 'Project not found' });
    }
    
    // Verify user has access to this project
    if (!project.members.includes(req.user.id) && project.owner !== req.user.id) {
      return res.status(403).json({ message: 'Access denied' });
    }
    
    const format = req.body.format || 'react';
    let exportedCode;
    
    // Use the appropriate agent based on the format
    const codeAgent = new CodeAgent();
    exportedCode = await codeAgent.exportDesign(design, format);
    
    res.json({ 
      exportedCode,
      format 
    });
  } catch (error) {
    logger.error('Error exporting design:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};
