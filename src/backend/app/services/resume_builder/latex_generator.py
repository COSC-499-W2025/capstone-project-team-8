"""
LaTeX Resume Generator using Jake's Resume Template.
Generates a professional resume in LaTeX format from user and project data.
"""
from typing import List, Dict, Any, TYPE_CHECKING
from django.contrib.auth import get_user_model
from app.models import Project, ProgrammingLanguage, Framework

if TYPE_CHECKING:
    from app.models import User as UserType
else:
    UserType = get_user_model()

User = get_user_model()


class JakesResumeGenerator:
    """
    Generates a LaTeX resume using Jake's Resume template.
    https://github.com/jakegut/resume (Modified BSD 3-Clause License)
    """
    
    def __init__(self, user):
        self.user = user
        
    def generate(self) -> str:
        """Generate the complete LaTeX resume."""
        return self._build_document()
    
    def _build_document(self) -> str:
        """Build the complete LaTeX document."""
        sections = [
            self._build_preamble(),
            self._build_header(),
            self._build_education(),
            self._build_experience(),
            self._build_projects(),
            self._build_skills(),
            self._build_footer()
        ]
        return "\n".join(sections)
    
    def _build_preamble(self) -> str:
        """Build the LaTeX preamble with Jake's Resume template styling."""
        return r"""%-------------------------
% Resume in Latex
% Based on Jake's Resume Template
%------------------------

\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\input{glyphtounicode}

%----------FONT OPTIONS----------
\usepackage[sfdefault]{FiraSans}
\usepackage[sfdefault]{roboto}
\usepackage[sfdefault]{noto-sans}
\usepackage[default]{sourcesanspro}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

% Ensure that generate pdf is machine readable/ATS parsable
\pdfgentounicode=1

%-------------------------
% Custom commands
\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubSubheading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \textit{\small#1} & \textit{\small #2} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

%-------------------------------------------
%%%%%%  RESUME STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%

\begin{document}"""
    
    def _build_header(self) -> str:
        """Build the resume header with contact information."""
        full_name = self.user.get_full_name() or self.user.username
        email = self.user.email
        
        # Build contact links
        contact_parts = []
        
        if self.user.github_username:
            github_url = f"https://github.com/{self.user.github_username}"
            contact_parts.append(f"\\href{{{github_url}}}{{github.com/{self.user.github_username}}}")
        
        if self.user.linkedin_url:
            contact_parts.append(f"\\href{{{self.user.linkedin_url}}}{{LinkedIn}}")
        
        if self.user.portfolio_url:
            contact_parts.append(f"\\href{{{self.user.portfolio_url}}}{{Portfolio}}")
        
        contact_line = " $|$ ".join(contact_parts) if contact_parts else ""
        
        header = f"""
%----------HEADING----------
\\begin{{center}}
    \\textbf{{\\Huge \\scshape {self._escape_latex(full_name)}}} \\\\ \\vspace{{1pt}}
    \\small \\href{{mailto:{email}}}{{{email}}}"""
        
        if contact_line:
            header += f" $|$ \n    {contact_line}"
        
        header += "\n\\end{center}\n"
        
        return header
    
    def _build_education(self) -> str:
        """Build the education section from user data."""
        # Use user's education data if available, otherwise use placeholder
        university = self._escape_latex(self.user.university) if self.user.university else "Your University"
        location = ""
        if self.user.education_city and self.user.education_state:
            location = f"{self._escape_latex(self.user.education_city)}, {self._escape_latex(self.user.education_state)}"
        elif self.user.education_city:
            location = self._escape_latex(self.user.education_city)
        elif self.user.education_state:
            location = self._escape_latex(self.user.education_state)
        else:
            location = "City, State"
        
        degree = self._escape_latex(self.user.degree_major) if self.user.degree_major else "Bachelor of Science in Computer Science"
        
        grad_date = ""
        if self.user.expected_graduation:
            grad_date = f"Expected Graduation: {self.user.expected_graduation.strftime('%B %Y')}"
        else:
            grad_date = "Expected Graduation: Month Year"
        
        return f"""
%-----------EDUCATION-----------
\\section{{Education}}
  \\resumeSubHeadingListStart
    \\resumeSubheading
      {{{university}}}{{{location}}}
      {{{degree}}}{{{grad_date}}}
  \\resumeSubHeadingListEnd
"""
    
    def _build_experience(self) -> str:
        """Build the experience section (placeholder for now)."""
        return r"""
%-----------EXPERIENCE-----------
\section{Experience}
  \resumeSubHeadingListStart
    % Add your work experience here
    % \resumeSubheading
    %   {Company Name}{City, State}
    %   {Position Title}{Start Date -- End Date}
    %   \resumeItemListStart
    %     \resumeItem{Achievement or responsibility}
    %   \resumeItemListEnd
  \resumeSubHeadingListEnd
"""
    
    def _build_projects(self) -> str:
        """Build the projects section from database projects."""
        # Get user's projects
        projects = Project.objects.filter(
            user=self.user
        ).prefetch_related(
            'languages', 
            'frameworks'
        ).order_by('-created_at')[:5]  # Top 5 most recent
        
        if not projects:
            return ""
        
        latex = "\n%-----------PROJECTS-----------\n"
        latex += "\\section{Projects}\n"
        latex += "    \\resumeSubHeadingListStart\n"
        
        for project in projects:
            # Get technologies used
            techs = []
            
            # Add languages
            languages = project.languages.all()[:3]  # Top 3 languages
            techs.extend([lang.name for lang in languages])
            
            # Add frameworks
            frameworks = project.frameworks.all()[:3]  # Top 3 frameworks
            techs.extend([fw.name for fw in frameworks])
            
            tech_string = ", ".join(techs) if techs else "Various Technologies"
            
            # Project name with GitHub link if available
            project_name = self._escape_latex(project.name)
            if self.user.github_username:
                # Assuming project name might be repo name
                github_link = f"https://github.com/{self.user.github_username}/{project.name.replace(' ', '-').lower()}"
                project_title = f"\\textbf{{{project_name}}} $|$ \\emph{{\\small {self._escape_latex(tech_string)}}}"
            else:
                project_title = f"\\textbf{{{project_name}}} $|$ \\emph{{\\small {self._escape_latex(tech_string)}}}"
            
            # Date
            date_str = ""
            if project.created_at:
                date_str = project.created_at.strftime("%B %Y")
            
            latex += f"      \\resumeProjectHeading\n"
            latex += f"          {{{project_title}}}{{{date_str}}}\n"
            latex += "          \\resumeItemListStart\n"
            
            # Add project description if available
            if project.description:
                desc = self._escape_latex(project.description)[:200]  # Limit length
                latex += f"            \\resumeItem{{{desc}}}\n"
            
            # Add resume bullet points
            bullet_points = project.resume_bullet_points or []
            for bullet in bullet_points[:3]:  # Max 3 bullets per project
                clean_bullet = self._escape_latex(str(bullet))
                latex += f"            \\resumeItem{{{clean_bullet}}}\n"
            
            # If no bullets, add a default one
            if not project.description and not bullet_points:
                latex += f"            \\resumeItem{{Developed a {project.classification_type} project with {project.code_files_count} code files}}\n"
            
            latex += "          \\resumeItemListEnd\n"
        
        latex += "    \\resumeSubHeadingListEnd\n"
        
        return latex
    
    def _build_skills(self) -> str:
        """Build the skills section from user's projects."""
        # Aggregate skills from all projects
        languages = ProgrammingLanguage.objects.filter(
            projects__user=self.user
        ).distinct().order_by('name')
        
        frameworks = Framework.objects.filter(
            projects__user=self.user
        ).distinct().order_by('name')
        
        if not languages and not frameworks:
            return ""
        
        latex = "\n%-----------TECHNICAL SKILLS-----------\n"
        latex += "\\section{Technical Skills}\n"
        latex += " \\begin{itemize}[leftmargin=0.15in, label={}]\n"
        latex += "    \\small{\\item{\n"
        
        # Languages
        if languages:
            lang_list = ", ".join([self._escape_latex(lang.name) for lang in languages])
            latex += f"     \\textbf{{Languages}}{{: {lang_list}}} \\\\\n"
        
        # Frameworks & Libraries
        if frameworks:
            fw_list = ", ".join([self._escape_latex(fw.name) for fw in frameworks])
            latex += f"     \\textbf{{Frameworks \\& Libraries}}{{: {fw_list}}} \\\\\n"
        
        return latex
    
    def _build_footer(self) -> str:
        """Build the document footer."""
        return "\n%-------------------------------------------\n\\end{document}\n"
    
    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters."""
        if not text:
            return ""
        
        # LaTeX special characters that need escaping
        replacements = {
            '\\': r'\textbackslash{}',
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text
