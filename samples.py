"""Sample resume, job description text, and 5-minute presentation demo script."""

SAMPLE_RESUME = """
ALEXANDER RIVERA
Senior Full Stack Engineer | alex.rivera@example.com | San Francisco, CA | linkedin.com/in/alex-rivera-dev

PROFESSIONAL SUMMARY
Versatile Full Stack Software Engineer with 6+ years of experience designing and shipping scalable web applications and distributed backend systems. Proficient in Python, FastAPI, Node.js, React, and AWS cloud infrastructure. Passionate about system design, performance optimization, and clean architecture.

TECHNICAL SKILLS
- Languages: Python, JavaScript, TypeScript, SQL, Bash
- Frameworks & Libraries: FastAPI, Django, React, Redux, Express.js, Next.js, PyTest
- Databases & Caching: PostgreSQL, Redis, MongoDB
- Cloud & DevOps: AWS (EC2, S3, RDS, Lambda), Docker, GitHub Actions, Linux
- Concepts: RESTful APIs, Microservices, CI/CD, Agile/Scrum, Distributed Caching

WORK EXPERIENCE
Senior Software Engineer | CloudScale Tech | Jan 2022 – Present
- Architected and deployed microservices backend using FastAPI and PostgreSQL, serving 1.5M daily active users with 99.98% uptime.
- Optimized database queries and implemented distributed Redis caching, reducing p99 API response latency by 42% (from 320ms to 185ms).
- Led a team of 4 engineers in migrating legacy monolith endpoints to containerized services on Docker and AWS ECS.
- Spearheaded CI/CD automation with GitHub Actions, cutting average deployment cycle from 45 minutes to 8 minutes.

Software Engineer | Apex Digital Solutions | Jun 2019 – Dec 2021
- Developed interactive web portals using React, TypeScript, and TailwindCSS, improving user conversion rates by 18%.
- Integrated third-party payment gateways (Stripe, PayPal) and webhook listeners handling $2M+ in monthly transaction volume.
- Collaborated with product designers and backend engineers to implement OAuth2 / JWT authentication pipelines.

EDUCATION
B.S. in Computer Science | University of California, Davis | 2015 – 2019
"""

SAMPLE_JD = """
Staff / Senior AI Systems Engineer
Company: NextGen AI Platform Inc.
Location: Remote / Hybrid

About the Role:
We are seeking a Senior AI Systems Engineer to join our core intelligence team. You will lead the design and implementation of production AI microservices, high-throughput LLM evaluation pipelines, and scalable cloud infrastructure on Azure and Kubernetes.

Responsibilities:
- Architect, build, and deploy low-latency, scalable AI microservices in Python (FastAPI / AsyncIO).
- Manage container orchestration, service mesh, and autoscaling across Kubernetes (AKS) clusters using Terraform.
- Implement streaming LLM workflows, retrieval-augmented generation (RAG) pipelines, and asynchronous vector search indexing.
- Establish strict observability, telemetry, and load testing using Prometheus, Grafana, and OpenTelemetry.
- Mentor junior and mid-level engineers, conduct code reviews, and drive architectural decision records (ADRs).

Requirements:
- 5+ years of production software engineering experience in Python or Go.
- Deep expertise with Kubernetes (K8s), Helm, and Infrastructure as Code (Terraform).
- Hands-on experience with Microsoft Azure AI Foundry, Azure OpenAI Service, or LangChain/LlamaIndex.
- Strong knowledge of vector databases (e.g. Qdrant, Pinecone, pgvector) and distributed message brokers (Kafka or RabbitMQ).
- Excellent communication skills, system design instincts, and familiarity with STAR-method behavioral leadership.
"""

# Relatable 3-question presentation demo script for quick 5-minute demos
DEMO_QUESTIONS = [
    "Can you tell me about a major software project you built recently, why you chose that tech stack, and what part you found most challenging?",
    "Describe a difficult bug or roadblock you ran into while developing a feature, and the exact steps you took to debug and resolve it.",
    "Tell me about a time you worked on a team or academic project where there was a disagreement or someone fell behind on a deadline. How did you handle it?",
]

DEMO_ANSWERS = [
    "I built a full-stack web application using React and FastAPI. I chose React for component-based UI and FastAPI for fast asynchronous API endpoints. The most challenging part was designing clean REST endpoints and handling database state efficiently.",
    "I ran into an API timeout bug when handling concurrent requests. I used logging and Postman to isolate the issue, traced it to an unindexed database query, added an index on the user ID column, and reduced latency from 1.2s to 80ms.",
    "During a team hackathon, our backend teammate struggled with authentication, putting our submission deadline at risk. I scheduled a quick pair-programming session, simplified the auth flow, redistributed tasks, and we successfully delivered the working project on time.",
]
