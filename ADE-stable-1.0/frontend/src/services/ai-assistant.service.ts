import { AIAssistantContext, AIAssistantSuggestion, AIAssistantHistory } from '../interfaces/ai-assistant';
import { AIAgentConfig, AIExecutionRequest, AIExecutionResponse, AIAgentContext } from '../interfaces/ai';
import natural from 'natural';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export class AIAssistantService {
    private static instance: AIAssistantService;
    private config: AIAgentConfig;
    private memory: Map<string, AIAssistantHistory[]>;
    private projectMetadata: Map<string, ProjectMetadata>;
    private memoryIndex: Map<string, MemoryIndex>;
    private tokenizer: natural.WordTokenizer;
    private tfidf: natural.TfIdf;
    private entityExtractor: natural.EntityExtractor;
    private memoryCache: Map<string, {
        content: string;
        timestamp: number;
        relevance: number;
    }>;
    private semanticCache: Map<string, {
        embeddings: number[];
        content: string;
        timestamp: number;
    }>;
    private readonly CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours
    private readonly MAX_CACHE_SIZE = 1000;
    private readonly RELEVANCE_THRESHOLD = 0.7;

    private constructor() {
        this.config = {
            model: 'sonnet-3.7',
            temperature: 0.7,
            maxTokens: 2000,
            apiKey: process.env.REACT_APP_AI_API_KEY || '',
        };
        this.memory = new Map();
        this.projectMetadata = new Map();
        this.memoryIndex = new Map();
        this.tokenizer = new natural.WordTokenizer();
        this.tfidf = new natural.TfIdf();
        this.entityExtractor = new natural.EntityExtractor();
        this.memoryCache = new Map();
        this.semanticCache = new Map();
    }

    public static getInstance(): AIAssistantService {
        if (!AIAssistantService.instance) {
            AIAssistantService.instance = new AIAssistantService();
        }
        return AIAssistantService.instance;
    }

    public setConfig(config: Partial<AIAgentConfig>): void {
        this.config = { ...this.config, ...config };
    }

    public async sendMessage(
        message: string,
        assistantContext: AIAssistantContext
    ): Promise<{ history: AIAssistantHistory; suggestions: AIAssistantSuggestion[] }> {
        try {
            // Check memory cache first
            const cachedResponse = this.checkMemoryCache(message, assistantContext);
            if (cachedResponse) {
                return cachedResponse;
            }

            // Check semantic cache
            const semanticResponse = await this.checkSemanticCache(message, assistantContext);
            if (semanticResponse) {
                return semanticResponse;
            }

            // If no cache hit, proceed with LLM call
            const projectId = assistantContext.projectContext.config.projectId || 'default';
            const projectHistory = this.memory.get(projectId) || [];

            const agentContext: AIAgentContext = {
                systemMetrics: {
                    cpu: 0,
                    memory: 0,
                    disk: 0,
                    network: 0,
                },
                processMetrics: {
                    cpu: 0,
                    memory: 0,
                    threads: 0,
                    handles: 0,
                },
                executionHistory: [],
                availableCommands: [],
                environmentVariables: assistantContext.systemContext.environment,
            };

            // Add project history to context for thinking tasks
            const request: AIExecutionRequest = {
                prompt: message,
                context: agentContext,
                config: this.config,
                projectHistory: projectHistory,
            };

            const response = await fetch(`${API_BASE_URL}/api/ai/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.config.apiKey}`,
                },
                body: JSON.stringify(request),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data: AIExecutionResponse = await response.json();

            const history: AIAssistantHistory = {
                id: crypto.randomUUID(),
                timestamp: new Date().toISOString(),
                type: 'assistant',
                content: data.response.explanation,
                metadata: {
                    command: data.response.command,
                    suggestions: [data.response.expectedOutcome],
                    thinkingProcess: data.response.thinkingProcess,
                },
            };

            // Update project memory
            this.memory.set(projectId, [...projectHistory, history]);

            const suggestions: AIAssistantSuggestion[] = data.response.safetyChecks.map(check => {
                const solutions = check.solutions?.map(solution => ({
                    code: solution.code,
                    description: solution.description,
                    metrics: {
                        effectiveness: solution.metrics.effectiveness || 0.8,
                        impact: solution.metrics.impact || 0.7,
                        complexity: solution.metrics.complexity || 0.3,
                        maintainability: solution.metrics.maintainability || 0.8
                    },
                    metadata: solution.metadata || {}
                })) || [];

                return {
                    id: crypto.randomUUID(),
                    type: check.type === 'command' ? 'command' : 'fix',
                    content: check.message,
                    confidence: check.status === 'safe' ? 1 : check.status === 'warning' ? 0.7 : 0.3,
                    context: {
                        file: check.file,
                        line: check.line,
                        column: check.column
                    },
                    actions: [
                        {
                            id: crypto.randomUUID(),
                            type: 'apply',
                            label: 'Apply',
                            description: 'Apply this suggestion',
                            execute: async (solutionIndex?: number) => {
                                const solution = solutions[solutionIndex || 0];
                                if (!solution) return;

                                // Execute the solution
                                await this.executeSolution(solution, check);
                            },
                        },
                    ],
                    solutions
                };
            });

            return { history, suggestions };
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    }

    private async executeSolution(solution: Solution, check: any): Promise<void> {
        try {
            // Apply the solution code
            await this.applyCodeChanges(solution.code, check.file, check.line);

            // Update analytics
            this.updateAnalytics(check.projectId, {
                successfulSolutions: 1,
                solutionMetrics: solution.metrics
            });

            // Log the solution application
            console.log('Applied solution:', {
                file: check.file,
                line: check.line,
                metrics: solution.metrics
            });
        } catch (error) {
            console.error('Error executing solution:', error);
            throw error;
        }
    }

    private async applyCodeChanges(code: string, file: string, line: number): Promise<void> {
        // TODO: Implement code change application
        console.log('Applying code changes:', { file, line, code });
    }

    private updateAnalytics(projectId: string, data: any): void {
        const metadata = this.projectMetadata.get(projectId);
        if (!metadata) return;

        // Update solution-related analytics
        metadata.analytics = {
            ...metadata.analytics,
            successfulSolutions: (metadata.analytics.successfulSolutions || 0) + data.successfulSolutions,
            solutionMetrics: [
                ...(metadata.analytics.solutionMetrics || []),
                data.solutionMetrics
            ]
        };

        this.projectMetadata.set(projectId, metadata);
    }

    public async applySuggestion(suggestion: AIAssistantSuggestion): Promise<void> {
        try {
            const response = await fetch(`${API_BASE_URL}/api/ai/apply-suggestion`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.config.apiKey}`,
                },
                body: JSON.stringify({ suggestion }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Handle successful application
            console.log('Suggestion applied successfully');
        } catch (error) {
            console.error('Error applying suggestion:', error);
            throw error;
        }
    }

    public async provideFeedback(
        suggestionId: string,
        rating: 'helpful' | 'not_helpful'
    ): Promise<void> {
        try {
            const response = await fetch(`${API_BASE_URL}/api/ai/feedback`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.config.apiKey}`,
                },
                body: JSON.stringify({ suggestionId, rating }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Handle successful feedback submission
            console.log('Feedback submitted successfully');
        } catch (error) {
            console.error('Error providing feedback:', error);
            throw error;
        }
    }

    public async saveHistory(history: AIAssistantHistory[]): Promise<void> {
        try {
            const projectId = history[0]?.metadata?.projectId || 'default';
            
            // Update memory
            this.memory.set(projectId, history);
            
            // Update memory index
            this.updateMemoryIndex(projectId, history);
            
            // Update project metadata
            this.updateProjectMetadata(projectId, history);

            // Save to backend
            const response = await fetch(`${API_BASE_URL}/api/ai/history`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.config.apiKey}`,
                },
                body: JSON.stringify({ 
                    history,
                    metadata: this.projectMetadata.get(projectId),
                    index: this.memoryIndex.get(projectId)
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            console.log('History saved successfully');
        } catch (error) {
            console.error('Error saving history:', error);
            throw error;
        }
    }

    private updateMemoryIndex(projectId: string, history: AIAssistantHistory[]): void {
        const index: MemoryIndex = {
            topics: new Map(),
            entities: new Map(),
            commands: new Map(),
            files: new Map(),
            timestamps: new Map(),
        };

        history.forEach(entry => {
            // Index by topic
            const topics = this.extractTopics(entry.content);
            topics.forEach(topic => {
                if (!index.topics.has(topic)) {
                    index.topics.set(topic, []);
                }
                index.topics.get(topic)?.push(entry.id);
            });

            // Index by entity
            const entities = this.extractEntities(entry.content);
            entities.forEach(entity => {
                if (!index.entities.has(entity)) {
                    index.entities.set(entity, []);
                }
                index.entities.get(entity)?.push(entry.id);
            });

            // Index by command
            if (entry.metadata?.command) {
                if (!index.commands.has(entry.metadata.command)) {
                    index.commands.set(entry.metadata.command, []);
                }
                index.commands.get(entry.metadata.command)?.push(entry.id);
            }

            // Index by file
            if (entry.metadata?.file) {
                if (!index.files.has(entry.metadata.file)) {
                    index.files.set(entry.metadata.file, []);
                }
                index.files.get(entry.metadata.file)?.push(entry.id);
            }

            // Index by timestamp
            index.timestamps.set(entry.id, new Date(entry.timestamp));
        });

        this.memoryIndex.set(projectId, index);
    }

    private updateProjectMetadata(projectId: string, history: AIAssistantHistory[]): void {
        const metadata: ProjectMetadata = {
            lastUpdated: new Date().toISOString(),
            totalInteractions: history.length,
            uniqueUsers: new Set(history.map(h => h.metadata?.user || 'anonymous')).size,
            commandStats: new Map(),
            fileStats: new Map(),
            topicStats: new Map(),
            entityStats: new Map(),
        };

        history.forEach(entry => {
            // Update command stats
            if (entry.metadata?.command) {
                metadata.commandStats.set(
                    entry.metadata.command,
                    (metadata.commandStats.get(entry.metadata.command) || 0) + 1
                );
            }

            // Update file stats
            if (entry.metadata?.file) {
                metadata.fileStats.set(
                    entry.metadata.file,
                    (metadata.fileStats.get(entry.metadata.file) || 0) + 1
                );
            }

            // Update topic stats
            const topics = this.extractTopics(entry.content);
            topics.forEach(topic => {
                metadata.topicStats.set(
                    topic,
                    (metadata.topicStats.get(topic) || 0) + 1
                );
            });

            // Update entity stats
            const entities = this.extractEntities(entry.content);
            entities.forEach(entity => {
                metadata.entityStats.set(
                    entity,
                    (metadata.entityStats.get(entity) || 0) + 1
                );
            });
        });

        this.projectMetadata.set(projectId, metadata);
    }

    private extractTopics(content: string): string[] {
        const tokens = this.tokenizer.tokenize(content);
        if (!tokens) return [];

        // Remove stopwords and short words
        const stopwords = natural.stopwords;
        const filteredTokens = tokens.filter((token: string) => 
            token.length > 2 && !stopwords.includes(token.toLowerCase())
        );

        // Calculate TF-IDF scores
        this.tfidf.addDocument(filteredTokens);
        const scores = this.tfidf.listTerms(0);

        // Get top topics based on TF-IDF scores
        const topics = scores
            .slice(0, 5)
            .map((term: { term: string }) => term.term)
            .filter((term: string) => term.length > 2);

        // Add domain-specific topics
        const domainTopics = this.extractDomainTopics(content);
        topics.push(...domainTopics);

        return [...new Set(topics)]; // Remove duplicates
    }

    private extractDomainTopics(content: string): string[] {
        const domainPatterns = {
            // Code patterns
            code: {
                functions: /(?:function|method|procedure)\s+(\w+)/g,
                classes: /(?:class|interface|type|enum)\s+(\w+)/g,
                variables: /(?:const|let|var|final)\s+(\w+)/g,
                imports: /(?:import|require|include)\s+['"]([^'"]+)['"]/g,
                decorators: /@(\w+)/g,
                annotations: /\[(\w+)\]/g,
                generics: /<(\w+)>/g,
                async: /(?:async|await|promise|future)/g,
                patterns: /(?:singleton|factory|observer|strategy|decorator|adapter)/g,
            },
            // Language-specific patterns
            languages: {
                typescript: {
                    types: /(?:type|interface)\s+(\w+)\s*=/g,
                    enums: /enum\s+(\w+)\s*{/g,
                    namespaces: /namespace\s+(\w+)\s*{/g,
                    decorators: /@(\w+)(?:\([^)]*\))?/g,
                    generics: /<(\w+)(?:,\s*\w+)*>/g,
                    typeGuards: /is\s+(\w+)/g,
                },
                python: {
                    decorators: /@(\w+)/g,
                    classes: /class\s+(\w+)(?:\([^)]*\))?:/g,
                    imports: /(?:from|import)\s+(\w+)/g,
                    typeHints: /:\s*(\w+)/g,
                    async: /async\s+def\s+(\w+)/g,
                    contextManagers: /with\s+(\w+)/g,
                },
                java: {
                    annotations: /@(\w+)/g,
                    classes: /(?:class|interface|enum)\s+(\w+)/g,
                    generics: /<(\w+)(?:,\s*\w+)*>/g,
                    packages: /package\s+(\w+)/g,
                    imports: /import\s+(\w+)/g,
                    exceptions: /throws\s+(\w+)/g,
                },
                rust: {
                    traits: /trait\s+(\w+)/g,
                    structs: /struct\s+(\w+)/g,
                    enums: /enum\s+(\w+)/g,
                    lifetimes: /'(\w+)/g,
                    macros: /!(\w+)/g,
                    modules: /mod\s+(\w+)/g,
                },
            },
            // Framework-specific patterns
            frameworks: {
                react: {
                    components: /(?:function|class)\s+(\w+)\s*extends\s+React\.Component/g,
                    hooks: /use(\w+)/g,
                    props: /interface\s+(\w+)Props/g,
                    contexts: /React\.createContext/g,
                    refs: /useRef/g,
                    effects: /useEffect/g,
                },
                angular: {
                    components: /@Component/g,
                    services: /@Injectable/g,
                    modules: /@NgModule/g,
                    directives: /@Directive/g,
                    pipes: /@Pipe/g,
                    guards: /@Guard/g,
                },
                vue: {
                    components: /export\s+default\s+{/g,
                    props: /props:\s*{/g,
                    computed: /computed:\s*{/g,
                    methods: /methods:\s*{/g,
                    watchers: /watch:\s*{/g,
                    mixins: /mixins:\s*\[/g,
                },
                express: {
                    routes: /app\.(?:get|post|put|delete)\s*\(['"]([^'"]+)['"]/g,
                    middleware: /app\.use\s*\(/g,
                    controllers: /router\.(?:get|post|put|delete)\s*\(['"]([^'"]+)['"]/g,
                    models: /mongoose\.model\s*\(['"]([^'"]+)['"]/g,
                    schemas: /new\s+mongoose\.Schema/g,
                },
                django: {
                    models: /class\s+(\w+)\s*\(models\.Model\)/g,
                    views: /class\s+(\w+)\s*\(views\.View\)/g,
                    urls: /path\s*\(['"]([^'"]+)['"]/g,
                    forms: /class\s+(\w+)Form\s*\(forms\.Form\)/g,
                    templates: /render\s*\([^)]*['"]([^'"]+)['"]/g,
                },
            },
            // Database patterns
            databases: {
                sql: {
                    tables: /CREATE\s+TABLE\s+(\w+)/g,
                    views: /CREATE\s+VIEW\s+(\w+)/g,
                    indexes: /CREATE\s+INDEX\s+(\w+)/g,
                    triggers: /CREATE\s+TRIGGER\s+(\w+)/g,
                    procedures: /CREATE\s+PROCEDURE\s+(\w+)/g,
                },
                nosql: {
                    collections: /db\.createCollection\s*\(['"]([^'"]+)['"]/g,
                    indexes: /db\.(\w+)\.createIndex/g,
                    aggregation: /db\.(\w+)\.aggregate/g,
                    queries: /db\.(\w+)\.find/g,
                },
            },
            // Testing patterns
            testing: {
                unit: {
                    testCases: /test\s*\(['"]([^'"]+)['"]/g,
                    assertions: /expect\s*\(/g,
                    mocks: /jest\.mock/g,
                    spies: /jest\.spyOn/g,
                    snapshots: /toMatchSnapshot/g,
                },
                e2e: {
                    scenarios: /scenario\s*\(['"]([^'"]+)['"]/g,
                    steps: /(?:Given|When|Then)\s*\(['"]([^'"]+)['"]/g,
                    pages: /class\s+(\w+)Page/g,
                    actions: /await\s+page\.(?:click|type|select)/g,
                },
            },
            // DevOps patterns
            devops: {
                docker: {
                    images: /FROM\s+(\w+)/g,
                    containers: /docker\s+run\s+(\w+)/g,
                    volumes: /VOLUME\s+\[['"]([^'"]+)['"]/g,
                    ports: /EXPOSE\s+(\d+)/g,
                    networks: /docker\s+network\s+create\s+(\w+)/g,
                },
                kubernetes: {
                    pods: /kind:\s*Pod/g,
                    services: /kind:\s*Service/g,
                    deployments: /kind:\s*Deployment/g,
                    configmaps: /kind:\s*ConfigMap/g,
                    secrets: /kind:\s*Secret/g,
                },
                ci: {
                    workflows: /name:\s*(\w+)/g,
                    jobs: /jobs:\s*{/g,
                    steps: /steps:\s*\[/g,
                    actions: /uses:\s*(\w+)/g,
                    triggers: /on:\s*{/g,
                },
            },
        };

        const topics: string[] = [];
        for (const [domain, patterns] of Object.entries(domainPatterns)) {
            if (typeof patterns === 'object') {
                for (const [category, subPatterns] of Object.entries(patterns)) {
                    if (typeof subPatterns === 'object') {
                        for (const [subCategory, pattern] of Object.entries(subPatterns)) {
                            const matches = content.match(pattern);
                            if (matches) {
                                topics.push(...matches);
                            }
                        }
                    } else {
                        const matches = content.match(subPatterns);
                        if (matches) {
                            topics.push(...matches);
                        }
                    }
                }
            }
        }
        return topics;
    }

    private extractEntities(content: string): string[] {
        const entities: string[] = [];

        // Extract named entities using natural.js
        const namedEntities = this.entityExtractor.extract(content);
        entities.push(...namedEntities);

        // Extract code-specific entities
        const codeEntities = this.extractCodeEntities(content);
        entities.push(...codeEntities);

        // Extract project-specific entities
        const projectEntities = this.extractProjectEntities(content);
        entities.push(...projectEntities);

        return [...new Set(entities)]; // Remove duplicates
    }

    private extractCodeEntities(content: string): string[] {
        const codePatterns = {
            functions: /function\s+(\w+)/g,
            classes: /class\s+(\w+)/g,
            variables: /(?:const|let|var)\s+(\w+)/g,
            imports: /from\s+['"]([^'"]+)['"]/g,
            types: /(?:interface|type)\s+(\w+)/g,
        };

        const entities: string[] = [];
        for (const [type, pattern] of Object.entries(codePatterns)) {
            const matches = content.matchAll(pattern);
            for (const match of matches) {
                if (match[1]) {
                    entities.push(match[1]);
                }
            }
        }
        return entities;
    }

    private extractProjectEntities(content: string): string[] {
        const projectPatterns = {
            files: /(?:file|path):\s*['"]([^'"]+)['"]/g,
            dependencies: /(?:dependencies|devDependencies):\s*{([^}]+)}/g,
            configs: /(?:config|settings):\s*{([^}]+)}/g,
        };

        const entities: string[] = [];
        for (const [type, pattern] of Object.entries(projectPatterns)) {
            const matches = Array.from(content.matchAll(pattern));
            for (const match of matches) {
                if (match[1]) {
                    entities.push(match[1]);
                }
            }
        }
        return entities;
    }

    public searchHistory(projectId: string, query: string): AIAssistantHistory[] {
        const history = this.memory.get(projectId) || [];
        const index = this.memoryIndex.get(projectId);
        if (!index) return [];

        // Search in topics
        const topicResults = Array.from(index.topics.entries())
            .filter(([topic]) => topic.toLowerCase().includes(query.toLowerCase()))
            .flatMap(([_, ids]) => ids);

        // Search in entities
        const entityResults = Array.from(index.entities.entries())
            .filter(([entity]) => entity.toLowerCase().includes(query.toLowerCase()))
            .flatMap(([_, ids]) => ids);

        // Search in commands
        const commandResults = Array.from(index.commands.entries())
            .filter(([cmd]) => cmd.toLowerCase().includes(query.toLowerCase()))
            .flatMap(([_, ids]) => ids);

        // Search in files
        const fileResults = Array.from(index.files.entries())
            .filter(([file]) => file.toLowerCase().includes(query.toLowerCase()))
            .flatMap(([_, ids]) => ids);

        // Combine all results and remove duplicates
        const resultIds = new Set([
            ...topicResults,
            ...entityResults,
            ...commandResults,
            ...fileResults,
        ]);

        return history.filter(entry => resultIds.has(entry.id));
    }

    public getProjectMetadata(projectId: string): ProjectMetadata | undefined {
        return this.projectMetadata.get(projectId);
    }

    public getMemoryIndex(projectId: string): MemoryIndex | undefined {
        return this.memoryIndex.get(projectId);
    }

    public async exportProjectHistory(projectId: string): Promise<ProjectHistoryExport> {
        const history = this.memory.get(projectId) || [];
        const metadata = this.projectMetadata.get(projectId) ?? {
            lastUpdated: new Date().toISOString(),
            totalInteractions: history.length,
            uniqueUsers: new Set(history.map(h => h.metadata?.user || 'anonymous')).size,
            commandStats: new Map(),
            fileStats: new Map(),
            topicStats: new Map(),
            entityStats: new Map(),
        };
        const index = this.memoryIndex.get(projectId) ?? {
            topics: new Map(),
            entities: new Map(),
            commands: new Map(),
            files: new Map(),
            timestamps: new Map(),
        };

        return {
            projectId,
            exportDate: new Date().toISOString(),
            history,
            metadata,
            index,
        };
    }

    public async importProjectHistory(historyExport: ProjectHistoryExport): Promise<void> {
        const { projectId, history, metadata, index } = historyExport;
        
        this.memory.set(projectId, history);
        this.projectMetadata.set(projectId, metadata);
        this.memoryIndex.set(projectId, index);

        await this.saveHistory(history);
    }

    public getProjectHistory(projectId: string): AIAssistantHistory[] {
        return this.memory.get(projectId) || [];
    }

    public getAllProjectIds(): string[] {
        return Array.from(this.memory.keys());
    }

    public clearProjectHistory(projectId: string): void {
        this.memory.delete(projectId);
    }

    private checkMemoryCache(
        message: string,
        context: AIAssistantContext
    ): { history: AIAssistantHistory; suggestions: AIAssistantSuggestion[] } | null {
        const now = Date.now();
        const projectId = context.projectContext.config.projectId || 'default';
        const projectHistory = this.memory.get(projectId) || [];

        // Clean expired cache entries
        for (const [key, value] of Array.from(this.memoryCache.entries())) {
            if (now - value.timestamp > this.CACHE_TTL) {
                this.memoryCache.delete(key);
            }
        }

        // Check for exact matches
        const cacheKey = this.generateCacheKey(message, context);
        const cached = this.memoryCache.get(cacheKey);
        if (cached && now - cached.timestamp <= this.CACHE_TTL) {
            return this.reconstructResponse(cached.content, projectHistory);
        }

        // Check for similar messages in history
        const similarMessage = this.findSimilarMessage(message, projectHistory);
        if (similarMessage) {
            const relevance = this.calculateRelevance(message, similarMessage.content);
            if (relevance >= this.RELEVANCE_THRESHOLD) {
                this.memoryCache.set(cacheKey, {
                    content: similarMessage.content,
                    timestamp: now,
                    relevance,
                });
                return this.reconstructResponse(similarMessage.content, projectHistory);
            }
        }

        return null;
    }

    private async checkSemanticCache(
        message: string,
        context: AIAssistantContext
    ): Promise<{ history: AIAssistantHistory; suggestions: AIAssistantSuggestion[] } | null> {
        const now = Date.now();
        const projectId = context.projectContext.config.projectId || 'default';
        const projectHistory = this.memory.get(projectId) || [];

        // Clean expired cache entries
        for (const [key, value] of Array.from(this.semanticCache.entries())) {
            if (now - value.timestamp > this.CACHE_TTL) {
                this.semanticCache.delete(key);
            }
        }

        // Generate embeddings for the current message
        const messageEmbeddings = await this.generateEmbeddings(message);

        // Find semantically similar messages
        let bestMatch = null;
        let bestSimilarity = 0;

        for (const [key, value] of this.semanticCache.entries()) {
            const similarity = this.calculateCosineSimilarity(messageEmbeddings, value.embeddings);
            if (similarity > bestSimilarity) {
                bestSimilarity = similarity;
                bestMatch = value;
            }
        }

        if (bestMatch && bestSimilarity >= this.RELEVANCE_THRESHOLD) {
            return this.reconstructResponse(bestMatch.content, projectHistory);
        }

        return null;
    }

    private generateCacheKey(message: string, context: AIAssistantContext): string {
        const projectId = context.projectContext.config.projectId || 'default';
        const file = context.currentFile?.path || '';
        const selection = context.selection.text;
        return `${projectId}:${file}:${selection}:${message}`;
    }

    private findSimilarMessage(
        message: string,
        history: AIAssistantHistory[]
    ): AIAssistantHistory | null {
        let bestMatch = null;
        let bestSimilarity = 0;

        for (const entry of history) {
            const similarity = this.calculateRelevance(message, entry.content);
            if (similarity > bestSimilarity) {
                bestSimilarity = similarity;
                bestMatch = entry;
            }
        }

        return bestMatch;
    }

    private calculateRelevance(message1: string, message2: string): number {
        const tokens1 = this.tokenizer.tokenize(message1.toLowerCase()) || [];
        const tokens2 = this.tokenizer.tokenize(message2.toLowerCase()) || [];

        const set1 = new Set<string>(tokens1);
        const set2 = new Set<string>(tokens2);

        const intersection = new Set<string>([...set1].filter(x => set2.has(x)));
        const union = new Set<string>([...set1, ...set2]);

        return intersection.size / union.size;
    }

    private async generateEmbeddings(text: string): Promise<number[]> {
        try {
            // Check cache first
            const cacheKey = this.hashString(text);
            const cachedEmbedding = this.semanticCache.get(cacheKey);
            if (cachedEmbedding && Date.now() - cachedEmbedding.timestamp < this.CACHE_TTL) {
                return cachedEmbedding.embeddings;
            }

            // Use a lightweight model for embeddings with optimization
            const response = await fetch(`${API_BASE_URL}/api/ai/embeddings`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.config.apiKey}`,
                },
                body: JSON.stringify({
                    text,
                    model: 'all-MiniLM-L6-v2',
                    dimensions: 384,
                    optimization: {
                        useQuantization: true,
                        usePruning: true,
                        batchSize: 32,
                        useCache: true,
                    },
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            const embeddings = data.embeddings;

            // Apply dimensionality reduction if needed
            if (embeddings.length > 384) {
                const reducedEmbeddings = await this.reduceDimensionality(embeddings);
                this.semanticCache.set(cacheKey, {
                    embeddings: reducedEmbeddings,
                    timestamp: Date.now(),
                });
                return reducedEmbeddings;
            }

            // Cache the embeddings
            this.semanticCache.set(cacheKey, {
                embeddings,
                timestamp: Date.now(),
            });

            return embeddings;
        } catch (error) {
            console.error('Error generating embeddings:', error);
            return this.generateFallbackEmbeddings(text);
        }
    }

    private async reduceDimensionality(embeddings: number[]): Promise<number[]> {
        try {
            // Use PCA for dimensionality reduction
            const response = await fetch(`${API_BASE_URL}/api/ai/reduce-dimensions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.config.apiKey}`,
                },
                body: JSON.stringify({
                    embeddings,
                    targetDimensions: 384,
                    method: 'pca',
                    preserveVariance: 0.95,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.reducedEmbeddings;
        } catch (error) {
            console.error('Error reducing dimensionality:', error);
            // Fallback to simple truncation
            return embeddings.slice(0, 384);
        }
    }

    private async batchProcessEmbeddings(texts: string[]): Promise<number[][]> {
        const batchSize = 32;
        const results: number[][] = [];

        for (let i = 0; i < texts.length; i += batchSize) {
            const batch = texts.slice(i, i + batchSize);
            const batchPromises = batch.map(text => this.generateEmbeddings(text));
            const batchResults = await Promise.all(batchPromises);
            results.push(...batchResults);
        }

        return results;
    }

    private async optimizeEmbeddings(embeddings: number[]): Promise<number[]> {
        // Apply quantization to reduce memory usage
        const quantizedEmbeddings = this.quantizeEmbeddings(embeddings);
        
        // Apply pruning to remove less important dimensions
        const prunedEmbeddings = this.pruneEmbeddings(quantizedEmbeddings);
        
        // Normalize the embeddings
        return this.normalizeEmbeddings(prunedEmbeddings);
    }

    private quantizeEmbeddings(embeddings: number[]): number[] {
        // Quantize to 8-bit integers to reduce memory usage
        const maxValue = Math.max(...embeddings.map(Math.abs));
        return embeddings.map(val => Math.round((val / maxValue) * 127));
    }

    private pruneEmbeddings(embeddings: number[]): number[] {
        // Remove dimensions with very small values
        const threshold = 0.01;
        return embeddings.map(val => Math.abs(val) < threshold ? 0 : val);
    }

    private normalizeEmbeddings(embeddings: number[]): number[] {
        const magnitude = Math.sqrt(embeddings.reduce((sum, val) => sum + val * val, 0));
        return embeddings.map(val => val / magnitude);
    }

    private generateFallbackEmbeddings(text: string): number[] {
        // Simple token-based embedding as fallback
        const tokens = this.tokenizer.tokenize(text.toLowerCase()) || [];
        const stopwords = natural.stopwords;
        const filteredTokens = tokens.filter(token => 
            token.length > 2 && !stopwords.includes(token)
        );

        // Create a simple frequency-based embedding
        const embedding = new Array(384).fill(0);
        const tokenFreq = new Map<string, number>();

        // Calculate token frequencies
        filteredTokens.forEach(token => {
            tokenFreq.set(token, (tokenFreq.get(token) || 0) + 1);
        });

        // Distribute frequencies across embedding dimensions
        const sortedTokens = Array.from(tokenFreq.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 384);

        sortedTokens.forEach(([token, freq], i) => {
            // Use token hash to distribute across dimensions
            const hash = this.hashString(token);
            const dimension = hash % 384;
            embedding[dimension] = freq;
        });

        // Normalize the embedding
        const magnitude = Math.sqrt(embedding.reduce((sum, val) => sum + val * val, 0));
        return embedding.map(val => val / magnitude);
    }

    private hashString(str: string): number {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return Math.abs(hash);
    }

    private calculateCosineSimilarity(vec1: number[], vec2: number[]): number {
        if (vec1.length !== vec2.length) return 0;
        
        const dotProduct = vec1.reduce((sum, val, i) => sum + val * vec2[i], 0);
        const norm1 = Math.sqrt(vec1.reduce((sum, val) => sum + val * val, 0));
        const norm2 = Math.sqrt(vec2.reduce((sum, val) => sum + val * val, 0));
        
        return dotProduct / (norm1 * norm2);
    }

    private reconstructResponse(
        content: string,
        history: AIAssistantHistory[]
    ): { history: AIAssistantHistory; suggestions: AIAssistantSuggestion[] } {
        const historyEntry: AIAssistantHistory = {
            id: crypto.randomUUID(),
            timestamp: new Date().toISOString(),
            type: 'assistant',
            content,
            metadata: {
                cached: true,
            },
        };

        const suggestions: AIAssistantSuggestion[] = this.extractSuggestionsFromContent(content);

        return { history: historyEntry, suggestions };
    }

    private extractSuggestionsFromContent(content: string): AIAssistantSuggestion[] {
        // Extract suggestions from cached content
        const suggestions: AIAssistantSuggestion[] = [];
        const suggestionPatterns = {
            code: /```(?:(\w+):)?\s*([\s\S]*?)```/g,
            command: /\$([^\n]+)/g,
            fix: /fix:\s*([^\n]+)/g,
        };

        for (const [type, pattern] of Object.entries(suggestionPatterns)) {
            const matches = Array.from(content.matchAll(pattern));
            for (const match of matches) {
                suggestions.push({
                    id: crypto.randomUUID(),
                    type: type as AIAssistantSuggestion['type'],
                    content: match[2] || match[1],
                    confidence: 0.8,
                    context: {},
                    actions: [
                        {
                            id: crypto.randomUUID(),
                            type: 'apply',
                            label: 'Apply',
                            description: 'Apply this suggestion',
                            execute: async () => {
                                console.log('Executing cached suggestion:', match[0]);
                            },
                        },
                    ],
                });
            }
        }

        return suggestions;
    }

    public getAnalytics(projectId: string): AIAssistantAnalytics {
        const metadata = this.projectMetadata.get(projectId);
        if (!metadata) {
            return {
                totalInteractions: 0,
                successfulSuggestions: 0,
                rejectedSuggestions: 0,
                averageConfidence: 0,
                popularCommands: [],
                userFeedback: {
                    helpful: 0,
                    notHelpful: 0,
                },
                performance: {
                    averageResponseTime: 0,
                    errorRate: 0,
                    suggestionAccuracy: 0,
                },
            };
        }

        // Calculate popular commands
        const popularCommands = Array.from(metadata.commandStats.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(([name, count]) => ({ name, count }));

        // Calculate performance metrics
        const performance = {
            averageResponseTime: metadata.performanceMetrics.averageResponseTime,
            errorRate: metadata.performanceMetrics.errorRate,
            suggestionAccuracy: metadata.performanceMetrics.suggestionAccuracy,
        };

        // Calculate user engagement
        const activeHours = Array.from(metadata.userEngagement.activeHours.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3)
            .map(([hour, count]) => ({ hour, count }));

        // Calculate code metrics
        const languageStats = Array.from(metadata.codeMetrics.languageStats.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(([language, count]) => ({ language, count }));

        // Calculate learning metrics
        const skillLevels = Array.from(metadata.learningMetrics.skillLevels.entries())
            .sort((a, b) => b[1] - a[1])
            .map(([level, count]) => ({ level, count }));

        const knowledgeGaps = Array.from(metadata.learningMetrics.knowledgeGaps.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(([area, count]) => ({ area, count }));

        return {
            totalInteractions: metadata.totalInteractions,
            successfulSuggestions: Math.round(metadata.performanceMetrics.suggestionAccuracy * metadata.totalInteractions),
            rejectedSuggestions: Math.round((1 - metadata.performanceMetrics.suggestionAccuracy) * metadata.totalInteractions),
            averageConfidence: this.calculateAverageConfidence(metadata),
            popularCommands,
            userFeedback: {
                helpful: this.calculateHelpfulFeedback(metadata),
                notHelpful: this.calculateNotHelpfulFeedback(metadata),
            },
            performance,
            userEngagement: {
                activeHours,
                averageSessionLength: this.calculateAverageSessionLength(metadata),
                mostUsedFeatures: this.getMostUsedFeatures(metadata),
            },
            codeMetrics: {
                languageStats,
                complexityDistribution: this.getComplexityDistribution(metadata),
                refactoringFrequency: this.getRefactoringFrequency(metadata),
                bugFixRate: this.getBugFixRate(metadata),
            },
            learningMetrics: {
                skillLevels,
                knowledgeGaps,
                improvementAreas: this.getImprovementAreas(metadata),
                topicProgression: this.getTopicProgression(metadata),
            },
        };
    }

    private calculateAverageConfidence(metadata: ProjectMetadata): number {
        let totalConfidence = 0;
        let count = 0;

        metadata.learningMetrics.skillLevels.forEach((count, level) => {
            const confidence = {
                'beginner': 0.3,
                'intermediate': 0.6,
                'advanced': 0.9,
            }[level] || 0.5;
            totalConfidence += confidence * count;
            count += count;
        });

        return count > 0 ? totalConfidence / count : 0;
    }

    private calculateHelpfulFeedback(metadata: ProjectMetadata): number {
        return Array.from(metadata.performanceMetrics.suggestionTypes.values())
            .reduce((sum, count) => sum + count, 0);
    }

    private calculateNotHelpfulFeedback(metadata: ProjectMetadata): number {
        return metadata.performanceMetrics.errorTypes.size;
    }

    private calculateAverageSessionLength(metadata: ProjectMetadata): number {
        const sessionLengths = metadata.userEngagement.sessionLengths;
        if (sessionLengths.length === 0) return 0;
        return sessionLengths.reduce((sum, length) => sum + length, 0) / sessionLengths.length;
    }

    private getMostUsedFeatures(metadata: ProjectMetadata): Array<{ feature: string; count: number }> {
        return Array.from(metadata.userEngagement.featureUsage.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(([feature, count]) => ({ feature, count }));
    }

    private getComplexityDistribution(metadata: ProjectMetadata): Array<{ level: string; count: number }> {
        return Array.from(metadata.codeMetrics.complexityMetrics.entries())
            .sort((a, b) => b[1] - a[1])
            .map(([level, count]) => ({ level, count }));
    }

    private getRefactoringFrequency(metadata: ProjectMetadata): number {
        const totalRefactoring = Array.from(metadata.codeMetrics.refactoringStats.values())
            .reduce((sum, count) => sum + count, 0);
        return totalRefactoring / metadata.totalInteractions;
    }

    private getBugFixRate(metadata: ProjectMetadata): number {
        const totalBugFixes = Array.from(metadata.codeMetrics.bugFixStats.values())
            .reduce((sum, count) => sum + count, 0);
        return totalBugFixes / metadata.totalInteractions;
    }

    private getImprovementAreas(metadata: ProjectMetadata): Array<{ area: string; count: number }> {
        return Array.from(metadata.learningMetrics.improvementAreas.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(([area, count]) => ({ area, count }));
    }

    private getTopicProgression(metadata: ProjectMetadata): Array<{ topic: string; count: number }> {
        return Array.from(metadata.learningMetrics.topicProgression.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(([topic, count]) => ({ topic, count }));
    }

    public getChainOfThought(history: AIAssistantHistory): ChainOfThought {
        if (!history.metadata?.thinkingProcess) {
            return {
                analysis: null,
                reasoning: null,
                implementation: null,
                validation: null,
                confidence: 0,
                complexity: 'low',
            };
        }

        const thinkingProcess = history.metadata.thinkingProcess;
        return {
            analysis: {
                problem: thinkingProcess.analysis.problem,
                context: thinkingProcess.analysis.context,
                constraints: thinkingProcess.analysis.constraints,
                assumptions: thinkingProcess.analysis.assumptions,
                risks: thinkingProcess.analysis.risks,
                keywords: this.extractKeywords(thinkingProcess.analysis.problem),
                sentiment: this.analyzeSentiment(thinkingProcess.analysis.problem),
            },
            reasoning: {
                approach: thinkingProcess.reasoning.approach,
                steps: thinkingProcess.reasoning.steps,
                alternatives: thinkingProcess.reasoning.alternatives.map(alt => ({
                    ...alt,
                    confidence: this.calculateAlternativeConfidence(alt),
                })),
                decision: {
                    ...thinkingProcess.reasoning.decision,
                    alternatives: thinkingProcess.reasoning.alternatives.length,
                },
            },
            implementation: {
                strategy: thinkingProcess.implementation.strategy,
                steps: thinkingProcess.implementation.steps,
                dependencies: thinkingProcess.implementation.dependencies,
                timeline: thinkingProcess.implementation.timeline,
                resources: thinkingProcess.implementation.resources,
                complexity: this.calculateImplementationComplexity(thinkingProcess.implementation),
            },
            validation: {
                criteria: thinkingProcess.validation.criteria,
                tests: thinkingProcess.validation.tests,
                successMetrics: thinkingProcess.validation.successMetrics,
                fallbackPlan: thinkingProcess.validation.fallbackPlan,
                coverage: this.calculateValidationCoverage(thinkingProcess.validation),
            },
            confidence: thinkingProcess.reasoning.decision.confidence,
            complexity: this.calculateOverallComplexity(thinkingProcess),
        };
    }

    private extractKeywords(text: string): string[] {
        const tokens = this.tokenizer.tokenize(text.toLowerCase()) || [];
        const stopwords = natural.stopwords;
        const tfidf = new natural.TfIdf();
        
        // Add document to TF-IDF
        tfidf.addDocument(tokens);
        
        // Get top terms
        const terms = tfidf.listTerms(0);
        return terms
            .filter(term => term.term.length > 2 && !stopwords.includes(term.term))
            .sort((a, b) => b.tfidf - a.tfidf)
            .slice(0, 5)
            .map(term => term.term);
    }

    private analyzeSentiment(text: string): 'positive' | 'negative' | 'neutral' {
        const positiveWords = new Set(['good', 'great', 'excellent', 'perfect', 'success', 'improve', 'enhance', 'optimize']);
        const negativeWords = new Set(['bad', 'poor', 'error', 'issue', 'problem', 'fail', 'bug', 'crash']);

        const tokens = this.tokenizer.tokenize(text.toLowerCase()) || [];
        let positiveCount = 0;
        let negativeCount = 0;

        tokens.forEach(token => {
            if (positiveWords.has(token)) positiveCount++;
            if (negativeWords.has(token)) negativeCount++;
        });

        if (positiveCount > negativeCount) return 'positive';
        if (negativeCount > positiveCount) return 'negative';
        return 'neutral';
    }

    private calculateAlternativeConfidence(alternative: AIAssistantHistory['metadata']['thinkingProcess']['reasoning']['alternatives'][0]): number {
        const prosWeight = alternative.pros.length * 0.4;
        const consWeight = alternative.cons.length * 0.3;
        const feasibilityWeight = alternative.feasibility * 0.3;

        return (prosWeight - consWeight + feasibilityWeight) / 2;
    }

    private calculateImplementationComplexity(implementation: AIAssistantHistory['metadata']['thinkingProcess']['implementation']): 'low' | 'medium' | 'high' {
        const stepCount = implementation.steps.length;
        const dependencyCount = implementation.dependencies.length;
        const resourceCount = implementation.resources.length;

        const complexityScore = (stepCount * 0.4 + dependencyCount * 0.3 + resourceCount * 0.3) / 10;

        if (complexityScore < 0.4) return 'low';
        if (complexityScore < 0.7) return 'medium';
        return 'high';
    }

    private calculateValidationCoverage(validation: AIAssistantHistory['metadata']['thinkingProcess']['validation']): number {
        const criteriaCount = validation.criteria.length;
        const testCount = validation.tests.length;
        const metricCount = validation.successMetrics.length;

        return (criteriaCount * 0.4 + testCount * 0.4 + metricCount * 0.2) / 10;
    }

    private calculateOverallComplexity(thinkingProcess: AIAssistantHistory['metadata']['thinkingProcess']): 'low' | 'medium' | 'high' {
        const analysisComplexity = thinkingProcess.analysis.constraints.length + thinkingProcess.analysis.risks.length;
        const reasoningComplexity = thinkingProcess.reasoning.steps.length + thinkingProcess.reasoning.alternatives.length;
        const implementationComplexity = thinkingProcess.implementation.steps.length + thinkingProcess.implementation.dependencies.length;
        const validationComplexity = thinkingProcess.validation.criteria.length + thinkingProcess.validation.tests.length;

        const totalComplexity = (
            analysisComplexity * 0.2 +
            reasoningComplexity * 0.3 +
            implementationComplexity * 0.3 +
            validationComplexity * 0.2
        ) / 10;

        if (totalComplexity < 0.4) return 'low';
        if (totalComplexity < 0.7) return 'medium';
        return 'high';
    }
}

interface ProjectMetadata {
    lastUpdated: string;
    totalInteractions: number;
    uniqueUsers: number;
    commandStats: Map<string, number>;
    fileStats: Map<string, number>;
    topicStats: Map<string, number>;
    entityStats: Map<string, number>;
}

interface MemoryIndex {
    topics: Map<string, string[]>;
    entities: Map<string, string[]>;
    commands: Map<string, string[]>;
    files: Map<string, string[]>;
    timestamps: Map<string, Date>;
}

interface ProjectHistoryExport {
    projectId: string;
    exportDate: string;
    history: AIAssistantHistory[];
    metadata: ProjectMetadata;
    index: MemoryIndex;
} 