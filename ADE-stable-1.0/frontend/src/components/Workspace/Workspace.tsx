import React, { useState, useEffect } from 'react';
import { styled } from '@mui/material/styles';
import { Box, Paper, IconButton, Tooltip, Divider } from '@mui/material';
import {
    ChevronLeft as ChevronLeftIcon,
    ChevronRight as ChevronRightIcon,
    ChevronUp as ChevronUpIcon,
    ChevronDown as ChevronDownIcon,
    Settings as SettingsIcon,
    Fullscreen as FullscreenIcon,
    FullscreenExit as FullscreenExitIcon
} from '@mui/icons-material';
import { CommandCenter } from '../CommandCenter/CommandCenter';
import { FileExplorer } from '../FileExplorer/FileExplorer';
import { Editor } from '../Editor/Editor';
import { Terminal } from '../Terminal/Terminal';
import { StatusBar } from '../StatusBar/StatusBar';
import { IDELayout, IDEConfig, ProjectConfig } from '../../interfaces/ide';
import { CommandCenterConfig } from '../../interfaces/command-center';

const WorkspaceContainer = styled(Box)(({ theme }) => ({
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    backgroundColor: theme.palette.background.default,
    overflow: 'hidden'
}));

const MainContent = styled(Box)({
    display: 'flex',
    flex: 1,
    overflow: 'hidden'
});

const Sidebar = styled(Paper)<{ width: number; collapsed: boolean }>(
    ({ theme, width, collapsed }) => ({
        width: collapsed ? 48 : width,
        transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen
        }),
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        borderRight: `1px solid ${theme.palette.divider}`
    })
);

const EditorContainer = styled(Box)({
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden'
});

const TerminalContainer = styled(Paper)<{ height: number; collapsed: boolean }>(
    ({ theme, height, collapsed }) => ({
        height: collapsed ? 48 : height,
        transition: theme.transitions.create('height', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen
        }),
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        borderTop: `1px solid ${theme.palette.divider}`
    })
);

const ResizeHandle = styled(Box)(({ theme }) => ({
    width: 4,
    backgroundColor: theme.palette.divider,
    cursor: 'col-resize',
    '&:hover': {
        backgroundColor: theme.palette.primary.main
    }
}));

const ResizeHandleVertical = styled(ResizeHandle)({
    cursor: 'row-resize'
});

interface WorkspaceProps {
    layout: IDELayout;
    config: IDEConfig;
    projectConfig: ProjectConfig;
    commandCenterConfig: CommandCenterConfig;
    onLayoutChange: (layout: IDELayout) => void;
    onConfigChange: (config: IDEConfig) => void;
}

export const Workspace: React.FC<WorkspaceProps> = ({
    layout,
    config,
    projectConfig,
    commandCenterConfig,
    onLayoutChange,
    onConfigChange
}) => {
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [isResizing, setIsResizing] = useState(false);
    const [resizeStartX, setResizeStartX] = useState(0);
    const [resizeStartY, setResizeStartY] = useState(0);
    const [initialWidth, setInitialWidth] = useState(0);
    const [initialHeight, setInitialHeight] = useState(0);

    const handleResizeStart = (direction: 'horizontal' | 'vertical', event: React.MouseEvent) => {
        setIsResizing(true);
        setResizeStartX(event.clientX);
        setResizeStartY(event.clientY);
        setInitialWidth(layout.fileExplorer.width);
        setInitialHeight(layout.terminal.height);
    };

    const handleResizeMove = (event: MouseEvent) => {
        if (!isResizing) return;

        if (event.clientX !== resizeStartX) {
            const delta = event.clientX - resizeStartX;
            const newWidth = Math.max(200, Math.min(600, initialWidth + delta));
            onLayoutChange({
                ...layout,
                fileExplorer: {
                    ...layout.fileExplorer,
                    width: newWidth
                }
            });
        }

        if (event.clientY !== resizeStartY) {
            const delta = event.clientY - resizeStartY;
            const newHeight = Math.max(100, Math.min(400, initialHeight - delta));
            onLayoutChange({
                ...layout,
                terminal: {
                    ...layout.terminal,
                    height: newHeight
                }
            });
        }
    };

    const handleResizeEnd = () => {
        setIsResizing(false);
    };

    useEffect(() => {
        if (isResizing) {
            window.addEventListener('mousemove', handleResizeMove);
            window.addEventListener('mouseup', handleResizeEnd);
        }

        return () => {
            window.removeEventListener('mousemove', handleResizeMove);
            window.removeEventListener('mouseup', handleResizeEnd);
        };
    }, [isResizing]);

    const toggleFullscreen = () => {
        setIsFullscreen(!isFullscreen);
        if (!isFullscreen) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    };

    const toggleSidebar = () => {
        onLayoutChange({
            ...layout,
            fileExplorer: {
                ...layout.fileExplorer,
                collapsed: !layout.fileExplorer.collapsed
            }
        });
    };

    const toggleTerminal = () => {
        onLayoutChange({
            ...layout,
            terminal: {
                ...layout.terminal,
                collapsed: !layout.terminal.collapsed
            }
        });
    };

    return (
        <WorkspaceContainer>
            <CommandCenter
                config={commandCenterConfig}
                layout={layout.commandCenter}
                onLayoutChange={(commandCenterLayout) =>
                    onLayoutChange({ ...layout, commandCenter: commandCenterLayout })
                }
            />
            <MainContent>
                <Sidebar
                    width={layout.fileExplorer.width}
                    collapsed={layout.fileExplorer.collapsed}
                >
                    <FileExplorer
                        root={layout.fileExplorer.root}
                        config={config.fileExplorer}
                        collapsed={layout.fileExplorer.collapsed}
                    />
                    <Box sx={{ p: 1, display: 'flex', justifyContent: 'flex-end' }}>
                        <Tooltip title={layout.fileExplorer.collapsed ? "Expand" : "Collapse"}>
                            <IconButton size="small" onClick={toggleSidebar}>
                                {layout.fileExplorer.collapsed ? <ChevronRightIcon /> : <ChevronLeftIcon />}
                            </IconButton>
                        </Tooltip>
                    </Box>
                </Sidebar>
                <ResizeHandle
                    onMouseDown={(e) => handleResizeStart('horizontal', e)}
                    sx={{ cursor: isResizing ? 'col-resize' : 'default' }}
                />
                <EditorContainer>
                    <Editor
                        tabs={layout.editor.tabs}
                        activeTab={layout.editor.activeTab}
                        config={config.editor}
                        splitView={layout.editor.splitView}
                        onTabChange={(activeTab) =>
                            onLayoutChange({ ...layout, editor: { ...layout.editor, activeTab } })
                        }
                        onSplitViewChange={(splitView) =>
                            onLayoutChange({ ...layout, editor: { ...layout.editor, splitView } })
                        }
                    />
                    <TerminalContainer
                        height={layout.terminal.height}
                        collapsed={layout.terminal.collapsed}
                    >
                        <Terminal
                            sessions={layout.terminal.sessions}
                            config={config.terminal}
                            collapsed={layout.terminal.collapsed}
                        />
                        <Box sx={{ p: 1, display: 'flex', justifyContent: 'flex-end' }}>
                            <Tooltip title={layout.terminal.collapsed ? "Expand" : "Collapse"}>
                                <IconButton size="small" onClick={toggleTerminal}>
                                    {layout.terminal.collapsed ? <ChevronUpIcon /> : <ChevronDownIcon />}
                                </IconButton>
                            </Tooltip>
                        </Box>
                    </TerminalContainer>
                </EditorContainer>
            </MainContent>
            <StatusBar
                height={layout.statusBar.height}
                components={layout.statusBar.components}
            />
            <Box
                sx={{
                    position: 'fixed',
                    bottom: 16,
                    right: 16,
                    display: 'flex',
                    gap: 1,
                    zIndex: 1000
                }}
            >
                <Tooltip title="Settings">
                    <IconButton color="primary" onClick={() => {}}>
                        <SettingsIcon />
                    </IconButton>
                </Tooltip>
                <Tooltip title={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}>
                    <IconButton color="primary" onClick={toggleFullscreen}>
                        {isFullscreen ? <FullscreenExitIcon /> : <FullscreenIcon />}
                    </IconButton>
                </Tooltip>
            </Box>
        </WorkspaceContainer>
    );
}; 