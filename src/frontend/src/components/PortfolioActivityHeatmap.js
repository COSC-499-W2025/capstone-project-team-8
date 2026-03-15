'use client';

import { useEffect, useState } from 'react';
import config from '@/config';

export default function PortfolioActivityHeatmap({ portfolioId, token }) {
  const [heatmapData, setHeatmapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [hoveredDate, setHoveredDate] = useState(null);
  const [hoveredData, setHoveredData] = useState(null);
  const [currentYearIndex, setCurrentYearIndex] = useState(0);

  useEffect(() => {
    const fetchHeatmapData = async () => {
      try {
        const headers = {};
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(
          `${config.API_URL}/api/portfolio/${portfolioId}/activity-heatmap/`,
          { headers }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch heatmap data');
        }

        const data = await response.json();
        setHeatmapData(data);
        setCurrentYearIndex(0); // Reset to first year when data loads
      } catch (err) {
        console.error('Error fetching heatmap data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchHeatmapData();
  }, [portfolioId, token]);

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 border border-slate-700">
        <h2 className="text-xl font-bold text-white mb-4">Activity Heatmap</h2>
        <div className="flex justify-center items-center h-40">
          <div className="animate-pulse text-slate-400">Loading activity data...</div>
        </div>
      </div>
    );
  }

  if (error || !heatmapData) {
    return (
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 border border-slate-700">
        <h2 className="text-xl font-bold text-white mb-4">Activity Heatmap</h2>
        <div className="text-slate-400 text-center py-8">
          {error ? `Error: ${error}` : 'No activity data available'}
        </div>
      </div>
    );
  }

  // Generate calendar weeks grouped by year
  const generateCalendarByYear = () => {
    if (!heatmapData.activity_data || heatmapData.activity_data.length === 0) {
      return {};
    }

    const startDate = new Date(heatmapData.date_range.start);
    const endDate = new Date(heatmapData.date_range.end);

    // Create activity lookup
    const activityMap = {};
    heatmapData.activity_data.forEach((entry) => {
      activityMap[entry.date] = entry;
    });

    // Group by year
    const yearData = {};
    let currentDate = new Date(startDate);

    // Find the Monday before or on the start date
    currentDate.setDate(currentDate.getDate() - currentDate.getDay());

    while (currentDate <= endDate) {
      const year = currentDate.getFullYear();

      if (!yearData[year]) {
        yearData[year] = [];
      }

      // Create week
      const week = [];
      for (let i = 0; i < 7; i++) {
        const dateStr = currentDate.toISOString().split('T')[0];
        const activity = activityMap[dateStr];
        week.push({
          date: new Date(currentDate),
          dateStr,
          activity: activity || { count: 0, projects: [] },
        });
        currentDate.setDate(currentDate.getDate() + 1);
      }

      yearData[year].push(week);
    }

    return yearData;
  };

  const getActivityColor = (count) => {
    if (count === 0) return 'bg-slate-700';
    if (count === 1) return 'bg-blue-900';
    if (count <= 3) return 'bg-blue-700';
    if (count <= 7) return 'bg-blue-500';
    if (count <= 14) return 'bg-blue-400';
    return 'bg-blue-300';
  };

  const getActivityIntensity = (count) => {
    if (count === 0) return 'None';
    if (count === 1) return 'Very Low';
    if (count <= 3) return 'Low';
    if (count <= 7) return 'Medium';
    if (count <= 14) return 'High';
    return 'Very High';
  };

  const dayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 border border-slate-700">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white">Activity Heatmap</h2>
        {heatmapData.total_activity > 0 && (
          <div className="text-right">
            <div className="text-sm text-slate-400">Total Activity</div>
            <div className="text-2xl font-bold text-blue-400">{heatmapData.total_activity}</div>
          </div>
        )}
      </div>

      {heatmapData.date_range.start && heatmapData.date_range.end && (
        <div className="text-sm text-slate-400 mb-4">
          {heatmapData.date_range.start} to {heatmapData.date_range.end}
        </div>
      )}

      {heatmapData.activity_data.length === 0 ? (
        <div className="text-slate-400 text-center py-8">
          No activity data available for this portfolio
        </div>
      ) : (
        <>
          {(() => {
            const yearData = generateCalendarByYear();
            const years = Object.keys(yearData)
              .map((y) => parseInt(y))
              .sort((a, b) => a - b);

            if (years.length === 0) {
              return (
                <div className="text-slate-400 text-center py-8">
                  No activity data available for this portfolio
                </div>
              );
            }

            const currentYear = years[currentYearIndex];
            const weeks = yearData[currentYear];

            return (
              <>
                {/* Year navigation */}
                <div className="flex items-center justify-between mb-6">
                  <button
                    onClick={() =>
                      setCurrentYearIndex(Math.max(0, currentYearIndex - 1))
                    }
                    disabled={currentYearIndex === 0}
                    className="px-3 py-1.5 rounded bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium transition-colors"
                  >
                    ← Previous
                  </button>

                  <h3 className="text-lg font-bold text-white">{currentYear}</h3>

                  <button
                    onClick={() =>
                      setCurrentYearIndex(
                        Math.min(years.length - 1, currentYearIndex + 1)
                      )
                    }
                    disabled={currentYearIndex === years.length - 1}
                    className="px-3 py-1.5 rounded bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium transition-colors"
                  >
                    Next →
                  </button>
                </div>

                {/* Year indicator */}
                <div className="flex justify-center gap-1 mb-4">
                  {years.map((year, idx) => (
                    <button
                      key={year}
                      onClick={() => setCurrentYearIndex(idx)}
                      className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                        idx === currentYearIndex
                          ? 'bg-blue-500 text-white'
                          : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                      }`}
                    >
                      {year}
                    </button>
                  ))}
                </div>

                {/* Day labels */}
                <div className="flex gap-1 mb-2">
                  <div className="w-10"></div>
                  <div className="flex gap-1">
                    {dayLabels.map((day) => (
                      <div
                        key={day}
                        className="w-3 h-3 text-xs text-slate-500 flex items-center justify-center"
                      >
                        {day.charAt(0)}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Heatmap grid for current year */}
                <div className="space-y-1">
                  {weeks.map((week, weekIdx) => (
                    <div key={weekIdx} className="flex gap-1">
                      {/* Month label */}
                      <div className="w-10 text-xs text-slate-500 flex items-start pt-1">
                        {weekIdx === 0 || week[0].date.getDate() <= 7 ? (
                          <span>
                            {week[0].date.toLocaleDateString('en-US', {
                              month: 'short',
                            })}
                          </span>
                        ) : null}
                      </div>

                      {/* Day cells */}
                      <div className="flex gap-1">
                        {week.map((day) => (
                          <div
                            key={day.dateStr}
                            className="relative group"
                            onMouseEnter={() => {
                              setHoveredDate(day.dateStr);
                              setHoveredData(day.activity);
                            }}
                            onMouseLeave={() => {
                              setHoveredDate(null);
                              setHoveredData(null);
                            }}
                          >
                            <div
                              className={`w-3 h-3 rounded-sm cursor-pointer transition-all duration-200 ${getActivityColor(
                                day.activity.count
                              )} hover:ring-2 hover:ring-blue-400`}
                              title={`${day.dateStr}: ${day.activity.count} activities`}
                            />

                            {/* Tooltip */}
                            {hoveredDate === day.dateStr && hoveredData && (
                              <div className="absolute z-10 bg-slate-950 border border-slate-600 rounded-lg p-3 text-sm text-white whitespace-nowrap -top-32 -left-8 pointer-events-none">
                                <div className="font-semibold">
                                  {day.dateStr}
                                </div>
                                <div className="text-slate-300">
                                  Activity:{' '}
                                  <span className="text-blue-400 font-bold">
                                    {hoveredData.count}
                                  </span>
                                </div>
                                <div className="text-slate-400 text-xs">
                                  Intensity:{' '}
                                  {getActivityIntensity(hoveredData.count)}
                                </div>
                                {hoveredData.projects &&
                                  hoveredData.projects.length > 0 && (
                                    <div className="mt-2 border-t border-slate-600 pt-2">
                                      <div className="text-slate-400 text-xs mb-1">
                                        Project Breakdown:
                                      </div>
                                      {hoveredData.projects
                                        .slice(0, 3)
                                        .map((project, idx) => (
                                          <div
                                            key={idx}
                                            className="text-slate-300 text-xs"
                                          >
                                            • {project.name}: {project.count}
                                          </div>
                                        ))}
                                      {hoveredData.projects.length > 3 && (
                                        <div className="text-slate-400 text-xs mt-1">
                                          +{hoveredData.projects.length - 3}{' '}
                                          more
                                        </div>
                                      )}
                                    </div>
                                  )}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </>
            );
          })()}

          {/* Legend */}
          <div className="mt-6 flex items-center gap-4 text-xs text-slate-400 flex-wrap">
            <span>Less</span>
            <div className="flex gap-1">
              {['bg-slate-700', 'bg-blue-900', 'bg-blue-700', 'bg-blue-500', 'bg-blue-400', 'bg-blue-300'].map(
                (color, idx) => (
                  <div key={idx} className={`w-3 h-3 rounded-sm ${color}`} />
                )
              )}
            </div>
            <span>More</span>
          </div>

          {/* Stats */}
          <div className="mt-6 grid grid-cols-3 gap-4 text-sm">
            <div>
              <div className="text-slate-400">Max Daily Activity</div>
              <div className="text-xl font-bold text-blue-400">{heatmapData.max_activity}</div>
            </div>
            <div>
              <div className="text-slate-400">Min Daily Activity</div>
              <div className="text-xl font-bold text-blue-300">{heatmapData.min_activity}</div>
            </div>
            <div>
              <div className="text-slate-400">Total Days Active</div>
              <div className="text-xl font-bold text-blue-400">
                {heatmapData.activity_data.filter((d) => d.count > 0).length}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
