import { ResourceUsage } from './execution';

export interface SystemMetrics {
    cpu: {
        percent: number;
        cores: number;
        frequency: number;
        temperature?: number;
    };
    memory: {
        total: number;
        available: number;
        used: number;
        percent: number;
        swap: {
            total: number;
            used: number;
            percent: number;
        };
    };
    disk: {
        total: number;
        used: number;
        free: number;
        percent: number;
        partitions: DiskPartition[];
    };
    network: {
        interfaces: NetworkInterface[];
        connections: NetworkConnection[];
        io: {
            bytesSent: number;
            bytesReceived: number;
            packetsSent: number;
            packetsReceived: number;
        };
    };
    processes: {
        total: number;
        running: number;
        blocked: number;
        topProcesses: ProcessInfo[];
    };
}

export interface ProcessMetrics {
    pid: number;
    name: string;
    cpu: {
        percent: number;
        user: number;
        system: number;
    };
    memory: {
        percent: number;
        rss: number;
        vms: number;
    };
    threads: number;
    openFiles: number;
    connections: number;
    status: string;
    createTime: number;
    command: string[];
    environment: Record<string, string>;
}

export interface DiskPartition {
    device: string;
    mountpoint: string;
    fstype: string;
    total: number;
    used: number;
    free: number;
    percent: number;
}

export interface NetworkInterface {
    name: string;
    address: string;
    netmask: string;
    broadcast: string;
    mac: string;
    speed: number;
    duplex: string;
    mtu: number;
    status: string;
}

export interface NetworkConnection {
    localAddress: string;
    localPort: number;
    remoteAddress: string;
    remotePort: number;
    status: string;
    type: string;
    pid?: number;
}

export interface ProcessInfo {
    pid: number;
    name: string;
    cpu: number;
    memory: number;
    command: string;
}

export interface MonitoringConfig {
    updateInterval: number;
    retentionPeriod: number;
    thresholds: {
        cpu: {
            warning: number;
            critical: number;
        };
        memory: {
            warning: number;
            critical: number;
        };
        disk: {
            warning: number;
            critical: number;
        };
        network: {
            warning: number;
            critical: number;
        };
    };
    alerts: {
        enabled: boolean;
        channels: string[];
        cooldown: number;
    };
}

export interface MonitoringMetrics {
    systemMetrics: SystemMetrics;
    processMetrics: ProcessMetrics[];
    resourceUsage: ResourceUsage;
    alerts: Alert[];
    history: {
        timestamp: string;
        metrics: SystemMetrics;
    }[];
}

export interface Alert {
    id: string;
    type: 'warning' | 'critical' | 'info';
    message: string;
    timestamp: string;
    acknowledged: boolean;
    details?: any;
} 