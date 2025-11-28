import { clsx, type ClassValue } from 'clsx';

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatNumber(num: number | string | boolean | undefined | null): string {
  if (num === undefined || num === null) {
    return '0';
  }
  if (typeof num === 'boolean') {
    return num ? '1' : '0';
  }
  if (typeof num === 'string') {
    const parsed = parseFloat(num);
    if (isNaN(parsed)) return num;
    num = parsed;
  }
  if (isNaN(num)) {
    return '0';
  }
  if (num >= 1_000_000) {
    return (num / 1_000_000).toFixed(2) + 'M';
  } else if (num >= 1_000) {
    return (num / 1_000).toFixed(1) + 'K';
  } else {
    return num.toFixed(0);
  }
}

export function formatCurrency(value: number | string | boolean | undefined | null, decimals: number = 0): string {
  if (value === undefined || value === null) return '$0';
  if (typeof value === 'boolean') return '$0';
  if (typeof value === 'string') {
    const parsed = parseFloat(value);
    if (isNaN(parsed)) return '$0';
    value = parsed;
  }
  if (!isFinite(value)) return '$0';
  return '$' + value.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function formatPercent(value: number, decimals: number = 1): string {
  return value.toFixed(decimals) + '%';
}

export function formatDetailedNumber(value: number, decimals: number = 2): string {
  if (!isFinite(value)) return '0';
  if (Math.abs(value) >= 1000) {
    return value.toLocaleString(undefined, { maximumFractionDigits: 0 });
  }
  return value.toLocaleString(undefined, { maximumFractionDigits: decimals });
}

// Color utilities for module styling
export const moduleColors = {
  identity: {
    bg: 'bg-violet-500',
    text: 'text-violet-500',
    border: 'border-violet-500',
    light: 'bg-violet-50',
  },
  content: {
    bg: 'bg-pink-500',
    text: 'text-pink-500',
    border: 'border-pink-500',
    light: 'bg-pink-50',
  },
  advertising: {
    bg: 'bg-blue-500',
    text: 'text-blue-500',
    border: 'border-blue-500',
    light: 'bg-blue-50',
  },
  rewards: {
    bg: 'bg-amber-500',
    text: 'text-amber-500',
    border: 'border-amber-500',
    light: 'bg-amber-50',
  },
};

// Get status color based on value
export function getStatusColor(value: number, thresholds: { danger: number; warning: number }): string {
  if (value < thresholds.danger) return 'text-red-500';
  if (value < thresholds.warning) return 'text-amber-500';
  return 'text-emerald-500';
}

// Get margin status
export function getMarginStatus(margin: number): { color: string; label: string } {
  if (margin >= 50) return { color: 'text-emerald-500', label: 'Excellent' };
  if (margin >= 30) return { color: 'text-emerald-400', label: 'Good' };
  if (margin >= 10) return { color: 'text-amber-500', label: 'Moderate' };
  if (margin >= 0) return { color: 'text-amber-400', label: 'Low' };
  return { color: 'text-red-500', label: 'Negative' };
}

// Get recapture status
export function getRecaptureStatus(rate: number): { color: string; label: string } {
  if (rate >= 40) return { color: 'text-emerald-500', label: 'Excellent' };
  if (rate >= 20) return { color: 'text-emerald-400', label: 'High' };
  if (rate >= 10) return { color: 'text-amber-500', label: 'Moderate' };
  return { color: 'text-red-500', label: 'Low' };
}

// Deep merge objects
export function deepMerge<T extends object>(target: T, source: Partial<T>): T {
  const output = { ...target } as T;
  
  for (const key in source) {
    if (Object.prototype.hasOwnProperty.call(source, key)) {
      const sourceValue = source[key as keyof T];
      const targetValue = target[key as keyof T];
      
      if (sourceValue !== undefined) {
        if (
          typeof sourceValue === 'object' &&
          sourceValue !== null &&
          !Array.isArray(sourceValue) &&
          typeof targetValue === 'object' &&
          targetValue !== null
        ) {
          (output as Record<string, unknown>)[key] = deepMerge(
            targetValue as object,
            sourceValue as object
          );
        } else {
          (output as Record<string, unknown>)[key] = sourceValue;
        }
      }
    }
  }
  
  return output;
}

