import { useContext } from 'react';
import { ProjectContext } from '../contexts/ProjectContext';

export const useProjectContext = () => {
  const context = useContext(ProjectContext);
  
  if (!context) {
    throw new Error('useProjectContext must be used within a ProjectProvider');
  }
  
  return context;
};
