import useSWR from 'swr';
import { fetchWithRetry } from './fetchWithRetry';

interface UserProfile {
  id: number;
  name: string;
  email: string;
}

const fetcher = async (url: string) => {
  const response = await fetchWithRetry(url);
  if (!response.ok) {
    throw new Error('Failed to fetch data');
  }
  return response.json();
};

export function useUserProfile(userId: number) {
  const { data, error, isLoading } = useSWR<UserProfile>(`/api/users/${userId}`, fetcher);

  return {
    user: data,
    isLoading,
    isError: error,
  };
}

// Example of how to use it in a component:
/*
import React from 'react';
import { useUserProfile } from '../lib/useData';

function UserProfileComponent({ userId }: { userId: number }) {
  const { user, isLoading, isError } = useUserProfile(userId);

  if (isLoading) return <div>Loading...</div>;
  if (isError) return <div>Error: {isError.message}</div>;
  if (!user) return <div>No user data</div>;

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}
*/