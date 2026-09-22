"""Sample resume, job description text, and 5-minute presentation demo script."""

SAMPLE_RESUME = """
ALEX TAYLOR
Computer Science Student | alex.taylor@example.edu | github.com/alextaylor

EDUCATION
B.S. in Computer Science | State University | Expected May 2027
Relevant Coursework: Data Structures, Algorithms, Web Development, Databases

TECHNICAL SKILLS
- Languages: Python, Java, JavaScript, HTML/CSS, SQL
- Frameworks & Tools: React, Flask, Node.js, Git, GitHub, VS Code
- Concepts: REST APIs, Object-Oriented Programming, Agile Teamwork

ACADEMIC & PERSONAL PROJECTS
Task Manager Web App (React, Python, Flask, SQLite)
- Built a full-stack to-do list application to help students track assignments.
- Created a REST API with Flask to handle user data and store tasks in a SQLite database.
- Designed a responsive frontend using React and CSS, allowing users to easily filter tasks.
- Used Git for version control and collaborated with a partner using GitHub pull requests.

Live Weather Dashboard (JavaScript, HTML, CSS)
- Developed a web dashboard that fetches and displays live weather data using a public REST API.
- Implemented asynchronous JavaScript (Promises/Fetch) to handle API responses without freezing the page.

EXPERIENCE
Teaching Assistant - Intro to Programming | State University | Aug 2025 - Present
- Help students debug Python code and explain core concepts like loops and functions during weekly lab sessions.
"""

SAMPLE_JD = """
Software Engineering Intern (Summer)
Company: TechNova Solutions
Location: Remote

About the Role:
We are looking for an enthusiastic Software Engineering Intern to join our web development team. You will work alongside experienced engineers to build features for our internal tools and customer-facing web applications.

Responsibilities:
- Write clean, maintainable code in Python or JavaScript.
- Assist in developing frontend components using React and backend APIs.
- Participate in daily stand-ups and sprint planning meetings.
- Debug and fix minor bugs reported by the QA team.

Requirements:
- Currently pursuing a B.S. in Computer Science or a related technical field.
- Solid understanding of core programming concepts (Data Structures, OOP).
- Basic familiarity with web development (HTML, CSS, JavaScript) or backend logic (Python, Java).
- Experience with version control (Git/GitHub) through class projects or hackathons.
- Strong problem-solving skills and a willingness to learn and ask questions.
"""

# Relatable 3-question presentation demo script for quick 5-minute demos
DEMO_QUESTIONS = [
    "Can you tell me about a recent coding project you built, why you chose the tools you used, and what you learned from it?",
    "Describe a time you ran into a tough bug in your code. How did you figure it out and fix it?",
    "Tell me about a time you worked on a group project for a class and someone wasn't doing their share of the work. How did you handle it?",
]

DEMO_ANSWERS = [
    "For my web development class, I built a full-stack Task Manager app. I chose React for the frontend because I wanted to learn component-based UI, and Python with Flask for the backend since I was already comfortable with Python from my introductory classes. The most challenging part was connecting the frontend to the backend API, but I learned a lot about how HTTP requests work and how to correctly parse JSON data.",
    "While building my weather dashboard project, I had a bug where the API data wasn't loading on the page and the screen stayed blank. I started by using `console.log` to print the API response, but nothing showed up. I then opened the browser's Network tab and realized the API request was actually failing due to a typo in the URL. Once I fixed the URL string, the data loaded perfectly. It taught me how to use developer tools to debug network issues.",
    "During a group software engineering project, one of our teammates missed a deadline for designing our database schema. Instead of getting upset or doing the work for them, I reached out to them privately. I found out they were really overwhelmed with midterms in another class. I offered to hop on a Zoom call and pair-program with them for an hour to get the database set up. We finished it together, and it helped them get back on track for the rest of the project.",
]
