import React, { useState } from 'react';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  Typography,
  IconButton,
  Tooltip,
  makeStyles,
  Theme,
  createStyles,
} from '@material-ui/core';
import {
  Palette as PaletteIcon,
  ViewQuilt as LayoutIcon,
  Style as StyleIcon,
  Preview as PreviewIcon,
  Save as SaveIcon,
  Code as CodeIcon,
} from '@material-ui/icons';

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
    },
    header: {
      padding: theme.spacing(2),
      borderBottom: `1px solid ${theme.palette.divider}`,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
    },
    content: {
      flex: 1,
      display: 'flex',
      overflow: 'hidden',
    },
    sidebar: {
      width: 300,
      borderRight: `1px solid ${theme.palette.divider}`,
      display: 'flex',
      flexDirection: 'column',
    },
    canvas: {
      flex: 1,
      padding: theme.spacing(2),
      backgroundColor: theme.palette.background.default,
    },
    previewContainer: {
      border: `1px solid ${theme.palette.divider}`,
      borderRadius: theme.shape.borderRadius,
      height: '100%',
      overflow: 'auto',
      backgroundColor: '#fff',
    },
    toolbar: {
      padding: theme.spacing(1),
      borderBottom: `1px solid ${theme.palette.divider}`,
      display: 'flex',
      gap: theme.spacing(1),
    },
  })
);

interface DesignAgentProps {
  projectId: string;
  onSave: (design: any) => void;
  onGenerateCode: (design: any) => void;
}

const DesignAgent: React.FC<DesignAgentProps> = ({ projectId, onSave, onGenerateCode }) => {
  const classes = useStyles();
  const [activeTab, setActiveTab] = useState(0);
  const [currentDesign, setCurrentDesign] = useState<any>({
    layout: {},
    styles: {},
    components: [],
  });

  const handleTabChange = (event: React.ChangeEvent<{}>, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleSave = () => {
    onSave(currentDesign);
  };

  const handleGenerateCode = () => {
    onGenerateCode(currentDesign);
  };

  return (
    <div className={classes.root}>
      <div className={classes.header}>
        <Typography variant="h6">Design Agent</Typography>
        <Box>
          <Tooltip title="Save Design">
            <IconButton onClick={handleSave}>
              <SaveIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Generate Code">
            <IconButton onClick={handleGenerateCode}>
              <CodeIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </div>
      
      <div className={classes.content}>
        <Paper className={classes.sidebar}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="fullWidth"
            indicatorColor="primary"
            textColor="primary"
          >
            <Tab icon={<LayoutIcon />} label="Layout" />
            <Tab icon={<StyleIcon />} label="Style" />
            <Tab icon={<PaletteIcon />} label="Theme" />
          </Tabs>
          
          <div className={classes.toolbar}>
            {/* Tool buttons specific to active tab */}
            {activeTab === 0 && (
              <>
                <Tooltip title="Add Container">
                  <IconButton size="small">
                    <LayoutIcon />
                  </IconButton>
                </Tooltip>
                {/* Add more layout tools */}
              </>
            )}
            {/* Add tools for other tabs */}
          </div>
          
          {/* Tab content */}
          <Box p={2} flex={1} overflow="auto">
            {activeTab === 0 && (
              <Typography>Layout Editor</Typography>
              // Add layout editing components
            )}
            {activeTab === 1 && (
              <Typography>Style Editor</Typography>
              // Add style editing components
            )}
            {activeTab === 2 && (
              <Typography>Theme Editor</Typography>
              // Add theme editing components
            )}
          </Box>
        </Paper>
        
        <div className={classes.canvas}>
          <Box className={classes.previewContainer}>
            {/* Live preview of the design */}
            <Typography variant="body2" color="textSecondary" align="center">
              Design Preview
            </Typography>
          </Box>
        </div>
      </div>
    </div>
  );
};

export default DesignAgent; 