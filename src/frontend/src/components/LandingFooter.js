import Link from 'next/link';

export default function LandingFooter() {
  return (
    <footer style={{ background: '#060812', borderTop: '1px solid rgba(255, 255, 255, 0.06)' }}>
      <div className="max-w-6xl mx-auto px-6 py-12">
        <div className="flex flex-col md:flex-row justify-between items-start gap-8">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-white font-bold text-lg">Team 8</span>
            </div>
            <p className="text-sm max-w-xs" style={{ color: '#64748b' }}>
              A capstone project by Team 8 for COSC499. Building a portfolio builder to help young professionals showcase their work.
            </p>
          </div>

          {/* Links */}
          <div className="flex gap-16">
            <div>
              <h4 className="text-sm font-semibold text-white mb-3">Product</h4>
              <div className="flex flex-col gap-2">
                <Link href="#features" className="text-sm no-underline transition-colors" style={{ color: '#64748b' }}>Features</Link>
                <Link href="#how-it-works" className="text-sm no-underline transition-colors" style={{ color: '#64748b' }}>How It Works</Link>
              </div>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-white mb-3">Account</h4>
              <div className="flex flex-col gap-2">
                <Link href="/login" className="text-sm no-underline transition-colors" style={{ color: '#64748b' }}>Login</Link>
                <Link href="/signup" className="text-sm no-underline transition-colors" style={{ color: '#64748b' }}>Sign Up</Link>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-12 pt-6" style={{ borderTop: '1px solid rgba(255, 255, 255, 0.06)' }}>
          <p className="text-xs text-center" style={{ color: '#475569' }}>
            © {new Date().getFullYear()} Team 8 Capstone Project. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
