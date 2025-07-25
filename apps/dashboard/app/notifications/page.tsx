'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useSession } from 'next-auth/react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../../frontend/components/ui/card';
import { Button } from '../../../../frontend/components/ui/button';
import { ScrollArea } from '../../../../frontend/components/ui/scroll-area';
import { toast } from 'sonner';
import { Alert, AlertDescription } from '../../../../frontend/components/ui/alert';

interface InAppNotification {
  id: number;
  user_id: number;
  message: string;
  details: Record<string, any>;
  is_read: boolean;
  created_at: string;
}

// ErrorBoundary component
function ErrorBoundary({ children }: { children: React.ReactNode }) {
  const [error, setError] = useState<Error | null>(null)
  return error ? (
    <Alert variant="destructive" className="mb-4" role="alert" aria-live="assertive">
      <AlertDescription>
        <div className="flex justify-between items-center">
          <span>{error.message || "An unexpected error occurred. Please try again."}</span>
          <button onClick={() => setError(null)} className="ml-4 text-lg font-bold focus:outline-none" aria-label="Dismiss error">&times;</button>
        </div>
      </AlertDescription>
    </Alert>
  ) : (
    <ErrorBoundaryInner setError={setError}>{children}</ErrorBoundaryInner>
  )
}
class ErrorBoundaryInner extends React.Component<{ setError: (e: Error) => void; children: React.ReactNode }> {
  componentDidCatch(error: Error) {
    this.props.setError(error)
  }
  render() {
    return this.props.children
  }
}

export default function NotificationsPage() {
  const session = useSession()?.data;
  const [notifications, setNotifications] = useState<InAppNotification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const prevNotificationIds = useRef<Set<number>>(new Set());

  const userId = session?.user?.id; // Assuming user ID is available in session

  useEffect(() => {
    if (userId) {
      fetchNotifications();
      // Polling for real-time updates every 10 seconds
      const interval = setInterval(() => {
        fetchNotifications(true);
      }, 10000);
      return () => clearInterval(interval);
    }
  }, [userId]);

  const fetchNotifications = async (isPolling = false) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/notifications/${userId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: InAppNotification[] = await response.json();
      // Detect new notifications
      if (isPolling) {
        const newIds = new Set(data.map(n => n.id));
        const prevIds = prevNotificationIds.current;
        const newNotifications = data.filter(n => !prevIds.has(n.id));
        if (newNotifications.length > 0) {
          newNotifications.forEach(n => {
            toast(n.message, {
              description: n.details?.subject || 'You have a new notification',
            });
          });
        }
        prevNotificationIds.current = newIds;
      } else {
        prevNotificationIds.current = new Set(data.map(n => n.id));
      }
      setNotifications(data);
    } catch (e: any) {
      setError(e.message);
      toast.error('Failed to fetch notifications', { description: e.message });
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId: number) => {
    try {
      const response = await fetch(`/api/notifications/${notificationId}/mark-read`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      setNotifications((prev) =>
        prev.map((n) => (n.id === notificationId ? { ...n, is_read: true } : n))
      );
      toast.success('Notification marked as read.');
      console.log('Analytics: Notification marked as read', notificationId);
    } catch (e: any) {
      toast.error('Failed to mark notification as read', { description: e.message });
    }
  };

  const deleteNotification = async (notificationId: number) => {
    try {
      const response = await fetch(`/api/notifications/${notificationId}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      setNotifications((prev) => prev.filter((n) => n.id !== notificationId));
      toast.success('Notification deleted.');
      console.log('Analytics: Notification deleted', notificationId);
    } catch (e: any) {
      toast.error('Failed to delete notification', { description: e.message });
    }
  };

  if (loading) {
    return <div className="p-4" role="status" aria-label="Loading notifications">Loading notifications...</div>;
  }

  if (error) {
    return (
      <Alert variant="destructive" className="mb-4" role="alert" aria-live="assertive">
        <AlertDescription>
          <div className="flex justify-between items-center">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="ml-4 text-lg font-bold focus:outline-none" aria-label="Dismiss error">&times;</button>
          </div>
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <ErrorBoundary>
      <main role="main" aria-label="Notifications" tabIndex={-1} className="container mx-auto p-4 focus:outline-none">
        <h1 className="text-3xl font-bold mb-6">Your Notifications</h1>
        <ScrollArea className="h-[600px] w-full rounded-md border p-4">
          {notifications.length === 0 ? (
            <p>No notifications to display.</p>
          ) : (
            notifications.map((notification) => (
              <Card key={notification.id} className={`mb-4 ${notification.is_read ? 'bg-gray-100' : 'bg-white'}`} tabIndex={0} aria-label={`Notification: ${notification.message}`}>
                <CardHeader>
                  <CardTitle className="flex justify-between items-center">
                    <span>{notification.message}</span>
                    <div className="space-x-2">
                      {!notification.is_read && (
                        <Button variant="outline" size="sm" onClick={() => markAsRead(notification.id)} aria-label="Mark as read">
                          Mark as Read
                        </Button>
                      )}
                      <Button variant="destructive" size="sm" onClick={() => deleteNotification(notification.id)} aria-label="Delete notification">
                        Delete
                      </Button>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-500">Received: {new Date(notification.created_at).toLocaleString()}</p>
                  {notification.details && Object.keys(notification.details).length > 0 && (
                    <div className="mt-2 text-xs text-gray-600">
                      <strong>Details:</strong>
                      <pre className="bg-gray-50 p-2 rounded mt-1">{JSON.stringify(notification.details, null, 2)}</pre>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </ScrollArea>
      </main>
    </ErrorBoundary>
  );
}
