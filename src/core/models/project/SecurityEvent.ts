export enum SecurityEventType {
  POLICY_CHANGE = 'POLICY_CHANGE',
  USER_ACCESS = 'USER_ACCESS',
  NETWORK_CHANGE = 'NETWORK_CHANGE',
  PERMISSION_CHANGE = 'PERMISSION_CHANGE',
  SECURITY_VIOLATION = 'SECURITY_VIOLATION',
  CONTAINER_START = 'CONTAINER_START',
  CONTAINER_STOP = 'CONTAINER_STOP',
  RESOURCE_LIMIT = 'RESOURCE_LIMIT',
  CAPABILITY_CHANGE = 'CAPABILITY_CHANGE'
}

export interface SecurityEvent {
  timestamp: string;
  eventType: SecurityEventType;
  containerId: string;
  userId: string;
  action: string;
  details: Record<string, any>;
  severity: 'low' | 'medium' | 'high' | 'critical';
} 