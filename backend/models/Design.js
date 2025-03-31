const mongoose = require('mongoose');
const Schema = mongoose.Schema;

// Schema for design component
const DesignComponentSchema = new Schema({
  id: {
    type: String,
    required: true
  },
  name: {
    type: String,
    required: true
  },
  type: {
    type: String,
    required: true
  },
  properties: {
    type: Map,
    of: Schema.Types.Mixed,
    default: {}
  },
  styles: {
    type: Map,
    of: String,
    default: {}
  },
  pageId: {
    type: String
  },
  parentId: {
    type: String
  },
  children: {
    type: [String],
    default: []
  }
});

// Schema for design style
const DesignStyleSchema = new Schema({
  id: {
    type: String,
    required: true
  },
  name: {
    type: String,
    required: true
  },
  type: {
    type: String,
    enum: ['FILL', 'TEXT', 'EFFECT', 'GRID'],
    required: true
  },
  value: {
    type: String,
    required: true
  },
  scope: {
    type: String,
    enum: ['global', 'page', 'component'],
    required: true
  },
  targetId: {
    type: String
  }
});

// Schema for design page
const DesignPageSchema = new Schema({
  id: {
    type: String,
    required: true
  },
  name: {
    type: String,
    required: true
  },
  path: {
    type: String,
    required: true
  },
  components: {
    type: [String],
    default: []
  },
  styles: {
    type: [String],
    default: []
  },
  layout: {
    type: {
      type: String,
      required: true
    },
    properties: {
      type: Map,
      of: Schema.Types.Mixed,
      default: {}
    }
  }
});

// Schema for design implementation
const DesignImplementationSchema = new Schema({
  components: {
    type: [{
      id: String,
      code: String,
      dependencies: [String]
    }],
    default: []
  },
  styles: {
    type: [{
      id: String,
      code: String,
      dependencies: [String]
    }],
    default: []
  },
  pages: {
    type: [{
      id: String,
      code: String,
      dependencies: [String]
    }],
    default: []
  },
  layout: {
    type: {
      type: String
    },
    components: [String]
  }
});

// Schema for design theme
const DesignThemeSchema = new Schema({
  colors: {
    primary: String,
    secondary: String,
    background: String,
    surface: String,
    error: String,
    text: String,
    textSecondary: String
  },
  typography: {
    fontFamily: String,
    fontSize: Number,
    h1: {
      fontSize: String,
      fontWeight: Number,
      lineHeight: Number,
      letterSpacing: String
    },
    h2: {
      fontSize: String,
      fontWeight: Number,
      lineHeight: Number,
      letterSpacing: String
    },
    h3: {
      fontSize: String,
      fontWeight: Number,
      lineHeight: Number,
      letterSpacing: String
    },
    body: {
      fontSize: String,
      fontWeight: Number,
      lineHeight: Number,
      letterSpacing: String
    }
  },
  spacing: {
    unit: Number,
    xs: Number,
    sm: Number,
    md: Number,
    lg: Number,
    xl: Number
  },
  borderRadius: {
    sm: Number,
    md: Number,
    lg: Number
  },
  breakpoints: {
    xs: Number,
    sm: Number,
    md: Number,
    lg: Number,
    xl: Number
  },
  shadows: [String],
  transitions: {
    duration: {
      short: Number,
      standard: Number,
      complex: Number
    },
    easing: {
      easeIn: String,
      easeOut: String,
      easeInOut: String
    }
  }
});

// Schema for design metadata
const DesignMetadataSchema = new Schema({
  name: {
    type: String,
    required: true
  },
  description: {
    type: String
  },
  version: {
    type: String,
    required: true
  },
  lastModified: {
    type: String,
    required: true
  },
  createdBy: {
    type: String,
    required: true
  },
  zoom: {
    type: Number,
    default: 1
  },
  showGrid: {
    type: Boolean,
    default: true
  },
  snapToGrid: {
    type: Boolean,
    default: true
  },
  gridSize: {
    type: Number,
    default: 8
  },
  snapThreshold: {
    type: Number,
    default: 4
  },
  exportWithComments: {
    type: Boolean,
    default: true
  },
  exportWithStyles: {
    type: Boolean,
    default: true
  },
  integrations: {
    figma: {
      enabled: {
        type: Boolean,
        default: false
      },
      token: String
    }
  }
});

// Main Design schema
const DesignSchema = new Schema({
  id: {
    type: String,
    default: () => new mongoose.Types.ObjectId().toString()
  },
  projectId: {
    type: Schema.Types.ObjectId,
    ref: 'Project',
    required: true
  },
  name: {
    type: String,
    required: true
  },
  description: {
    type: String
  },
  components: {
    type: [DesignComponentSchema],
    default: []
  },
  styles: {
    type: [DesignStyleSchema],
    default: []
  },
  pages: {
    type: [DesignPageSchema],
    default: []
  },
  implementation: {
    type: DesignImplementationSchema,
    default: {}
  },
  metadata: {
    type: DesignMetadataSchema,
    required: true
  },
  currentPage: {
    type: String
  },
  theme: {
    type: DesignThemeSchema,
    required: true
  },
  version: {
    type: String,
    required: true,
    default: '1.0.0'
  },
  createdBy: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, { timestamps: true });

// Pre-save hook to ensure the ID is set if not provided
DesignSchema.pre('save', function(next) {
  if (!this.id) {
    this.id = new mongoose.Types.ObjectId().toString();
  }
  next();
});

module.exports = mongoose.model('Design', DesignSchema);
