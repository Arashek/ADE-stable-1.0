import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ProjectsPage from '../components/projects/ProjectsPage';
import ProjectDetailsPage from '../components/projects/ProjectDetailsPage';

const ProjectRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<ProjectsPage />} />
      <Route path="/:id" element={<ProjectDetailsPage />} />
      <Route path="*" element={<Navigate to="/projects" replace />} />
    </Routes>
  );
};

export default ProjectRoutes; 