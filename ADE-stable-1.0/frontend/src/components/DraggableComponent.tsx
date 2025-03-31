import React, { useRef } from 'react';
import { useDrag, useDrop } from 'react-dnd';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Tooltip,
  ResizeHandle,
} from '@mui/material';
import {
  DragIndicator as DragIcon,
  Resize as ResizeIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';

interface DraggableComponentProps {
  id: string;
  type: 'container' | 'button' | 'input' | 'text' | 'image' | 'card';
  content: string;
  style: React.CSSProperties;
  position: { x: number; y: number };
  size: { width: number; height: number };
  isSelected: boolean;
  onSelect: (id: string) => void;
  onUpdate: (id: string, updates: any) => void;
  onDelete: (id: string) => void;
}

export const DraggableComponent: React.FC<DraggableComponentProps> = ({
  id,
  type,
  content,
  style,
  position,
  size,
  isSelected,
  onSelect,
  onUpdate,
  onDelete,
}) => {
  const ref = useRef<HTMLDivElement>(null);
  const resizeRef = useRef<HTMLDivElement>(null);

  const [{ isDragging }, drag] = useDrag({
    type: 'COMPONENT',
    item: { id, type },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  const [{ isOver }, drop] = useDrop({
    accept: 'COMPONENT',
    drop: (item: { id: string; type: string }) => {
      if (item.id !== id) {
        // Handle component reordering
        onUpdate(id, { position });
      }
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
  });

  drag(drop(ref));

  const handleResize = (e: React.MouseEvent, direction: string) => {
    e.stopPropagation();
    const newSize = {
      width: size.width + (direction.includes('right') ? 10 : -10),
      height: size.height + (direction.includes('bottom') ? 10 : -10),
    };
    onUpdate(id, { size: newSize });
  };

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    // Implement edit functionality
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete(id);
  };

  return (
    <Box
      ref={ref}
      sx={{
        position: 'absolute',
        left: position.x,
        top: position.y,
        width: size.width,
        height: size.height,
        opacity: isDragging ? 0.5 : 1,
        cursor: 'move',
        border: isSelected ? '2px solid #1976d2' : '1px solid #ccc',
        borderRadius: 1,
        '&:hover': {
          borderColor: '#1976d2',
        },
      }}
      onClick={() => onSelect(id)}
    >
      <Paper
        sx={{
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
        }}
      >
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            bgcolor: 'rgba(0, 0, 0, 0.1)',
            p: 0.5,
            opacity: isSelected ? 1 : 0,
            transition: 'opacity 0.2s',
            '&:hover': {
              opacity: 1,
            },
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <DragIcon fontSize="small" />
            <Typography variant="caption">{type}</Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            <Tooltip title="Edit">
              <IconButton size="small" onClick={handleEdit}>
                <EditIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete">
              <IconButton size="small" onClick={handleDelete}>
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        <Box
          sx={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            p: 2,
          }}
        >
          {content || type}
        </Box>

        {isSelected && (
          <>
            <ResizeHandle
              ref={resizeRef}
              position="top-left"
              onResize={(e) => handleResize(e, 'top-left')}
            />
            <ResizeHandle
              position="top-right"
              onResize={(e) => handleResize(e, 'top-right')}
            />
            <ResizeHandle
              position="bottom-left"
              onResize={(e) => handleResize(e, 'bottom-left')}
            />
            <ResizeHandle
              position="bottom-right"
              onResize={(e) => handleResize(e, 'bottom-right')}
            />
          </>
        )}
      </Paper>
    </Box>
  );
}; 