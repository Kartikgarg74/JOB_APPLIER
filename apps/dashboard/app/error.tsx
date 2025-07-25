'use client';

import { useEffect } from 'react';

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  useEffect(() => {
    // Optionally log error to an error reporting service
    // console.error(error);
  }, [error]);

  return (
    <div style={{ textAlign: 'center', marginTop: '10vh' }}>
      <h1 style={{ fontSize: '3rem', fontWeight: 'bold' }}>500 - Server Error</h1>
      <p>Something went wrong. Please try again later.</p>
      <button onClick={reset} style={{ marginTop: 20, padding: '10px 20px', fontSize: '1rem' }}>
        Try again
      </button>
    </div>
  );
}
