import axios from 'axios';

export class MidjourneyAPI {
    private apiKey: string;
    private baseUrl: string;

    constructor(apiKey: string) {
        this.apiKey = apiKey;
        this.baseUrl = 'https://api.midjourney.com/v1';
    }

    public async generateAssets(params: {
        prompt: string[];
        style?: {
            colorScheme?: string;
            layout?: string;
        };
        format?: 'svg' | 'png' | 'jpg';
    }): Promise<string[]> {
        try {
            const enhancedPrompts = params.prompt.map(prompt => 
                this.buildAssetPrompt(prompt, params.style)
            );

            const results = await Promise.all(
                enhancedPrompts.map(prompt =>
                    this.generateSingleAsset(prompt, params.format)
                )
            );

            return results.filter(Boolean) as string[];
        } catch (error) {
            console.error('Error generating assets:', error);
            throw error;
        }
    }

    private async generateSingleAsset(
        prompt: string,
        format: 'svg' | 'png' | 'jpg' = 'svg'
    ): Promise<string | null> {
        try {
            const response = await axios.post(
                `${this.baseUrl}/imagine`,
                {
                    prompt,
                    format,
                    quality: 'high',
                    style: 'icon',
                },
                {
                    headers: {
                        'Authorization': `Bearer ${this.apiKey}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (response.data && response.data.result) {
                return response.data.result;
            }

            return null;
        } catch (error) {
            console.error('Error generating single asset:', error);
            return null;
        }
    }

    private buildAssetPrompt(
        basePrompt: string,
        style?: {
            colorScheme?: string;
            layout?: string;
        }
    ): string {
        let enhancedPrompt = `Create a minimalist, professional ${basePrompt}`;

        if (style) {
            const { colorScheme, layout } = style;
            
            if (colorScheme) {
                enhancedPrompt += ` using ${colorScheme} colors`;
            }
            
            if (layout) {
                enhancedPrompt += ` with ${layout} composition`;
            }
        }

        enhancedPrompt += ' --style modern-icon --quality high --no-text';
        
        return enhancedPrompt;
    }
} 