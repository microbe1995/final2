export class PushNotificationService {
  private static instance: PushNotificationService;
  private swRegistration: ServiceWorkerRegistration | null = null;

  private constructor() {}

  static getInstance(): PushNotificationService {
    if (!PushNotificationService.instance) {
      PushNotificationService.instance = new PushNotificationService();
    }
    return PushNotificationService.instance;
  }

  async initialize(): Promise<void> {
    try {
      if ('serviceWorker' in navigator && 'PushManager' in window) {
        this.swRegistration = await navigator.serviceWorker.register('/sw.js');
        // Service Worker 등록 성공
      }
    } catch (error) {
      // Service Worker 등록 실패
    }
  }

  async requestPermission(): Promise<NotificationPermission> {
    if (!('Notification' in window)) {
      return 'denied';
    }

    if (Notification.permission === 'default') {
      return await Notification.requestPermission();
    }

    return Notification.permission;
  }

  async subscribe(): Promise<PushSubscription | null> {
    if (!this.swRegistration) {
      return null;
    }

    try {
      const permission = await this.requestPermission();
      if (permission !== 'granted') {
        return null;
      }

      const subscription = await this.swRegistration.pushManager.subscribe({
        userVisibleOnly: true,
      });

      // 서버에 구독 정보 전송
      await this.sendSubscriptionToServer(subscription);

      return subscription;
    } catch (error) {
      // 구독 실패
      return null;
    }
  }

  private async sendSubscriptionToServer(
    subscription: PushSubscription
  ): Promise<void> {
    try {
      const response = await fetch('/api/push/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          subscription,
          userAgent: navigator.userAgent,
        }),
      });

      if (!response.ok) {
        // 서버 전송 실패
      }
    } catch (error) {
      // 네트워크 오류
    }
  }

  async unsubscribe(): Promise<boolean> {
    if (!this.swRegistration) {
      return false;
    }

    try {
      const subscription =
        await this.swRegistration.pushManager.getSubscription();
      if (subscription) {
        await subscription.unsubscribe();
        // 서버에서 구독 정보 제거
        return true;
      }
      return false;
    } catch (error) {
      return false;
    }
  }

  async showNotification(
    title: string,
    options?: NotificationOptions
  ): Promise<void> {
    if (Notification.permission === 'granted') {
      new Notification(title, options);
    }
  }

  async getSubscription(): Promise<PushSubscription | null> {
    if (!this.swRegistration) {
      return null;
    }

    try {
      return await this.swRegistration.pushManager.getSubscription();
    } catch (error) {
      return null;
    }
  }

  isSupported(): boolean {
    return 'serviceWorker' in navigator && 'PushManager' in window;
  }
}
