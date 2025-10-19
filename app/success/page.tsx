'use client';

import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';

function SuccessContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session_id');

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-blue-950 to-slate-950 flex items-center justify-center">
      <div className="max-w-2xl mx-auto px-4 text-center">
        <div className="mb-8">
          <svg
            className="w-20 h-20 text-green-400 mx-auto"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>

        <h1 className="text-4xl font-bold text-white mb-4">
          Welcome to WalterFetch!
        </h1>

        <p className="text-xl text-gray-300 mb-8">
          Your subscription is now active. We'll start generating your leads right away.
        </p>

        <div className="bg-white/5 border border-white/10 rounded-lg p-6 mb-8">
          <h2 className="text-lg font-semibold text-white mb-4">What happens next?</h2>
          <ul className="text-left text-gray-300 space-y-3">
            <li className="flex items-start">
              <span className="text-blue-400 mr-2">1.</span>
              Check your email for account setup instructions
            </li>
            <li className="flex items-start">
              <span className="text-blue-400 mr-2">2.</span>
              Define your Ideal Customer Profile (ICP)
            </li>
            <li className="flex items-start">
              <span className="text-blue-400 mr-2">3.</span>
              Receive your first batch of verified leads within 48 hours
            </li>
          </ul>
        </div>

        {sessionId && (
          <p className="text-sm text-gray-500 mb-4">
            Session ID: {sessionId}
          </p>
        )}

        <a
          href="mailto:hello@waltersignal.ai"
          className="inline-block px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition"
        >
          Contact Support
        </a>
      </div>
    </main>
  );
}

export default function SuccessPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-b from-slate-950 via-blue-950 to-slate-950 flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    }>
      <SuccessContent />
    </Suspense>
  );
}
