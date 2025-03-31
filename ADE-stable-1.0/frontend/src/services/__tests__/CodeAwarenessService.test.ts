import { Socket } from 'socket.io-client';
import { DefaultEventsMap } from 'socket.io/dist/typed-events';
import { CodeAwarenessService, CodeNode, CodeEdge, AgentContext, ErrorContext, ProjectInsights, CollaborativeUpdate, Task, TaskAnalysis, ErrorAnalysisIntegration, AgentSystemIntegration, ProjectAwarenessIntegration } from '../CodeAwarenessService';
import * as monaco from 'monaco-editor';

describe('CodeAwarenessService', () => {
  let mockSocket: jest.Mocked<Socket<DefaultEventsMap, DefaultEventsMap>>;
  let mockEditor: jest.Mocked<monaco.editor.IStandaloneCodeEditor>;
  let service: CodeAwarenessService;
  let mockOnNodeClick: jest.Mock;
  let mockOnEdgeClick: jest.Mock;

  beforeEach(() => {
    mockSocket = {
      emit: jest.fn(),
      on: jest.fn(),
      off: jest.fn(),
    } as unknown as jest.Mocked<Socket<DefaultEventsMap, DefaultEventsMap>>;

    mockEditor = {
      onDidChangeModelContent: jest.fn(),
      getModel: jest.fn(),
    } as unknown as jest.Mocked<monaco.editor.IStandaloneCodeEditor>;

    mockOnNodeClick = jest.fn();
    mockOnEdgeClick = jest.fn();

    service = new CodeAwarenessService({
      ws: mockSocket,
      editor: mockEditor,
      onNodeClick: mockOnNodeClick,
      onEdgeClick: mockOnEdgeClick,
    });
  });

  afterEach(() => {
    service.dispose();
  });

  it('should initialize with correct configuration', () => {
    expect(mockSocket.on).toHaveBeenCalledWith('fileChanged', expect.any(Function));
    expect(mockSocket.on).toHaveBeenCalledWith('dependenciesChanged', expect.any(Function));
    expect(mockSocket.on).toHaveBeenCalledWith('analysisUpdated', expect.any(Function));
    expect(mockEditor.onDidChangeModelContent).toHaveBeenCalledWith(expect.any(Function));
  });

  it('should request initial code analysis', () => {
    expect(mockSocket.emit).toHaveBeenCalledWith('requestCodeAnalysis', {}, expect.any(Function));
  });

  it('should handle code analysis updates', () => {
    const mockNode: CodeNode = {
      id: '1',
      type: 'file',
      name: 'test.ts',
      path: '/test/test.ts',
      dependencies: [],
      metrics: {
        complexity: 1,
        lines: 10,
        dependencies: 0,
        coverage: 80,
        maintainability: 70,
        cognitiveComplexity: 2,
        cyclomaticComplexity: 1,
        halsteadVolume: 100,
        halsteadDifficulty: 1,
        halsteadEffort: 100,
        halsteadTime: 1,
        halsteadBugs: 0,
      },
      relationships: {
        imports: ['other.ts'],
        exports: ['main'],
        extends: [],
        implements: [],
        uses: ['other.ts'],
        usedBy: ['main.ts'],
      },
      context: {
        namespace: 'test',
        module: 'test.ts',
        scope: 'module',
        visibility: 'public',
      },
      analysis: {
        patterns: ['singleton'],
        smells: ['long method'],
        vulnerabilities: [],
        suggestions: ['consider splitting method'],
        documentation: 'Test file',
        lastModified: new Date(),
        contributors: ['user1'],
        gitHistory: [{
          commit: 'abc123',
          author: 'user1',
          date: new Date(),
          changes: ['initial commit'],
        }],
      },
    };

    const mockEdge: CodeEdge = {
      from: '1',
      to: '2',
      type: 'import',
      weight: 1,
      metadata: {
        lineNumber: 1,
        context: 'import statement',
        strength: 1,
        bidirectional: false,
      },
    };

    const mockCallback = mockSocket.emit.mock.calls[0][2];
    if (mockCallback) {
      mockCallback({ nodes: [mockNode], edges: [mockEdge] });
    }

    const node = service.getNodeInfo('1');
    expect(node).toBeDefined();
    expect(node?.metrics.cognitiveComplexity).toBe(2);
    expect(node?.relationships.imports).toContain('other.ts');
    expect(node?.analysis.patterns).toContain('singleton');
  });

  it('should handle file changes', () => {
    const mockModel = {
      getValue: jest.fn().mockReturnValue('test content'),
      uri: { path: '/test/test.ts' },
    };

    mockEditor.getModel = jest.fn().mockReturnValue(mockModel as unknown as monaco.editor.ITextModel);

    service['updateEditorCodeAnalysis']();

    expect(mockSocket.emit).toHaveBeenCalledWith('analyzeCode', {
      path: '/test/test.ts',
      content: 'test content',
    }, expect.any(Function));
  });

  it('should handle dependency updates', () => {
    const mockNode: CodeNode = {
      id: '1',
      type: 'file',
      name: 'test.ts',
      path: '/test/test.ts',
      dependencies: [],
      metrics: {
        complexity: 1,
        lines: 10,
        dependencies: 0,
        coverage: 80,
        maintainability: 70,
        cognitiveComplexity: 2,
        cyclomaticComplexity: 1,
        halsteadVolume: 100,
        halsteadDifficulty: 1,
        halsteadEffort: 100,
        halsteadTime: 1,
        halsteadBugs: 0,
      },
      relationships: {
        imports: [],
        exports: [],
        extends: [],
        implements: [],
        uses: [],
        usedBy: [],
      },
      context: {
        namespace: 'test',
        module: 'test.ts',
        scope: 'module',
        visibility: 'public',
      },
      analysis: {
        patterns: [],
        smells: [],
        vulnerabilities: [],
        suggestions: [],
        documentation: '',
        lastModified: new Date(),
        contributors: [],
        gitHistory: [],
      },
    };

    service['updateNodeDependencies']('/test/test.ts', ['other.ts']);

    const node = service.getNodeInfo('1');
    expect(node?.dependencies).toContain('other.ts');
  });

  it('should handle analysis updates', () => {
    const mockAnalysis = {
      patterns: ['singleton'],
      smells: ['long method'],
      vulnerabilities: [],
      suggestions: ['consider splitting method'],
      documentation: 'Updated documentation',
      lastModified: new Date(),
      contributors: ['user1', 'user2'],
      gitHistory: [{
        commit: 'abc123',
        author: 'user1',
        date: new Date(),
        changes: ['initial commit'],
      }],
    };

    service['updateNodeAnalysis']('/test/test.ts', mockAnalysis);

    const cachedAnalysis = service.getAnalysisCache('/test/test.ts');
    expect(cachedAnalysis).toBeDefined();
    expect(cachedAnalysis.data.patterns).toContain('singleton');
    expect(cachedAnalysis.data.smells).toContain('long method');
  });

  it('should track change history', () => {
    const mockChanges = {
      content: 'new content',
      dependencies: ['other.ts'],
      analysis: {
        patterns: ['singleton'],
      },
    };

    service['addToChangeHistory']('file', '/test/test.ts', mockChanges.content);
    service['addToChangeHistory']('dependency', '/test/test.ts', mockChanges.dependencies);
    service['addToChangeHistory']('analysis', '/test/test.ts', mockChanges.analysis);

    const history = service.getChangeHistory();
    expect(history).toHaveLength(3);
    expect(history[0].type).toBe('file');
    expect(history[1].type).toBe('dependency');
    expect(history[2].type).toBe('analysis');
  });

  it('should search nodes with enhanced criteria', () => {
    const mockNode: CodeNode = {
      id: '1',
      type: 'file',
      name: 'test.ts',
      path: '/test/test.ts',
      dependencies: [],
      metrics: {
        complexity: 1,
        lines: 10,
        dependencies: 0,
        coverage: 80,
        maintainability: 70,
        cognitiveComplexity: 2,
        cyclomaticComplexity: 1,
        halsteadVolume: 100,
        halsteadDifficulty: 1,
        halsteadEffort: 100,
        halsteadTime: 1,
        halsteadBugs: 0,
      },
      relationships: {
        imports: [],
        exports: [],
        extends: [],
        implements: [],
        uses: [],
        usedBy: [],
      },
      context: {
        namespace: 'test',
        module: 'test.ts',
        scope: 'module',
        visibility: 'public',
      },
      analysis: {
        patterns: ['singleton'],
        smells: ['long method'],
        vulnerabilities: [],
        suggestions: ['consider splitting method'],
        documentation: 'Test file with singleton pattern',
        lastModified: new Date(),
        contributors: ['user1'],
        gitHistory: [],
      },
    };

    const mockCallback = mockSocket.emit.mock.calls[0][2];
    if (mockCallback) {
      mockCallback({ nodes: [mockNode], edges: [] });
    }

    service.searchNodes('singleton');
    expect(service['searchResults'].has('1')).toBe(true);
  });

  it('should filter nodes with enhanced criteria', () => {
    const mockNode: CodeNode = {
      id: '1',
      type: 'file',
      name: 'test.ts',
      path: '/test/test.ts',
      dependencies: [],
      metrics: {
        complexity: 5,
        lines: 50,
        dependencies: 3,
        coverage: 60,
        maintainability: 50,
        cognitiveComplexity: 10,
        cyclomaticComplexity: 5,
        halsteadVolume: 500,
        halsteadDifficulty: 5,
        halsteadEffort: 500,
        halsteadTime: 5,
        halsteadBugs: 1,
      },
      relationships: {
        imports: [],
        exports: [],
        extends: [],
        implements: [],
        uses: [],
        usedBy: [],
      },
      context: {
        namespace: 'test',
        module: 'test.ts',
        scope: 'module',
        visibility: 'public',
      },
      analysis: {
        patterns: ['singleton'],
        smells: ['long method'],
        vulnerabilities: ['sql injection'],
        suggestions: ['consider splitting method'],
        documentation: '',
        lastModified: new Date(),
        contributors: [],
        gitHistory: [],
      },
    };

    const mockCallback = mockSocket.emit.mock.calls[0][2];
    if (mockCallback) {
      mockCallback({ nodes: [mockNode], edges: [] });
    }

    service.filterNodes({
      type: ['file'],
      complexity: { min: 1, max: 10 },
      coverage: { min: 50, max: 100 },
      maintainability: { min: 40, max: 100 },
      patterns: ['singleton'],
      smells: ['long method'],
      vulnerabilities: ['sql injection'],
    });
  });

  it('should clean up resources on dispose', () => {
    service.dispose();
    expect(mockSocket.off).toHaveBeenCalledWith('fileChanged');
    expect(mockSocket.off).toHaveBeenCalledWith('dependenciesChanged');
    expect(mockSocket.off).toHaveBeenCalledWith('analysisUpdated');
  });

  describe('Agent Integration', () => {
    it('should provide agent context', () => {
      const agentContext: AgentContext = {
        agentId: 'test-agent',
        capabilities: ['code-analysis'],
        currentTask: 'implement feature',
        requiredContext: ['dependencies', 'metrics']
      };

      const context = service.provideAgentContext(agentContext);
      expect(context).toHaveProperty('nodes');
      expect(context).toHaveProperty('relationships');
      expect(context).toHaveProperty('metrics');
      expect(context).toHaveProperty('suggestions');
    });
  });

  describe('Error Analysis', () => {
    it('should analyze error context', () => {
      const error = new Error('Test error in component');
      const context = service.analyzeErrorContext(error);
      
      expect(context).toHaveProperty('affectedComponents');
      expect(context).toHaveProperty('errorPatterns');
      expect(context).toHaveProperty('suggestedFixes');
      expect(context).toHaveProperty('impactAnalysis');
    });
  });

  describe('Project Insights', () => {
    it('should provide project insights', () => {
      const insights = service.getProjectInsights();
      
      expect(insights).toHaveProperty('architecture');
      expect(insights).toHaveProperty('dependencies');
      expect(insights).toHaveProperty('codeQuality');
      expect(insights).toHaveProperty('maintainability');
      expect(insights).toHaveProperty('suggestions');
    });
  });

  describe('Collaborative Updates', () => {
    it('should handle collaborative updates', () => {
      const update: CollaborativeUpdate = {
        agentId: 'test-agent',
        changes: [{
          type: 'add',
          path: 'new.ts',
          content: 'new content'
        }],
        context: {
          task: 'add new file',
          reason: 'feature implementation',
          impact: ['new functionality']
        }
      };

      service.handleCollaborativeUpdate(update);
      expect(service.getNodeInfo('new.ts')).toBeDefined();
    });
  });

  describe('Task Analysis', () => {
    it('should analyze task requirements', () => {
      const task: Task = {
        id: 'task-1',
        description: 'Implement new feature',
        requirements: ['add tests', 'update docs'],
        dependencies: ['component-1'],
        priority: 'high'
      };

      const analysis = service.analyzeTaskRequirements(task);
      
      expect(analysis).toHaveProperty('requiredComponents');
      expect(analysis).toHaveProperty('dependencies');
      expect(analysis).toHaveProperty('complexity');
      expect(analysis).toHaveProperty('suggestedApproach');
    });
  });

  describe('Integration Tests', () => {
    it('should handle complete workflow', () => {
      // 1. Initialize with test data
      const testNode: CodeNode = {
        id: 'test-node',
        name: 'TestComponent',
        type: 'component',
        path: 'test.ts',
        metrics: {
          complexity: 0.5,
          lines: 100,
          dependencies: 3,
          coverage: 0.8,
          maintainability: 0.7,
          cognitiveComplexity: 10,
          cyclomaticComplexity: 5,
          halsteadVolume: 1000,
          halsteadDifficulty: 20,
          halsteadEffort: 20000,
          halsteadTime: 1111,
          halsteadBugs: 0.5
        },
        analysis: {
          patterns: ['singleton'],
          smells: ['complexity'],
          vulnerabilities: [],
          suggestions: [],
          documentation: 'Test component documentation',
          lastModified: new Date(),
          contributors: ['test-user'],
          gitHistory: [{
            commit: 'abc123',
            author: 'test-user',
            date: new Date(),
            changes: ['Initial commit']
          }]
        },
        dependencies: [],
        relationships: {
          imports: [],
          exports: [],
          extends: [],
          implements: [],
          uses: [],
          usedBy: []
        },
        context: {
          namespace: 'test',
          module: 'test-module',
          scope: 'module',
          visibility: 'public'
        }
      };

      // 2. Simulate agent task
      const agentContext: AgentContext = {
        agentId: 'test-agent',
        capabilities: ['code-analysis'],
        currentTask: 'implement feature',
        requiredContext: ['dependencies', 'metrics']
      };

      // 3. Get agent context
      const context = service.provideAgentContext(agentContext);
      expect(context.nodes).toBeDefined();
      expect(context.metrics).toBeDefined();

      // 4. Analyze error
      const error = new Error('Test error in TestComponent');
      const errorContext = service.analyzeErrorContext(error);
      expect(errorContext.affectedComponents).toBeDefined();
      expect(errorContext.suggestedFixes).toBeDefined();

      // 5. Get project insights
      const insights = service.getProjectInsights();
      expect(insights.architecture).toBeDefined();
      expect(insights.dependencies).toBeDefined();

      // 6. Handle collaborative update
      const update: CollaborativeUpdate = {
        agentId: 'test-agent',
        changes: [{
          type: 'modify',
          path: 'test.ts',
          content: 'updated content'
        }],
        context: {
          task: 'update feature',
          reason: 'bug fix',
          impact: ['performance']
        }
      };

      service.handleCollaborativeUpdate(update);
      expect(mockSocket.emit).toHaveBeenCalledWith('agentNotification', expect.any(Object));

      // 7. Analyze task
      const task: Task = {
        id: 'task-1',
        description: 'Implement new feature',
        requirements: ['add tests', 'update docs'],
        dependencies: ['component-1'],
        priority: 'high'
      };

      const taskAnalysis = service.analyzeTaskRequirements(task);
      expect(taskAnalysis.requiredComponents).toBeDefined();
      expect(taskAnalysis.suggestedApproach).toBeDefined();
    });
  });

  describe('Integration Points', () => {
    describe('Error Analysis Integration', () => {
      it('should handle error analysis updates', () => {
        const errorData: ErrorAnalysisIntegration = {
          errorId: 'error-1',
          errorType: 'runtime',
          stackTrace: ['Error: Test error', 'at test.ts:10:5'],
          context: {
            file: 'test.ts',
            line: 10,
            column: 5
          },
          severity: 'high',
          relatedNodes: ['test-node'],
          suggestedFixes: ['Add error handling']
        };

        service['handleErrorAnalysis'](errorData);
        expect(mockSocket.emit).toHaveBeenCalledWith('errorAnalysis', expect.any(Object));
      });

      it('should report errors', () => {
        const error = new Error('Test error');
        service.reportError(error);
        expect(mockSocket.emit).toHaveBeenCalledWith('reportError', expect.any(Object));
      });

      it('should handle multiple related nodes in error analysis', () => {
        const errorData: ErrorAnalysisIntegration = {
          errorId: 'error-2',
          errorType: 'runtime',
          stackTrace: ['Error: Test error', 'at test.ts:10:5', 'at other.ts:15:3'],
          context: {
            file: 'test.ts',
            line: 10,
            column: 5
          },
          severity: 'high',
          relatedNodes: ['test-node', 'other-node'],
          suggestedFixes: ['Add error handling', 'Check null values']
        };

        service['handleErrorAnalysis'](errorData);
        expect(mockSocket.emit).toHaveBeenCalledWith('errorAnalysis', expect.objectContaining({
          affectedNodes: expect.arrayContaining(['test-node', 'other-node'])
        }));
      });

      it('should handle error analysis with missing context', () => {
        const errorData: ErrorAnalysisIntegration = {
          errorId: 'error-3',
          errorType: 'runtime',
          stackTrace: ['Error: Test error'],
          context: {
            file: '',
            line: 0,
            column: 0
          },
          severity: 'low',
          relatedNodes: [],
          suggestedFixes: []
        };

        service['handleErrorAnalysis'](errorData);
        expect(mockSocket.emit).toHaveBeenCalledWith('errorAnalysis', expect.any(Object));
      });

      it('should handle error reporting with stack trace', () => {
        const error = new Error('Test error');
        error.stack = 'Error: Test error\n    at test.ts:10:5\n    at other.ts:15:3';
        service.reportError(error);
        expect(mockSocket.emit).toHaveBeenCalledWith('reportError', expect.objectContaining({
          stackTrace: expect.arrayContaining(['Error: Test error', 'at test.ts:10:5', 'at other.ts:15:3'])
        }));
      });
    });

    describe('Agent System Integration', () => {
      it('should handle agent updates', () => {
        const agentData: AgentSystemIntegration = {
          agentId: 'agent-1',
          agentType: 'code-analysis',
          capabilities: ['code-analysis', 'error-detection'],
          currentTask: {
            id: 'task-1',
            description: 'Analyze code',
            status: 'in_progress',
            priority: 'high'
          },
          context: {
            relevantFiles: ['test.ts'],
            dependencies: ['other.ts'],
            metrics: { complexity: 0.5 }
          }
        };

        service['handleAgentUpdate'](agentData);
        expect(mockSocket.emit).toHaveBeenCalledWith('agentUpdate', expect.any(Object));
      });

      it('should update agent context', () => {
        service.updateAgentContext('agent-1', 'task-1');
        expect(mockSocket.emit).toHaveBeenCalledWith('requestAgentContext', {
          agentId: 'agent-1',
          taskId: 'task-1'
        }, expect.any(Function));
      });

      it('should handle agent updates with task status changes', () => {
        const agentData: AgentSystemIntegration = {
          agentId: 'agent-2',
          agentType: 'code-analysis',
          capabilities: ['code-analysis', 'error-detection'],
          currentTask: {
            id: 'task-2',
            description: 'Analyze code',
            status: 'completed',
            priority: 'high'
          },
          context: {
            relevantFiles: ['test.ts'],
            dependencies: ['other.ts'],
            metrics: { complexity: 0.5 }
          }
        };

        service['handleAgentUpdate'](agentData);
        expect(mockSocket.emit).toHaveBeenCalledWith('agentUpdate', expect.objectContaining({
          taskStatus: 'completed'
        }));
      });

      it('should handle agent updates with empty context', () => {
        const agentData: AgentSystemIntegration = {
          agentId: 'agent-3',
          agentType: 'code-analysis',
          capabilities: [],
          currentTask: {
            id: 'task-3',
            description: '',
            status: 'pending',
            priority: 'low'
          },
          context: {
            relevantFiles: [],
            dependencies: [],
            metrics: {}
          }
        };

        service['handleAgentUpdate'](agentData);
        expect(mockSocket.emit).toHaveBeenCalledWith('agentUpdate', expect.any(Object));
      });

      it('should handle agent context update with invalid task ID', () => {
        service.updateAgentContext('agent-4', 'invalid-task');
        expect(mockSocket.emit).toHaveBeenCalledWith('requestAgentContext', {
          agentId: 'agent-4',
          taskId: 'invalid-task'
        }, expect.any(Function));
      });
    });

    describe('Project Awareness Integration', () => {
      it('should handle project updates', () => {
        const projectData: ProjectAwarenessIntegration = {
          projectId: 'project-1',
          structure: {
            files: ['test.ts', 'other.ts'],
            directories: ['src', 'tests'],
            dependencies: {
              'test.ts': ['other.ts']
            }
          },
          metrics: {
            complexity: 0.5,
            maintainability: 0.8,
            testCoverage: 0.9,
            documentation: 0.7
          },
          patterns: {
            architecture: ['MVC'],
            antiPatterns: ['God Object'],
            suggestions: ['Split into smaller components']
          }
        };

        service['handleProjectUpdate'](projectData);
        expect(mockSocket.emit).toHaveBeenCalledWith('projectUpdate', expect.any(Object));
      });

      it('should update project structure', () => {
        const structure = {
          files: ['new.ts'],
          directories: ['src'],
          dependencies: {
            'new.ts': ['other.ts']
          }
        };

        service['updateProjectStructure'](structure);
        expect(service.getNodeInfo('new.ts')).toBeDefined();
      });

      it('should update project metrics', () => {
        const metrics = {
          complexity: 0.5,
          maintainability: 0.8,
          testCoverage: 0.9,
          documentation: 0.7
        };

        service['updateProjectMetrics'](metrics);
        const insights = service.getProjectInsights();
        expect(insights.codeQuality.metrics).toMatchObject(metrics);
      });

      it('should update project patterns', () => {
        const patterns = {
          architecture: ['MVC'],
          antiPatterns: ['God Object'],
          suggestions: ['Split into smaller components']
        };

        service['updateProjectPatterns'](patterns);
        const insights = service.getProjectInsights();
        expect(insights.architecture.patterns).toEqual(patterns.architecture);
        expect(insights.architecture.issues).toEqual(patterns.antiPatterns);
        expect(insights.architecture.recommendations).toEqual(patterns.suggestions);
      });

      it('should request project updates', () => {
        service.requestProjectUpdate();
        expect(mockSocket.emit).toHaveBeenCalledWith('requestProjectUpdate', {}, expect.any(Function));
      });

      it('should handle project updates with circular dependencies', () => {
        const projectData: ProjectAwarenessIntegration = {
          projectId: 'project-2',
          structure: {
            files: ['test.ts', 'other.ts'],
            directories: ['src', 'tests'],
            dependencies: {
              'test.ts': ['other.ts'],
              'other.ts': ['test.ts']
            }
          },
          metrics: {
            complexity: 0.5,
            maintainability: 0.8,
            testCoverage: 0.9,
            documentation: 0.7
          },
          patterns: {
            architecture: ['MVC'],
            antiPatterns: ['Circular Dependency'],
            suggestions: ['Break circular dependency']
          }
        };

        service['handleProjectUpdate'](projectData);
        expect(mockSocket.emit).toHaveBeenCalledWith('projectUpdate', expect.objectContaining({
          patterns: expect.objectContaining({
            antiPatterns: expect.arrayContaining(['Circular Dependency'])
          })
        }));
      });

      it('should handle project updates with missing files', () => {
        const projectData: ProjectAwarenessIntegration = {
          projectId: 'project-3',
          structure: {
            files: [],
            directories: ['src'],
            dependencies: {}
          },
          metrics: {
            complexity: 0,
            maintainability: 0,
            testCoverage: 0,
            documentation: 0
          },
          patterns: {
            architecture: [],
            antiPatterns: [],
            suggestions: []
          }
        };

        service['handleProjectUpdate'](projectData);
        expect(mockSocket.emit).toHaveBeenCalledWith('projectUpdate', expect.any(Object));
      });

      it('should handle project structure update with invalid paths', () => {
        const structure = {
          files: ['../invalid.ts'],
          directories: ['../invalid'],
          dependencies: {
            '../invalid.ts': ['other.ts']
          }
        };

        service['updateProjectStructure'](structure);
        expect(service.getNodeInfo('../invalid.ts')).toBeUndefined();
      });

      it('should handle project metrics update with invalid values', () => {
        const metrics = {
          complexity: -1,
          maintainability: 2,
          testCoverage: -0.5,
          documentation: 1.5
        };

        service['updateProjectMetrics'](metrics);
        const insights = service.getProjectInsights();
        expect(insights.codeQuality.metrics).toMatchObject({
          complexity: 0,
          maintainability: 1,
          testCoverage: 0,
          documentation: 1
        });
      });
    });

    describe('Integration Event Handlers', () => {
      it('should register error analysis callback', () => {
        const callback = jest.fn();
        service.onErrorAnalysis(callback);
        expect(service.listeners('errorAnalysis')).toContain(callback);
      });

      it('should register agent update callback', () => {
        const callback = jest.fn();
        service.onAgentUpdate(callback);
        expect(service.listeners('agentUpdate')).toContain(callback);
      });

      it('should register project update callback', () => {
        const callback = jest.fn();
        service.onProjectUpdate(callback);
        expect(service.listeners('projectUpdate')).toContain(callback);
      });
    });

    describe('Integration Initialization', () => {
      it('should initialize integrations', () => {
        service['initializeIntegrations']();
        expect(mockSocket.emit).toHaveBeenCalledWith('initializeIntegrations', {}, expect.any(Function));
      });

      it('should set up integration event listeners', () => {
        service['setupIntegrationEventListeners']();
        expect(mockSocket.on).toHaveBeenCalledWith('errorDetected', expect.any(Function));
        expect(mockSocket.on).toHaveBeenCalledWith('agentUpdate', expect.any(Function));
        expect(mockSocket.on).toHaveBeenCalledWith('projectUpdate', expect.any(Function));
      });
    });

    describe('Integration Error Handling', () => {
      it('should handle socket connection errors', () => {
        const error = new Error('Socket connection failed');
        mockSocket.emit.mockImplementation((event, data, callback) => {
          if (callback) callback(error);
          return mockSocket;
        });

        service['initializeIntegrations']();
        expect(mockSocket.emit).toHaveBeenCalledWith('initializeIntegrations', {}, expect.any(Function));
      });

      it('should handle invalid integration responses', () => {
        const invalidResponse = { invalid: 'data' };
        mockSocket.emit.mockImplementation((event, data, callback) => {
          if (callback) callback(invalidResponse);
          return mockSocket;
        });

        service['initializeIntegrations']();
        expect(mockSocket.emit).toHaveBeenCalledWith('initializeIntegrations', {}, expect.any(Function));
      });

      it('should handle missing event handlers', () => {
        const callback = jest.fn();
        service.onErrorAnalysis(callback);
        service.onAgentUpdate(callback);
        service.onProjectUpdate(callback);

        // Simulate events without handlers
        service.emit('errorAnalysis', {});
        service.emit('agentUpdate', {});
        service.emit('projectUpdate', {});

        expect(callback).not.toHaveBeenCalled();
      });
    });

    describe('Integration Edge Cases', () => {
      it('should handle concurrent updates from multiple agents', () => {
        const agent1Update: AgentSystemIntegration = {
          agentId: 'agent-1',
          agentType: 'code-analysis',
          capabilities: ['analysis'],
          currentTask: {
            id: 'task-1',
            description: 'Task 1',
            status: 'in_progress',
            priority: 'high'
          },
          context: {
            relevantFiles: ['test.ts'],
            dependencies: [],
            metrics: {}
          }
        };

        const agent2Update: AgentSystemIntegration = {
          agentId: 'agent-2',
          agentType: 'code-analysis',
          capabilities: ['analysis'],
          currentTask: {
            id: 'task-2',
            description: 'Task 2',
            status: 'in_progress',
            priority: 'high'
          },
          context: {
            relevantFiles: ['other.ts'],
            dependencies: [],
            metrics: {}
          }
        };

        service['handleAgentUpdate'](agent1Update);
        service['handleAgentUpdate'](agent2Update);

        expect(mockSocket.emit).toHaveBeenCalledTimes(2);
      });

      it('should handle rapid project updates', () => {
        const updates: ProjectAwarenessIntegration[] = [
          {
            projectId: 'project-1',
            structure: { files: ['test.ts'], directories: [], dependencies: {} },
            metrics: { complexity: 0.5, maintainability: 0.8, testCoverage: 0.9, documentation: 0.7 },
            patterns: { architecture: [], antiPatterns: [], suggestions: [] }
          },
          {
            projectId: 'project-1',
            structure: { files: ['test.ts', 'other.ts'], directories: [], dependencies: {} },
            metrics: { complexity: 0.6, maintainability: 0.7, testCoverage: 0.8, documentation: 0.6 },
            patterns: { architecture: [], antiPatterns: [], suggestions: [] }
          }
        ];

        updates.forEach(update => service['handleProjectUpdate'](update));
        expect(mockSocket.emit).toHaveBeenCalledTimes(2);
      });

      it('should handle large error analysis data', () => {
        const largeStackTrace = Array(1000).fill('at test.ts:1:1');
        const errorData: ErrorAnalysisIntegration = {
          errorId: 'error-4',
          errorType: 'runtime',
          stackTrace: ['Error: Test error', ...largeStackTrace],
          context: {
            file: 'test.ts',
            line: 1,
            column: 1
          },
          severity: 'high',
          relatedNodes: Array(100).fill('node'),
          suggestedFixes: Array(50).fill('fix')
        };

        service['handleErrorAnalysis'](errorData);
        expect(mockSocket.emit).toHaveBeenCalledWith('errorAnalysis', expect.any(Object));
      });
    });
  });

  describe('Performance Monitoring', () => {
    it('should track operation performance', () => {
      const startTime = Date.now();
      service['trackPerformance']('testOperation', startTime);
      
      const metrics = service.getPerformanceMetrics();
      expect(metrics.operationCounts.get('testOperation')).toBe(1);
      expect(metrics.averageTimes.get('testOperation')).toBeDefined();
    });

    it('should maintain performance history', () => {
      for (let i = 0; i < 5; i++) {
        const startTime = Date.now();
        service['trackPerformance']('testOperation', startTime);
      }

      const metrics = service.getPerformanceMetrics();
      expect(metrics.operationCounts.get('testOperation')).toBe(5);
      expect(metrics.averageTimes.get('testOperation')).toBeGreaterThan(0);
    });
  });

  describe('Health Check', () => {
    it('should report healthy status when all checks pass', () => {
      const health = service.getHealthStatus();
      expect(health.status).toBe('healthy');
      expect(health.issues).toHaveLength(0);
      expect(health.metrics).toBeDefined();
    });

    it('should report degraded status when some issues are present', () => {
      // Simulate stale cache
      service['metricsCache'].set('test', { 
        timestamp: new Date(Date.now() - 600000),
        data: { complexity: 10, maintainability: 0.8 }
      });
      
      const health = service.getHealthStatus();
      expect(health.status).toBe('degraded');
      expect(health.issues).toContain('Cache data is stale');
    });

    it('should report unhealthy status when multiple issues are present', () => {
      // Simulate stale cache and slow operations
      service['metricsCache'].set('test', { 
        timestamp: new Date(Date.now() - 600000),
        data: { complexity: 10, maintainability: 0.8 }
      });
      service['performanceMetrics'].operationTimes.set('slowOperation', [2000, 3000]);
      
      const health = service.getHealthStatus();
      expect(health.status).toBe('unhealthy');
      expect(health.issues).toContain('Cache data is stale');
      expect(health.issues).toContain('Slow operation detected: slowOperation');
    });
  });

  describe('Validation', () => {
    it('should validate node data', () => {
      const validNode = { id: 'test', type: 'file' };
      const invalidNode = { id: 'test' };

      expect(service['validationRules'].get('node')!(validNode)).toBe(true);
      expect(service['validationRules'].get('node')!(invalidNode)).toBe(false);
    });

    it('should validate edge data', () => {
      const validEdge = { source: 'node1', target: 'node2' };
      const invalidEdge = { source: 'node1' };

      expect(service['validationRules'].get('edge')!(validEdge)).toBe(true);
      expect(service['validationRules'].get('edge')!(invalidEdge)).toBe(false);
    });

    it('should validate metrics data', () => {
      const validMetrics = { complexity: 10, maintainability: 0.8 };
      const invalidMetrics = { complexity: 'high' };

      expect(service['validationRules'].get('metrics')!(validMetrics)).toBe(true);
      expect(service['validationRules'].get('metrics')!(invalidMetrics)).toBe(false);
    });
  });

  describe('Error Handling', () => {
    it('should handle validation errors', () => {
      const errorHandler = service['errorHandlers'].get('validation');
      expect(errorHandler).toBeDefined();
      
      const error = new Error('Test validation error');
      errorHandler!(error);
      
      // Verify error event was emitted
      expect(mockSocket.emit).toHaveBeenCalledWith('error', {
        type: 'validation',
        error
      });
    });

    it('should handle analysis errors', () => {
      const errorHandler = service['errorHandlers'].get('analysis');
      expect(errorHandler).toBeDefined();
      
      const error = new Error('Test analysis error');
      errorHandler!(error);
      
      // Verify error event was emitted
      expect(mockSocket.emit).toHaveBeenCalledWith('error', {
        type: 'analysis',
        error
      });
    });

    it('should handle integration errors', () => {
      const errorHandler = service['errorHandlers'].get('integration');
      expect(errorHandler).toBeDefined();
      
      const error = new Error('Test integration error');
      errorHandler!(error);
      
      // Verify error event was emitted
      expect(mockSocket.emit).toHaveBeenCalledWith('error', {
        type: 'integration',
        error
      });
    });
  });

  describe('Batch Operations', () => {
    it('should process batch updates efficiently', () => {
      const updates = [
        {
          type: 'node' as const,
          operation: 'add' as const,
          data: {
            id: 'node1',
            type: 'file',
            name: 'test1.ts',
            path: '/test/test1.ts',
            dependencies: [],
            metrics: { complexity: 1, maintainability: 0.8 },
            relationships: { imports: [], exports: [], extends: [], implements: [], uses: [], usedBy: [] },
            context: { namespace: 'test', module: 'test1', scope: 'module', visibility: 'public' },
            analysis: { patterns: [], smells: [], vulnerabilities: [], suggestions: [], documentation: '', lastModified: new Date(), contributors: [], gitHistory: [] }
          }
        },
        {
          type: 'edge' as const,
          operation: 'add' as const,
          data: {
            from: 'node1',
            to: 'node2',
            type: 'import',
            weight: 1,
            metadata: { lineNumber: 1, context: 'import', strength: 1, bidirectional: false }
          }
        }
      ];

      service.batchUpdate(updates);
      expect(service.getNodeInfo('node1')).toBeDefined();
      expect(service['edges'].has('node1-node2')).toBe(true);
    });

    it('should handle large batches of updates', () => {
      const updates = Array(60).fill(null).map((_, i) => ({
        type: 'node' as const,
        operation: 'add' as const,
        data: {
          id: `node${i}`,
          type: 'file',
          name: `test${i}.ts`,
          path: `/test/test${i}.ts`,
          dependencies: [],
          metrics: { complexity: 1, maintainability: 0.8 },
          relationships: { imports: [], exports: [], extends: [], implements: [], uses: [], usedBy: [] },
          context: { namespace: 'test', module: `test${i}`, scope: 'module', visibility: 'public' },
          analysis: { patterns: [], smells: [], vulnerabilities: [], suggestions: [], documentation: '', lastModified: new Date(), contributors: [], gitHistory: [] }
        }
      }));

      service.batchUpdate(updates);
      expect(service['nodes'].size).toBe(60);
    });

    it('should process batch updates with timeouts', (done) => {
      const updates = [
        {
          type: 'node' as const,
          operation: 'add' as const,
          data: {
            id: 'node1',
            type: 'file',
            name: 'test1.ts',
            path: '/test/test1.ts',
            dependencies: [],
            metrics: { complexity: 1, maintainability: 0.8 },
            relationships: { imports: [], exports: [], extends: [], implements: [], uses: [], usedBy: [] },
            context: { namespace: 'test', module: 'test1', scope: 'module', visibility: 'public' },
            analysis: { patterns: [], smells: [], vulnerabilities: [], suggestions: [], documentation: '', lastModified: new Date(), contributors: [], gitHistory: [] }
          }
        }
      ];

      service.batchUpdate(updates);
      setTimeout(() => {
        expect(service.getNodeInfo('node1')).toBeDefined();
        done();
      }, 150);
    });
  });

  describe('Performance Profiling', () => {
    it('should track performance profiles', () => {
      const profileId = 'test-profile';
      const operations = ['nodeUpdate', 'edgeUpdate', 'analysisUpdate'];

      service.startProfile(profileId, operations);
      
      // Perform some operations
      service.batchUpdate([
        {
          type: 'node' as const,
          operation: 'add' as const,
          data: {
            id: 'node1',
            type: 'file',
            name: 'test1.ts',
            path: '/test/test1.ts',
            dependencies: [],
            metrics: { complexity: 1, maintainability: 0.8 },
            relationships: { imports: [], exports: [], extends: [], implements: [], uses: [], usedBy: [] },
            context: { namespace: 'test', module: 'test1', scope: 'module', visibility: 'public' },
            analysis: { patterns: [], smells: [], vulnerabilities: [], suggestions: [], documentation: '', lastModified: new Date(), contributors: [], gitHistory: [] }
          }
        }
      ]);

      const results = service.endProfile(profileId);
      expect(results).toBeDefined();
      expect(results?.duration).toBeGreaterThan(0);
      expect(results?.memoryUsage).toBeGreaterThan(0);
      expect(results?.operationMetrics.size).toBe(3);
    });

    it('should handle multiple concurrent profiles', () => {
      const profile1 = 'profile1';
      const profile2 = 'profile2';
      const operations = ['nodeUpdate', 'edgeUpdate'];

      service.startProfile(profile1, operations);
      service.startProfile(profile2, operations);

      // Perform operations
      service.batchUpdate([
        {
          type: 'node' as const,
          operation: 'add' as const,
          data: {
            id: 'node1',
            type: 'file',
            name: 'test1.ts',
            path: '/test/test1.ts',
            dependencies: [],
            metrics: { complexity: 1, maintainability: 0.8 },
            relationships: { imports: [], exports: [], extends: [], implements: [], uses: [], usedBy: [] },
            context: { namespace: 'test', module: 'test1', scope: 'module', visibility: 'public' },
            analysis: { patterns: [], smells: [], vulnerabilities: [], suggestions: [], documentation: '', lastModified: new Date(), contributors: [], gitHistory: [] }
          }
        }
      ]);

      const results1 = service.endProfile(profile1);
      const results2 = service.endProfile(profile2);

      expect(results1).toBeDefined();
      expect(results2).toBeDefined();
      expect(results1?.duration).toBeGreaterThan(0);
      expect(results2?.duration).toBeGreaterThan(0);
    });

    it('should return null for non-existent profiles', () => {
      const results = service.endProfile('non-existent');
      expect(results).toBeNull();
    });
  });

  describe('Cache Optimization', () => {
    it('should optimize cache based on usage patterns', () => {
      // Add test data to cache
      for (let i = 0; i < 100; i++) {
        service['metricsCache'].set(`test${i}`, {
          timestamp: new Date(Date.now() - i * 1000),
          data: { complexity: i, maintainability: 0.8 }
        });
      }

      service['optimizeCache']();
      expect(service['metricsCache'].size).toBeLessThan(100);
    });

    it('should keep most frequently used items in cache', () => {
      // Add test data with different access patterns
      for (let i = 0; i < 100; i++) {
        service['metricsCache'].set(`test${i}`, {
          timestamp: new Date(Date.now() - (i % 2 === 0 ? 1000 : 10000)),
          data: { complexity: i, maintainability: 0.8 }
        });
      }

      service['optimizeCache']();
      const remainingKeys = Array.from(service['metricsCache'].keys());
      expect(remainingKeys.length).toBeGreaterThan(0);
      expect(remainingKeys.length).toBeLessThan(100);
    });
  });
}); 