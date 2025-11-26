'use client';

import React, { useState } from 'react';
import { FomoEvent, GrowthScenario } from '@/types/simulation';
import { GROWTH_SCENARIOS, FOMO_EVENTS } from '@/lib/constants';

interface FomoTimelineProps {
  events?: FomoEvent[];
  scenario?: GrowthScenario;
  triggeredEvents?: FomoEvent[];
  showExpected?: boolean;
}

const EVENT_ICONS: Record<string, string> = {
  tge_launch: '🚀',
  partnership: '🤝',
  viral_moment: '🔥',
  exchange_listing: '📊',
  influencer: '⭐',
  holiday: '🎄',
  feature_launch: '✨',
  milestone: '🏆',
};

const EVENT_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  tge_launch: { bg: 'bg-purple-900/30', border: 'border-purple-500', text: 'text-purple-400' },
  partnership: { bg: 'bg-blue-900/30', border: 'border-blue-500', text: 'text-blue-400' },
  viral_moment: { bg: 'bg-orange-900/30', border: 'border-orange-500', text: 'text-orange-400' },
  exchange_listing: { bg: 'bg-green-900/30', border: 'border-green-500', text: 'text-green-400' },
  influencer: { bg: 'bg-yellow-900/30', border: 'border-yellow-500', text: 'text-yellow-400' },
  holiday: { bg: 'bg-red-900/30', border: 'border-red-500', text: 'text-red-400' },
  feature_launch: { bg: 'bg-cyan-900/30', border: 'border-cyan-500', text: 'text-cyan-400' },
  milestone: { bg: 'bg-amber-900/30', border: 'border-amber-500', text: 'text-amber-400' },
};

export const FomoTimeline: React.FC<FomoTimelineProps> = ({
  events,
  scenario = 'base',
  triggeredEvents = [],
  showExpected = true,
}) => {
  const [selectedEvent, setSelectedEvent] = useState<FomoEvent | null>(null);
  
  // Use provided events or get from scenario config
  const timelineEvents = events || (showExpected ? GROWTH_SCENARIOS[scenario].fomoEvents : []);
  
  // Group events by month for visualization
  const eventsByMonth = timelineEvents.reduce((acc, event) => {
    if (!acc[event.month]) acc[event.month] = [];
    acc[event.month].push(event);
    return acc;
  }, {} as Record<number, FomoEvent[]>);

  // Check if event was triggered
  const isTriggered = (event: FomoEvent): boolean => {
    return triggeredEvents.some(
      e => e.month === event.month && e.eventType === event.eventType
    );
  };

  return (
    <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-semibold text-white">⚡ FOMO Events Timeline</h3>
          <span className="px-2 py-0.5 text-xs rounded-full bg-purple-500/20 text-purple-400">
            {timelineEvents.length} events
          </span>
        </div>
        <div className="text-xs text-slate-400">
          {scenario.charAt(0).toUpperCase() + scenario.slice(1)} Scenario
        </div>
      </div>

      {/* Timeline */}
      <div className="relative">
        {/* Month markers */}
        <div className="flex justify-between mb-2">
          {Array.from({ length: 12 }, (_, i) => i + 1).map((month) => (
            <div key={month} className="flex-1 text-center">
              <span className="text-[10px] text-slate-500">M{month}</span>
            </div>
          ))}
        </div>

        {/* Timeline bar */}
        <div className="relative h-16 bg-slate-700/50 rounded-lg overflow-hidden">
          {/* Progress bar (if we have triggered events) */}
          {triggeredEvents.length > 0 && (
            <div
              className="absolute inset-y-0 left-0 bg-emerald-500/20"
              style={{
                width: `${(Math.max(...triggeredEvents.map(e => e.month)) / 12) * 100}%`,
              }}
            />
          )}

          {/* Event markers */}
          {timelineEvents.map((event, index) => {
            const left = ((event.month - 0.5) / 12) * 100;
            const colors = EVENT_COLORS[event.eventType] || EVENT_COLORS.milestone;
            const triggered = isTriggered(event);

            return (
              <button
                key={`${event.month}-${event.eventType}-${index}`}
                onClick={() => setSelectedEvent(selectedEvent === event ? null : event)}
                className={`absolute top-1/2 -translate-y-1/2 w-10 h-10 rounded-full flex items-center justify-center
                  transition-all hover:scale-110 z-10 border-2
                  ${colors.bg} ${colors.border}
                  ${triggered ? 'ring-2 ring-emerald-400 ring-offset-2 ring-offset-slate-800' : ''}
                  ${selectedEvent === event ? 'scale-125 z-20' : ''}
                `}
                style={{ left: `calc(${left}% - 20px)` }}
              >
                <span className="text-lg">{EVENT_ICONS[event.eventType] || '⚡'}</span>
              </button>
            );
          })}
        </div>

        {/* Month lines */}
        <div className="absolute inset-x-0 top-8 h-16 flex pointer-events-none">
          {Array.from({ length: 12 }, (_, i) => (
            <div
              key={i}
              className="flex-1 border-l border-slate-700/50 first:border-l-0"
            />
          ))}
        </div>
      </div>

      {/* Selected Event Detail */}
      {selectedEvent && (
        <div className={`mt-4 p-4 rounded-lg border ${
          EVENT_COLORS[selectedEvent.eventType]?.bg || 'bg-slate-700/50'
        } ${EVENT_COLORS[selectedEvent.eventType]?.border || 'border-slate-600'}`}>
          <div className="flex items-start gap-3">
            <span className="text-3xl">{EVENT_ICONS[selectedEvent.eventType] || '⚡'}</span>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <h4 className={`font-semibold ${
                  EVENT_COLORS[selectedEvent.eventType]?.text || 'text-white'
                }`}>
                  {selectedEvent.eventType.split('_').map(w => 
                    w.charAt(0).toUpperCase() + w.slice(1)
                  ).join(' ')}
                </h4>
                <span className="text-xs text-slate-400">Month {selectedEvent.month}</span>
                {isTriggered(selectedEvent) && (
                  <span className="px-1.5 py-0.5 text-[10px] rounded bg-emerald-500/20 text-emerald-400">
                    ✓ Triggered
                  </span>
                )}
              </div>
              <p className="text-sm text-slate-300">{selectedEvent.description}</p>
              <div className="flex gap-4 mt-2 text-xs">
                <span className="text-slate-400">
                  Impact: <span className="text-amber-400">{selectedEvent.impactMultiplier}x</span>
                </span>
                <span className="text-slate-400">
                  Duration: <span className="text-slate-300">{selectedEvent.durationDays} days</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Event Summary */}
      <div className="mt-4 grid grid-cols-4 gap-2">
        {Object.entries(
          timelineEvents.reduce((acc, event) => {
            acc[event.eventType] = (acc[event.eventType] || 0) + 1;
            return acc;
          }, {} as Record<string, number>)
        ).map(([type, count]) => {
          const colors = EVENT_COLORS[type] || EVENT_COLORS.milestone;
          const triggeredCount = triggeredEvents.filter(e => e.eventType === type).length;
          
          return (
            <div
              key={type}
              className={`p-2 rounded ${colors.bg} border ${colors.border} text-center`}
            >
              <div className="text-lg mb-1">{EVENT_ICONS[type] || '⚡'}</div>
              <div className="text-[10px] text-slate-400 truncate">
                {type.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
              </div>
              <div className={`text-xs font-semibold ${colors.text}`}>
                {triggeredCount > 0 ? `${triggeredCount}/${count}` : count}
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-4 pt-3 border-t border-slate-700 flex flex-wrap gap-2 text-[10px]">
        <span className="flex items-center gap-1 text-slate-400">
          <span className="w-2 h-2 rounded-full bg-emerald-500" /> Triggered
        </span>
        <span className="flex items-center gap-1 text-slate-400">
          <span className="w-2 h-2 rounded-full bg-slate-500" /> Scheduled
        </span>
        <span className="text-slate-500 ml-auto">
          Total Impact: {timelineEvents.reduce((sum, e) => sum + e.impactMultiplier, 0).toFixed(1)}x
        </span>
      </div>
    </div>
  );
};

export default FomoTimeline;

