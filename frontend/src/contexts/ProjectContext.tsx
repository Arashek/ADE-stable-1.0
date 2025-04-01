import React, { createContext, useState, useEffect, ReactNode } from 'react';
import { Project } from '../hooks/useProject';
import { ProjectService } from '../services/project.service';

interface ProjectContextType {
  currentProject: Project | null;
  projects: Project[];
  loading: boolean;
  error: string | null;
  setCurrentProject: (project: Project | null) => void;
  refreshProjects: () => Promise<void>;
  createProject: (project: Partial<Project>) => Promise<Project | null>;
  updateProject: (id: string, updates: Partial<Project>) => Promise<Project | null>;
  deleteProject: (id: string) => Promise<boolean>;
}

export const ProjectContext = createContext<ProjectContextType | null>(null);

interface ProjectProviderProps {
  children: ReactNode;
}

export const ProjectProvider: React.FC<ProjectProviderProps> = ({ children }) => {
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  const projectService = new ProjectService();

  const refreshProjects = async () => {
    setLoading(true);
    setError(null);
    try {
      const projectList = await projectService.getProjects();
      setProjects(projectList);
      return projectList;
    } catch (err) {
      setError((err as Error).message);
      console.error('Error fetching projects:', err);
      return [];
    } finally {
      setLoading(false);
    }
  };

  const createProject = async (project: Partial<Project>): Promise<Project | null> => {
    setLoading(true);
    setError(null);
    try {
      const newProject = await projectService.createProject(project);
      setProjects(prev => [...prev, newProject]);
      return newProject;
    } catch (err) {
      setError((err as Error).message);
      console.error('Error creating project:', err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const updateProject = async (id: string, updates: Partial<Project>): Promise<Project | null> => {
    setLoading(true);
    setError(null);
    try {
      const updatedProject = await projectService.updateProject(id, updates);
      setProjects(prev => 
        prev.map(p => p.id === id ? updatedProject : p)
      );
      
      // Update current project if it's the one being updated
      if (currentProject && currentProject.id === id) {
        setCurrentProject(updatedProject);
      }
      
      return updatedProject;
    } catch (err) {
      setError((err as Error).message);
      console.error('Error updating project:', err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const deleteProject = async (id: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      await projectService.deleteProject(id);
      setProjects(prev => prev.filter(p => p.id !== id));
      
      // Clear current project if it's the one being deleted
      if (currentProject && currentProject.id === id) {
        setCurrentProject(null);
      }
      
      return true;
    } catch (err) {
      setError((err as Error).message);
      console.error('Error deleting project:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Load projects on initial mount
  useEffect(() => {
    refreshProjects();
  }, []);

  return (
    <ProjectContext.Provider
      value={{
        currentProject,
        projects,
        loading,
        error,
        setCurrentProject,
        refreshProjects,
        createProject,
        updateProject,
        deleteProject
      }}
    >
      {children}
    </ProjectContext.Provider>
  );
};
