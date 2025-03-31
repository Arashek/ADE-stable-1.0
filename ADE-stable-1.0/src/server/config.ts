import dotenv from 'dotenv';

dotenv.config();

export const config = {
  port: process.env.PORT || 3001,
  jwtSecret: process.env.JWT_SECRET || 'your-jwt-secret',
  wsPath: '/ws',
  corsOrigins: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000'],
  db: {
    url: process.env.DATABASE_URL || 'mongodb://localhost:27017/ade',
  },
  redis: {
    url: process.env.REDIS_URL || 'redis://localhost:6379',
  },
  ws: {
    pingInterval: 30000, // 30 seconds
    pongTimeout: 5000,   // 5 seconds
    maxPayloadSize: 1024 * 1024, // 1MB
  },
  auth: {
    tokenExpiration: '24h',
    refreshTokenExpiration: '7d',
  }
}; 