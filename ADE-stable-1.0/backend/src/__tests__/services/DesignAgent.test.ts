import { DesignAgent } from '../../services/design/DesignAgent';
import { ClaudeAPI } from '../../services/design/providers/claude';
import { DallE3API } from '../../services/design/providers/dalle';
import { MidjourneyAPI } from '../../services/design/providers/midjourney';
import { DesignCache } from '../../services/design/cache/DesignCache';
import { ConfigService } from '../../services/config/ConfigService';
import { Logger } from '../../services/logging/Logger';

jest.mock('../../services/design/providers/claude');
jest.mock('../../services/design/providers/dalle');
jest.mock('../../services/design/providers/midjourney');
jest.mock('../../services/design/cache/DesignCache');
jest.mock('../../services/config/ConfigService');
jest.mock('../../services/logging/Logger');

describe('DesignAgent', () => {
    let designAgent: DesignAgent;
    let mockClaudeAPI: jest.Mocked<ClaudeAPI>;
    let mockDallE3API: jest.Mocked<DallE3API>;
    let mockMidjourneyAPI: jest.Mocked<MidjourneyAPI>;
    let mockCache: jest.Mocked<DesignCache>;

    const mockRequest = {
        id: 'test-id',
        requirements: ['responsive layout', 'modern design'],
        projectContext: {
            name: 'Test Project',
            description: 'A test project',
            type: 'web' as const,
            framework: 'react',
            dependencies: {},
        },
        style: {
            colorScheme: 'light',
            typography: 'modern',
        },
        dimensions: {
            width: 1024,
            height: 1024,
        },
    };

    const mockDesignSpec = {
        components: [],
        designSystem: {
            colors: {},
            typography: { fontFamily: 'Arial', headings: {}, body: {} },
            spacing: { unit: 8, scale: [1, 2, 3] },
            breakpoints: {},
        },
        visualPrompt: 'A modern web interface',
    };

    beforeEach(() => {
        jest.clearAllMocks();

        // Setup mock implementations
        (ConfigService.getInstance as jest.Mock).mockReturnValue({
            get: jest.fn().mockReturnValue('test-api-key'),
        });

        (Logger.getInstance as jest.Mock).mockReturnValue({
            error: jest.fn(),
            info: jest.fn(),
        });

        mockCache = new DesignCache() as jest.Mocked<DesignCache>;
        mockClaudeAPI = new ClaudeAPI('test-key') as jest.Mocked<ClaudeAPI>;
        mockDallE3API = new DallE3API('test-key') as jest.Mocked<DallE3API>;
        mockMidjourneyAPI = new MidjourneyAPI('test-key') as jest.Mocked<MidjourneyAPI>;

        designAgent = DesignAgent.getInstance();
    });

    describe('generateUIMockup', () => {
        it('should return cached response if available', async () => {
            const cachedResponse = {
                id: 'test-id',
                mockup: 'cached-mockup',
                styles: 'cached-styles',
                components: [],
                designSystem: mockDesignSpec.designSystem,
                timestamp: new Date().toISOString(),
            };

            mockCache.get.mockReturnValue(cachedResponse);

            const result = await designAgent.generateUIMockup(mockRequest);

            expect(result).toEqual(cachedResponse);
            expect(mockClaudeAPI.generateDesignSpec).not.toHaveBeenCalled();
            expect(mockDallE3API.generateImage).not.toHaveBeenCalled();
        });

        it('should generate new mockup if no cache exists', async () => {
            mockCache.get.mockReturnValue(null);
            mockClaudeAPI.generateDesignSpec.mockResolvedValue(mockDesignSpec);
            mockDallE3API.generateImage.mockResolvedValue('generated-image');

            const result = await designAgent.generateUIMockup(mockRequest);

            expect(result).toMatchObject({
                id: mockRequest.id,
                mockup: 'generated-image',
            });
            expect(mockClaudeAPI.generateDesignSpec).toHaveBeenCalledWith({
                requirements: mockRequest.requirements,
                context: mockRequest.projectContext,
                constraints: undefined,
            });
            expect(mockDallE3API.generateImage).toHaveBeenCalled();
            expect(mockCache.set).toHaveBeenCalled();
        });

        it('should handle errors gracefully', async () => {
            mockCache.get.mockReturnValue(null);
            mockClaudeAPI.generateDesignSpec.mockRejectedValue(new Error('API Error'));

            await expect(designAgent.generateUIMockup(mockRequest)).rejects.toThrow('API Error');
        });
    });

    describe('analyzeExistingDesign', () => {
        const mockDesign = {
            id: 'test-component',
            name: 'Test Component',
            type: 'button',
            props: {},
            styles: '',
        };

        const mockAnalysis = {
            usability: { score: 85, issues: [], recommendations: [] },
            accessibility: { score: 90, issues: [], recommendations: [] },
            consistency: { score: 95, issues: [], recommendations: [] },
            performance: { score: 88, issues: [], recommendations: [] },
        };

        it('should analyze design and return feedback', async () => {
            mockClaudeAPI.analyzeDesign.mockResolvedValue(mockAnalysis);

            const result = await designAgent.analyzeExistingDesign(mockDesign);

            expect(result).toMatchObject({
                analysis: mockAnalysis,
                timestamp: expect.any(String),
            });
            expect(mockClaudeAPI.analyzeDesign).toHaveBeenCalledWith({
                component: mockDesign,
                context: mockDesign.context,
            });
        });

        it('should handle analysis errors gracefully', async () => {
            mockClaudeAPI.analyzeDesign.mockRejectedValue(new Error('Analysis Error'));

            await expect(designAgent.analyzeExistingDesign(mockDesign)).rejects.toThrow('Analysis Error');
        });
    });

    describe('generateVisualAssets', () => {
        const mockAssetRequest = {
            ...mockRequest,
            assetRequirements: ['icon-home', 'icon-settings'],
            assetFormat: 'svg' as const,
        };

        it('should generate visual assets successfully', async () => {
            const mockAssets = ['asset1-data', 'asset2-data'];
            mockMidjourneyAPI.generateAssets.mockResolvedValue(mockAssets);

            const result = await designAgent.generateVisualAssets(mockAssetRequest);

            expect(result).toEqual(mockAssets);
            expect(mockMidjourneyAPI.generateAssets).toHaveBeenCalledWith({
                prompt: mockAssetRequest.assetRequirements,
                style: mockAssetRequest.style,
                format: mockAssetRequest.assetFormat,
            });
        });

        it('should handle asset generation errors gracefully', async () => {
            mockMidjourneyAPI.generateAssets.mockRejectedValue(new Error('Asset Generation Error'));

            await expect(designAgent.generateVisualAssets(mockAssetRequest)).rejects.toThrow('Asset Generation Error');
        });
    });

    describe('singleton pattern', () => {
        it('should always return the same instance', () => {
            const instance1 = DesignAgent.getInstance();
            const instance2 = DesignAgent.getInstance();

            expect(instance1).toBe(instance2);
        });
    });
}); 