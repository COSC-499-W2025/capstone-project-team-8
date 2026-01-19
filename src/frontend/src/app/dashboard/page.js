'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { getCurrentUser } from '@/utils/api';
import Header from '@/components/Header';
import config from '@/config';

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, token, user, setCurrentUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [projects, setProjects] = useState([]);
  const [skills, setSkills] = useState({
    languages: {},
    frameworks: {},
  });

  useEffect(() => {
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
      } catch (err) {
        console.log('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

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
                <div className="space-y-2 mb-6 border-t border-white/10 pt-6">
                  <Link
                    href="/profile"
                    className="block w-full px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium text-center transition-colors text-sm"
                  >
                    Edit Profile
                  </Link>
                  <a
                    href={user?.portfolio_url || '#'}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block w-full px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white font-medium text-center transition-colors text-sm"
                  >
                    View Portfolio
                  </a>
                </div>

                {/* Skills Breakdown */}
                <div className="border-t border-white/10 pt-6">
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
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
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
              </div>

              {/* Previous Projects - Scrollable Carousel */}
              <div className="bg-[var(--card-bg)] rounded-lg p-6">
                <h2 className="text-2xl font-bold text-white mb-4">Recent Projects</h2>
                {projects.length > 0 ? (
                  <div className="flex gap-4 overflow-x-auto pb-2 snap-x">
                    {projects.slice(0, 10).map((project) => (
                      <Link
                        key={project.id}
                        href={`/projects/${project.id}`}
                        className="flex-shrink-0 w-72 bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-white/20 rounded-lg overflow-hidden snap-start hover:border-white/40 transition-colors"
                      >
                        {/* Thumbnail */}
                        <div className="h-40 bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center overflow-hidden">
                          {project.thumbnail_url ? (
                            <img
                              src={project.thumbnail_url}
                              alt={project.name}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <span className="text-4xl">📁</span>
                          )}
                        </div>
                        
                        {/* Content */}
                        <div className="p-4">
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <h3 className="text-lg font-semibold text-white line-clamp-2">{project.name}</h3>
                              <p className="text-white/60 text-sm">
                                {new Date(project.created_at).toLocaleDateString()}
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
                      className="inline-block px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded transition-colors"
                    >
                      Upload Your First Project
                    </Link>
                  </div>
                )}
              </div>

              {/* Upload New Project Section */}
              <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-lg p-6">
                <h2 className="text-2xl font-bold text-white mb-2">Analyze a New Project</h2>
                <p className="text-white/70 mb-4">Upload your portfolio to extract skills, frameworks, and get AI-powered insights</p>
                <Link
                  href="/upload"
                  className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
                >
                  Upload Portfolio
                </Link>
              </div>

              {/* Recent Activity / Quick Links */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Link
                  href="/projects"
                  className="bg-[var(--card-bg)] rounded-lg p-6 hover:bg-white/5 transition-colors"
                >
                  <h3 className="text-xl font-bold text-white mb-2">View All Projects</h3>
                  <p className="text-white/60 text-sm">Explore all your uploaded and analyzed projects</p>
                  <p className="text-blue-400 text-sm mt-4 font-medium">View Projects →</p>
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
    </>
  );
}

