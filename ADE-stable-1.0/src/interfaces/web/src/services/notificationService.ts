import { Subject } from 'rxjs';

export type NotificationSeverity = 'success' | 'info' | 'warning' | 'error';

export interface Notification {
  message: string;
  severity: NotificationSeverity;
  duration?: number;
}

class NotificationService {
  private notificationSubject = new Subject<Notification>();

  public notify(notification: Notification) {
    this.notificationSubject.next(notification);
  }

  public success(message: string, duration = 3000) {
    this.notify({ message, severity: 'success', duration });
  }

  public info(message: string, duration = 3000) {
    this.notify({ message, severity: 'info', duration });
  }

  public warning(message: string, duration = 4000) {
    this.notify({ message, severity: 'warning', duration });
  }

  public error(message: string, duration = 5000) {
    this.notify({ message, severity: 'error', duration });
  }

  public onNotification() {
    return this.notificationSubject.asObservable();
  }
}

export const notificationService = new NotificationService(); 