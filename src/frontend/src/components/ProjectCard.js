'use client';

import { useState } from 'react';

export default function ProjectCard({ project, index }) {
  const [expanded, setExpanded] = useState(false);

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
          <div className="text-left">
            <h3 className="font-semibold text-gray-800">
              {project.root || 'Project'}
            </h3>
            <p className="text-sm text-gray-500">
              {contributors.length} contributor{contributors.length !== 1 ? 's' : ''} • {files.code?.length || 0} code files
            </p>
          </div>
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
        </div>
      )}
    </div>
  );
}
