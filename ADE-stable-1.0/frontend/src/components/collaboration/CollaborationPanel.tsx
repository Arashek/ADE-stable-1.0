import React, { useEffect, useRef, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Avatar,
  AvatarGroup,
  Tooltip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  Videocam as VideoIcon,
  VideocamOff as VideoOffIcon,
  Mic as MicIcon,
  MicOff as MicOffIcon,
  Share as ShareIcon,
  PersonAdd as PersonAddIcon,
} from '@mui/icons-material';
import { CollaborationService, CollaborationState, CollaborationUser } from '../../services/collaboration/CollaborationService';

const CollaborationContainer = styled(Paper)(({ theme }) => ({
  position: 'fixed',
  bottom: theme.spacing(2),
  right: theme.spacing(2),
  width: '300px',
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
  boxShadow: theme.shadows[6],
  zIndex: 1000,
}));

const VideoContainer = styled(Box)(({ theme }) => ({
  display: 'grid',
  gridTemplateColumns: '1fr 1fr',
  gap: theme.spacing(1),
  padding: theme.spacing(1),
  backgroundColor: theme.palette.background.default,
  borderRadius: theme.shape.borderRadius,
  '& video': {
    width: '100%',
    borderRadius: theme.shape.borderRadius,
    backgroundColor: theme.palette.grey[900],
  },
}));

const ControlBar = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'space-around',
  alignItems: 'center',
  padding: theme.spacing(1),
  borderTop: `1px solid ${theme.palette.divider}`,
}));

const ParticipantList = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1),
  borderBottom: `1px solid ${theme.palette.divider}`,
}));

interface CollaborationPanelProps {
  sessionId: string;
  currentUser: {
    id: string;
    name: string;
    avatar?: string;
  };
}

export const CollaborationPanel: React.FC<CollaborationPanelProps> = ({
  sessionId,
  currentUser,
}) => {
  const collaborationService = CollaborationService.getInstance();
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideoRef = useRef<HTMLVideoElement>(null);
  const [state, setState] = useState<CollaborationState>({
    users: [],
    activeFile: null,
    isRecording: false,
    isPeerConnected: false,
  });
  const [isVideoEnabled, setIsVideoEnabled] = useState(true);
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [isInviteDialogOpen, setIsInviteDialogOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');

  useEffect(() => {
    // Initialize collaboration
    collaborationService.startCollaboration(sessionId, currentUser.id, currentUser.name);

    // Set up video streams
    const localStream = collaborationService.getLocalStream();
    const remoteStream = collaborationService.getRemoteStream();

    if (localVideoRef.current && localStream) {
      localVideoRef.current.srcObject = localStream;
    }

    if (remoteVideoRef.current && remoteStream) {
      remoteVideoRef.current.srcObject = remoteStream;
    }

    // Subscribe to state changes
    const subscription = collaborationService.onStateChange().subscribe(newState => {
      setState(newState);
    });

    return () => {
      subscription.unsubscribe();
      collaborationService.endCollaboration();
    };
  }, [sessionId, currentUser]);

  const toggleVideo = () => {
    const localStream = collaborationService.getLocalStream();
    if (localStream) {
      localStream.getVideoTracks().forEach(track => {
        track.enabled = !isVideoEnabled;
      });
      setIsVideoEnabled(!isVideoEnabled);
    }
  };

  const toggleAudio = () => {
    const localStream = collaborationService.getLocalStream();
    if (localStream) {
      localStream.getAudioTracks().forEach(track => {
        track.enabled = !isAudioEnabled;
      });
      setIsAudioEnabled(!isAudioEnabled);
    }
  };

  const handleInvite = async () => {
    try {
      await fetch('/api/collaboration/invite', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sessionId,
          email: inviteEmail,
        }),
      });
      setIsInviteDialogOpen(false);
      setInviteEmail('');
    } catch (error) {
      console.error('Error sending invitation:', error);
    }
  };

  const renderParticipants = () => {
    return (
      <ParticipantList>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="subtitle2">Participants ({state.users.length})</Typography>
          <IconButton size="small" onClick={() => setIsInviteDialogOpen(true)}>
            <PersonAddIcon />
          </IconButton>
        </Box>
        <AvatarGroup max={4} sx={{ justifyContent: 'flex-start', mt: 1 }}>
          {state.users.map((user) => (
            <Tooltip key={user.id} title={user.name}>
              <Avatar src={user.avatar} alt={user.name}>
                {user.name.charAt(0)}
              </Avatar>
            </Tooltip>
          ))}
        </AvatarGroup>
      </ParticipantList>
    );
  };

  return (
    <>
      <CollaborationContainer>
        {renderParticipants()}
        
        <VideoContainer>
          <Box>
            <video
              ref={localVideoRef}
              autoPlay
              muted
              playsInline
              style={{ opacity: isVideoEnabled ? 1 : 0.5 }}
            />
            <Typography variant="caption" align="center" display="block">
              You
            </Typography>
          </Box>
          {state.isPeerConnected && (
            <Box>
              <video
                ref={remoteVideoRef}
                autoPlay
                playsInline
              />
              <Typography variant="caption" align="center" display="block">
                Peer
              </Typography>
            </Box>
          )}
        </VideoContainer>

        <ControlBar>
          <IconButton onClick={toggleVideo}>
            {isVideoEnabled ? <VideoIcon /> : <VideoOffIcon />}
          </IconButton>
          <IconButton onClick={toggleAudio}>
            {isAudioEnabled ? <MicIcon /> : <MicOffIcon />}
          </IconButton>
          <IconButton>
            <ShareIcon />
          </IconButton>
        </ControlBar>
      </CollaborationContainer>

      <Dialog open={isInviteDialogOpen} onClose={() => setIsInviteDialogOpen(false)}>
        <DialogTitle>Invite Collaborator</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Email Address"
            type="email"
            fullWidth
            variant="outlined"
            value={inviteEmail}
            onChange={(e) => setInviteEmail(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsInviteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleInvite} variant="contained" color="primary">
            Send Invitation
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}; 