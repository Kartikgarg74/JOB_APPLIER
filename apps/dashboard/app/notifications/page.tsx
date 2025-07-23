'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';

interface InAppNotification {
  id: number;
  user_id: number;
  message: string;
  details: Record<string, any>;
  is_read: boolean;
  created_at: string;
}

export default function NotificationsPage() {
  const { data: session } = useSession();
  const [notifications, setNotifications] = useState<InAppNotification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const userId = session?.user?.id; // Assuming user ID is available in session

  useEffect(() => {
    if (userId) {
      fetchNotifications();
    }
  }, [userId]);

  const fetchNotifications = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/notifications/${userId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: InAppNotification[] = await response.json();
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
    } catch (e: any) {
      toast.error('Failed to delete notification', { description: e.message });
    }
  };

  if (loading) {
    return <div className="p-4">Loading notifications...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">Error: {error}</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Your Notifications</h1>
      <ScrollArea className="h-[600px] w-full rounded-md border p-4">
        {notifications.length === 0 ? (
          <p>No notifications to display.</p>
        ) : (
          notifications.map((notification) => (
            <Card key={notification.id} className={`mb-4 ${notification.is_read ? 'bg-gray-100' : 'bg-white'}`}>
              <CardHeader>
                <CardTitle className="flex justify-between items-center">
                  <span>{notification.message}</span>
                  <div className="space-x-2">
                    {!notification.is_read && (
                      <Button variant="outline" size="sm" onClick={() => markAsRead(notification.id)}>
                        Mark as Read
                      </Button>
                    )}
                    <Button variant="destructive" size="sm" onClick={() => deleteNotification(notification.id)}>
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
    </div>
  );
}