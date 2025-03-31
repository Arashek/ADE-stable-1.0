import React, { useState, useEffect } from 'react';
import { FigmaService } from '../../../backend/src/services/design/FigmaService';
import { DesignSystem } from '../../../types/design';
import { DesignAgent } from '../../../services/DesignAgent';

interface FigmaIntegrationProps {
  onFileSelect: (fileKey: string) => void;
  onComponentSelect: (componentKey: string) => void;
  onStyleSelect: (styleKey: string) => void;
  onDesignUpdate: (design: Partial<DesignSystem>) => void;
  onFinalize: (design: DesignSystem) => void;
  designAgent: DesignAgent;
}

export const FigmaIntegration: React.FC<FigmaIntegrationProps> = ({
  onFileSelect,
  onComponentSelect,
  onStyleSelect,
  onDesignUpdate,
  onFinalize,
  designAgent,
}) => {
  const [accessToken, setAccessToken] = useState<string>('');
  const [teamId, setTeamId] = useState<string>('');
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [files, setFiles] = useState<any[]>([]);
  const [components, setComponents] = useState<any[]>([]);
  const [styles, setStyles] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [selectedDesign, setSelectedDesign] = useState<Partial<DesignSystem>>({});

  const figmaService = new FigmaService(
    { accessToken, teamId },
    {} as any, // Mock DB service
    {} as any  // Mock File service
  );

  const handleAuthenticate = async () => {
    try {
      setLoading(true);
      setError('');
      const isValid = await figmaService.validateAccessToken();
      setIsAuthenticated(isValid);
      if (!isValid) {
        setError('Invalid access token');
      }
    } catch (err) {
      setError('Failed to authenticate with Figma');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadFiles = async () => {
    if (!isAuthenticated) return;

    try {
      setLoading(true);
      setError('');
      const mockFiles = [
        { key: 'file1', name: 'Design System' },
        { key: 'file2', name: 'UI Components' },
      ];
      setFiles(mockFiles);
    } catch (err) {
      setError('Failed to load Figma files');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadComponents = async () => {
    if (!isAuthenticated || !teamId) return;

    try {
      setLoading(true);
      setError('');
      const teamComponents = await figmaService.getTeamComponents(teamId);
      setComponents(teamComponents);
    } catch (err) {
      setError('Failed to load components');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadStyles = async () => {
    if (!isAuthenticated || !teamId) return;

    try {
      setLoading(true);
      setError('');
      const teamStyles = await figmaService.getTeamStyles(teamId);
      setStyles(teamStyles);
    } catch (err) {
      setError('Failed to load styles');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleComponentSelect = async (componentKey: string) => {
    try {
      const component = components.find(c => c.key === componentKey);
      if (!component) return;

      // Get component details from Figma
      const componentDetails = await figmaService.getFileNodes(component.file_key, [component.node_id]);
      const node = componentDetails[component.node_id];

      // Update design system with component
      const updatedDesign = {
        ...selectedDesign,
        components: [
          ...(selectedDesign.components || []),
          {
            id: component.key,
            name: component.name,
            type: node.type,
            properties: node.componentProperties,
            styles: node.styles,
          },
        ],
      };

      setSelectedDesign(updatedDesign);
      onDesignUpdate(updatedDesign);
      onComponentSelect(componentKey);

      // Notify design agent about the new component
      await designAgent.handleComponentAddition(component);
    } catch (err) {
      setError('Failed to process component');
      console.error(err);
    }
  };

  const handleStyleSelect = async (styleKey: string) => {
    try {
      const style = styles.find(s => s.key === styleKey);
      if (!style) return;

      // Update design system with style
      const updatedDesign = {
        ...selectedDesign,
        styles: [
          ...(selectedDesign.styles || []),
          {
            id: style.key,
            name: style.name,
            type: style.styleType,
            value: style.description,
          },
        ],
      };

      setSelectedDesign(updatedDesign);
      onDesignUpdate(updatedDesign);
      onStyleSelect(styleKey);

      // Notify design agent about the new style
      await designAgent.handleStyleAddition(style);
    } catch (err) {
      setError('Failed to process style');
      console.error(err);
    }
  };

  const handleFinalize = async () => {
    try {
      // Validate design system
      const validationResult = await designAgent.validateDesign(selectedDesign);
      if (!validationResult.isValid) {
        setError(validationResult.errors.join(', '));
        return;
      }

      // Generate implementation details
      const implementation = await designAgent.generateImplementation(selectedDesign);
      
      // Create final design system
      const finalDesign: DesignSystem = {
        ...selectedDesign,
        implementation,
        metadata: {
          source: 'figma',
          lastModified: new Date().toISOString(),
          version: '1.0.0',
        },
      };

      // Trigger finalization process
      onFinalize(finalDesign);
    } catch (err) {
      setError('Failed to finalize design');
      console.error(err);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      handleLoadFiles();
      handleLoadComponents();
      handleLoadStyles();
    }
  }, [isAuthenticated, teamId]);

  return (
    <div className="p-4 border rounded-lg shadow-sm">
      <h2 className="text-lg font-semibold mb-4">Figma Integration</h2>

      {/* Authentication */}
      <div className="mb-4">
        <div className="flex gap-2 mb-2">
          <input
            type="password"
            placeholder="Figma Access Token"
            value={accessToken}
            onChange={(e) => setAccessToken(e.target.value)}
            className="flex-1 px-3 py-2 border rounded"
          />
          <input
            type="text"
            placeholder="Team ID"
            value={teamId}
            onChange={(e) => setTeamId(e.target.value)}
            className="flex-1 px-3 py-2 border rounded"
          />
          <button
            onClick={handleAuthenticate}
            disabled={loading}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? 'Authenticating...' : 'Authenticate'}
          </button>
        </div>
        {error && <p className="text-red-500 text-sm">{error}</p>}
      </div>

      {isAuthenticated && (
        <>
          {/* Files */}
          <div className="mb-4">
            <h3 className="text-md font-medium mb-2">Files</h3>
            <div className="grid grid-cols-2 gap-2">
              {files.map((file) => (
                <button
                  key={file.key}
                  onClick={() => onFileSelect(file.key)}
                  className="p-2 border rounded hover:bg-gray-50 text-left"
                >
                  {file.name}
                </button>
              ))}
            </div>
          </div>

          {/* Components */}
          <div className="mb-4">
            <h3 className="text-md font-medium mb-2">Components</h3>
            <div className="grid grid-cols-2 gap-2">
              {components.map((component) => (
                <button
                  key={component.key}
                  onClick={() => handleComponentSelect(component.key)}
                  className="p-2 border rounded hover:bg-gray-50 text-left"
                >
                  {component.name}
                </button>
              ))}
            </div>
          </div>

          {/* Styles */}
          <div className="mb-4">
            <h3 className="text-md font-medium mb-2">Styles</h3>
            <div className="grid grid-cols-2 gap-2">
              {styles.map((style) => (
                <button
                  key={style.key}
                  onClick={() => handleStyleSelect(style.key)}
                  className="p-2 border rounded hover:bg-gray-50 text-left"
                >
                  {style.name}
                </button>
              ))}
            </div>
          </div>

          {/* Finalize Button */}
          <div className="mt-4">
            <button
              onClick={handleFinalize}
              disabled={!selectedDesign.components?.length}
              className="w-full px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
            >
              Finalize Design
            </button>
          </div>
        </>
      )}
    </div>
  );
}; 