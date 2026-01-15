'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { getCurrentUser } from '@/utils/api';
import Header from '@/components/Header';

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, token, user, setCurrentUser } = useAuth();
  const [loading, setLoading] = useState(true);

  // Mock resume data
  const mockResumes = [
    { id: 1, title: 'Tech Resume 2024', date: 'Jan 14, 2024', downloads: 3 },
    { id: 2, title: 'Full Stack Resume', date: 'Dec 20, 2023', downloads: 1 },
    { id: 3, title: 'Frontend Specialist', date: 'Nov 15, 2023', downloads: 5 },
    { id: 4, title: 'Python Developer', date: 'Oct 10, 2023', downloads: 2 },
  ];

  // Mock skills data
  const mockSkills = {
    languages: { Python: 16, JavaScript: 12, TypeScript: 8 },
    frameworks: { Django: 10, React: 8, 'Next.js': 6 },
    tools: { Git: 14, Docker: 5, PostgreSQL: 8 },
  };

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const fetchUser = async () => {
      try {
        const data = await getCurrentUser(token);
        setCurrentUser(data.user);
      } catch (err) {
        console.log('Could not fetch user profile:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
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
                      {Object.entries(mockSkills.languages).map(([lang, count]) => (
                        <div key={lang} className="flex justify-between items-center">
                          <span className="text-white/60 text-sm">{lang}</span>
                          <span className="text-white font-bold">{count} projects</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Frameworks */}
                  <div className="mb-4">
                    <p className="text-white/70 text-sm font-medium mb-2">Frameworks</p>
                    <div className="space-y-2">
                      {Object.entries(mockSkills.frameworks).map(([fw, count]) => (
                        <div key={fw} className="flex justify-between items-center">
                          <span className="text-white/60 text-sm">{fw}</span>
                          <span className="text-white font-bold">{count} projects</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Tools */}
                  <div>
                    <p className="text-white/70 text-sm font-medium mb-2">Tools</p>
                    <div className="space-y-2">
                      {Object.entries(mockSkills.tools).map(([tool, count]) => (
                        <div key={tool} className="flex justify-between items-center">
                          <span className="text-white/60 text-sm">{tool}</span>
                          <span className="text-white font-bold">{count} projects</span>
                        </div>
                      ))}
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
                  <p className="text-3xl font-bold text-white">24</p>
                </div>
                <div className="bg-[var(--card-bg)] rounded-lg p-4">
                  <p className="text-white/60 text-sm mb-1">Languages Used</p>
                  <p className="text-3xl font-bold text-white">12</p>
                </div>
                <div className="bg-[var(--card-bg)] rounded-lg p-4">
                  <p className="text-white/60 text-sm mb-1">Resumes Generated</p>
                  <p className="text-3xl font-bold text-white">{mockResumes.length}</p>
                </div>
              </div>

              {/* Previous Resumes - Scrollable Carousel */}
              <div className="bg-[var(--card-bg)] rounded-lg p-6">
                <h2 className="text-2xl font-bold text-white mb-4">Generated Resumes</h2>
                <div className="flex gap-4 overflow-x-auto pb-2 snap-x">
                  {mockResumes.map((resume) => (
                    <div
                      key={resume.id}
                      className="flex-shrink-0 w-64 bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-white/20 rounded-lg p-4 snap-start hover:border-white/40 transition-colors cursor-pointer"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="text-lg font-semibold text-white">{resume.title}</h3>
                          <p className="text-white/60 text-sm">{resume.date}</p>
                        </div>
                        <span className="text-2xl">📄</span>
                      </div>
                      <div className="text-white/60 text-sm mb-3">
                        ⬇️ {resume.downloads} downloads
                      </div>
                      <div className="flex gap-2">
                        <button className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded transition-colors">
                          View
                        </button>
                        <button className="flex-1 px-3 py-2 bg-white/10 hover:bg-white/20 text-white text-sm font-medium rounded transition-colors">
                          Download
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
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

