'use client';

import { useState } from 'react';

export default function ProjectCard({ project, index, evaluation }) {
  const [expanded, setExpanded] = useState(false);

  const getGrade = (score) => {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  };

  const getGradeStyle = (grade) => {
    if (grade === 'A') return 'text-green-700 bg-green-100';
    if (grade === 'B') return 'text-blue-700 bg-blue-100';
    if (grade === 'C') return 'text-yellow-700 bg-yellow-100';
    if (grade === 'D') return 'text-orange-700 bg-orange-100';
    return 'text-red-700 bg-red-100';
  };

  const getBarColor = (score) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 80) return 'bg-blue-500';
    if (score >= 70) return 'bg-yellow-500';
    if (score >= 60) return 'bg-orange-500';
    return 'bg-red-500';
  };

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
          <span className="text-2xl font-bold text-gray-400">#{index + 1}</span>
          <div className="text-left flex-1">
            <h3 className="font-semibold text-gray-800">
              {project.root || 'Project'}
            </h3>
            <p className="text-sm" style={{ color: '#a1a1aa' }}>
              {contributors.length} contributor{contributors.length !== 1 ? 's' : ''} • {files.code?.length || 0} code files
              {project.first_commit_date && (
                <>
                  {' '}•{' '}
                  <span className="text-zinc-400">
                    {new Date(project.first_commit_date * 1000).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                    {project.last_commit_date && project.last_commit_date !== project.first_commit_date ? ` — ${new Date(project.last_commit_date * 1000).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}` : ''}
                    {project.duration_days !== undefined && project.duration_days !== null && ` (${project.duration_days < 30 ? project.duration_days + 'd' : project.duration_days < 365 ? Math.floor(project.duration_days / 30) + 'mo' : (project.duration_days / 365).toFixed(1) + 'y'})`}
                  </span>
                </>
              )}
            </p>
          </div>
          {evaluation && (
            <span className={`px-2 py-1 rounded text-sm font-bold ${getGradeStyle(getGrade(evaluation.overall_score))}`}>
              {getGrade(evaluation.overall_score)} · {evaluation.overall_score.toFixed(0)}%
            </span>
          )}
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

          {/* Quality Evaluation */}
          {evaluation && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-3">Quality Evaluation</h4>
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <span className={`inline-block px-3 py-1 rounded-full text-lg font-bold ${getGradeStyle(getGrade(evaluation.overall_score))}`}>
                      Grade: {getGrade(evaluation.overall_score)}
                    </span>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-gray-800">{evaluation.overall_score.toFixed(1)}%</p>
                    <p className="text-xs text-gray-500">{evaluation.language}</p>
                  </div>
                </div>

                {/* Category Breakdown */}
                {evaluation.category_scores && (
                  <div className="space-y-2">
                    {Object.entries(evaluation.category_scores).map(([category, score]) => (
                      <div key={category}>
                        <div className="flex justify-between items-center mb-0.5">
                          <span className="text-xs text-gray-600 capitalize">{category.replace(/_/g, ' ')}</span>
                          <span className="text-xs font-semibold text-gray-700">{score.toFixed(0)}%</span>
                        </div>
                        <div className="w-full bg-gray-100 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full transition-all ${getBarColor(score)}`}
                            style={{ width: `${Math.min(score, 100)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Strengths & Improvements */}
                {evaluation.category_scores && (
                  <div className="grid grid-cols-2 gap-3 mt-3 pt-3 border-t border-gray-100">
                    <div>
                      <p className="text-xs font-semibold text-green-700 mb-1">Strengths</p>
                      {Object.entries(evaluation.category_scores)
                        .sort(([,a], [,b]) => b - a)
                        .slice(0, 2)
                        .map(([cat]) => (
                          <p key={cat} className="text-xs text-gray-600 capitalize">✓ {cat.replace(/_/g, ' ')}</p>
                        ))}
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-orange-700 mb-1">Improve</p>
                      {Object.entries(evaluation.category_scores)
                        .filter(([, s]) => s < 70)
                        .sort(([,a], [,b]) => a - b)
                        .slice(0, 2)
                        .map(([cat]) => (
                          <p key={cat} className="text-xs text-gray-600 capitalize">↑ {cat.replace(/_/g, ' ')}</p>
                        ))}
                      {Object.entries(evaluation.category_scores).filter(([, s]) => s < 70).length === 0 && (
                        <p className="text-xs text-gray-400">All good!</p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
