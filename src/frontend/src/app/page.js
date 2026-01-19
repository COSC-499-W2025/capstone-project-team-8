'use client';

import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { useEffect } from "react";
import { initializeButtons } from "@/utils/buttonAnimation";

export default function Home() {
  useEffect(() => {
    initializeButtons();
  }, []);

  return (
    <div className="min-h-screen bg-primary flex flex-col items-center justify-center p-8">
      {/* Main Title */}
      <div className="text-center mb-4 fade-in">
        <h2 className="text-4xl font-bold" style={{ color: 'white', letterSpacing: '0.05em', lineHeight: '1' }}>
          Team 8 Be Great Analyzer
        </h2>
      </div>


      {/* Main Content Card */}
      <div className="max-w-2xl w-full glow-box rounded-lg p-12 text-center fade-in" style={{ 
        background: '#292828',
        borderRadius: '12px'
      }}>
        <h1 className="text-5xl font-bold mb-4" style={{ color: 'white' }}>
          Portfolio Analyzer
        </h1>
        <p className="text-lg mb-8" style={{ color: 'white' }}>
          Analyze your projects and generate insights from your codebase
        </p>

        {/* Buttons */}
        <div className="space-y-4 mb-8">
          <Link
            href="/login"
            className="inline-block w-full button-lift"
            data-block="button"
          >
            <span className="button__flair"></span>
            <span className="button__label">Login to Your Account</span>
          </Link>

          <Link
            href="/signup"
            className="inline-block w-full button-lift"
            data-block="button"
          >
            <span className="button__flair"></span>
            <span className="button__label">Create New Account</span>
          </Link>

          <button
            disabled
            className="w-full button-lift cursor-not-allowed opacity-40 transition-all"
            title="Feature coming soon"
            style={{ 
              background: 'rgba(255, 255, 255, 0.3)',
              color: 'white',
              border: 'none',
            }}
          >
            Generate One-Time Resume (Coming Soon)
          </button>
        </div>

        <p className="text-sm mb-8" style={{ color: 'white' }}>
          Supported: ZIP files containing git repositories and project files
        </p>
      </div>
    </div>
  );
}
