# PARALLEL_MINDS

PROJECT NAME:READAPT

PROBLEEM STATEMENT ID: PS02EDU

TEAM NAME:PARALLEL_MINDS

COLLEGE NAME:MAHATMA GANDHI MEMORIAL COOLEGE,UDUPI

Problem Statement:
Standard educational materials and digital platforms are rarely designed with cognitive accessibility in mind. For learners with dyslexia and other reading differences, dense text, poor font choices, and lack of visual spacing create severe cognitive overload. This creates an invisible barrier, preventing equitable access to educational resources and hindering independent learning. The challenge is to build a digital library that removes these barriers through customizable, accessible reading features.

Proposed Solution:
ReadApt: The AI-Powered Accessible Library
ReadApt is a comprehensive, web-based digital library specifically engineered for neurodivergent readers. It solves the problem by transforming standard, inaccessible PDFs into highly customizable reading environments.
Accessible Ingestion: Users can upload standard educational PDFs, which the backend safely parses and strips of distracting visual clutter.
Customizable Presentation: The reader interface features a dedicated "Dyslexia Mode" that instantly applies the scientifically-backed Lexend font, increases letter spacing, and shifts the background to a high-contrast, low-glare tint.
Cognitive Support: It integrates continuous reading aids, allowing users to dynamically adjust text size, line height, and utilize multi-modal learning tools.

Innovation & Creativity:
Contextual AI Summarization
Micro & Macro Text-to-Speech (TTS)
Visual-First Library
Frictionless "Guest First" UX

Tech Stack & Complexity:
The application is built using a lightweight, highly responsive architecture to ensure it runs smoothly even on lower-end devices typically found in schools:

Frontend: Pure HTML5, CSS3, and Vanilla JavaScript (No heavy frameworks to ensure instant load times). Utilizes the native Web Speech API for TTS.

Backend: Python with Flask. Built to handle RESTful API requests efficiently.

Database: SQLite via SQLAlchemy for lightweight, robust relational data storage (Users, Books, History).

PDF Processing Engine: pdfplumber with secure temporary file handling to prevent server memory crashes during extraction.

AI Integration: Google GenAI SDK (gemini-2.0-flash model) for hyper-fast, accurate text simplification.

External APIs: UI-Avatars API for automatic, database-free cover generation.

Usability and Impact:
Target Users: Students with dyslexia, ADHD, or visual impairments; educators seeking to provide accessible materials; and anyone who experiences reading fatigue.
Real-World Value: ReadApt directly promotes inclusive education (UN SDG 4). By giving students control over how they consume information, it reduces study time, lowers anxiety, and fosters independent learning. The ability to upload any PDF means it can be immediately integrated into any existing school curriculum without waiting for publishers to release accessible versions.

