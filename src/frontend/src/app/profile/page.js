'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { getCurrentUser } from '@/utils/api';
import Header from '@/components/Header';
import Toast from '@/components/Toast';
import { initializeButtons } from '@/utils/buttonAnimation';
import config from '@/config';

export default function ProfilePage() {
  const router = useRouter();
  const { isAuthenticated, token, user, setCurrentUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    bio: '',
    github_username: '',
    github_email: '',
    linkedin_url: '',
    portfolio_url: '',
    twitter_username: '',
    university: '',
    degree_major: '',
    education_city: '',
    education_state: '',
    expected_graduation: '',
  });

  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  const [profileImagePreview, setProfileImagePreview] = useState(user?.profile_image_url || '');
  const [uploadingImage, setUploadingImage] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const fetchUser = async () => {
      try {
        const data = await getCurrentUser(token);
        setCurrentUser(data.user);
        setFormData({
          username: data.user.username || '',
          email: data.user.email || '',
          first_name: data.user.first_name || '',
          last_name: data.user.last_name || '',
          bio: data.user.bio || '',
          github_username: data.user.github_username || '',
          github_email: data.user.github_email || '',
          linkedin_url: data.user.linkedin_url || '',
          portfolio_url: data.user.portfolio_url || '',
          twitter_username: data.user.twitter_username || '',
          university: data.user.university || '',
          degree_major: data.user.degree_major || '',
          education_city: data.user.education_city || '',
          education_state: data.user.education_state || '',
          expected_graduation: data.user.expected_graduation || '',
        });
      } catch (err) {
        console.error('Error fetching user:', err);
        setMessage({ type: 'error', text: 'Failed to load profile information' });
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  // Initialize button animations after component render with multiple delays to catch all buttons
  useEffect(() => {
    if (loading) return;
    
    const timer1 = setTimeout(() => {
      initializeButtons();
    }, 100);
    
    const timer2 = setTimeout(() => {
      initializeButtons();
    }, 300);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, [loading]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({ ...prev, [name]: value }));
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await fetch(`${config.API_URL}/api/users/me/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const text = await response.text();
        let errorMessage = 'Failed to update profile';
        try {
          const errorData = JSON.parse(text);
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          // If it's HTML (error page), show a generic message
          if (text.includes('<!DOCTYPE') || text.includes('<html')) {
            errorMessage = 'API endpoint not found. Check your backend connection.';
          }
          console.error('Error response:', text);
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setCurrentUser(data.user);
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordUpdate = async (e) => {
    e.preventDefault();
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage({ type: 'error', text: 'New passwords do not match' });
      return;
    }

    if (passwordData.new_password.length < 8) {
      setMessage({ type: 'error', text: 'Password must be at least 8 characters long' });
      return;
    }

    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await fetch(`${config.API_URL}/api/users/password/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          current_password: passwordData.current_password,
          new_password: passwordData.new_password,
        }),
      });

      if (!response.ok) {
        const text = await response.text();
        let errorMessage = 'Failed to update password';
        try {
          const errorData = JSON.parse(text);
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          // If it's HTML (error page), show a generic message
          if (text.includes('<!DOCTYPE') || text.includes('<html')) {
            errorMessage = 'API endpoint not found. Check your backend connection.';
          }
        }
        throw new Error(errorMessage);
      }

      setMessage({ type: 'success', text: 'Password updated successfully!' });
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    } finally {
      setSaving(false);
    }
  };

  const handleProfileImageChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setProfileImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleProfileImageUpload = async (e) => {
    e.preventDefault();
    const fileInput = document.querySelector('input[type="file"][name="profile_image"]');
    const file = fileInput?.files?.[0];

    if (!file) {
      setMessage({ type: 'error', text: 'Please select an image' });
      return;
    }

    setUploadingImage(true);
    setMessage({ type: '', text: '' });

    try {
      const formData = new FormData();
      formData.append('profile_image', file);

      const response = await fetch(`${config.API_URL}/api/users/me/profile-image/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const text = await response.text();
        let errorMessage = 'Failed to upload image';
        try {
          const errorData = JSON.parse(text);
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          if (text.includes('<!DOCTYPE') || text.includes('<html')) {
            errorMessage = 'API endpoint not found. Check your backend connection.';
          }
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setCurrentUser({ ...user, profile_image_url: data.user.profile_image_url });
      setProfileImagePreview(data.user.profile_image_url);
      setMessage({ type: 'success', text: 'Profile image uploaded successfully!' });
      fileInput.value = '';
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    } finally {
      setUploadingImage(false);
    }
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
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-white mb-8">Profile Settings</h1>

          {/* Profile Picture Upload - Moved to Top */}
          <div className="bg-[var(--card-bg)] rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold text-white mb-6">Profile Picture</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-1 flex justify-center">
                <div className="w-48 h-48 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center overflow-hidden">
                  {profileImagePreview ? (
                    <img
                      src={profileImagePreview}
                      alt="Profile preview"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <span className="text-4xl font-bold text-white">
                      {user?.username?.charAt(0).toUpperCase()}
                    </span>
                  )}
                </div>
              </div>
              <div className="md:col-span-2">
                <div>
                  <label className="block text-white/80 text-sm font-medium mb-2">
                    Upload New Profile Picture
                  </label>
                  <input
                    type="file"
                    name="profile_image"
                    accept="image/*"
                    onChange={handleProfileImageChange}
                    className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-white/30 transition-colors"
                  />
                  <p className="text-white/60 text-xs mt-2">Supported formats: JPG, PNG, GIF. Max size: 5MB</p>
                </div>
                <button
                  onClick={handleProfileImageUpload}
                  disabled={uploadingImage || !profileImagePreview}
                  className="mt-4 w-full font-semibold button-lift disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                  data-block="button"
                >
                  <span className="button__flair"></span>
                  <span className="button__label">{uploadingImage ? 'Uploading...' : 'Upload Image'}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Personal Information */}
          <div className="bg-[var(--card-bg)] rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold text-white mb-6">Personal Information</h2>
            <form onSubmit={handleProfileUpdate}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-white/80 text-sm font-medium mb-2">
                    Username (Read-only)
                  </label>
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    disabled
                    className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white/60 focus:outline-none transition-colors opacity-60"
                  />
                </div>

                <div>
                  <label className="block text-white/80 text-sm font-medium mb-2">
                    Email (Read-only)
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    disabled
                    className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white/60 focus:outline-none transition-colors opacity-60"
                  />
                </div>

                <div>
                  <label className="block text-white/80 text-sm font-medium mb-2">
                    First Name
                  </label>
                  <input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-white/30 transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-white/80 text-sm font-medium mb-2">
                    Last Name
                  </label>
                  <input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-white/30 transition-colors"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-white/80 text-sm font-medium mb-2">
                    Bio
                  </label>
                  <textarea
                    name="bio"
                    value={formData.bio}
                    onChange={handleInputChange}
                    rows="3"
                    className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-white/30 transition-colors"
                    placeholder="Tell us about yourself"
                  />
                </div>

                <div>
                  <label className="block text-white/80 text-sm font-medium mb-2">
                    GitHub Username
                  </label>
                  <input
                    type="text"
                    name="github_username"
                    value={formData.github_username}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-white/30 transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-white/80 text-sm font-medium mb-2">
                    GitHub Email
                  </label>
                  <input
                    type="email"
                    name="github_email"
                    value={formData.github_email}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-white/30 transition-colors"
                  />
                </div>
              </div>
              {/* Social Links */}
              <div className="mt-8">
                <h3 className="text-lg font-semibold text-white mb-4">Social & Professional Links</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-white/80 text-sm font-medium mb-2">
                      LinkedIn URL
                    </label>
                    <input
                      type="url"
                      name="linkedin_url"
                      value={formData.linkedin_url}
                      onChange={handleInputChange}
                      placeholder="https://linkedin.com/in/username"
                      className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-white/30 transition-colors"
                    />
                  </div>

                  <div>
                    <label className="block text-white/80 text-sm font-medium mb-2">
                      Portfolio URL
                    </label>
                    <input
                      type="url"
                      name="portfolio_url"
                      value={formData.portfolio_url}
                      onChange={handleInputChange}
                      placeholder="https://yourportfolio.com"
                      className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-white/30 transition-colors"
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-white/80 text-sm font-medium mb-2">
                      Twitter Username
                    </label>
                    <input
                      type="text"
                      name="twitter_username"
                      value={formData.twitter_username}
                      onChange={handleInputChange}
                      placeholder="@username"
                      className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-white/30 transition-colors"
                    />
                  </div>
                </div>
              </div>

              {/* Education */}
              <div className="mt-8">
                <h3 className="text-lg font-semibold text-white mb-4">Education</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-white/80 text-sm font-medium mb-2">
                      University
                    </label>
                    <input
                      type="text"
                      name="university"
                      value={formData.university}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-white/30 transition-colors"
                    />
                  </div>

                  <div>
                    <label className="block text-white/80 text-sm font-medium mb-2">
                      Degree/Major
                    </label>
                    <input
                      type="text"
                      name="degree_major"
                      value={formData.degree_major}
                      onChange={handleInputChange}
                      placeholder="e.g., Bachelor of Science in Computer Science"
                      className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-white/30 transition-colors"
                    />
                  </div>

                  <div>
                    <label className="block text-white/80 text-sm font-medium mb-2">
                      Education City
                    </label>
                    <input
                      type="text"
                      name="education_city"
                      value={formData.education_city}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-white/30 transition-colors"
                    />
                  </div>

                  <div>
                    <label className="block text-white/80 text-sm font-medium mb-2">
                      Education State/Province
                    </label>
                    <input
                      type="text"
                      name="education_state"
                      value={formData.education_state}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-white/30 transition-colors"
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-white/80 text-sm font-medium mb-2">
                      Expected Graduation Date
                    </label>
                    <input
                      type="date"
                      name="expected_graduation"
                      value={formData.expected_graduation}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-white/30 transition-colors"
                    />
                  </div>
                </div>
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  type="submit"
                  disabled={saving}
                  className="font-semibold button-lift disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                  data-block="button"
                >
                  <span className="button__flair"></span>
                  <span className="button__label">{saving ? 'Saving...' : 'Save Changes'}</span>
                </button>
              </div>
            </form>
          </div>

          {/* Change Password */}
          <div className="bg-[var(--card-bg)] rounded-lg p-6 mt-6">
            <h2 className="text-xl font-semibold text-white mb-6">Change Password</h2>
            <form onSubmit={handlePasswordUpdate}>
              <div className="space-y-6">
                <div>
                  <label className="block text-white/80 text-sm font-medium mb-2">
                    Current Password
                  </label>
                  <input
                    type="password"
                    name="current_password"
                    value={passwordData.current_password}
                    onChange={handlePasswordChange}
                    className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-white/30 transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-white/80 text-sm font-medium mb-2">
                    New Password
                  </label>
                  <input
                    type="password"
                    name="new_password"
                    value={passwordData.new_password}
                    onChange={handlePasswordChange}
                    className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-white/30 transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-white/80 text-sm font-medium mb-2">
                    Confirm New Password
                  </label>
                  <input
                    type="password"
                    name="confirm_password"
                    value={passwordData.confirm_password}
                    onChange={handlePasswordChange}
                    className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-white/30 transition-colors"
                  />
                </div>
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  type="submit"
                  disabled={saving}
                  className="font-semibold button-lift disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                  data-block="button"
                >
                  <span className="button__flair"></span>
                  <span className="button__label">{saving ? 'Updating...' : 'Update Password'}</span>
                </button>
              </div>
            </form>
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
