import React, { useEffect, useRef, useState } from 'react';
import { Terminal as XTerm } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import { SearchAddon } from 'xterm-addon-search';
import { WebglAddon } from 'xterm-addon-webgl';
import 'xterm/css/xterm.css';
import { styled } from '@mui/material/styles';
import { Paper, Box, Typography, IconButton, Tooltip, LinearProgress, Grid, Collapse, Chip } from '@mui/material';
import {
    Refresh as RefreshIcon,
    Close as CloseIcon,
    Search as SearchIcon,
    ZoomIn as ZoomInIcon,
    ZoomOut as ZoomOutIcon,
    Memory as MemoryIcon,
    Storage as StorageIcon,
    Speed as SpeedIcon,
    NetworkCheck as NetworkIcon,
    ExpandMore as ExpandMoreIcon,
    ExpandLess as ExpandLessIcon,
    FiberManualRecord as StatusIcon,
    Timer as TimerIcon
} from '@mui/icons-material';

const TerminalContainer = styled(Paper)(({ theme }) => ({
    width: '100%',
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    backgroundColor: '#000000',
    borderRadius: theme.shape.borderRadius
}));

const TerminalHeader = styled(Box)(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    padding: theme.spacing(1),
    backgroundColor: theme.palette.grey[900],
    borderBottom: `1px solid ${theme.palette.grey[800]}`
}));

const TerminalTitle = styled(Typography)(({ theme }) => ({
    color: theme.palette.common.white,
    flexGrow: 1
}));

const TerminalContent = styled(Box)({
    flexGrow: 1,
    padding: '4px',
    overflow: 'hidden'
});

const MetricsContainer = styled(Box)(({ theme }) => ({
    padding: theme.spacing(1),
    backgroundColor: theme.palette.grey[900],
    borderTop: `1px solid ${theme.palette.grey[800]}`
}));

const MetricItem = styled(Box)(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(1),
    color: theme.palette.common.white
}));

const MetricLabel = styled(Typography)(({ theme }) => ({
    fontSize: '0.75rem',
    color: theme.palette.grey[400]
}));

const MetricValue = styled(Typography)(({ theme }) => ({
    fontSize: '0.75rem',
    color: theme.palette.common.white
}));

const StatusIndicator = styled(StatusIcon)<{ connected: boolean }>(({ theme, connected }) => ({
    color: connected ? theme.palette.success.main : theme.palette.error.main,
    fontSize: '0.75rem',
    marginRight: theme.spacing(1)
}));

const RefreshRateChip = styled(Chip)(({ theme }) => ({
    backgroundColor: theme.palette.grey[800],
    color: theme.palette.common.white,
    '& .MuiChip-icon': {
        color: theme.palette.common.white
    }
}));

const MetricProgress = styled(LinearProgress)<{ severity: 'normal' | 'warning' | 'error' }>(
    ({ theme, severity }) => ({
        height: 4,
        borderRadius: 2,
        backgroundColor: theme.palette.grey[800],
        '& .MuiLinearProgress-bar': {
            backgroundColor: severity === 'normal' 
                ? theme.palette.success.main 
                : severity === 'warning'
                ? theme.palette.warning.main
                : theme.palette.error.main
        }
    })
);

interface ResourceMetrics {
    cpu_percent: number;
    memory_percent: number;
    disk_usage_percent: number;
    process_count: number;
    network_io: {
        bytes_sent: number;
        bytes_recv: number;
        packets_sent: number;
        packets_recv: number;
    };
    terminal_sessions: number;
}

interface ProcessMetrics {
    cpu_percent: number;
    memory_percent: number;
    threads: number;
    open_files: number;
    connections: number;
}

interface TerminalProps {
    sessionId?: string;
    apiKey: string;
    onClose?: () => void;
}

interface Thresholds {
    cpu: { warning: number; error: number };
    memory: { warning: number; error: number };
    disk: { warning: number; error: number };
}

const DEFAULT_THRESHOLDS: Thresholds = {
    cpu: { warning: 70, error: 85 },
    memory: { warning: 75, error: 90 },
    disk: { warning: 80, error: 95 }
};

export const Terminal: React.FC<TerminalProps> = ({ sessionId, apiKey, onClose }) => {
    const terminalRef = useRef<HTMLDivElement>(null);
    const xtermRef = useRef<XTerm>();
    const wsRef = useRef<WebSocket>();
    const [connected, setConnected] = useState(false);
    const [fontSize, setFontSize] = useState(14);
    const [systemMetrics, setSystemMetrics] = useState<ResourceMetrics | null>(null);
    const [processMetrics, setProcessMetrics] = useState<ProcessMetrics | null>(null);
    const [metricsExpanded, setMetricsExpanded] = useState(true);
    const [refreshRate, setRefreshRate] = useState(5);
    const [lastMetricsUpdate, setLastMetricsUpdate] = useState<Date | null>(null);

    useEffect(() => {
        if (!terminalRef.current) return;

        // Initialize XTerm
        const term = new XTerm({
            fontSize,
            fontFamily: 'Menlo, Monaco, "Courier New", monospace',
            theme: {
                background: '#000000',
                foreground: '#ffffff',
                cursor: '#ffffff',
                black: '#000000',
                red: '#e06c75',
                green: '#98c379',
                yellow: '#d19a66',
                blue: '#61afef',
                magenta: '#c678dd',
                cyan: '#56b6c2',
                white: '#abb2bf',
                brightBlack: '#5c6370',
                brightRed: '#e06c75',
                brightGreen: '#98c379',
                brightYellow: '#d19a66',
                brightBlue: '#61afef',
                brightMagenta: '#c678dd',
                brightCyan: '#56b6c2',
                brightWhite: '#ffffff'
            }
        });

        // Add addons
        const fitAddon = new FitAddon();
        const webLinksAddon = new WebLinksAddon();
        const searchAddon = new SearchAddon();
        const webglAddon = new WebglAddon();

        term.loadAddon(fitAddon);
        term.loadAddon(webLinksAddon);
        term.loadAddon(searchAddon);
        term.loadAddon(webglAddon);

        // Open terminal
        term.open(terminalRef.current);
        fitAddon.fit();

        // Connect WebSocket
        const ws = new WebSocket(`ws://localhost:8000/ws/terminal/${sessionId || ''}`);
        ws.onopen = () => {
            setConnected(true);
            term.write('\x1b[32mConnected to terminal.\x1b[0m\r\n');
        };

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.type === 'output') {
                term.write(message.data);
            } else if (message.type === 'error') {
                term.write(`\x1b[31m${message.data}\x1b[0m\r\n`);
            } else if (message.type === 'metrics') {
                setSystemMetrics(message.data.system);
                setProcessMetrics(message.data.process);
            }
        };

        ws.onclose = () => {
            setConnected(false);
            term.write('\x1b[31mDisconnected from terminal.\x1b[0m\r\n');
        };

        // Handle terminal input
        term.onData((data) => {
            if (connected) {
                ws.send(JSON.stringify({
                    type: 'input',
                    data
                }));
            }
        });

        // Handle terminal resize
        const handleResize = () => {
            fitAddon.fit();
            if (connected) {
                ws.send(JSON.stringify({
                    type: 'resize',
                    rows: term.rows,
                    cols: term.cols
                }));
            }
        };

        window.addEventListener('resize', handleResize);

        // Store references
        xtermRef.current = term;
        wsRef.current = ws;

        // Cleanup
        return () => {
            window.removeEventListener('resize', handleResize);
            term.dispose();
            ws.close();
        };
    }, [sessionId, fontSize]);

    const handleRefresh = () => {
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = new WebSocket(`ws://localhost:8000/ws/terminal/${sessionId || ''}`);
        }
    };

    const handleSearch = () => {
        const searchTerm = prompt('Enter search term:');
        if (searchTerm && xtermRef.current) {
            const searchAddon = new SearchAddon();
            xtermRef.current.loadAddon(searchAddon);
            searchAddon.findNext(searchTerm);
        }
    };

    const handleZoomIn = () => {
        setFontSize(prev => Math.min(prev + 2, 24));
    };

    const handleZoomOut = () => {
        setFontSize(prev => Math.max(prev - 2, 8));
    };

    const formatBytes = (bytes: number) => {
        const units = ['B', 'KB', 'MB', 'GB'];
        let value = bytes;
        let unitIndex = 0;
        
        while (value >= 1024 && unitIndex < units.length - 1) {
            value /= 1024;
            unitIndex++;
        }
        
        return `${value.toFixed(1)} ${units[unitIndex]}/s`;
    };

    const getSeverity = (value: number, type: keyof Thresholds): 'normal' | 'warning' | 'error' => {
        if (value >= DEFAULT_THRESHOLDS[type].error) return 'error';
        if (value >= DEFAULT_THRESHOLDS[type].warning) return 'warning';
        return 'normal';
    };

    const formatDuration = (date: Date) => {
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const seconds = Math.floor(diff / 1000);
        return `${seconds}s ago`;
    };

    useEffect(() => {
        if (systemMetrics) {
            setLastMetricsUpdate(new Date());
        }
    }, [systemMetrics]);

    return (
        <TerminalContainer elevation={3}>
            <TerminalHeader>
                <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
                    <StatusIndicator connected={connected} />
                    <TerminalTitle variant="subtitle2">
                        Terminal {sessionId ? `(${sessionId})` : ''}
                    </TerminalTitle>
                    {lastMetricsUpdate && (
                        <Tooltip title="Last metrics update">
                            <RefreshRateChip
                                icon={<TimerIcon />}
                                label={formatDuration(lastMetricsUpdate)}
                                size="small"
                                sx={{ ml: 1 }}
                            />
                        </Tooltip>
                    )}
                </Box>
                <Tooltip title="Search">
                    <IconButton size="small" onClick={handleSearch} sx={{ color: 'white' }}>
                        <SearchIcon />
                    </IconButton>
                </Tooltip>
                <Tooltip title="Zoom In">
                    <IconButton size="small" onClick={handleZoomIn} sx={{ color: 'white' }}>
                        <ZoomInIcon />
                    </IconButton>
                </Tooltip>
                <Tooltip title="Zoom Out">
                    <IconButton size="small" onClick={handleZoomOut} sx={{ color: 'white' }}>
                        <ZoomOutIcon />
                    </IconButton>
                </Tooltip>
                <Tooltip title="Refresh">
                    <IconButton size="small" onClick={handleRefresh} sx={{ color: 'white' }}>
                        <RefreshIcon />
                    </IconButton>
                </Tooltip>
                <Tooltip title={metricsExpanded ? "Collapse metrics" : "Expand metrics"}>
                    <IconButton 
                        size="small" 
                        onClick={() => setMetricsExpanded(!metricsExpanded)} 
                        sx={{ color: 'white' }}
                    >
                        {metricsExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                    </IconButton>
                </Tooltip>
                {onClose && (
                    <Tooltip title="Close">
                        <IconButton size="small" onClick={onClose} sx={{ color: 'white' }}>
                            <CloseIcon />
                        </IconButton>
                    </Tooltip>
                )}
            </TerminalHeader>
            <TerminalContent ref={terminalRef} />
            <Collapse in={metricsExpanded}>
                <MetricsContainer>
                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={6} md={3}>
                            <Tooltip title={`CPU Usage: ${systemMetrics?.cpu_percent.toFixed(1)}%`}>
                                <MetricItem>
                                    <SpeedIcon fontSize="small" />
                                    <Box sx={{ flexGrow: 1 }}>
                                        <MetricLabel>CPU Usage</MetricLabel>
                                        <MetricProgress 
                                            variant="determinate" 
                                            value={systemMetrics?.cpu_percent || 0}
                                            severity={getSeverity(systemMetrics?.cpu_percent || 0, 'cpu')}
                                        />
                                        <MetricValue>{systemMetrics?.cpu_percent.toFixed(1)}%</MetricValue>
                                    </Box>
                                </MetricItem>
                            </Tooltip>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Tooltip title={`Memory Usage: ${systemMetrics?.memory_percent.toFixed(1)}%`}>
                                <MetricItem>
                                    <MemoryIcon fontSize="small" />
                                    <Box sx={{ flexGrow: 1 }}>
                                        <MetricLabel>Memory Usage</MetricLabel>
                                        <MetricProgress 
                                            variant="determinate" 
                                            value={systemMetrics?.memory_percent || 0}
                                            severity={getSeverity(systemMetrics?.memory_percent || 0, 'memory')}
                                        />
                                        <MetricValue>{systemMetrics?.memory_percent.toFixed(1)}%</MetricValue>
                                    </Box>
                                </MetricItem>
                            </Tooltip>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Tooltip title={`Disk Usage: ${systemMetrics?.disk_usage_percent.toFixed(1)}%`}>
                                <MetricItem>
                                    <StorageIcon fontSize="small" />
                                    <Box sx={{ flexGrow: 1 }}>
                                        <MetricLabel>Disk Usage</MetricLabel>
                                        <MetricProgress 
                                            variant="determinate" 
                                            value={systemMetrics?.disk_usage_percent || 0}
                                            severity={getSeverity(systemMetrics?.disk_usage_percent || 0, 'disk')}
                                        />
                                        <MetricValue>{systemMetrics?.disk_usage_percent.toFixed(1)}%</MetricValue>
                                    </Box>
                                </MetricItem>
                            </Tooltip>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Tooltip title={`Network I/O: ${formatBytes(systemMetrics?.network_io.bytes_recv || 0)} received / ${formatBytes(systemMetrics?.network_io.bytes_sent || 0)} sent`}>
                                <MetricItem>
                                    <NetworkIcon fontSize="small" />
                                    <Box sx={{ flexGrow: 1 }}>
                                        <MetricLabel>Network I/O</MetricLabel>
                                        <MetricValue>
                                            {systemMetrics ? 
                                                `${formatBytes(systemMetrics.network_io.bytes_recv)} / ${formatBytes(systemMetrics.network_io.bytes_sent)}` 
                                                : '0 B/s'
                                            }
                                        </MetricValue>
                                    </Box>
                                </MetricItem>
                            </Tooltip>
                        </Grid>
                        {processMetrics && (
                            <>
                                <Grid item xs={12}>
                                    <Typography variant="subtitle2" sx={{ color: 'white', mb: 1 }}>
                                        Process Metrics
                                    </Typography>
                                </Grid>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Tooltip title={`Process CPU: ${processMetrics.cpu_percent.toFixed(1)}%`}>
                                        <MetricItem>
                                            <SpeedIcon fontSize="small" />
                                            <Box sx={{ flexGrow: 1 }}>
                                                <MetricLabel>Process CPU</MetricLabel>
                                                <MetricProgress 
                                                    variant="determinate" 
                                                    value={processMetrics.cpu_percent}
                                                    severity={getSeverity(processMetrics.cpu_percent, 'cpu')}
                                                />
                                                <MetricValue>{processMetrics.cpu_percent.toFixed(1)}%</MetricValue>
                                            </Box>
                                        </MetricItem>
                                    </Tooltip>
                                </Grid>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Tooltip title={`Process Memory: ${processMetrics.memory_percent.toFixed(1)}%`}>
                                        <MetricItem>
                                            <MemoryIcon fontSize="small" />
                                            <Box sx={{ flexGrow: 1 }}>
                                                <MetricLabel>Process Memory</MetricLabel>
                                                <MetricProgress 
                                                    variant="determinate" 
                                                    value={processMetrics.memory_percent}
                                                    severity={getSeverity(processMetrics.memory_percent, 'memory')}
                                                />
                                                <MetricValue>{processMetrics.memory_percent.toFixed(1)}%</MetricValue>
                                            </Box>
                                        </MetricItem>
                                    </Tooltip>
                                </Grid>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Tooltip title={`Threads: ${processMetrics.threads}`}>
                                        <MetricItem>
                                            <SpeedIcon fontSize="small" />
                                            <Box sx={{ flexGrow: 1 }}>
                                                <MetricLabel>Threads</MetricLabel>
                                                <MetricValue>{processMetrics.threads}</MetricValue>
                                            </Box>
                                        </MetricItem>
                                    </Tooltip>
                                </Grid>
                                <Grid item xs={12} sm={6} md={3}>
                                    <Tooltip title={`Open Files: ${processMetrics.open_files}`}>
                                        <MetricItem>
                                            <StorageIcon fontSize="small" />
                                            <Box sx={{ flexGrow: 1 }}>
                                                <MetricLabel>Open Files</MetricLabel>
                                                <MetricValue>{processMetrics.open_files}</MetricValue>
                                            </Box>
                                        </MetricItem>
                                    </Tooltip>
                                </Grid>
                            </>
                        )}
                    </Grid>
                </MetricsContainer>
            </Collapse>
        </TerminalContainer>
    );
}; 