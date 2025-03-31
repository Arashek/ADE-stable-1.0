import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Card,
  CardMedia,
  CardContent,
  Typography,
  IconButton,
  Tooltip,
  Collapse,
  Chip,
  LinearProgress
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Download,
  ExpandMore,
  ExpandLess,
  Image as ImageIcon,
  Mic,
  Description
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { MessageType } from '../../../core/models/chat/types';

const MessageCard = styled(Card)(({ theme }) => ({
  maxWidth: '80%',
  margin: theme.spacing(1),
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.spacing(2),
  overflow: 'hidden'
}));

const MediaContainer = styled(Box)(({ theme }) => ({
  position: 'relative',
  width: '100%',
  height: 'auto',
  maxHeight: '400px',
  overflow: 'hidden'
}));

const ControlsContainer = styled(Box)(({ theme }) => ({
  position: 'absolute',
  bottom: theme.spacing(1),
  right: theme.spacing(1),
  display: 'flex',
  gap: theme.spacing(1),
  backgroundColor: 'rgba(0, 0, 0, 0.5)',
  borderRadius: theme.spacing(1),
  padding: theme.spacing(0.5)
}));

interface MediaMessageProps {
  type: MessageType;
  metadata: any;
  url: string;
  isOwnMessage: boolean;
  text?: string;
  analysis?: any;
  onDownload?: () => void;
}

export const MediaMessage: React.FC<MediaMessageProps> = ({
  type,
  metadata,
  url,
  isOwnMessage,
  text,
  analysis,
  onDownload
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    if (audioRef.current) {
      const audio = audioRef.current;
      
      const handleTimeUpdate = () => {
        setProgress((audio.currentTime / audio.duration) * 100);
      };

      const handleLoadedMetadata = () => {
        setDuration(audio.duration);
      };

      const handleEnded = () => {
        setIsPlaying(false);
        setProgress(0);
      };

      audio.addEventListener('timeupdate', handleTimeUpdate);
      audio.addEventListener('loadedmetadata', handleLoadedMetadata);
      audio.addEventListener('ended', handleEnded);

      return () => {
        audio.removeEventListener('timeupdate', handleTimeUpdate);
        audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
        audio.removeEventListener('ended', handleEnded);
      };
    }
  }, []);

  const handlePlayPause = async () => {
    if (audioRef.current) {
      try {
        if (isPlaying) {
          await audioRef.current.pause();
        } else {
          await audioRef.current.play();
        }
        setIsPlaying(!isPlaying);
      } catch (error) {
        console.error('Error playing audio:', error);
      }
    }
  };

  const handleDownload = () => {
    if (onDownload) {
      onDownload();
    } else {
      const link = document.createElement('a');
      link.href = url;
      link.download = metadata.fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const renderMediaContent = () => {
    switch (type) {
      case MessageType.IMAGE:
        return (
          <CardMedia
            component="img"
            image={url}
            alt={metadata.fileName}
            sx={{ maxHeight: 400, objectFit: 'contain' }}
          />
        );
      case MessageType.VOICE:
        return (
          <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
            <IconButton onClick={handlePlayPause} color="primary">
              {isPlaying ? <Pause /> : <PlayArrow />}
            </IconButton>
            <Box sx={{ flex: 1 }}>
              <LinearProgress
                variant="determinate"
                value={progress}
                sx={{ height: 4, borderRadius: 2 }}
              />
              <Typography variant="caption" color="text.secondary">
                {Math.floor(audioRef.current?.currentTime || 0)}s / {Math.floor(duration)}s
              </Typography>
            </Box>
            <audio ref={audioRef} src={url} />
          </Box>
        );
      case MessageType.FILE:
        return (
          <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
            <Description sx={{ fontSize: 40 }} />
            <Box sx={{ flex: 1 }}>
              <Typography variant="subtitle1">{metadata.fileName}</Typography>
              <Typography variant="caption" color="text.secondary">
                {(metadata.fileSize / 1024).toFixed(2)} KB
              </Typography>
            </Box>
          </Box>
        );
      default:
        return null;
    }
  };

  const renderAnalysis = () => {
    if (!analysis) return null;

    switch (type) {
      case MessageType.IMAGE:
        return (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              {analysis.description}
            </Typography>
            <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {analysis.objects.map((obj: string) => (
                <Chip key={obj} label={obj} size="small" />
              ))}
            </Box>
            {analysis.text && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Text detected: {analysis.text}
              </Typography>
            )}
          </Box>
        );
      case MessageType.VOICE:
        return (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              {analysis.text}
            </Typography>
            <Box sx={{ mt: 1 }}>
              {analysis.segments.map((segment: any, index: number) => (
                <Typography key={index} variant="caption" color="text.secondary">
                  {segment.text} ({segment.start}s - {segment.end}s)
                </Typography>
              ))}
            </Box>
          </Box>
        );
      case MessageType.FILE:
        return (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              {analysis.summary}
            </Typography>
            <Box sx={{ mt: 1 }}>
              <Typography variant="subtitle2">Key Points:</Typography>
              <ul>
                {analysis.keyPoints.map((point: string, index: number) => (
                  <li key={index}>
                    <Typography variant="body2">{point}</Typography>
                  </li>
                ))}
              </ul>
            </Box>
            {analysis.sentiment && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="subtitle2">Sentiment:</Typography>
                <Chip
                  label={analysis.sentiment.label}
                  color={analysis.sentiment.score > 0.5 ? 'success' : 'error'}
                  size="small"
                />
              </Box>
            )}
          </Box>
        );
      default:
        return null;
    }
  };

  return (
    <MessageCard>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          {type === MessageType.IMAGE && <ImageIcon sx={{ mr: 1 }} />}
          {type === MessageType.VOICE && <Mic sx={{ mr: 1 }} />}
          {type === MessageType.FILE && <Description sx={{ mr: 1 }} />}
          <Typography variant="subtitle2">{metadata.fileName}</Typography>
          <Box sx={{ flex: 1 }} />
          <Tooltip title="Download">
            <IconButton onClick={handleDownload} size="small">
              <Download />
            </IconButton>
          </Tooltip>
          {(text || analysis) && (
            <Tooltip title={isExpanded ? "Show less" : "Show more"}>
              <IconButton onClick={() => setIsExpanded(!isExpanded)} size="small">
                {isExpanded ? <ExpandLess /> : <ExpandMore />}
              </IconButton>
            </Tooltip>
          )}
        </Box>
        <MediaContainer>
          {renderMediaContent()}
          <ControlsContainer>
            <Tooltip title="Download">
              <IconButton onClick={handleDownload} size="small" sx={{ color: 'white' }}>
                <Download />
              </IconButton>
            </Tooltip>
          </ControlsContainer>
        </MediaContainer>
        <Collapse in={isExpanded}>
          {text && (
            <Typography variant="body2" sx={{ mt: 2 }}>
              {text}
            </Typography>
          )}
          {renderAnalysis()}
        </Collapse>
      </CardContent>
    </MessageCard>
  );
}; 