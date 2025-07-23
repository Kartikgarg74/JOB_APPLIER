'use client';
// [CONTEXT] Custom hook for centralized UI authorization logic
import { useEffect, useState } from 'react';
import { supabase } from '../../lib/supabase';
import { User } from '@supabase/supabase-js';

export const useAuthorization = () => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const getSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setUser(session?.user || null);
      setIsLoading(false);
    };

    getSession();

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user || null);
      setIsLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const isAuthenticated = !!user;

  // Example: Check if user has a specific role
  const hasRole = (role: string) => {
    // This is a placeholder. In a real application, user roles would come from your authentication system.
    // For Supabase, you might store roles in a separate table and link them to the user.
    // For example: return user?.user_metadata?.roles?.includes(role) || false;
    return user?.user_metadata?.roles?.includes(role) || false;
  };

  // Example: Check if user can perform a specific action
  const can = (action: string) => {
    // This is a placeholder. Implement your permission logic here.
    // This could involve checking user roles, specific permissions, or other attributes.
    // [CONTEXT] Implement more granular permission logic here based on roles or other attributes
    // For example, a simple check could be:
    // if (action === 'create_job' && user?.user_metadata?.roles?.includes('admin')) return true;
    // if (action === 'view_profile' && (user?.user_metadata?.roles?.includes('user') || user?.user_metadata?.roles?.includes('admin'))) return true;
    return user?.user_metadata?.roles?.includes("admin") || false; // Placeholder: only admin can do anything for now
  };

  return {
    isAuthenticated,
    user,
    hasRole,
    can,
    isLoading,
  };
};
