'use client';

import { useState } from 'react';

export default function ProjectCard({ project, index }) {
  const [expanded, setExpanded] = useState(false);

  const getTypeColor = (type) => {
    const colors = {
      coding: 'bg-blue-500/15 text-blue-300',
      documentation: 'bg-green-500/15 text-green-300',
      data_analysis: 'bg-purple-500/15 text-purple-300',
      design: 'bg-pink-500/15 text-pink-300',
      research: 'bg-orange-500/15 text-orange-300',
      other: 'bg-white/10 text-white/70',
    };
    return colors[type] || colors.other;
  };

  const getActivityColor = (type) => {
    const colors = {
      code: 'bg-blue-500/10 border-blue-500/20',
      test: 'bg-green-500/10 border-green-500/20',
      documentation: 'bg-yellow-500/10 border-yellow-500/20',
      design: 'bg-purple-500/10 border-purple-500/20',
      configuration: 'bg-white/5 border-white/10',
    };
    return colors[type] || colors.code;
  };

  const classification = project.classification || {};
  const contributors = project.contributors || [];
  const files = project.files || {};

  return (
    <div className="rounded-lg overflow-hidden transition-all" style={{ background: '#18181b', border: '1px solid #27272a' }}>
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-white/5 transition-colors"
        style={{ background: '#18181b' }}
      >
        <div className="flex items-center gap-4 flex-1">
          <span className="text-2xl font-bold text-white/30">#{index + 1}</span>
          <div className="text-left">
            <h3 className="font-semibold text-white">
              {project.root || 'Project'}
            </h3>
            <p className="text-sm" style={{ color: '#a1a1aa' }}>
              {contributors.length} contributor{contributors.length !== 1 ? 's' : ''} • {files.code?.length || 0} code files
            </p>
          </div>
        </div>
        <span className={`transform transition-transform text-white/40 ${expanded ? 'rotate-180' : ''}`}>
          ▼
        </span>
      </button>

      {/* Expanded Content */}
      {expanded && (
        <div className="p-6 space-y-6" style={{ borderTop: '1px solid #27272a' }}>
          {/* Classification */}
          <div>
            <h4 className="font-semibold text-white mb-3">Classification</h4>
            <div className="flex flex-wrap gap-2">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getTypeColor(classification.type)}`}>
                {classification.type}
              </span>
              <span className="px-3 py-1 rounded-full text-sm font-medium bg-white/10 text-white/70">
                Confidence: {(classification.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>

          {/* Frameworks */}
          {classification.frameworks && classification.frameworks.length > 0 && (
            <div>
              <h4 className="font-semibold text-white mb-2">Frameworks</h4>
              <div className="flex flex-wrap gap-2">
                {classification.frameworks.map((fw, i) => (
                  <span key={i} className="px-3 py-1 rounded-full text-sm" style={{ background: 'rgba(79, 124, 247, 0.15)', color: '#7ba4f7' }}>
                    {fw}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Contributors */}
          <div>
            <h4 className="font-semibold text-white mb-3">Contributors</h4>
            <div className="space-y-3">
              {contributors.map((contributor, i) => (
                <div key={i} className="rounded p-3" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid #27272a' }}>
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-semibold text-white">{contributor.name}</p>
                      <p className="text-xs" style={{ color: '#71717a' }}>{contributor.email}</p>
                    </div>
                    <span className="text-sm font-semibold" style={{ color: '#7ba4f7' }}>
                      {contributor.percent_commits}% of commits
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-sm mb-3">
                    <div>
                      <p style={{ color: '#a1a1aa' }}>Commits: <span className="font-semibold text-white">{contributor.commits}</span></p>
                      <p style={{ color: '#a1a1aa' }}>+{contributor.lines_added} -{contributor.lines_deleted}</p>
                    </div>
                    <div>
                      {contributor.contribution_duration_months && (
                        <>
                          <p style={{ color: '#a1a1aa' }}>Duration: <span className="font-semibold text-white">{contributor.contribution_duration_months} months</span></p>
                          <p style={{ color: '#a1a1aa' }}>({contributor.contribution_duration_days} days)</p>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Activity Types */}
                  {contributor.activity_types && Object.keys(contributor.activity_types).length > 0 ? (
                    <div className="mb-2">
                      <p className="text-xs mb-2" style={{ color: '#a1a1aa' }}>Activity Types:</p>
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(contributor.activity_types).map(([type, stats]) => (
                          <span
                            key={type}
                            className={`px-2 py-1 text-xs rounded ${getActivityColor(type)} border`}
                            title={`${stats.count} commits, +${stats.lines_added} -${stats.lines_deleted}`}
                          >
                            {type} ({stats.count})
                          </span>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="mb-2">
                      <p className="text-xs" style={{ color: '#71717a' }}>Activity types not available</p>
                    </div>
                  )}

                  {/* Primary Languages */}
                  {contributor.primary_languages && contributor.primary_languages.length > 0 && (
                    <div>
                      <p className="text-xs mb-2" style={{ color: '#a1a1aa' }}>Languages: {contributor.primary_languages.join(', ')}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* File Statistics */}
          <div>
            <h4 className="font-semibold text-white mb-3">Files</h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p style={{ color: '#a1a1aa' }}>Code Files</p>
                <p className="font-semibold text-lg" style={{ color: '#7ba4f7' }}>{files.code?.length || 0}</p>
              </div>
              <div>
                <p style={{ color: '#a1a1aa' }}>Content Files</p>
                <p className="font-semibold text-lg" style={{ color: '#4ade80' }}>{files.content?.length || 0}</p>
              </div>
              <div>
                <p style={{ color: '#a1a1aa' }}>Images</p>
                <p className="font-semibold text-lg" style={{ color: '#f472b6' }}>{files.image?.length || 0}</p>
              </div>
              <div>
                <p style={{ color: '#a1a1aa' }}>Other</p>
                <p className="font-semibold text-lg text-white/60">{files.other?.length || 0}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
