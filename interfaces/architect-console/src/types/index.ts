import React from 'react';
import { Node, Edge } from 'reactflow';

// Message types for ChatPanel
export interface Message {
  id: number;
  sender: 'System' | 'User';
  message: string;
  timestamp: string;
}

// Agent types for AgentCollaboration
export interface Agent {
  id: number;
  name: string;
  role: string;
  status: 'active' | 'inactive';
  icon: React.ReactNode;
  lastActivity: string;
}

// Step types for DeploymentPipeline
export interface PipelineStep {
  label: string;
  description: string;
  icon: React.ReactNode;
  status: 'completed' | 'active' | 'pending';
}

// Node and Edge types for SystemArchitecture and DecisionTree
export interface CustomNode extends Node {
  data: {
    label: string;
  };
}

export interface CustomEdge extends Edge {
  id: string;
  source: string;
  target: string;
}

// Resource data types for ResourceMonitor
export interface ResourceData {
  time: string;
  cpu: number;
  memory: number;
  disk: number;
} 