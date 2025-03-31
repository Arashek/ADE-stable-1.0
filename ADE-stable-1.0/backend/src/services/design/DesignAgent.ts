import { OpenAI } from 'openai';
import { MidjourneyAPI } from './providers/midjourney';
import { DallE3API } from './providers/dalle';
import { ClaudeAPI } from './providers/claude';
import { DesignCache } from './cache/DesignCache';
import { ProjectContext } from '../../types/ProjectContext';
import { DesignRequest, DesignResponse, UIComponent, DesignFeedback } from './types';
import { ConfigService } from '../config/ConfigService';
import { Logger } from '../logging/Logger';

export class DesignAgent {
    private static instance: DesignAgent;
    private openai: OpenAI;
    private midjourney: MidjourneyAPI;
    private dalle: DallE3API;
    private claude: ClaudeAPI;
    private cache: DesignCache;
    private config: ConfigService;
    private logger: Logger;

    private constructor() {
        this.config = ConfigService.getInstance();
        this.logger = Logger.getInstance();
        this.cache = new DesignCache();
        
        // Initialize AI providers
        this.initializeProviders();
    }

    public static getInstance(): DesignAgent {
        if (!DesignAgent.instance) {
            DesignAgent.instance = new DesignAgent();
        }
        return DesignAgent.instance;
    }

    private async initializeProviders() {
        // Initialize with appropriate API keys and configurations
        this.openai = new OpenAI({
            apiKey: this.config.get('OPENAI_API_KEY'),
        });

        this.midjourney = new MidjourneyAPI(
            this.config.get('MIDJOURNEY_API_KEY')
        );

        this.dalle = new DallE3API(
            this.config.get('DALLE_API_KEY')
        );

        this.claude = new ClaudeAPI(
            this.config.get('ANTHROPIC_API_KEY')
        );
    }

    public async generateUIMockup(request: DesignRequest): Promise<DesignResponse> {
        try {
            // Check cache first
            const cachedDesign = this.cache.get(request.id);
            if (cachedDesign) {
                return cachedDesign;
            }

            // Use Claude for high-level design reasoning
            const designSpec = await this.claude.generateDesignSpec({
                requirements: request.requirements,
                context: request.projectContext,
                constraints: request.constraints
            });

            // Generate visual mockup using DALL-E 3
            const mockupImage = await this.dalle.generateImage({
                prompt: designSpec.visualPrompt,
                style: request.style,
                dimensions: request.dimensions
            });

            // Generate CSS/SCSS using GPT-4
            const styles = await this.openai.chat.completions.create({
                model: "gpt-4",
                messages: [{
                    role: "system",
                    content: "You are an expert frontend developer. Generate clean, maintainable CSS/SCSS code for the following design specification."
                }, {
                    role: "user",
                    content: JSON.stringify(designSpec)
                }]
            });

            const response: DesignResponse = {
                id: request.id,
                mockup: mockupImage,
                styles: styles.choices[0].message.content,
                components: designSpec.components,
                designSystem: designSpec.designSystem,
                timestamp: new Date().toISOString()
            };

            // Cache the result
            this.cache.set(request.id, response);

            return response;
        } catch (error) {
            this.logger.error('Error in generateUIMockup:', error);
            throw error;
        }
    }

    public async analyzeExistingDesign(design: UIComponent): Promise<DesignFeedback> {
        try {
            // Use Claude for design analysis
            const analysis = await this.claude.analyzeDesign({
                component: design,
                context: design.context
            });

            // Get improvement suggestions from GPT-4
            const suggestions = await this.openai.chat.completions.create({
                model: "gpt-4",
                messages: [{
                    role: "system",
                    content: "You are an expert UI/UX designer. Analyze the design and provide specific, actionable improvements."
                }, {
                    role: "user",
                    content: JSON.stringify(analysis)
                }]
            });

            return {
                analysis: analysis,
                suggestions: suggestions.choices[0].message.content,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            this.logger.error('Error in analyzeExistingDesign:', error);
            throw error;
        }
    }

    public async generateVisualAssets(request: DesignRequest): Promise<string[]> {
        try {
            // Use Midjourney for detailed visual assets
            const assets = await this.midjourney.generateAssets({
                prompt: request.assetRequirements,
                style: request.style,
                format: request.assetFormat
            });

            return assets;
        } catch (error) {
            this.logger.error('Error in generateVisualAssets:', error);
            throw error;
        }
    }
} 