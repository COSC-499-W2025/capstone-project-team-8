import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import config from '@/config';

export default function SkillsTimeline({ portfolioId }) {
  const { isAuthenticated, token, loading: authLoading } = useAuth();
  const [timelineData, setTimelineData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cols, setCols] = useState(6);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) setCols(6); // lg
      else if (window.innerWidth >= 768) setCols(4); // md
      else if (window.innerWidth >= 640) setCols(3); // sm
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
        
        // Format dates
        const formatted = data.timeline.map(item => {
          const date = new Date(item.date);
          return {
            skill: item.skill,
            date: date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
          };
        });
        
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

  // Chunk data into rows based on the current reactive columns constraint
  const rows = [];
  for (let i = 0; i < timelineData.length; i += cols) {
    rows.push(timelineData.slice(i, i + cols));
  }

  const colWidthClass = cols === 2 ? 'w-1/2' : cols === 3 ? 'w-1/3' : cols === 4 ? 'w-1/4' : 'w-1/6';

  return (
    <div className="w-full flex flex-col items-center py-8 overflow-hidden">
      <h2 className="text-2xl font-bold text-white mb-10">Skills Progression</h2>
      
      <div className="w-full max-w-4xl mx-auto px-8 sm:px-16 md:px-24 mt-4">
        {rows.map((row, rowIndex) => {
          const isEvenRow = rowIndex % 2 === 0;
          
          // Reverse odd rows so they physically render right-to-left mimicking a 'snake'
          const displayRow = isEvenRow ? row : [...row].reverse();

          return (
            <div 
              key={rowIndex} 
              className={`flex flex-wrap items-stretch w-full mb-12 ${isEvenRow ? 'justify-start' : 'justify-end'}`}
            >
              {displayRow.map((item, i) => {
                const timelineIndex = isEvenRow ? (rowIndex * cols + i) : (rowIndex * cols + (row.length - 1 - i));
                const isFarRightNode = i === (isEvenRow ? displayRow.length - 1 : 0);
                const isFarLeftNode = i === (isEvenRow ? 0 : displayRow.length - 1);
                
                // Which side of the current display row holds the connecting nodes?
                // Even rows bridge to the next row on their far right node
                const dropsDownFromRight = isEvenRow && i === displayRow.length - 1 && rowIndex < rows.length - 1;
                // Odd rows bridge to the next row on their far left node (which is visually left, so i=0 in reversed DOM)
                const dropsDownFromLeft = !isEvenRow && i === 0 && rowIndex < rows.length - 1;

                return (
                  <div key={timelineIndex} className={`relative flex flex-col items-center ${colWidthClass} group h-full`}>
                    
                    {/* Internal Horizontal connecting line */}
                    {i !== displayRow.length - 1 && (
                      <div className="absolute top-[10px] left-1/2 w-full h-[4px] bg-blue-500 z-0"></div>
                    )}

                    {/* Right U-turn connecting line */}
                    {dropsDownFromRight && (
                      <div 
                        className="absolute top-[10px] left-1/2 w-[calc(50%+1.5rem)] h-[calc(100%+3rem+4px)] 
                                   border-t-[4px] border-r-[4px] border-b-[4px] rounded-r-[2rem] border-blue-500 
                                   z-0 box-border pointer-events-none"
                      ></div>
                    )}

                    {/* Left U-turn connecting line */}
                    {dropsDownFromLeft && (
                      <div 
                        className="absolute top-[10px] right-1/2 w-[calc(50%+1.5rem)] h-[calc(100%+3rem+4px)] 
                                   border-t-[4px] border-l-[4px] border-b-[4px] rounded-l-[2rem] border-blue-500 
                                   z-0 box-border pointer-events-none"
                      ></div>
                    )}

                    {/* Timeline Node/Circle */}
                    <div className="relative z-10 w-6 h-6 shrink-0 rounded-full bg-[#18181b] border-[#18181b] border-4 shadow-[0_0_0_4px_#3b82f6] group-hover:scale-125 group-hover:bg-blue-500 transition-all duration-300"></div>
                    
                    {/* Content Card */}
                    <div className="mt-4 text-center px-1 z-10">
                      <h3 className="text-sm font-bold text-white mb-1 break-words leading-tight">{item.skill}</h3>
                      <div className="inline-block px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-300 text-[11px] font-semibold tracking-wider whitespace-nowrap">
                        {item.date}
                      </div>
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
