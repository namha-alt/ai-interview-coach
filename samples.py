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
    "In my last role, we needed a scalable backend to handle a 300% spike in daily active users. I was tasked with migrating our monolithic legacy system. I chose FastAPI for its native async support and high throughput, paired with React on the frontend. I architected a microservices approach, utilizing Docker and AWS ECS to ensure modularity. The most challenging part was ensuring zero downtime during data migration, which I solved by implementing a dual-write pattern. Ultimately, we improved p99 API latency by 45% and successfully handled the user load.",
    "During a high-traffic product launch, we experienced severe API timeouts that threatened user onboarding. I needed to immediately identify and resolve the bottleneck. I initiated our incident response protocol, utilizing Datadog traces and PostgreSQL EXPLAIN ANALYZE to isolate the slow queries. I discovered that a crucial user-lookup query was missing a composite index. I deployed a hotfix to add the missing index and implemented a Redis caching layer for frequent read-heavy requests. This reduced our average response time from 1.2 seconds down to 60ms, stabilizing the platform completely.",
    "In a recent cross-functional project, our backend developer fell behind schedule due to unexpected authentication complexities, putting our launch date at risk. As the technical lead, I needed to get the project back on track without creating friction. Instead of reassigning the work, I scheduled a 1-on-1 pair programming session to deeply understand the blocker. We realized the OAuth2 implementation was overly complex, so we simplified the flow using a managed identity provider. By collaborating directly and removing the complexity, we not only met our deadline but also improved the team's understanding of secure auth flows.",
]