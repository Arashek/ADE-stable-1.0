import OpenAI from 'openai';

export class DallE3API {
    private client: OpenAI;
    private readonly model = 'dall-e-3';

    constructor(apiKey: string) {
        this.client = new OpenAI({
            apiKey: apiKey
        });
    }

    public async generateImage(params: {
        prompt: string;
        style?: {
            colorScheme?: string;
            typography?: string;
            spacing?: string;
            layout?: string;
        };
        dimensions?: {
            width: number;
            height: number;
        };
    }): Promise<string> {
        try {
            const enhancedPrompt = this.buildImagePrompt(params);
            
            const response = await this.client.images.generate({
                model: this.model,
                prompt: enhancedPrompt,
                n: 1,
                size: this.getDimensions(params.dimensions),
                response_format: 'b64_json'
            });

            return response.data[0].b64_json || '';
        } catch (error) {
            console.error('Error generating image:', error);
            throw error;
        }
    }

    private buildImagePrompt(params: {
        prompt: string;
        style?: {
            colorScheme?: string;
            typography?: string;
            spacing?: string;
            layout?: string;
        };
    }): string {
        let enhancedPrompt = params.prompt;

        if (params.style) {
            const { colorScheme, typography, spacing, layout } = params.style;
            
            if (colorScheme) {
                enhancedPrompt += ` Use a ${colorScheme} color scheme.`;
            }
            
            if (typography) {
                enhancedPrompt += ` Apply ${typography} typography style.`;
            }
            
            if (spacing) {
                enhancedPrompt += ` Maintain ${spacing} spacing between elements.`;
            }
            
            if (layout) {
                enhancedPrompt += ` Follow a ${layout} layout structure.`;
            }
        }

        enhancedPrompt += ' The image should be a clean, professional UI design with clear hierarchy and modern aesthetics.';
        
        return enhancedPrompt;
    }

    private getDimensions(dimensions?: { width: number; height: number }): string {
        if (!dimensions) {
            return '1024x1024';
        }

        // DALL-E 3 supports specific dimensions
        const validSizes = ['1024x1024', '1024x1792', '1792x1024'];
        const requestedSize = `${dimensions.width}x${dimensions.height}`;
        
        if (validSizes.includes(requestedSize)) {
            return requestedSize;
        }

        // Default to square if invalid dimensions
        return '1024x1024';
    }
} 