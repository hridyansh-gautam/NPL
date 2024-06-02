%%
%% This is file `LMIReport.cls',
%% 
%% ============================================================================
%%  LaTeX class for Lunar Metrology Institute Calibration Reports
%% 
%% ============================================================================
%% This files is the property of the Lunar Metrology Institute of The Moon (LMI).
%% 
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{LMIReport}[2024/05/17  v1.0.0 LMIReport class]

\LoadClass[11pt,a4paper]{article}

% Paper size and margins 
\RequirePackage[    
    a4paper,
    headheight=2\baselineskip,
    hmargin=25mm,
    vmargin=30mm]{geometry}

\RequirePackage[T1]{fontenc}
\RequirePackage[scaled]{helvet}
\RequirePackage{stix}           % Need this or font looks funny

\RequirePackage[UKenglish]{babel}
\RequirePackage[UKenglish,cleanlook]{isodate}   % Date format: day month year
  
\RequirePackage{upgreek}
\RequirePackage{amsmath}
\RequirePackage{siunitx}

%% Make captions without using LaFeX floating figure or table environments 
\RequirePackage{capt-of}
\newcommand{\LMICaption}[3]{
    \begin{minipage}{.8\textwidth}        
        \captionof{#1}{\small #3}
        \label{#2}     
    \end{minipage}
    \vspace{.5\baselineskip}
}

%% This package finds the number of pages in a document.
%% The complier must be run twice to find the LastPage number.
\RequirePackage{lastpage}       % To allow page 'n' of 'm'
\newcommand{\thispageof}{Page~\thepage~of~\pageref*{LastPage}}

%% For including images
\RequirePackage{graphicx}

\RequirePackage{parskip}        % Paragraph formatting
\RequirePackage{setspace}       % Control of line spacing 
% \singlespacing
% \onehalfspacing
% \doublespacing

\RequirePackage{multirow}   % Allows table column entries that span rows
\RequirePackage{array}      % Extends the tabular environment, provides \extrarowheight
\RequirePackage{dcolumn}    % Allows alignment on decimal points

\RequirePackage{hyperref}
\hypersetup{
    colorlinks=true,        % links are coloured
    urlcolor=blue,          % URLs, etc
    linkcolor=black,        % Pages, etc
    citecolor=blue
}
%% Set up a header and footer
\RequirePackage{fancyhdr}
\fancypagestyle{fancy}{%
    \fancyhf{}
    \renewcommand{\headrulewidth}{0pt}  % Suppress a line ruled by fancyhdr
    \fancyhead[L]{\small\textnormal{\ReportReference}}
    \fancyhead[C]{\small\textbf{\LMI}\\}
    \fancyhead[R]{\small\textnormal{\thispageof}}
    \fancyfoot[C]{\small\textit{\RestrictionsLMI}}
}

%% Defined strings
\newcommand{\LMI}{Lunar Metrology Institute}

\newcommand{\RestrictionsLMI}{%
This report may not be reproduced, 
except in full, without the written consent of the\\
Chief Metrologist, Lunar Metrology Institute}

\newcommand{\referenceGUM}{%
For information about uncertainty terminology, see: 
BIPM, IEC, IFCC, ISO, IUPAC, IUPAP and OIML, 
\textit{``Evaluation of measurement data---Guide to the expression of uncertainty in measurement''}, 
BIPM Joint Committee for Guides in Metrology, Paris, S\`evres, edition 1, JCGM~100:2008, 2008. 
A PDF version is available on-line:

    \begin{center}
	    \href{%
		https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf
	    }{%
		https://www.bipm.org/documents/20126/2071204/JCGM\_100\_2008\_E.pdf
	    }
    \end{center}
}

%% Define information for the report
\RequirePackage{xspace}         % Helps to manage space in LaTeX macros
\newcommand{\ReportNumber}[1]{\renewcommand{\ReportNumber}{#1}}
\newcommand{\ReportTitle}[1]{\renewcommand{\ReportTitle}{#1}}
\newcommand{\ReportReference}{Report No.\xspace \ReportNumber, \@date\xspace}
\newcommand{\Metrologist}[1]{\renewcommand{\Metrologist}{#1}}
\newcommand{\ChiefMetrologist}[1]{\renewcommand{\ChiefMetrologist}{#1}}

%% This command composes displays who has been involved in the report. 
\newcommand{\MetrologyTeam}{
    \begin{minipage}{\textwidth}
    \begin{tabbing}
        \textbf{Prepared by:}\hspace{5mm} \= \Metrologist \\
        \textbf{Authorised by:} \> \ChiefMetrologist
    \end{tabbing}   
    \end{minipage}
}

%% Packages to load the PDF artwork for the title page
\RequirePackage{pdfpages}
\RequirePackage{eso-pic}

%% A command to produce the title page
\newcommand{\maketitlepage}{%

    % Supress header and footer 
    \thispagestyle{empty}    

    % Page 1 of N is written at the top left
    \thispageof
    
    % A vertical space is inserted before writing
    % the report title in a large font size 
    \vspace*{50mm}
    \textbf{\huge \ReportTitle}\\

    \vspace{\baselineskip}
    \textbf{\LARGE \ReportReference}
    
    \vspace{\baselineskip}
    \MetrologyTeam    

    \vfill
    
    % Load the background image
    \AddToShipoutPictureBG*{%
        \includegraphics[scale=1]{LMI_cover.pdf}
    }
    % These commands must come after everything else.
    % They insert the background image and signal that 
    % the page is completed. 
    \ClearShipoutPicture
    \clearpage
}

% Fonts!!
% Arial is not in the public domain but Helvetica is very similar.
% So, we use Helvetica (phv).
% The default normal text should be 11-pt. In that case, LaTeX (ref, WikiBooks)
%   \HUGE ~= 23 pt
%   \huge ~= 19 pt
%   \LARGE ~= 16 pt
%   \Large ~= 14 pt
%   \large ~= 12 pt
%   \normal ~= 11 pt
%   \small ~= 10 pt
%   \footnotesize ~= 9 pt
%   \scriptsiize ~= 8.5 pt
%   \tiny ~= 7 pt
%
% The third parameter is the fontseries: `bc` stands for bold condensed
\newcommand{\lmiboldarialnarrow}{\usefont{T1}{phv}{bc}{n}}
\newcommand{\lmiarial}{\usefont{T1}{phv}{m}{n}}
\newcommand{\lmiboldarialsnarrowlanted}{\usefont{T1}{phv}{bc}{sl}}

%% Define the layout of section headings
%% We we would like special fonts and no section numbers 
\RequirePackage{titlesec}
%% Command formats:
%% \titleformat{<command>}[<shape>]{<format>}
%%      {<label>}{<sep>}{<before-code>}[<after-code>]
%% \titlespacing{<command>}
%%      {<left>}{<before-sep>}{<after-sep>}

\titleformat{\section}
  {\lmiboldarialnarrow\Large}{}{0pt}{}
\titlespacing*{\section}
  {0pt}{\baselineskip}{0.5\baselineskip} 

\titleformat{\subsection}
    {\lmiboldarialnarrow\large}{}{0.5em}{}
\titlespacing*{\subsection}
    {0pt}{\baselineskip}{0pt}

\titleformat{\subsubsection}
    {\lmiboldarialsnarrowlanted\normalsize}{}{0.5em}{}
\titlespacing*{\subsubsection}
    {0pt}{\baselineskip}{0pt}

%% For embedded files
\RequirePackage{embedfile}
\embedfilesetup{     
      filesystem=URL,
      afrelationship={/Data},
      stringmethod=escape
}

%%-------------------------------------------------------------------
\RequirePackage{etoolbox}           % Provides \AtEndPreamble
\AtEndPreamble{
    % Executes after the document preamble has been processed,
    % so definitions made in the document can be accessed here.
    \hypersetup{
        pdftitle={\ReportTitle},
        pdfauthor={\LMI},
        pdfnumpages={\pageref*{LastPage}},
        pdfpagemode={UseAttachments}    % Prompts PDF reader
    }
}
%%-------------------------------------------------------------------
\AtBeginDocument{
    \maketitlepage
    
    % Page style defined for the report
    \pagestyle{fancy}
    \raggedright        % Does not adjust the right margin
    
    \vspace*{4\baselineskip}
    \textbf{\LARGE\ReportTitle}    
}
\endinput
%%
%% End of file `LMIReport.cls'.