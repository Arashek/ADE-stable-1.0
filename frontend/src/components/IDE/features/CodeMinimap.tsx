import React from 'react';
import { Box } from '@mui/material';
import { useTheme } from '@mui/material/styles';

interface CodeMinimapProps {
  code: string;
  height: number;
  onPositionChange: (scrollTop: number) => void;
}

export const CodeMinimap: React.FC<CodeMinimapProps> = ({
  code,
  height,
  onPositionChange
}) => {
  const theme = useTheme();
  const canvasRef = React.useRef<HTMLCanvasElement>(null);

  React.useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw minimap
    const lines = code.split('\n');
    const lineHeight = 2;
    const totalHeight = lines.length * lineHeight;
    const scale = height / totalHeight;

    ctx.fillStyle = theme.palette.text.secondary;
    lines.forEach((line, index) => {
      const y = index * lineHeight * scale;
      const width = (line.length / 100) * canvas.width;
      ctx.fillRect(0, y, width, lineHeight * scale);
    });
  }, [code, height, theme]);

  const handleClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const y = e.clientY - rect.top;
    const percentage = y / height;
    onPositionChange(percentage);
  };

  return (
    <Box
      sx={{
        position: 'absolute',
        right: 0,
        top: 0,
        width: 50,
        height: '100%',
        backgroundColor: theme.palette.background.paper,
        borderLeft: `1px solid ${theme.palette.divider}`,
      }}
    >
      <canvas
        ref={canvasRef}
        width={50}
        height={height}
        onClick={handleClick}
        style={{ cursor: 'pointer' }}
      />
    </Box>
  );
};
