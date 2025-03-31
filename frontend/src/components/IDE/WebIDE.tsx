import React, { useState, useEffect, useCallback } from 'react';
import { Box, Grid, Paper } from '@mui/material';
import Editor from '@monaco-editor/react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { useCommandCenter, Task, TaskUpdate } from '../../hooks/useCommandCenter';
import { useResourceMonitor } from '../../hooks/useResourceMonitor';
import { useCodebaseAwareness } from '../../hooks/useCodebaseAwareness';
import { ResourceMonitor, ResourceMetrics } from '../ResourceMonitor';
import { CommandCenterPanel } from '../CommandCenterPanel';
import { AgentActivityPanel } from '../AgentActivityPanel';
import { CodebaseAwarenessPanel } from '../CodebaseAwarenessPanel';

interface AgentActivity {
  id: string;
  type: string;
  timestamp: string;
  details: any;
}

interface WebIDEProps {
  projectId: string;
  initialCode?: string;
  initialFile?: string;
}

export const WebIDE: React.FC<WebIDEProps> = ({
  projectId,
  initialCode = '',
  initialFile = 'index.ts'
}) => {
  const [code, setCode] = useState(initialCode);
  const [currentFile, setCurrentFile] = useState(initialFile);
  const [agentActivities, setAgentActivities] = useState<AgentActivity[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [resources, setResources] = useState<ResourceMetrics>({
    cpu: { usage: 0, cores: 0 },
    memory: { total: 0, used: 0, free: 0 },
    disk: { total: 0, used: 0, free: 0 },
    network: { bytesIn: 0, bytesOut: 0, connections: 0 }
  });

  const socket = useWebSocket(projectId);
  const { getTasks, updateTask, createTask, deleteTask } = useCommandCenter(socket);
  const { startMonitoring, stopMonitoring } = useResourceMonitor(socket);
  const { analyzeFile, getDependencies, resolveSymbol } = useCodebaseAwareness(socket);

  useEffect(() => {
    if (socket) {
      socket.on('agent:activity', (activity: AgentActivity) => {
        setAgentActivities(prev => [...prev, activity]);
      });

      socket.on('command-center:task-update', (task: Task) => {
        setTasks(prev => prev.map(t => t.id === task.id ? task : t));
      });

      socket.on('resource:metrics', (metrics: ResourceMetrics) => {
        setResources(metrics);
      });

      startMonitoring();
    }

    return () => {
      if (socket) {
        socket.off('agent:activity');
        socket.off('command-center:task-update');
        socket.off('resource:metrics');
        stopMonitoring();
      }
    };
  }, [socket, startMonitoring, stopMonitoring]);

  useEffect(() => {
    if (socket) {
      getTasks().then(setTasks);
    }
  }, [socket, getTasks]);

  const handleEditorMount = useCallback((editor: any) => {
    if (socket) {
      socket.emit('editor:register', {
        id: editor.getId(),
        capabilities: [
          'code-analysis',
          'dependency-analysis',
          'symbol-resolution'
        ]
      });
    }
  }, [socket]);

  const handleEditorChange = useCallback((value: string | undefined) => {
    if (value && socket) {
      setCode(value);
      socket.emit('editor:change', {
        file: currentFile,
        content: value
      });

      // Analyze code changes
      analyzeFile(currentFile, value).then(context => {
        socket.emit('agent:context', {
          file: currentFile,
          context
        });
      });
    }
  }, [socket, currentFile, analyzeFile]);

  const handleSymbolClick = useCallback((symbol: any) => {
    if (socket) {
      resolveSymbol(symbol).then(result => {
        socket.emit('agent:symbol', {
          symbol,
          result
        });
      });
    }
  }, [socket, resolveSymbol]);

  const handleTaskUpdate = useCallback((taskId: string, update: TaskUpdate) => {
    if (socket) {
      updateTask(taskId, update).then(updatedTask => {
        setTasks(prev => prev.map(t => t.id === taskId ? updatedTask : t));
      });
    }
  }, [socket, updateTask]);

  return (
    <Grid container spacing={2} sx={{ height: '100vh' }}>
      <Grid item xs={9}>
        <Paper sx={{ height: '100%', overflow: 'hidden' }}>
          <Editor
            height="100%"
            defaultLanguage="typescript"
            defaultValue={code}
            onMount={handleEditorMount}
            onChange={handleEditorChange}
            options={{
              minimap: { enabled: true },
              fontSize: 14,
              lineNumbers: 'on',
              roundedSelection: false,
              scrollBeyondLastLine: false,
              readOnly: false,
              cursorStyle: 'line',
              automaticLayout: true,
              hover: {
                enabled: true,
                delay: 300
              }
            }}
          />
        </Paper>
      </Grid>
      <Grid item xs={3}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, height: '100%' }}>
          <CodebaseAwarenessPanel
            currentFile={currentFile}
            onSymbolClick={handleSymbolClick}
          />
          <AgentActivityPanel activities={agentActivities} />
          <CommandCenterPanel
            tasks={tasks}
            onTaskUpdate={handleTaskUpdate}
          />
          <ResourceMonitor resources={resources} />
        </Box>
      </Grid>
    </Grid>
  );
}; 