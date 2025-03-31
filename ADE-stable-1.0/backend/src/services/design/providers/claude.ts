import Anthropic from '@anthropic-ai/sdk';
import { UIComponent } from '../types';

export class ClaudeAPI {
    private client: Anthropic;
    private readonly model = 'claude-3-opus-20240229';

    constructor(apiKey: string) {
        this.client = new Anthropic({
            apiKey: apiKey
        });
    }

    public async generateDesignSpec(params: {
        requirements: string[];
        context: any;
        constraints: any;
    }): Promise<any> {
        try {
            const prompt = this.buildDesignSpecPrompt(params);
            
            const response = await this.client.messages.create({
                model: this.model,
                max_tokens: 4096,
                messages: [{
                    role: 'user',
                    content: prompt
                }]
            });

            return JSON.parse(response.content[0].text);
        } catch (error) {
            console.error('Error generating design spec:', error);
            throw error;
        }
    }

    public async analyzeDesign(params: {
        component: UIComponent;
        context: any;
    }): Promise<any> {
        try {
            const prompt = this.buildDesignAnalysisPrompt(params);
            
            const response = await this.client.messages.create({
                model: this.model,
                max_tokens: 4096,
                messages: [{
                    role: 'user',
                    content: prompt
                }]
            });

            return JSON.parse(response.content[0].text);
        } catch (error) {
            console.error('Error analyzing design:', error);
            throw error;
        }
    }

    private buildDesignSpecPrompt(params: {
        requirements: string[];
        context: any;
        constraints: any;
    }): string {
        return `As an expert UI/UX designer, create a comprehensive design specification based on the following requirements and context:

Requirements:
${params.requirements.map(req => `- ${req}`).join('\n')}

Project Context:
${JSON.stringify(params.context, null, 2)}

Constraints:
${JSON.stringify(params.constraints, null, 2)}

Please provide a detailed design specification in JSON format that includes:
1. Visual design elements (colors, typography, spacing)
2. Component hierarchy and structure
3. Interaction patterns
4. Responsive design considerations
5. Accessibility features
6. Visual prompt for image generation

The response should be a valid JSON object with the following structure:
{
    "components": [...],
    "designSystem": {...},
    "visualPrompt": "string"
}`;
    }

    private buildDesignAnalysisPrompt(params: {
        component: UIComponent;
        context: any;
    }): string {
        return `As an expert UI/UX designer, analyze the following UI component and its context:

Component:
${JSON.stringify(params.component, null, 2)}

Context:
${JSON.stringify(params.context, null, 2)}

Please provide a detailed analysis in JSON format that includes:
1. Usability assessment
2. Accessibility evaluation
3. Visual consistency check
4. Performance considerations
5. Specific recommendations for improvement

The response should be a valid JSON object with the following structure:
{
    "usability": { "score": number, "issues": [], "recommendations": [] },
    "accessibility": { "score": number, "issues": [], "recommendations": [] },
    "consistency": { "score": number, "issues": [], "recommendations": [] },
    "performance": { "score": number, "issues": [], "recommendations": [] }
}`;
    }
} 