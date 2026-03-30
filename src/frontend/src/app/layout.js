import { Montserrat } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";

const montserrat = Montserrat({
  variable: "--font-montserrat",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
});

export const metadata = {
  title: {
    default: 'Portfolio Analyzer — Showcase Your Best Work',
    template: '%s | Portfolio Analyzer',
  },
  description: 'Upload your coding projects, automatically extract skills and frameworks, and generate professional portfolios and resumes.',
  keywords: ['portfolio', 'resume builder', 'project analysis', 'developer tools', 'AI insights', 'code analysis', 'skills extraction'],
  authors: [{ name: 'Portfolio Analyzer' }],
  openGraph: {
    type: 'website',
    siteName: 'Portfolio Analyzer',
    title: 'Portfolio Analyzer',
    description: 'Analyze your coding projects, extract skills and frameworks, generate professional portfolios and resumes with AI-powered insights.',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Portfolio Analyzer',
    description: 'Analyze your coding projects, extract skills and frameworks, generate professional portfolios and resumes with AI-powered insights.',
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${montserrat.variable} antialiased`}
      >
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
