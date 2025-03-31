import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Typography,
  Box,
  DialogProps,
  styled,
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import Button from './Button';

interface ModalProps extends Omit<DialogProps, 'title'> {
  title?: React.ReactNode;
  actions?: React.ReactNode;
  showCloseButton?: boolean;
  onClose?: () => void;
}

const StyledDialog = styled(Dialog)(({ theme }) => ({
  '& .MuiDialog-paper': {
    borderRadius: '12px',
    padding: theme.spacing(2),
  },
}));

const Modal: React.FC<ModalProps> = ({
  title,
  children,
  actions,
  showCloseButton = true,
  onClose,
  ...props
}) => {
  return (
    <StyledDialog onClose={onClose} {...props}>
      <Box sx={{ position: 'relative' }}>
        {showCloseButton && (
          <IconButton
            aria-label="close"
            onClick={onClose}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              color: 'grey.500',
            }}
          >
            <CloseIcon />
          </IconButton>
        )}

        {title && (
          <DialogTitle>
            <Typography variant="h6">{title}</Typography>
          </DialogTitle>
        )}

        <DialogContent>{children}</DialogContent>

        {actions && (
          <DialogActions sx={{ padding: 2, pt: 0 }}>{actions}</DialogActions>
        )}
      </Box>
    </StyledDialog>
  );
};

export const ModalActions: React.FC<{
  onCancel?: () => void;
  onConfirm?: () => void;
  cancelText?: string;
  confirmText?: string;
  children?: React.ReactNode;
}> = ({
  onCancel,
  onConfirm,
  cancelText = 'Cancel',
  confirmText = 'Confirm',
  children,
}) => {
  return (
    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
      {children}
      {onCancel && (
        <Button variant="outline" onClick={onCancel}>
          {cancelText}
        </Button>
      )}
      {onConfirm && (
        <Button variant="primary" onClick={onConfirm}>
          {confirmText}
        </Button>
      )}
    </Box>
  );
};

export default Modal; 