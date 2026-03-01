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
      coding: 'bg-blue-100 text-blue-800',
      documentation: 'bg-green-100 text-green-800',
      data_analysis: 'bg-purple-100 text-purple-800',
      design: 'bg-pink-100 text-pink-800',
      research: 'bg-orange-100 text-orange-800',
      other: 'bg-gray-100 text-gray-800',
    };
    return colors[type] || colors.other;
  };

  const getActivityColor = (type) => {
    const colors = {
      code: 'bg-blue-50 border-blue-200',
      test: 'bg-green-50 border-green-200',
      documentation: 'bg-yellow-50 border-yellow-200',
      design: 'bg-purple-50 border-purple-200',
      configuration: 'bg-gray-50 border-gray-200',
    };
    return colors[type] || colors.code;
  };

  const classification = project.classification || {};
  const contributors = project.contributors || [];
  const files = project.files || {};

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full bg-gray-50 hover:bg-gray-100 p-4 flex items-center justify-between"
      >
        <div className="flex items-center gap-4 flex-1">
          <span className="text-2xl font-bold text-gray-400">#{index + 1}</span>
          <div className="text-left flex-1">
            <h3 className="font-semibold text-gray-800">
              {project.root || 'Project'}
            </h3>
            <p className="text-sm text-gray-500">
              {contributors.length} contributor{contributors.length !== 1 ? 's' : ''} • {files.code?.length || 0} code files
            </p>
          </div>
          {evaluation && (
            <span className={`px-2 py-1 rounded text-sm font-bold ${getGradeStyle(getGrade(evaluation.overall_score))}`}>
              {getGrade(evaluation.overall_score)} · {evaluation.overall_score.toFixed(0)}%
            </span>
          )}
        </div>
        <span className={`transform transition-transform ${expanded ? 'rotate-180' : ''}`}>
          ▼
        </span>
      </button>

      {/* Expanded Content */}
      {expanded && (
        <div className="p-6 bg-white border-t border-gray-200 space-y-6">
          {/* Classification */}
          <div>
            <h4 className="font-semibold text-gray-700 mb-3">Classification</h4>
            <div className="flex flex-wrap gap-2">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getTypeColor(classification.type)}`}>
                {classification.type}
              </span>
              <span className="px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                Confidence: {(classification.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>

          {/* Frameworks */}
          {classification.frameworks && classification.frameworks.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Frameworks</h4>
              <div className="flex flex-wrap gap-2">
                {classification.frameworks.map((fw, i) => (
                  <span key={i} className="px-3 py-1 rounded-full text-sm bg-indigo-50 text-indigo-700">
                    {fw}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Contributors */}
          <div>
            <h4 className="font-semibold text-gray-700 mb-3">Contributors</h4>
            <div className="space-y-3">
              {contributors.map((contributor, i) => (
                <div key={i} className="border border-gray-200 rounded p-3">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-semibold text-gray-800">{contributor.name}</p>
                      <p className="text-xs text-gray-500">{contributor.email}</p>
                    </div>
                    <span className="text-sm font-semibold text-indigo-600">
                      {contributor.percent_commits}% of commits
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-sm mb-3">
                    <div>
                      <p className="text-gray-600">Commits: <span className="font-semibold">{contributor.commits}</span></p>
                      <p className="text-gray-600">+{contributor.lines_added} -{contributor.lines_deleted}</p>
                    </div>
                    <div>
                      {contributor.contribution_duration_months && (
                        <>
                          <p className="text-gray-600">Duration: <span className="font-semibold">{contributor.contribution_duration_months} months</span></p>
                          <p className="text-gray-600">({contributor.contribution_duration_days} days)</p>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Activity Types */}
                  {contributor.activity_types && Object.keys(contributor.activity_types).length > 0 ? (
                    <div className="mb-2">
                      <p className="text-xs text-gray-600 mb-2">Activity Types:</p>
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
                      <p className="text-xs text-gray-500">Activity types not available</p>
                    </div>
                  )}

                  {/* Primary Languages */}
                  {contributor.primary_languages && contributor.primary_languages.length > 0 && (
                    <div>
                      <p className="text-xs text-gray-600 mb-2">Languages: {contributor.primary_languages.join(', ')}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* File Statistics */}
          <div>
            <h4 className="font-semibold text-gray-700 mb-3">Files</h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Code Files</p>
                <p className="font-semibold text-lg text-indigo-600">{files.code?.length || 0}</p>
              </div>
              <div>
                <p className="text-gray-600">Content Files</p>
                <p className="font-semibold text-lg text-green-600">{files.content?.length || 0}</p>
              </div>
              <div>
                <p className="text-gray-600">Images</p>
                <p className="font-semibold text-lg text-pink-600">{files.image?.length || 0}</p>
              </div>
              <div>
                <p className="text-gray-600">Other</p>
                <p className="font-semibold text-lg text-gray-600">{files.other?.length || 0}</p>
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
