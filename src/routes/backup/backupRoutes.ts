import { Router } from 'express';
import { BackupController } from '../../controllers/backup/BackupController';
import { BackupService } from '../../services/backup/BackupService';
import { Logger } from '../../core/logging/Logger';
import { Container } from '../../core/models/project/Container';
import { authenticate } from '../../middleware/auth';
import { validateRequest } from '../../middleware/validation';
import { z } from 'zod';

const router = Router();

// Validation schemas
const createBackupSchema = z.object({
  body: z.object({
    type: z.enum(['container', 'project']),
    tags: z.array(z.string()).optional()
  })
});

const listBackupsSchema = z.object({
  query: z.object({
    type: z.enum(['container', 'project']).optional(),
    status: z.enum(['completed', 'failed', 'in_progress']).optional(),
    startDate: z.string().datetime().optional(),
    endDate: z.string().datetime().optional()
  })
});

// Initialize backup service and controller
const backupService = new BackupService(
  new Container(), // This should be properly initialized with actual container instance
  new Logger(),
  {
    backupDir: process.env.BACKUP_DIR || './backups',
    retentionDays: parseInt(process.env.BACKUP_RETENTION_DAYS || '30'),
    compressionLevel: parseInt(process.env.BACKUP_COMPRESSION_LEVEL || '6'),
    excludePatterns: ['node_modules', '.git', '*.log'],
    maxConcurrentBackups: parseInt(process.env.MAX_CONCURRENT_BACKUPS || '3'),
    maxConcurrentRestores: parseInt(process.env.MAX_CONCURRENT_RESTORES || '1'),
    notificationEmail: process.env.BACKUP_NOTIFICATION_EMAIL,
    schedule: {
      frequency: 'daily',
      time: process.env.BACKUP_SCHEDULE_TIME || '00:00'
    }
  }
);

const backupController = new BackupController(backupService, new Logger());

// Routes
router.post(
  '/',
  authenticate,
  validateRequest(createBackupSchema),
  backupController.createBackup.bind(backupController)
);

router.post(
  '/:backupId/restore',
  authenticate,
  backupController.restoreBackup.bind(backupController)
);

router.get(
  '/',
  authenticate,
  validateRequest(listBackupsSchema),
  backupController.listBackups.bind(backupController)
);

router.delete(
  '/:backupId',
  authenticate,
  backupController.deleteBackup.bind(backupController)
);

router.get(
  '/active',
  authenticate,
  backupController.getActiveBackups.bind(backupController)
);

router.get(
  '/active/restores',
  authenticate,
  backupController.getActiveRestores.bind(backupController)
);

export default router; 