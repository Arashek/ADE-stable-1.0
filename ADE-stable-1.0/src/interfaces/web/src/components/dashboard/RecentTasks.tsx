import React from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import Table, { Column } from '../common/Table';
import { dashboardService } from '../../services/dashboardService';
import { useWebSocket } from '../../hooks/useWebSocket';

export interface Task {
  id: string;
  title: string;
  type: 'code_review' | 'test' | 'documentation' | 'deployment';
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  priority: 'low' | 'medium' | 'high';
  assignedTo: string;
  dueDate: string;
}

const mockTasks: Task[] = [
  {
    id: '1',
    title: 'Review PR #123',
    type: 'code_review',
    status: 'in_progress',
    priority: 'high',
    assignedTo: 'Code Review Agent',
    dueDate: '2024-03-21T10:00:00Z',
  },
  {
    id: '2',
    title: 'Generate unit tests',
    type: 'test',
    status: 'pending',
    priority: 'medium',
    assignedTo: 'Test Generator',
    dueDate: '2024-03-22T15:00:00Z',
  },
  {
    id: '3',
    title: 'Update API docs',
    type: 'documentation',
    status: 'completed',
    priority: 'low',
    assignedTo: 'Documentation Bot',
    dueDate: '2024-03-20T16:00:00Z',
  },
  {
    id: '4',
    title: 'Deploy to staging',
    type: 'deployment',
    status: 'failed',
    priority: 'high',
    assignedTo: 'Deployment Agent',
    dueDate: '2024-03-20T14:00:00Z',
  },
];

const getStatusColor = (status: Task['status']) => {
  switch (status) {
    case 'completed':
      return 'success';
    case 'in_progress':
      return 'info';
    case 'pending':
      return 'warning';
    case 'failed':
      return 'error';
    default:
      return 'default';
  }
};

const getPriorityColor = (priority: Task['priority']) => {
  switch (priority) {
    case 'high':
      return 'error';
    case 'medium':
      return 'warning';
    case 'low':
      return 'success';
    default:
      return 'default';
  }
};

const TaskActions: React.FC<{ task: Task }> = ({ task }) => {
  const queryClient = useQueryClient();

  const handleStatusChange = async (newStatus: Task['status']) => {
    try {
      await dashboardService.updateTaskStatus(task.id, newStatus);
    } catch (error) {
      console.error('Failed to update task status:', error);
    }
  };

  const handleDelete = async () => {
    try {
      await dashboardService.deleteTask(task.id);
    } catch (error) {
      console.error('Failed to delete task:', error);
    }
  };

  return (
    <Box sx={{ display: 'flex', gap: 1 }}>
      {task.status === 'pending' && (
        <Tooltip title="Start task">
          <IconButton
            size="small"
            color="primary"
            onClick={() => handleStatusChange('in_progress')}
          >
            <StartIcon />
          </IconButton>
        </Tooltip>
      )}
      {task.status === 'in_progress' && (
        <Tooltip title="Complete task">
          <IconButton
            size="small"
            color="success"
            onClick={() => handleStatusChange('completed')}
          >
            <StopIcon />
          </IconButton>
        </Tooltip>
      )}
      <Tooltip title="Delete task">
        <IconButton size="small" color="error" onClick={handleDelete}>
          <DeleteIcon />
        </IconButton>
      </Tooltip>
    </Box>
  );
};

const RecentTasks: React.FC = () => {
  useWebSocket('task');

  const { data: tasks, isLoading, error } = useQuery<Task[]>({
    queryKey: ['tasks'],
    queryFn: dashboardService.getTasks,
  });

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">Failed to load tasks</Alert>;
  }

  const columns: Column<Task>[] = [
    {
      id: 'title',
      label: 'Task',
      minWidth: 200,
      sortable: true,
      format: (value: string) => value
    },
    {
      id: 'status',
      label: 'Status',
      minWidth: 120,
      sortable: true,
      format: (value: Task['status']) => (
        <Chip
          size="small"
          label={value}
          color={getStatusColor(value)}
        />
      ),
    },
    {
      id: 'priority',
      label: 'Priority',
      minWidth: 100,
      sortable: true,
      format: (value: Task['priority']) => (
        <Chip
          size="small"
          label={value}
          color={getPriorityColor(value)}
        />
      ),
    },
    {
      id: 'assignedTo',
      label: 'Assigned To',
      minWidth: 150,
      sortable: true,
      format: (value: string) => value
    },
    {
      id: 'dueDate',
      label: 'Due Date',
      minWidth: 150,
      sortable: true,
      format: (value: string) => new Date(value).toLocaleString(),
    },
    {
      id: 'actions',
      label: 'Actions',
      minWidth: 100,
      sortable: false,
      format: (value: any, row: Task) => <TaskActions task={row} />,
    },
  ];

  return (
    <Table
      columns={columns}
      rows={tasks || []}
      defaultSortBy="dueDate"
      defaultOrder="asc"
      rowsPerPageOptions={[5, 10, 25]}
    />
  );
};

export default RecentTasks; 