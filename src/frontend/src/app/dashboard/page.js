'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { getCurrentUser } from '@/utils/api';
import Header from '@/components/Header';
import Toast from '@/components/Toast';
import config from '@/config';

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, token, user, setCurrentUser, loading: authLoading } = useAuth();
  const [loading, setLoading] = useState(true);
  const [projects, setProjects] = useState([]);
  const [topProjects, setTopProjects] = useState([]);
  const [rankedProjects, setRankedProjects] = useState([]);
  const [skills, setSkills] = useState({
    languages: {},
    frameworks: {},
  });
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const fetchData = async () => {
      try {
        // Fetch user data
        const userData = await getCurrentUser(token);
        setCurrentUser(userData.user);

        // Fetch projects
        const projectsResponse = await fetch(`${config.API_URL}/api/projects/`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (projectsResponse.ok) {
          const projectsData = await projectsResponse.json();
          const projectsList = projectsData.projects || [];
          setProjects(projectsList);

          // Calculate skills from projects
          const languageCount = {};
          const frameworkCount = {};

          projectsList.forEach((project) => {
            // Count primary classification as language
            if (project.classification_type) {
              const primaryLang = project.classification_type.split(':')[0].trim();
              languageCount[primaryLang] = (languageCount[primaryLang] || 0) + 1;
            }
            
            // Count frameworks if available in response
            if (project.frameworks && Array.isArray(project.frameworks)) {
              project.frameworks.forEach((fw) => {
                if (fw.name) {
                  frameworkCount[fw.name] = (frameworkCount[fw.name] || 0) + 1;
                }
              });
            }
          });

          setSkills({
            languages: languageCount,
            frameworks: frameworkCount,
          });
        }

        // Fetch ranked projects for avg score
        try {
          const rankedResponse = await fetch(`${config.API_URL}/api/projects/ranked/`, {
            headers: { 'Authorization': `Bearer ${token}` },
          });
          if (rankedResponse.ok) {
            const rankedData = await rankedResponse.json();
            setRankedProjects(rankedData.projects || []);
          }
        } catch (err) {
          console.log('Ranked projects not available:', err);
        }

        // Fetch top 3 ranked projects
        try {
          const topResponse = await fetch(`${config.API_URL}/api/projects/ranked/summary/`, {
            headers: { 'Authorization': `Bearer ${token}` },
          });
          if (topResponse.ok) {
            const topData = await topResponse.json();
            setTopProjects(topData.top_projects || []);
          }
        } catch (err) {
          console.log('Top projects not available:', err);
        }
      } catch (err) {
        console.log('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [authLoading, isAuthenticated, token, router]);

  const getGrade = (score) => {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  };

  const getGradeColor = (score) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 80) return 'text-blue-400';
    if (score >= 70) return 'text-yellow-400';
    if (score >= 60) return 'text-orange-400';
    return 'text-red-400';
  };

  const getGradeBg = (score) => {
    if (score >= 90) return 'bg-green-500/20 border-green-500/30';
    if (score >= 80) return 'bg-blue-500/20 border-blue-500/30';
    if (score >= 70) return 'bg-yellow-500/20 border-yellow-500/30';
    if (score >= 60) return 'bg-orange-500/20 border-orange-500/30';
    return 'bg-red-500/20 border-red-500/30';
  };

  const handleViewPortfolio = () => {
    if (user?.portfolio_url && user.portfolio_url.trim()) {
      // Open portfolio in new tab
      window.open(user.portfolio_url, '_blank', 'noopener,noreferrer');
    } else {
      // Show message that no portfolio link is available
      setMessage({ 
        type: 'error', 
        text: 'No portfolio link found. Please add your portfolio URL in your profile settings.' 
      });
    }
  };

  const avgScore = rankedProjects.length > 0
    ? rankedProjects.reduce((sum, p) => sum + (p.highlight_score || 0), 0) / rankedProjects.length
    : null;

  const getScoreForProject = (projectId) => {
    const rp = rankedProjects.find(p => p.id === projectId);
    return rp ? rp.highlight_score : null;
  };
  if (loading) {
    return (
      <>
        <Header />
        <div className="min-h-screen flex items-center justify-center">
          <p className="text-white">Loading...</p>
        </div>
      </>
    );
  }

  return (
    <>
      <Header />
      <div className="min-h-screen p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold text-white mb-12">Dashboard</h1>

          {/* Main Layout - Sushi Box Style */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-12">
            {/* Left Sidebar - Profile Section */}
            <div className="lg:col-span-1">
              <div className="bg-[var(--card-bg)] rounded-lg p-6 sticky top-8">
                {/* Profile Picture */}
                <div className="mb-6 text-center">
                  <div className="w-24 h-24 mx-auto rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center mb-4 overflow-hidden">
                    {user?.profile_image_url ? (
                      <img 
                        src={user.profile_image_url} 
                        alt={user.username}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <span className="text-4xl font-bold text-white">
                        {user?.username?.charAt(0).toUpperCase()}
                      </span>
                    )}
                  </div>
                  <h2 className="text-xl font-bold text-white">
                    {user?.first_name && user?.last_name 
                      ? `${user.first_name} ${user.last_name}`
                      : user?.username}
                  </h2>
                  <p className="text-white/60 text-sm mt-1">@{user?.username}</p>
                </div>

                {/* Profile Links */}
                <div className="space-y-2 mb-6 pt-6" style={{ borderTop: '1px solid #27272a' }}>
                  <Link
                    href="/profile"
                    className="block w-full px-4 py-2 rounded-lg text-white font-medium text-center transition-colors text-sm"
                    style={{ background: '#4f7cf7' }}
                    onMouseEnter={(e) => e.currentTarget.style.background = '#3b6ce4'}
                    onMouseLeave={(e) => e.currentTarget.style.background = '#4f7cf7'}
                  >
                    Edit Profile
                  </Link>
                  <button
                    onClick={handleViewPortfolio}
                    className="block w-full px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white font-medium text-center transition-colors text-sm"
                  >
                    View Portfolio
                  </button>
                </div>

                {/* Skills Breakdown */}
                <div className="pt-6" style={{ borderTop: '1px solid #27272a' }}>
                  <h3 className="text-lg font-semibold text-white mb-4">Skills Insights</h3>

                  {/* Languages */}
                  <div className="mb-4">
                    <p className="text-white/70 text-sm font-medium mb-2">Languages</p>
                    <div className="space-y-2">
                      {Object.entries(skills.languages).length > 0 ? (
                        Object.entries(skills.languages).map(([lang, count]) => (
                          <div key={lang} className="flex justify-between items-center">
                            <span className="text-white/60 text-sm">{lang}</span>
                            <span className="text-white font-bold">{count} {count === 1 ? 'project' : 'projects'}</span>
                          </div>
                        ))
                      ) : (
                        <p className="text-white/40 text-sm">No projects uploaded yet</p>
                      )}
                    </div>
                  </div>

                  {/* Frameworks */}
                  <div className="mb-4">
                    <p className="text-white/70 text-sm font-medium mb-2">Frameworks</p>
                    <div className="space-y-2">
                      {Object.entries(skills.frameworks).length > 0 ? (
                        Object.entries(skills.frameworks).map(([fw, count]) => (
                          <div key={fw} className="flex justify-between items-center">
                            <span className="text-white/60 text-sm">{fw}</span>
                            <span className="text-white font-bold">{count} {count === 1 ? 'project' : 'projects'}</span>
                          </div>
                        ))
                      ) : (
                        <p className="text-white/40 text-sm">No frameworks detected</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Content - Main Area */}
            <div className="lg:col-span-3 space-y-6">
              {/* Quick Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-[var(--card-bg)] rounded-lg p-4">
                  <p className="text-white/60 text-sm mb-1">Total Projects</p>
                  <p className="text-3xl font-bold text-white">{projects.length}</p>
                </div>
                <div className="bg-[var(--card-bg)] rounded-lg p-4">
                  <p className="text-white/60 text-sm mb-1">Languages Used</p>
                  <p className="text-3xl font-bold text-white">{Object.keys(skills.languages).length}</p>
                </div>
                <div className="bg-[var(--card-bg)] rounded-lg p-4">
                  <p className="text-white/60 text-sm mb-1">Frameworks Used</p>
                  <p className="text-3xl font-bold text-white">{Object.keys(skills.frameworks).length}</p>
                </div>
                <div className="bg-[var(--card-bg)] rounded-lg p-4">
                  <p className="text-white/60 text-sm mb-1">Avg Project Score</p>
                  {avgScore !== null ? (
                    <div className="flex items-baseline gap-2">
                      <p className={`text-3xl font-bold ${getGradeColor(avgScore)}`}>{getGrade(avgScore)}</p>
                      <p className="text-white/60 text-sm">{avgScore.toFixed(1)}/100</p>
                    </div>
                  ) : (
                    <p className="text-white/40 text-sm mt-1">No projects yet</p>
                  )}
                </div>
              </div>

              {/* Upload New Project Section */}
              <div className="rounded-lg p-6" style={{ background: 'rgba(79, 124, 247, 0.08)', border: '1px solid rgba(79, 124, 247, 0.15)' }}>
                <h2 className="text-2xl font-bold text-white mb-2">Analyze a New Project</h2>
                <p className="text-white/70 mb-4">Upload your project folder to extract skills, frameworks, and get AI-powered insights</p>
                <Link
                  href="/upload"
                  className="inline-block px-6 py-3 text-white font-semibold rounded-lg transition-colors"
                  style={{ background: '#4f7cf7' }}
                >
                  Upload Project
                </Link>
              </div>

              {/* Top Projects Spotlight */}
              {topProjects.length > 0 && (
                <div className="bg-[var(--card-bg)] rounded-lg p-6">
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h2 className="text-2xl font-bold text-white">Top 3 Projects</h2>
                      <p className="text-white/50 text-sm mt-1">Your highest-ranked work by quality, scale, effort &amp; breadth</p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    {topProjects.map((tp, idx) => {
                      const fc = tp.file_composition || { code: 0, content: 0, image: 0 };
                      const totalFiles = fc.code + fc.content + fc.image;

                      return (
                        <Link key={tp.project_id} href={`/projects/${tp.project_id}`} className="block">
                          <div
                            className="rounded-lg p-5 transition-all hover:scale-[1.01]"
                            style={{ background: 'rgba(79, 124, 247, 0.06)', border: '1px solid #27272a' }}
                            onMouseEnter={(e) => e.currentTarget.style.borderColor = '#4f7cf7'}
                            onMouseLeave={(e) => e.currentTarget.style.borderColor = '#27272a'}
                          >
                            {/* Header row */}
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex items-center gap-3">
                                <span className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-500/20 text-blue-400 font-bold text-sm">#{idx + 1}</span>
                                <div>
                                  <h3 className="text-lg font-semibold text-white">{tp.name}</h3>
                                  <div className="flex flex-wrap gap-1.5 mt-1">
                                    {tp.languages.slice(0, 3).map((lang) => (
                                      <span key={lang} className="px-2 py-0.5 bg-blue-500/20 text-blue-300 text-xs rounded-full">{lang}</span>
                                    ))}
                                    {tp.frameworks.slice(0, 2).map((fw) => (
                                      <span key={fw} className="px-2 py-0.5 bg-purple-500/20 text-purple-300 text-xs rounded-full">{fw}</span>
                                    ))}
                                  </div>
                                </div>
                              </div>
                              <div className="text-right">
                                <span className="text-white/50 text-xs">Project Score</span>
                                <p className={`text-xl font-bold ${getGradeColor(tp.highlight_score || 0)}`}>{tp.highlight_score || 0}<span className="text-sm text-white/40">/100</span></p>
                              </div>
                            </div>

                            {/* Summary */}
                            <p className="text-white/70 text-sm mb-3 line-clamp-2">{tp.summary}</p>

                            {/* Quick stats row */}
                            <div className="flex items-center gap-4 text-[11px] text-white/40">
                              {tp.total_commits > 0 && <span>{tp.total_commits} commits</span>}
                              {totalFiles > 0 && <span>{totalFiles} files</span>}
                              {tp.total_lines_changed > 0 && <span>{tp.total_lines_changed.toLocaleString()} lines changed</span>}
                            </div>
                          </div>
                        </Link>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Recent Projects - Scrollable Carousel */}
              <div className="bg-[var(--card-bg)] rounded-lg p-6">
                <h2 className="text-2xl font-bold text-white mb-4">Recent Projects</h2>
                {projects.length > 0 ? (
                  <div className="flex gap-4 overflow-x-auto pb-2 snap-x">
                    {projects.slice(0, 10).map((project) => (
                      <Link
                        key={project.id}
                        href={`/projects/${project.id}`}
                        className="flex-shrink-0 w-72 rounded-lg overflow-hidden snap-start transition-colors"
                        style={{ background: 'rgba(79, 124, 247, 0.08)', border: '1px solid #27272a' }}
                        onMouseEnter={(e) => e.currentTarget.style.borderColor = '#4f7cf7'}
                        onMouseLeave={(e) => e.currentTarget.style.borderColor = '#27272a'}
                      >
                        {/* Thumbnail */}
                        <div className="relative h-40 bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center overflow-hidden">
                          {project.thumbnail_url ? (
                            <img
                              src={project.thumbnail_url}
                              alt={project.name}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <span className="text-4xl">📁</span>
                          )}
                          {/* Grade Badge */}
                          {getScoreForProject(project.id) !== null && (
                            <div className={`absolute top-2 left-2 px-2 py-1 rounded text-xs font-bold border ${getGradeBg(getScoreForProject(project.id))} ${getGradeColor(getScoreForProject(project.id))}`}>
                              {getGrade(getScoreForProject(project.id))} · {getScoreForProject(project.id).toFixed(0)}
                            </div>
                          )}
                        </div>
                        
                        {/* Content */}
                        <div className="p-4">
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <h3 className="text-lg font-semibold text-white line-clamp-2">{project.name}</h3>
                              <p className="text-white/60 text-sm">
                                {new Date(project.created_at * 1000).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                          <div className="mb-3">
                            <p className="text-white/60 text-sm mb-2">
                              {project.classification_type || 'Mixed Technologies'}
                            </p>
                            <div className="flex flex-wrap gap-1">
                              {project.classification_type && (
                                <span className="inline-block px-2 py-1 bg-blue-500/30 text-blue-200 text-xs rounded">
                                  {project.classification_type}
                                </span>
                              )}
                              {project.framework_count > 0 && (
                                <span className="inline-block px-2 py-1 bg-purple-500/30 text-purple-200 text-xs rounded">
                                  {project.framework_count} frameworks
                                </span>
                              )}
                            </div>
                          </div>
                          <p className="text-blue-400 text-sm font-medium">View Project →</p>
                        </div>
                      </Link>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-white/60 mb-4">No projects uploaded yet</p>
                    <Link
                      href="/upload"
                      className="inline-block px-4 py-2 text-white font-medium rounded transition-colors"
                      style={{ background: '#4f7cf7' }}
                    >
                      Upload Your First Project
                    </Link>
                  </div>
                )}
              </div>

              {/* Recent Activity / Quick Links */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Link
                  href="/projects"
                  className="bg-[var(--card-bg)] rounded-lg p-6 hover:bg-white/5 transition-colors"
                >
                  <h3 className="text-xl font-bold text-white mb-2">View All Projects</h3>
                  <p className="text-white/60 text-sm">Explore all your uploaded and analyzed projects</p>
                  <p className="text-blue-400 text-sm mt-4 font-medium">View Projects →</p>
                </Link>

                <Link
                  href="/portfolios"
                  className="bg-[var(--card-bg)] rounded-lg p-6 hover:bg-white/5 transition-colors"
                >
                  <h3 className="text-xl font-bold text-white mb-2">My Portfolios</h3>
                  <p className="text-white/60 text-sm">Create and manage professional portfolios</p>
                  <p className="text-blue-400 text-sm mt-4 font-medium">View Portfolios →</p>
                </Link>

                <Link
                  href="/profile"
                  className="bg-[var(--card-bg)] rounded-lg p-6 hover:bg-white/5 transition-colors"
                >
                  <h3 className="text-xl font-bold text-white mb-2">Profile Settings</h3>
                  <p className="text-white/60 text-sm">Update your profile information and social links</p>
                  <p className="text-blue-400 text-sm mt-4 font-medium">Edit Profile →</p>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {message.text && (
        <Toast 
          message={message.text} 
          type={message.type}
          onClose={() => setMessage({ type: '', text: '' })}
        />
      )}
    </>
  );
}
