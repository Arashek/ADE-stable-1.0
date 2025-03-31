import type { Meta, StoryObj, StoryFn } from '@storybook/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import AIReviewPanel from './AIReviewPanel';
import { CodeQualityService, CodeIssue } from '../../services/codeAnalysis/CodeQualityService';
import React from 'react';

// Mock the CodeQualityService
const mockService = {
  subscribeToAnalysis: (_: string, callback: Function) => {
    callback(defaultAnalysis);
    return () => {};
  },
  getCachedAnalysis: () => defaultAnalysis,
};

(CodeQualityService.getInstance as jest.Mock) = jest.fn(() => mockService);

const defaultAnalysis = {
  metrics: {
    complexity: 0.75,
    maintainability: 0.85,
    testability: 0.90,
    security: 0.95,
    performance: 0.80,
  },
  issues: [
    {
      id: '1',
      type: 'error',
      message: 'Unused variable detected',
      line: 10,
      column: 5,
      severity: 2,
      rule: 'no-unused-vars',
      fix: {
        description: 'Remove unused variable',
        code: 'const unusedVar = 5;',
      },
    },
    {
      id: '2',
      type: 'warning',
      message: 'Function is too complex (cyclomatic complexity: 15)',
      line: 25,
      column: 1,
      severity: 1,
      rule: 'complexity',
      fix: {
        description: 'Consider breaking down this function into smaller functions',
        code: '// Example refactoring suggestion...',
      },
    },
    {
      id: '3',
      type: 'info',
      message: 'Consider adding type annotation',
      line: 42,
      column: 3,
      severity: 0,
      rule: 'explicit-types',
      fix: null,
    },
  ],
  aiInsights: [
    'The code could benefit from better error handling',
    'Consider implementing the Strategy pattern for better maintainability',
    'Unit tests coverage could be improved for edge cases',
  ],
};

const theme = createTheme();

const meta = {
  title: 'Code Review/AIReviewPanel',
  component: AIReviewPanel,
  parameters: {
    layout: 'fullscreen',
  },
  decorators: [
    (Story: StoryFn) => (
      <ThemeProvider theme={theme}>
        <div style={{ height: '100vh', padding: '20px' }}>
          <Story />
        </div>
      </ThemeProvider>
    ),
  ],
  tags: ['autodocs'],
} satisfies Meta<typeof AIReviewPanel>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    filePath: 'src/components/Example.tsx',
    onFixApply: (fix: CodeIssue['fix']) => console.log('Fix applied:', fix),
    onNavigateToIssue: (line: number, column: number) => console.log('Navigate to:', { line, column }),
  },
};

// Story with no issues
const noIssuesAnalysis = {
  ...defaultAnalysis,
  issues: [],
};

export const NoIssues: Story = {
  args: {
    ...Default.args,
  },
  parameters: {
    mockData: {
      analysis: noIssuesAnalysis,
    },
  },
  decorators: [
    (Story: React.ComponentType) => {
      const mockService = {
        subscribeToAnalysis: (_: string, callback: Function) => {
          callback(noIssuesAnalysis);
          return () => {};
        },
        getCachedAnalysis: () => noIssuesAnalysis,
      };
      (CodeQualityService.getInstance as jest.Mock).mockReturnValue(mockService);
      return <Story />;
    },
  ],
};

// Story with loading state
export const Loading: Story = {
  args: {
    ...Default.args,
  },
  decorators: [
    (Story: StoryFn) => {
      const mockService = {
        subscribeToAnalysis: () => () => {},
        getCachedAnalysis: () => null,
      };
      (CodeQualityService.getInstance as jest.Mock).mockReturnValue(mockService);
      return <Story />;
    },
  ],
};

// Story with only metrics
const onlyMetricsAnalysis = {
  metrics: defaultAnalysis.metrics,
  issues: [],
  aiInsights: [],
};

export const OnlyMetrics: Story = {
  args: {
    ...Default.args,
  },
  parameters: {
    mockData: {
      analysis: onlyMetricsAnalysis,
    },
  },
  decorators: [
    (Story: StoryFn) => {
      const mockService = {
        subscribeToAnalysis: (_: string, callback: Function) => {
          callback(onlyMetricsAnalysis);
          return () => {};
        },
        getCachedAnalysis: () => onlyMetricsAnalysis,
      };
      (CodeQualityService.getInstance as jest.Mock).mockReturnValue(mockService);
      return <Story />;
    },
  ],
};

// Story with only AI insights
const onlyInsightsAnalysis = {
  metrics: {},
  issues: [],
  aiInsights: defaultAnalysis.aiInsights,
};

export const OnlyInsights: Story = {
  args: {
    ...Default.args,
  },
  parameters: {
    mockData: {
      analysis: onlyInsightsAnalysis,
    },
  },
  decorators: [
    (Story: StoryFn) => {
      const mockService = {
        subscribeToAnalysis: (_: string, callback: Function) => {
          callback(onlyInsightsAnalysis);
          return () => {};
        },
        getCachedAnalysis: () => onlyInsightsAnalysis,
      };
      (CodeQualityService.getInstance as jest.Mock).mockReturnValue(mockService);
      return <Story />;
    },
  ],
};

// Story with many issues
const manyIssuesAnalysis = {
  ...defaultAnalysis,
  issues: Array(20).fill(null).map((_, index) => ({
    id: `issue-${index}`,
    type: ['error', 'warning', 'info', 'suggestion'][index % 4],
    message: `Issue ${index + 1}: ${['Unused variable', 'Complex function', 'Missing type', 'Consider refactoring'][index % 4]}`,
    line: index * 5,
    column: 1,
    severity: index % 3,
    rule: ['no-unused-vars', 'complexity', 'explicit-types', 'clean-code'][index % 4],
    fix: index % 2 === 0 ? {
      description: `Fix for issue ${index + 1}`,
      code: `// Example fix for issue ${index + 1}`,
    } : null,
  })),
};

export const ManyIssues: Story = {
  args: {
    ...Default.args,
  },
  parameters: {
    mockData: {
      analysis: manyIssuesAnalysis,
    },
  },
  decorators: [
    (Story: StoryFn) => {
      const mockService = {
        subscribeToAnalysis: (_: string, callback: Function) => {
          callback(manyIssuesAnalysis);
          return () => {};
        },
        getCachedAnalysis: () => manyIssuesAnalysis,
      };
      (CodeQualityService.getInstance as jest.Mock).mockReturnValue(mockService);
      return <Story />;
    },
  ],
}; 