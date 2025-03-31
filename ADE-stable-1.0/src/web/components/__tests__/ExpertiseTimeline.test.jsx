import React from 'react';
import { render, screen } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material';
import ExpertiseTimeline from '../ExpertiseTimeline';

// Mock data
const mockExpertiseData = {
  'python': 0.8,
  'javascript': 0.6,
  'typescript': 0.7
};

const mockLearningHistory = [
  {
    topic: 'Python Basics',
    timestamp: '2024-01-01T00:00:00Z',
    content: 'Learned Python fundamentals'
  },
  {
    topic: 'JavaScript Advanced',
    timestamp: '2024-01-02T00:00:00Z',
    content: 'Advanced JavaScript concepts'
  },
  {
    topic: 'TypeScript Introduction',
    timestamp: '2024-01-03T00:00:00Z',
    content: 'Started learning TypeScript'
  }
];

// Helper function to render with theme
const renderWithTheme = (component) => {
  const theme = createTheme();
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('ExpertiseTimeline', () => {
  it('renders without crashing', () => {
    renderWithTheme(
      <ExpertiseTimeline
        expertiseData={mockExpertiseData}
        learningHistory={mockLearningHistory}
      />
    );
    expect(screen.getByText('Expertise Development')).toBeInTheDocument();
  });

  it('renders with empty data', () => {
    renderWithTheme(
      <ExpertiseTimeline
        expertiseData={{}}
        learningHistory={[]}
      />
    );
    expect(screen.getByText('Expertise Development')).toBeInTheDocument();
  });

  it('displays all expertise domains', () => {
    renderWithTheme(
      <ExpertiseTimeline
        expertiseData={mockExpertiseData}
        learningHistory={mockLearningHistory}
      />
    );
    
    expect(screen.getByText('python')).toBeInTheDocument();
    expect(screen.getByText('javascript')).toBeInTheDocument();
    expect(screen.getByText('typescript')).toBeInTheDocument();
  });

  it('displays correct expertise levels', () => {
    renderWithTheme(
      <ExpertiseTimeline
        expertiseData={mockExpertiseData}
        learningHistory={mockLearningHistory}
      />
    );
    
    expect(screen.getByText('80.0%')).toBeInTheDocument();
    expect(screen.getByText('60.0%')).toBeInTheDocument();
    expect(screen.getByText('70.0%')).toBeInTheDocument();
  });

  it('displays info tooltip', () => {
    renderWithTheme(
      <ExpertiseTimeline
        expertiseData={mockExpertiseData}
        learningHistory={mockLearningHistory}
      />
    );
    
    const infoButton = screen.getByRole('button');
    expect(infoButton).toBeInTheDocument();
  });

  it('renders timeline chart', () => {
    renderWithTheme(
      <ExpertiseTimeline
        expertiseData={mockExpertiseData}
        learningHistory={mockLearningHistory}
      />
    );
    
    const chart = screen.getByRole('img');
    expect(chart).toBeInTheDocument();
  });

  it('displays learning history dates', () => {
    renderWithTheme(
      <ExpertiseTimeline
        expertiseData={mockExpertiseData}
        learningHistory={mockLearningHistory}
      />
    );
    
    // Check if dates are formatted correctly
    const dates = mockLearningHistory.map(event => 
      new Date(event.timestamp).toLocaleDateString()
    );
    dates.forEach(date => {
      expect(screen.getByText(date)).toBeInTheDocument();
    });
  });
}); 