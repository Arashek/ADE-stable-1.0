import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { container } from 'tsyringe';
import { ConfigService } from '../services/config/ConfigService';
import { Logger } from '../services/logger/Logger';
import { Socket } from 'socket.io';
import { verify } from 'jsonwebtoken';

const config = container.resolve(ConfigService);
const logger = container.resolve(Logger);

interface AuthenticatedRequest extends Request {
  user?: {
    id: string;
    role: string;
  };
}

export function authenticateUser(
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): void {
  try {
    // Get token from Authorization header
    const authHeader = req.headers.authorization;
    if (!authHeader) {
      res.status(401).json({ error: 'No authorization token provided' });
      return;
    }

    // Check token format
    const parts = authHeader.split(' ');
    if (parts.length !== 2 || parts[0] !== 'Bearer') {
      res.status(401).json({ error: 'Invalid authorization format' });
      return;
    }

    const token = parts[1];

    // Verify token
    const secret = config.get('JWT_SECRET');
    if (!secret) {
      logger.error('JWT_SECRET not configured');
      res.status(500).json({ error: 'Server configuration error' });
      return;
    }

    try {
      const decoded = jwt.verify(token, secret) as { id: string; role: string };
      req.user = decoded;
      next();
    } catch (error) {
      if (error instanceof jwt.TokenExpiredError) {
        res.status(401).json({ error: 'Token expired' });
      } else if (error instanceof jwt.JsonWebTokenError) {
        res.status(401).json({ error: 'Invalid token' });
      } else {
        logger.error('Token verification error:', error);
        res.status(500).json({ error: 'Token verification failed' });
      }
    }
  } catch (error) {
    logger.error('Authentication error:', error);
    res.status(500).json({ error: 'Authentication failed' });
  }
}

export function authorizeRole(roles: string[]) {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction): void => {
    try {
      if (!req.user) {
        res.status(401).json({ error: 'User not authenticated' });
        return;
      }

      if (!roles.includes(req.user.role)) {
        res.status(403).json({ error: 'Insufficient permissions' });
        return;
      }

      next();
    } catch (error) {
      logger.error('Authorization error:', error);
      res.status(500).json({ error: 'Authorization failed' });
    }
  };
}

export function validateApiKey(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  try {
    const apiKey = req.headers['x-api-key'];
    if (!apiKey) {
      res.status(401).json({ error: 'No API key provided' });
      return;
    }

    const validApiKey = config.get('API_KEY');
    if (!validApiKey) {
      logger.error('API_KEY not configured');
      res.status(500).json({ error: 'Server configuration error' });
      return;
    }

    if (apiKey !== validApiKey) {
      res.status(401).json({ error: 'Invalid API key' });
      return;
    }

    next();
  } catch (error) {
    logger.error('API key validation error:', error);
    res.status(500).json({ error: 'API key validation failed' });
  }
}

export const authenticateSocket = async (socket: Socket, next: (err?: Error) => void) => {
  try {
    const token = socket.handshake.auth.token;
    if (!token) {
      throw new Error('Authentication token not provided');
    }

    const decoded = verify(token, config.get('JWT_SECRET'));
    
    // Attach user info to socket
    socket.data.user = decoded;
    next();
  } catch (error) {
    next(new Error('Authentication failed'));
  }
};

export const authenticateUser = (req: any, res: any, next: any) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) {
      return res.status(401).json({ message: 'Authentication token not provided' });
    }

    const decoded = verify(token, config.get('JWT_SECRET'));
    
    // Attach user info to request
    req.user = decoded;
    next();
  } catch (error) {
    res.status(401).json({ message: 'Authentication failed' });
  }
}; 