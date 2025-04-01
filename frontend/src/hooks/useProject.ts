import { useState, useEffect } from 'react';
import { ProjectService } from '../services/project.service';

export interface Project {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
  language: string;
  framework?: string;
  status: 'active' | 'archived' | 'completed';
  metadata?: Record<string, any>;
}

export const useProject = (projectId?: string) => {
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const projectService = new ProjectService();

  useEffect(() => {
    if (!projectId) return;

    const fetchProject = async () => {
      setLoading(true);
      setError(null);
      try {
        const projectData = await projectService.getProject(projectId);
        setProject(projectData);
      } catch (err) {
        setError((err as Error).message);
        console.error('Error fetching project:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchProject();
  }, [projectId]);

  const updateProject = async (updates: Partial<Project>) => {
    if (!projectId || !project) return;
    
    setLoading(true);
    setError(null);
    try {
      const updatedProject = await projectService.updateProject(projectId, updates);
      setProject(updatedProject);
      return updatedProject;
    } catch (err) {
      setError((err as Error).message);
      console.error('Error updating project:', err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { project, loading, error, updateProject };
};
