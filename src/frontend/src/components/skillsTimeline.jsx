import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import config from '@/config';
import styles from './skillsTimeline.module.css';

export default function SkillsTimeline({ portfolioId }) {
  const { isAuthenticated, token, loading: authLoading } = useAuth();
  const [timelineData, setTimelineData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cols, setCols] = useState(6);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) setCols(5); // lg
      else if (window.innerWidth >= 768) setCols(3); // md
      else if (window.innerWidth >= 640) setCols(2); // sm
      else setCols(2); // mobile
    };
    handleResize(); // trigger initially
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    const fetchTimeline = async () => {
      try {
        let url = `${config.API_URL}/api/skills/timeline/`;
        if (portfolioId) {
          url += `?portfolio_id=${portfolioId}`;
        }

        const response = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch skills timeline');
        }

        const data = await response.json();
        
        // Group skills by month-year so each month is a single snake node.
        const groupedByMonth = {};
        (data.timeline || []).forEach((item) => {
          const date = new Date(item.date);
          if (Number.isNaN(date.getTime())) return;
          const dateLabel = date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
          if (!groupedByMonth[dateLabel]) {
            groupedByMonth[dateLabel] = new Set();
          }
          if (item.skill) {
            groupedByMonth[dateLabel].add(item.skill);
          }
        });

        const parseMonthYear = (label) => {
          const parsed = new Date(`${label} 01`);
          return Number.isNaN(parsed.getTime()) ? 0 : parsed.getTime();
        };

        const formatted = Object.entries(groupedByMonth)
          .map(([date, skillsSet]) => ({
            date,
            skills: Array.from(skillsSet).sort((a, b) => a.localeCompare(b)),
          }))
          .sort((a, b) => parseMonthYear(a.date) - parseMonthYear(b.date));
        
        setTimelineData(formatted);
      } catch (err) {
        console.error('Error fetching timeline:', err);
        setError(err.message || 'Failed to load timeline');
      } finally {
        setLoading(false);
      }
    };

    fetchTimeline();
  }, [isAuthenticated, token, authLoading, portfolioId]);

  if (loading || authLoading) {
    return (
      <div className="flex justify-center p-8">
        <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-400 p-4 text-center">
        <p>{error}</p>
      </div>
    );
  }

  if (timelineData.length === 0) {
    return (
      <div className="text-white/50 p-4 text-center">
        <p>No skills detected in your projects yet.</p>
      </div>
    );
  }

  const timelineItems = [
    ...timelineData,
    {
      isCta: true,
      date: '',
      skills: [],
    },
  ];

  // Chunk data into rows based on the current reactive columns constraint
  const rows = [];
  for (let i = 0; i < timelineItems.length; i += cols) {
    rows.push(timelineItems.slice(i, i + cols));
  }

  const colWidthClass = cols === 2 ? 'w-1/2' : cols === 3 ? 'w-1/3' : cols === 4 ? 'w-1/4' : 'w-1/5';

  return (
    <div className="w-full flex flex-col items-center py-8">
      <h2 className="text-2xl font-bold text-white mb-10">Skills Progression</h2>
      
      <div className="w-full max-w-4xl mx-auto px-8 sm:px-16 md:px-24 mt-4">
        {rows.map((row, rowIndex) => {
          const isEvenRow = rowIndex % 2 === 0;
          
          // Reverse odd rows so they physically render right-to-left mimicking a 'snake'
          const displayRow = isEvenRow ? row : [...row].reverse();

          return (
            <div 
              key={rowIndex} 
              className={`flex flex-wrap items-stretch w-full mb-16 overflow-visible ${isEvenRow ? 'justify-start' : 'justify-end'}`}
            >
              {displayRow.map((item, i) => {
                const timelineIndex = isEvenRow ? (rowIndex * cols + i) : (rowIndex * cols + (row.length - 1 - i));
                const nextItem = displayRow[i + 1];
                const nextRowHasCta = Boolean(rows[rowIndex + 1]?.some((rowItem) => rowItem.isCta));
                
                // Which side of the current display row holds the connecting nodes?
                // Even rows bridge to the next row on their far right node
                const dropsDownFromRight = isEvenRow && i === displayRow.length - 1 && rowIndex < rows.length - 1;
                // Odd rows bridge to the next row on their far left node (which is visually left, so i=0 in reversed DOM)
                const dropsDownFromLeft = !isEvenRow && i === 0 && rowIndex < rows.length - 1;
                const isCtaAdjacentSegment = Boolean(item.isCta || nextItem?.isCta);

                return (
                  <div key={timelineIndex} className={`relative flex flex-col items-center ${colWidthClass} group h-full z-0 hover:z-[120] focus-within:z-[120] group-hover:z-[120]`}>
                    
                    {/* Internal Horizontal connecting line */}
                    {i !== displayRow.length - 1 && (
                      <div
                        className={`absolute top-[10px] left-1/2 w-full z-0 ${
                          isCtaAdjacentSegment
                            ? 'h-0 border-t-[3px] border-dotted border-gray-500'
                            : 'h-[4px] bg-blue-500'
                        }`}
                      ></div>
                    )}

                    {/* Right U-turn connecting line */}
                    {dropsDownFromRight && (
                      <div 
                        className={`absolute top-[10px] left-1/2 w-[calc(50%+1.5rem)] h-[calc(100%+3rem+4px)] 
                                   border-t-[4px] border-r-[4px] border-b-[4px] rounded-r-[2rem]
                                   z-0 box-border pointer-events-none ${
                                     nextRowHasCta ? 'border-gray-500 border-dotted' : 'border-blue-500'
                                   }`}
                      ></div>
                    )}

                    {/* Left U-turn connecting line */}
                    {dropsDownFromLeft && (
                      <div 
                        className={`absolute top-[10px] right-1/2 w-[calc(50%+1.5rem)] h-[calc(100%+3rem+4px)] 
                                   border-t-[4px] border-l-[4px] border-b-[4px] rounded-l-[2rem]
                                   z-0 box-border pointer-events-none ${
                                     nextRowHasCta ? 'border-gray-500 border-dotted' : 'border-blue-500'
                                   }`}
                      ></div>
                    )}

                    {/* Timeline Node/Circle */}
                    <div className={`relative z-10 w-6 h-6 shrink-0 rounded-full border-4 transition-all duration-300 ${
                      item.isCta
                        ? 'bg-gray-500 border-gray-500 shadow-none'
                        : 'bg-[#18181b] border-[#18181b] shadow-[0_0_0_4px_#3b82f6] group-hover:scale-125 group-hover:bg-blue-500'
                    }`}></div>
                    
                    {/* Content Card */}
                    <div className="mt-6 text-center px-1 relative z-20 group-hover:z-[120]">
                      {item.isCta ? (
                        <div className="inline-block rounded-lg border border-dashed border-blue-400/50 bg-blue-500/5 px-3 py-2">
                          <h3 className="text-[11px] font-extralight text-white/45 leading-snug">
                            Upload more projects to unlock more skills
                          </h3>
                        </div>
                      ) : (
                        <>
                          <h3
                            className="text-sm font-bold text-white mb-1 break-words leading-tight"
                          >
                            {(() => {
                              const skills = item.skills || [];
                              const preview = skills.slice(0, 2).join(', ');
                              const remaining = Math.max(skills.length - 2, 0);
                              if (!preview) return 'No skills';
                              return remaining > 0 ? `${preview} + ${remaining} others` : preview;
                            })()}
                          </h3>

                          {/* Hover popup with full monthly skill list */}
                          <div className="absolute bottom-full left-1/2 mb-2 w-64 -translate-x-1/2 rounded-lg border border-white/15 bg-[#0f172a] p-3 text-left shadow-2xl opacity-0 invisible transition-opacity duration-150 group-hover:opacity-100 group-hover:visible z-[130] pointer-events-none group-hover:pointer-events-auto">
                            <p className="text-[10px] uppercase tracking-wide text-blue-300 mb-2">{item.date}</p>
                            <div className={`max-h-40 overflow-y-auto pr-1 ${styles.modernScrollbar}`}>
                              {(item.skills || []).length > 0 ? (
                                <ul className="space-y-1">
                                  {(item.skills || []).map((skillName) => (
                                    <li key={skillName} className="text-xs text-white/90 leading-tight">
                                      {skillName}
                                    </li>
                                  ))}
                                </ul>
                              ) : (
                                <p className="text-xs text-white/60">No skills found</p>
                              )}
                            </div>
                          </div>

                          <div className="inline-block px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-300 text-[11px] font-semibold tracking-wider whitespace-nowrap">
                            {item.date}
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>
    </div>
  );
}
