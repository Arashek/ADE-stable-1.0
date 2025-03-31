const express = require('express');
const { validateRequest } = require('../middleware/validation');
const designController = require('../controllers/designController');
const authMiddleware = require('../middleware/auth');

const router = express.Router();

// Apply authentication middleware to all design routes
router.use(authMiddleware.authenticate);

/**
 * @route GET /api/designs
 * @desc Get all designs for a project
 * @access Private
 */
router.get('/designs', 
  validateRequest({
    query: {
      projectId: { type: 'string', optional: false }
    }
  }),
  designController.getDesigns
);

/**
 * @route GET /api/designs/:id
 * @desc Get a design by ID
 * @access Private
 */
router.get('/designs/:id', designController.getDesignById);

/**
 * @route POST /api/designs
 * @desc Create a new design
 * @access Private
 */
router.post('/designs', 
  validateRequest({
    body: {
      projectId: { type: 'string', optional: false },
      name: { type: 'string', optional: false },
      description: { type: 'string', optional: true },
      components: { type: 'array', optional: true },
      styles: { type: 'array', optional: true },
      pages: { type: 'array', optional: true },
      theme: { type: 'object', optional: true }
    }
  }),
  designController.createDesign
);

/**
 * @route PUT /api/designs/:id
 * @desc Update a design
 * @access Private
 */
router.put('/designs/:id', 
  validateRequest({
    body: {
      name: { type: 'string', optional: true },
      description: { type: 'string', optional: true },
      components: { type: 'array', optional: true },
      styles: { type: 'array', optional: true },
      pages: { type: 'array', optional: true },
      theme: { type: 'object', optional: true },
      metadata: { type: 'object', optional: true },
      currentPage: { type: 'string', optional: true }
    }
  }),
  designController.updateDesign
);

/**
 * @route DELETE /api/designs/:id
 * @desc Delete a design
 * @access Private
 */
router.delete('/designs/:id', designController.deleteDesign);

/**
 * @route POST /api/designs/:id/validate
 * @desc Validate a design
 * @access Private
 */
router.post('/designs/:id/validate', designController.validateDesign);

/**
 * @route POST /api/designs/:id/generate-code
 * @desc Generate code from a design
 * @access Private
 */
router.post('/designs/:id/generate-code', 
  validateRequest({
    body: {
      format: { type: 'string', optional: true }
    }
  }),
  designController.generateCode
);

/**
 * @route POST /api/designs/:id/suggestions
 * @desc Get design improvement suggestions
 * @access Private
 */
router.post('/designs/:id/suggestions', designController.generateSuggestions);

/**
 * @route POST /api/designs/:id/export
 * @desc Export a design to various formats
 * @access Private
 */
router.post('/designs/:id/export',
  validateRequest({
    body: {
      format: { type: 'string', optional: true, default: 'react' }
    }
  }),
  designController.exportDesign
);

module.exports = router;
