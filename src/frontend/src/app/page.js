import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-8">
      <div className="max-w-2xl w-full">
        <div className="bg-white rounded-lg shadow-lg p-12 text-center">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">Portfolio Analyzer</h1>
          <p className="text-xl text-gray-600 mb-8">
            Analyze your projects and generate insights from your codebase
          </p>

          <div className="space-y-4">
            <Link
              href="/upload"
              className="inline-block w-full px-8 py-4 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors"
            >
              📤 Upload Portfolio
            </Link>

            <p className="text-gray-500 text-sm">
              Supported: ZIP files containing git repositories and project files
            </p>
          </div>

          <div className="mt-12 pt-8 border-t border-gray-200">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Features</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="font-semibold text-blue-900">📊 Analysis</p>
                <p className="text-sm text-blue-700 mt-1">Detect projects and frameworks automatically</p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <p className="font-semibold text-green-900">👥 Contributors</p>
                <p className="text-sm text-green-700 mt-1">Extract git history and contribution metrics</p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <p className="font-semibold text-purple-900">🎨 Customization</p>
                <p className="text-sm text-purple-700 mt-1">Add thumbnails and personalize your portfolio</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
