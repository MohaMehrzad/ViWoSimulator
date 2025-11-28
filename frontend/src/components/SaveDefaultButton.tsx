'use client';

import { useState, useEffect } from 'react';
import { SimulationParameters } from '@/types/simulation';

interface SaveDefaultButtonProps {
  parameters: SimulationParameters;
  onLoadSavedDefaults: (params: SimulationParameters) => void;
}

const STORAGE_KEY = 'vcoin_simulator_defaults';

export function SaveDefaultButton({ parameters, onLoadSavedDefaults }: SaveDefaultButtonProps) {
  const [showNotification, setShowNotification] = useState(false);
  const [hasSavedDefaults, setHasSavedDefaults] = useState(false);
  const [showActions, setShowActions] = useState(false);

  // Check if saved defaults exist on mount
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    setHasSavedDefaults(!!saved);
  }, []);

  const handleSave = () => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(parameters));
      setHasSavedDefaults(true);
      setShowNotification(true);
      setShowActions(false);
      setTimeout(() => setShowNotification(false), 3000);
    } catch (error) {
      console.error('Failed to save defaults:', error);
      alert('Failed to save defaults. Please try again.');
    }
  };

  const handleLoad = () => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const savedParams = JSON.parse(saved);
        onLoadSavedDefaults(savedParams);
        setShowNotification(true);
        setShowActions(false);
        setTimeout(() => setShowNotification(false), 3000);
      }
    } catch (error) {
      console.error('Failed to load defaults:', error);
      alert('Failed to load saved defaults. Please try again.');
    }
  };

  const handleClear = () => {
    if (confirm('Are you sure you want to clear your saved defaults? This action cannot be undone.')) {
      try {
        localStorage.removeItem(STORAGE_KEY);
        setHasSavedDefaults(false);
        setShowActions(false);
        setShowNotification(true);
        setTimeout(() => setShowNotification(false), 3000);
      } catch (error) {
        console.error('Failed to clear defaults:', error);
        alert('Failed to clear saved defaults. Please try again.');
      }
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      <div className="fixed bottom-8 right-8 z-50">
        {/* Actions Panel */}
        {showActions && (
          <div className="mb-4 bg-white rounded-2xl shadow-2xl border-2 border-indigo-200 p-4 min-w-[280px] animate-fadeIn">
            <div className="space-y-3">
              {/* Save Button */}
              <button
                onClick={handleSave}
                className="w-full px-6 py-3 rounded-xl font-semibold text-sm
                         bg-gradient-to-r from-indigo-600 to-purple-600 text-white
                         hover:from-indigo-700 hover:to-purple-700
                         transition-all duration-200 hover:-translate-y-0.5
                         shadow-lg hover:shadow-xl
                         flex items-center justify-center gap-2"
              >
                <span className="text-lg">💾</span>
                <span>Save Current as Default</span>
              </button>

              {/* Load Button - Only show if saved defaults exist */}
              {hasSavedDefaults && (
                <button
                  onClick={handleLoad}
                  className="w-full px-6 py-3 rounded-xl font-semibold text-sm
                           bg-gradient-to-r from-emerald-600 to-teal-600 text-white
                           hover:from-emerald-700 hover:to-teal-700
                           transition-all duration-200 hover:-translate-y-0.5
                           shadow-lg hover:shadow-xl
                           flex items-center justify-center gap-2"
                >
                  <span className="text-lg">📂</span>
                  <span>Load Saved Defaults</span>
                </button>
              )}

              {/* Clear Button - Only show if saved defaults exist */}
              {hasSavedDefaults && (
                <button
                  onClick={handleClear}
                  className="w-full px-6 py-3 rounded-xl font-semibold text-sm
                           bg-gradient-to-r from-red-500 to-rose-500 text-white
                           hover:from-red-600 hover:to-rose-600
                           transition-all duration-200 hover:-translate-y-0.5
                           shadow-lg hover:shadow-xl
                           flex items-center justify-center gap-2"
                >
                  <span className="text-lg">🗑️</span>
                  <span>Clear Saved Defaults</span>
                </button>
              )}

              {/* Info */}
              <div className="pt-2 border-t border-gray-200">
                <p className="text-xs text-gray-500 text-center">
                  {hasSavedDefaults 
                    ? '✅ Custom defaults saved'
                    : '💡 No custom defaults saved yet'}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Main FAB Button */}
        <button
          onClick={() => setShowActions(!showActions)}
          className={`w-16 h-16 rounded-full font-bold text-2xl
                     bg-gradient-to-r from-indigo-600 to-purple-600 text-white
                     hover:from-indigo-700 hover:to-purple-700
                     transition-all duration-200 hover:scale-110
                     shadow-2xl hover:shadow-indigo-500/50
                     flex items-center justify-center
                     border-4 border-white
                     ${showActions ? 'rotate-45' : ''}
                     relative`}
        >
          {hasSavedDefaults && !showActions && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-emerald-500 rounded-full border-2 border-white flex items-center justify-center text-xs">
              ✓
            </span>
          )}
          {showActions ? '✕' : '💾'}
        </button>
      </div>

      {/* Success Notification */}
      {showNotification && (
        <div className="fixed top-8 right-8 z-50 animate-slideInRight">
          <div className="bg-gradient-to-r from-emerald-500 to-teal-500 text-white px-6 py-4 rounded-2xl shadow-2xl border-2 border-white">
            <div className="flex items-center gap-3">
              <span className="text-2xl">✅</span>
              <div>
                <div className="font-bold">Success!</div>
                <div className="text-sm opacity-90">
                  {hasSavedDefaults 
                    ? 'Defaults updated successfully'
                    : 'Custom defaults cleared'}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

// Hook to auto-load saved defaults on app initialization
export function useSavedDefaults(): SimulationParameters | null {
  const [savedDefaults, setSavedDefaults] = useState<SimulationParameters | null>(null);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const params = JSON.parse(saved);
        setSavedDefaults(params);
      }
    } catch (error) {
      console.error('Failed to load saved defaults:', error);
    }
  }, []);

  return savedDefaults;
}

