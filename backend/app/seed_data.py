"""
Seed data generator creating the canonical job 'Senior Full Stack AI Engineer'
and the 8 distinct candidate archetypes specified in the competition prompt.
"""
from typing import Dict, Any, List

DEMO_JOB = {
    "title": "Senior Full Stack AI Engineer",
    "raw_description": """
About the Role:
We are seeking a Senior Full Stack AI Engineer to design and build our next-generation enterprise intelligence platform. You will architect robust, low-latency microservices, integrate generative AI / LLM APIs, and build reactive, high-density recruiter interfaces.

Core Responsibilities:
- Design and implement end-to-end full stack web applications with modern frontend and backend architectures.
- Build high-performance REST APIs in Python using FastAPI with PostgreSQL databases.
- Develop responsive, accessible web applications using React and TypeScript.
- Containerize and deploy services using Docker and orchestrate on AWS cloud infrastructure.
- Integrate modern LLM APIs (Gemini, Claude, GPT) with evaluation frameworks, streaming responses, and prompt optimization.
- Mentor junior engineers and participate in architectural design reviews.

Requirements:
- Minimum 3+ years of professional software engineering experience.
- Strong proficiency in Python and FastAPI backend development.
- Strong proficiency in React and TypeScript for frontend web applications.
- Solid experience with relational databases, schema design, and query optimization in PostgreSQL.
- Experience with Docker containerization and cloud infrastructure on AWS.
- Hands-on experience integrating LLM APIs and building generative AI workflows.
- Bachelor's degree in Computer Science, Software Engineering, or equivalent practical experience.
""",
    "seniority": "Senior",
    "min_years_experience": 3.0,
    "education_required": "Bachelor's degree in Computer Science or equivalent",
    "location": "San Francisco, CA / Remote",
    "work_mode": "Hybrid / Remote",
    "responsibilities": [
        "Design and implement end-to-end full stack web applications with modern frontend and backend architectures.",
        "Build high-performance REST APIs in Python using FastAPI with PostgreSQL databases.",
        "Develop responsive, accessible web applications using React and TypeScript.",
        "Containerize and deploy services using Docker and orchestrate on AWS cloud infrastructure.",
        "Integrate modern LLM APIs with evaluation frameworks, streaming responses, and prompt optimization."
    ],
    "tools_and_tech": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker", "AWS", "LLM APIs"],
    "domain_knowledge": ["Generative AI", "Full Stack Web Architecture", "Distributed Microservices"],
    "soft_skills": ["Technical Mentorship", "System Design", "Cross-Functional Collaboration"],
    "requirements": [
        {"name": "Python", "category": "skill", "tier": "MUST_HAVE", "expected_years": 3.0, "weight": 1.0},
        {"name": "FastAPI", "category": "skill", "tier": "MUST_HAVE", "expected_years": 2.0, "weight": 1.0},
        {"name": "React", "category": "skill", "tier": "MUST_HAVE", "expected_years": 3.0, "weight": 1.0},
        {"name": "TypeScript", "category": "skill", "tier": "MUST_HAVE", "expected_years": 2.5, "weight": 1.0},
        {"name": "PostgreSQL", "category": "skill", "tier": "MUST_HAVE", "expected_years": 3.0, "weight": 1.0},
        {"name": "Docker", "category": "skill", "tier": "SHOULD_HAVE", "expected_years": 2.0, "weight": 0.75},
        {"name": "AWS", "category": "skill", "tier": "SHOULD_HAVE", "expected_years": 2.0, "weight": 0.75},
        {"name": "LLM APIs", "category": "skill", "tier": "SHOULD_HAVE", "expected_years": 1.5, "weight": 0.75},
        {"name": "3+ Years Professional Experience", "category": "experience", "tier": "MUST_HAVE", "expected_years": 3.0, "weight": 1.0}
    ]
}

DEMO_CANDIDATES: List[Dict[str, Any]] = [
    # 1. The Perfect Candidate: High evidence across all Must-Haves, proven projects, zero flags
    {
        "name": "Rahul Sharma",
        "email": "rahul.sharma@example.com",
        "phone": "+1-415-555-0101",
        "location": "San Francisco, CA",
        "linkedin": "https://linkedin.com/in/rahulsharma-ai",
        "github": "https://github.com/rahulsharma-dev",
        "portfolio": "https://rahulsharma.io",
        "summary": "Full Stack AI Engineer with 4.5 years of production experience architecting high-scale Python microservices, TypeScript/React frontends, and LLM-powered enterprise workflows.",
        "total_experience_years": 4.5,
        "educations": [
            {
                "degree": "B.S. in Computer Science",
                "institution": "University of California, Berkeley",
                "graduation_year": "2021",
                "field": "Computer Science",
                "gpa": "3.85"
            }
        ],
        "experiences": [
            {
                "company": "Nexus AI Labs",
                "role": "Senior Full Stack Engineer",
                "start_date": "2023",
                "end_date": "Present",
                "duration_years": 2.5,
                "responsibilities": [
                    "Engineered asynchronous backend microservices in Python and FastAPI handling 12M monthly API requests.",
                    "Built reactive enterprise analytics dashboards using React, Next.js, and TypeScript with Tailwind CSS.",
                    "Integrated Gemini and Claude LLM APIs for automated document reasoning with streaming SSE responses.",
                    "Designed PostgreSQL database schemas with connection pooling, pgvector embeddings, and automated index tuning.",
                    "Containerized multi-service architectures with Docker and deployed via Terraform on AWS ECS and RDS."
                ],
                "achievements": [
                    "Decreased p95 API response latency from 320ms to 48ms via async connection multiplexing.",
                    "Achieved 99.98% service uptime across two consecutive production release cycles."
                ],
                "technologies": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker", "AWS", "LLM APIs"]
            },
            {
                "company": "Veloce Technologies",
                "role": "Software Engineer",
                "start_date": "2021",
                "end_date": "2023",
                "duration_years": 2.0,
                "responsibilities": [
                    "Developed customer-facing web applications using React and TypeScript.",
                    "Created RESTful endpoints in Python FastAPI and integrated relational PostgreSQL storage.",
                    "Configured CI/CD automated test pipelines using GitHub Actions and Docker."
                ],
                "achievements": ["Delivered self-service onboarding portal increasing user activation by 28%."],
                "technologies": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker"]
            }
        ],
        "skills": [
            {"name": "Python", "category": "technical", "years_of_experience": 4.5, "proficiency_claimed": "advanced"},
            {"name": "FastAPI", "category": "framework", "years_of_experience": 4.0, "proficiency_claimed": "advanced"},
            {"name": "React", "category": "framework", "years_of_experience": 4.5, "proficiency_claimed": "advanced"},
            {"name": "TypeScript", "category": "technical", "years_of_experience": 4.0, "proficiency_claimed": "advanced"},
            {"name": "PostgreSQL", "category": "database", "years_of_experience": 4.0, "proficiency_claimed": "advanced"},
            {"name": "Docker", "category": "technical", "years_of_experience": 3.5, "proficiency_claimed": "advanced"},
            {"name": "AWS", "category": "cloud", "years_of_experience": 3.0, "proficiency_claimed": "advanced"},
            {"name": "LLM APIs", "category": "technical", "years_of_experience": 2.5, "proficiency_claimed": "advanced"}
        ],
        "projects": [
            {
                "title": "DocuProof AI Intelligence Platform",
                "description": "Production SaaS application extracting, verifying, and matching complex enterprise contracts using FastAPI, React/TypeScript, and Gemini LLM APIs.",
                "technologies": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker", "AWS", "LLM APIs"],
                "contribution": "Principal architect and lead developer.",
                "results_metrics": "Processed over 450,000 PDF documents with 99.2% extraction accuracy and <800ms end-to-end processing time."
            },
            {
                "title": "AsyncPG Vector Search Cache",
                "description": "High-speed semantic search layer combining PostgreSQL pgvector and Redis caching for sub-10ms similarity queries.",
                "technologies": ["Python", "PostgreSQL", "Docker"],
                "contribution": "Sole creator and open-source maintainer.",
                "results_metrics": "Over 1,200 GitHub stars and adopted in production by 3 startup engineering teams."
            }
        ],
        "certifications": [
            {"name": "AWS Certified Solutions Architect – Associate", "issuer": "Amazon Web Services", "issue_date": "2023"}
        ],
        "explicit_claims": [
            {"claim_text": "4+ years building production full-stack AI systems in Python and React", "claimed_skill": "Full Stack AI", "claimed_duration_years": 4.5, "claimed_seniority": "Senior"}
        ]
    },

    # 2. Strong Candidate: Solid experience, strong evidence, minor gaps in AWS depth
    {
        "name": "Amit Patel",
        "email": "amit.patel@example.com",
        "phone": "+1-408-555-0102",
        "location": "San Jose, CA",
        "linkedin": "https://linkedin.com/in/amitpatel-dev",
        "github": "https://github.com/amitpatel",
        "portfolio": "https://amitpatel.dev",
        "summary": "Full Stack Engineer with 3.8 years experience focusing on Python FastAPI backends, React applications, and PostgreSQL data stores.",
        "total_experience_years": 3.8,
        "educations": [
            {
                "degree": "B.Tech in Computer Engineering",
                "institution": "National Institute of Technology",
                "graduation_year": "2022",
                "field": "Computer Engineering",
                "gpa": "3.8"
            }
        ],
        "experiences": [
            {
                "company": "Krypton Software",
                "role": "Full Stack Software Engineer",
                "start_date": "2022",
                "end_date": "Present",
                "duration_years": 3.8,
                "responsibilities": [
                    "Engineered Python FastAPI web services and integrated PostgreSQL relational tables.",
                    "Constructed interactive user interfaces using React, TypeScript, and state management via Redux Toolkit.",
                    "Containerized applications using Docker and deployed onto local and cloud staging servers.",
                    "Connected external generative AI LLM endpoints to automate customer ticket summaries."
                ],
                "achievements": ["Automated invoice reconciliation, reducing accounting manual review time by 60%."],
                "technologies": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker", "LLM APIs"]
            }
        ],
        "skills": [
            {"name": "Python", "category": "technical", "years_of_experience": 3.8, "proficiency_claimed": "advanced"},
            {"name": "FastAPI", "category": "framework", "years_of_experience": 3.5, "proficiency_claimed": "advanced"},
            {"name": "React", "category": "framework", "years_of_experience": 3.8, "proficiency_claimed": "advanced"},
            {"name": "TypeScript", "category": "technical", "years_of_experience": 3.0, "proficiency_claimed": "proficient"},
            {"name": "PostgreSQL", "category": "database", "years_of_experience": 3.5, "proficiency_claimed": "advanced"},
            {"name": "Docker", "category": "technical", "years_of_experience": 2.5, "proficiency_claimed": "proficient"},
            {"name": "LLM APIs", "category": "technical", "years_of_experience": 1.5, "proficiency_claimed": "proficient"}
        ],
        "projects": [
            {
                "title": "SmartSupport AI Ticketing",
                "description": "Real-time helpdesk application using FastAPI, TypeScript, React, and LLM text generation.",
                "technologies": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker", "LLM APIs"],
                "contribution": "Full stack implementer.",
                "results_metrics": "Deployed for 15,000 monthly active users."
            }
        ],
        "certifications": [],
        "explicit_claims": [
            {"claim_text": "3.8 years full stack experience with FastAPI and React", "claimed_skill": "Full Stack", "claimed_duration_years": 3.8, "claimed_seniority": "Mid"}
        ]
    },

    # 3. Transferable Skills Candidate: Deep Azure instead of AWS, PyTorch instead of standard LLM APIs
    {
        "name": "Priya Nair",
        "email": "priya.nair@example.com",
        "phone": "+1-206-555-0103",
        "location": "Seattle, WA",
        "linkedin": "https://linkedin.com/in/priyanair-cloud",
        "github": "https://github.com/priyanair",
        "portfolio": "https://priyanair.tech",
        "summary": "Senior Software & Cloud Systems Engineer with 4.2 years experience. Deep expertise in Python, FastAPI, React, TypeScript, PostgreSQL, and enterprise Microsoft Azure cloud infrastructure.",
        "total_experience_years": 4.2,
        "educations": [
            {
                "degree": "B.S. in Computer Science",
                "institution": "University of Washington",
                "graduation_year": "2021",
                "field": "Computer Science",
                "gpa": "3.7"
            }
        ],
        "experiences": [
            {
                "company": "Horizon Cloud Systems",
                "role": "Cloud Software Engineer",
                "start_date": "2021",
                "end_date": "Present",
                "duration_years": 4.2,
                "responsibilities": [
                    "Built full stack data portals with React, TypeScript, and Python FastAPI microservices.",
                    "Managed enterprise multi-tenant Azure Kubernetes Service (AKS), Azure Container Instances, and Azure Blob storage.",
                    "Tuned high-throughput PostgreSQL queries and automated database failover replicas.",
                    "Fine-tuned PyTorch machine learning models and wrapped inference endpoints with FastAPI."
                ],
                "achievements": ["Scaled enterprise cloud portal to 80,000 concurrent enterprise users on Azure."],
                "technologies": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker", "Azure", "PyTorch"]
            }
        ],
        "skills": [
            {"name": "Python", "category": "technical", "years_of_experience": 4.2, "proficiency_claimed": "advanced"},
            {"name": "FastAPI", "category": "framework", "years_of_experience": 3.5, "proficiency_claimed": "advanced"},
            {"name": "React", "category": "framework", "years_of_experience": 3.5, "proficiency_claimed": "advanced"},
            {"name": "TypeScript", "category": "technical", "years_of_experience": 3.0, "proficiency_claimed": "advanced"},
            {"name": "PostgreSQL", "category": "database", "years_of_experience": 4.0, "proficiency_claimed": "advanced"},
            {"name": "Docker", "category": "technical", "years_of_experience": 3.5, "proficiency_claimed": "advanced"},
            {"name": "Azure", "category": "cloud", "years_of_experience": 4.0, "proficiency_claimed": "advanced"},
            {"name": "PyTorch", "category": "technical", "years_of_experience": 3.0, "proficiency_claimed": "advanced"}
        ],
        "projects": [
            {
                "title": "Azure Neural Telemetry Suite",
                "description": "Real-time telemetry and anomaly detection platform deployed on Azure AKS with Python and React frontend.",
                "technologies": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker", "Azure", "PyTorch"],
                "contribution": "Lead architect and developer.",
                "results_metrics": "Ingested 50GB telemetry stream daily with zero message loss."
            }
        ],
        "certifications": [
            {"name": "Microsoft Certified: Azure Solutions Architect Expert", "issuer": "Microsoft", "issue_date": "2023"}
        ],
        "explicit_claims": [
            {"claim_text": "4 years enterprise cloud and full stack software engineering", "claimed_skill": "Cloud Engineering", "claimed_duration_years": 4.2, "claimed_seniority": "Senior"}
        ]
    },

    # 4. Missing Requirements Candidate: Great backend Python/FastAPI dev, but completely lacks React & TypeScript
    {
        "name": "Vikram Singh",
        "email": "vikram.singh@example.com",
        "phone": "+1-512-555-0104",
        "location": "Austin, TX",
        "linkedin": "https://linkedin.com/in/vikram-backend",
        "github": "https://github.com/vikramsingh-dev",
        "portfolio": "https://vikramsingh.dev",
        "summary": "Specialized Backend Distributed Systems Engineer with 5 years experience in Python, FastAPI, PostgreSQL, Docker, and AWS. Zero frontend/React involvement.",
        "total_experience_years": 5.0,
        "educations": [
            {
                "degree": "B.S. in Electrical and Computer Engineering",
                "institution": "University of Texas at Austin",
                "graduation_year": "2020",
                "field": "ECE",
                "gpa": "3.6"
            }
        ],
        "experiences": [
            {
                "company": "Apex Data Engines",
                "role": "Senior Backend Engineer",
                "start_date": "2020",
                "end_date": "Present",
                "duration_years": 5.0,
                "responsibilities": [
                    "Engineered asynchronous backend distributed services using Python, FastAPI, and gRPC.",
                    "Optimized complex PostgreSQL database queries, partitioning, and automated schema migrations.",
                    "Containerized microservices with Docker and deployed onto AWS EKS clusters.",
                    "Connected LangChain workflows to backend data pipelines."
                ],
                "achievements": ["Refactored payment processing pipeline achieving sub-20ms transaction finality."],
                "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "LLM APIs"]
            }
        ],
        "skills": [
            {"name": "Python", "category": "technical", "years_of_experience": 5.0, "proficiency_claimed": "advanced"},
            {"name": "FastAPI", "category": "framework", "years_of_experience": 4.0, "proficiency_claimed": "advanced"},
            {"name": "PostgreSQL", "category": "database", "years_of_experience": 5.0, "proficiency_claimed": "advanced"},
            {"name": "Docker", "category": "technical", "years_of_experience": 4.0, "proficiency_claimed": "advanced"},
            {"name": "AWS", "category": "cloud", "years_of_experience": 3.5, "proficiency_claimed": "advanced"},
            {"name": "LLM APIs", "category": "technical", "years_of_experience": 2.0, "proficiency_claimed": "proficient"}
        ],
        "projects": [
            {
                "title": "Async Payment Router",
                "description": "High-throughput financial message routing engine in FastAPI and PostgreSQL on AWS.",
                "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
                "contribution": "Core designer.",
                "results_metrics": "Processed $40M weekly transaction volume."
            }
        ],
        "certifications": [
            {"name": "AWS Certified Developer", "issuer": "Amazon Web Services", "issue_date": "2022"}
        ],
        "explicit_claims": [
            {"claim_text": "5 years Python backend distributed architecture", "claimed_skill": "Backend Engineering", "claimed_duration_years": 5.0, "claimed_seniority": "Senior"}
        ]
    },

    # 5. Contradictory Claim Candidate: Claims 5 yrs Python, timeline shows ~2.5 yrs; Senior Developer title while full-time master's student (2021-2023)
    {
        "name": "Ananya Sen",
        "email": "ananya.sen@example.com",
        "phone": "+1-617-555-0105",
        "location": "Boston, MA",
        "linkedin": "https://linkedin.com/in/ananyasen",
        "github": "https://github.com/ananyasen",
        "portfolio": "https://ananyasen.me",
        "summary": "Full Stack Software Engineer claiming 5+ years of Python, React, and AI experience. Passionate about rapid product delivery.",
        "total_experience_years": 2.5,
        "educations": [
            {
                "degree": "Full-time Master of Science in Computer Science",
                "institution": "Boston University",
                "graduation_year": "2021-2023",
                "field": "Computer Science",
                "gpa": "3.9"
            }
        ],
        "experiences": [
            {
                "company": "Zenith Global Tech",
                "role": "Senior Developer & Tech Lead",
                "start_date": "2021",
                "end_date": "2023",
                "duration_years": 2.0,
                "responsibilities": [
                    "Claimed role as Senior Developer and Tech Lead directing backend architecture.",
                    "Utilized Python and FastAPI for internal reporting tools."
                ],
                "achievements": ["Launched company internal dashboard."],
                "technologies": ["Python", "FastAPI", "PostgreSQL"]
            },
            {
                "company": "BrightSpark AI",
                "role": "Software Engineer",
                "start_date": "2024",
                "end_date": "Present",
                "duration_years": 1.0,
                "responsibilities": [
                    "Developing full stack React and FastAPI components for AI customer tools.",
                    "Configuring Docker containers and testing API routes."
                ],
                "achievements": ["Integrated customer feedback widget."],
                "technologies": ["Python", "FastAPI", "React", "Docker"]
            }
        ],
        "skills": [
            {"name": "Python", "category": "technical", "years_of_experience": 5.0, "proficiency_claimed": "advanced"},
            {"name": "FastAPI", "category": "framework", "years_of_experience": 3.0, "proficiency_claimed": "proficient"},
            {"name": "React", "category": "framework", "years_of_experience": 2.5, "proficiency_claimed": "proficient"},
            {"name": "PostgreSQL", "category": "database", "years_of_experience": 2.0, "proficiency_claimed": "proficient"},
            {"name": "Docker", "category": "technical", "years_of_experience": 1.5, "proficiency_claimed": "familiar"}
        ],
        "projects": [
            {
                "title": "Feedback Summarizer",
                "description": "Mini application wrapping OpenAI endpoints with Python FastAPI.",
                "technologies": ["Python", "FastAPI", "Docker"],
                "contribution": "Developer",
                "results_metrics": "Internal prototype"
            }
        ],
        "certifications": [],
        "explicit_claims": [
            {"claim_text": "5 years of Python development experience", "claimed_skill": "Python", "claimed_duration_years": 5.0, "claimed_seniority": "Senior"},
            {"claim_text": "Senior Developer & Tech Lead at Zenith Global Tech (2021-2023)", "claimed_skill": "Technical Leadership", "claimed_duration_years": 2.0, "claimed_seniority": "Lead"}
        ]
    },

    # 6. High Potential Candidate: 1.8 years experience, high velocity, great open source, Current Match 72%, Potential Match 90%
    {
        "name": "Rohan Mehta",
        "email": "rohan.mehta@example.com",
        "phone": "+1-650-555-0106",
        "location": "Palo Alto, CA",
        "linkedin": "https://linkedin.com/in/rohanmehta-dev",
        "github": "https://github.com/rohanmehta",
        "portfolio": "https://rohanmehta.dev",
        "summary": "Accelerated Junior/Mid Full Stack AI Engineer with 1.8 years experience. Top 1% competitive programmer, author of open-source FastAPI and Next.js tools, rapid learner with immense potential trajectory.",
        "total_experience_years": 1.8,
        "educations": [
            {
                "degree": "B.S. in Computer Science",
                "institution": "Stanford University",
                "graduation_year": "2024",
                "field": "Computer Science",
                "gpa": "3.95"
            }
        ],
        "experiences": [
            {
                "company": "HyperShift Software",
                "role": "Associate Software Engineer",
                "start_date": "2024",
                "end_date": "Present",
                "duration_years": 1.8,
                "responsibilities": [
                    "Authored high-performance FastAPI microservices and TypeScript React frontends.",
                    "Constructed PostgreSQL migration scripts and optimized query execution plans.",
                    "Containerized development workflows with Docker and Podman.",
                    "Built generative AI evaluation pipelines with Gemini and OpenAI APIs."
                ],
                "achievements": [
                    "Won HackMIT and HackStanford with AI developer productivity tools.",
                    "Reduced test build execution times by 45% using lightweight containerization."
                ],
                "technologies": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker", "LLM APIs"]
            }
        ],
        "skills": [
            {"name": "Python", "category": "technical", "years_of_experience": 2.5, "proficiency_claimed": "advanced"},
            {"name": "FastAPI", "category": "framework", "years_of_experience": 2.0, "proficiency_claimed": "advanced"},
            {"name": "React", "category": "framework", "years_of_experience": 2.0, "proficiency_claimed": "advanced"},
            {"name": "TypeScript", "category": "technical", "years_of_experience": 2.0, "proficiency_claimed": "advanced"},
            {"name": "PostgreSQL", "category": "database", "years_of_experience": 2.0, "proficiency_claimed": "proficient"},
            {"name": "Docker", "category": "technical", "years_of_experience": 2.0, "proficiency_claimed": "proficient"},
            {"name": "LLM APIs", "category": "technical", "years_of_experience": 2.0, "proficiency_claimed": "advanced"}
        ],
        "projects": [
            {
                "title": "FastNext AI Scaffold",
                "description": "Production-ready boilerplate bridging FastAPI, Next.js TypeScript, and multi-provider LLM streaming.",
                "technologies": ["Python", "FastAPI", "React", "TypeScript", "Docker", "LLM APIs"],
                "contribution": "Creator & primary author.",
                "results_metrics": "2,400+ GitHub stars, 18,000 monthly npm/pip installs."
            }
        ],
        "certifications": [],
        "explicit_claims": [
            {"claim_text": "Rapid engineering delivery across modern AI full-stack architectures", "claimed_skill": "Full Stack", "claimed_duration_years": 1.8, "claimed_seniority": "Junior-Mid"}
        ]
    },

    # 7. Excellent Experience But Weak Evidence: 7 years corporate title, but sparse project details and vague bullets
    {
        "name": "Siddharth Verma",
        "email": "siddharth.verma@example.com",
        "phone": "+1-312-555-0107",
        "location": "Chicago, IL",
        "linkedin": "https://linkedin.com/in/siddharth-verma",
        "github": "https://github.com/sverma",
        "portfolio": "",
        "summary": "Senior Technology Consultant with 7 years in software development. Managed projects, delivered IT solutions, and worked with cross-functional global teams.",
        "total_experience_years": 7.0,
        "educations": [
            {
                "degree": "B.E. in Information Technology",
                "institution": "State University",
                "graduation_year": "2018",
                "field": "Information Technology",
                "gpa": "3.3"
            }
        ],
        "experiences": [
            {
                "company": "Global IT Solutions",
                "role": "Senior Consultant",
                "start_date": "2021",
                "end_date": "Present",
                "duration_years": 4.5,
                "responsibilities": [
                    "Responsible for application development and client stakeholder communication.",
                    "Attended sprint planning, backlog grooming, and daily standup calls.",
                    "Worked on Python web services and general backend maintenance.",
                    "Assisted with cloud migration discussions and database administration."
                ],
                "achievements": ["Recognized by client management for timely milestone delivery."],
                "technologies": ["Python", "PostgreSQL", "AWS"]
            },
            {
                "company": "Matrix Enterprise Tech",
                "role": "Systems Analyst",
                "start_date": "2018",
                "end_date": "2021",
                "duration_years": 2.5,
                "responsibilities": [
                    "Maintained internal web portals and handled bug fixes.",
                    "Wrote SQL queries for quarterly reporting."
                ],
                "achievements": ["Resolved production tickets within SLA."],
                "technologies": ["Python", "SQL"]
            }
        ],
        "skills": [
            {"name": "Python", "category": "technical", "years_of_experience": 7.0, "proficiency_claimed": "proficient"},
            {"name": "PostgreSQL", "category": "database", "years_of_experience": 5.0, "proficiency_claimed": "proficient"},
            {"name": "AWS", "category": "cloud", "years_of_experience": 3.0, "proficiency_claimed": "familiar"},
            {"name": "Docker", "category": "technical", "years_of_experience": 2.0, "proficiency_claimed": "familiar"}
        ],
        "projects": [
            {
                "title": "Client Portal Maintenance",
                "description": "Maintained existing legacy client portal.",
                "technologies": ["Python", "SQL"],
                "contribution": "Maintenance team member",
                "results_metrics": "Ticket resolution"
            }
        ],
        "certifications": [],
        "explicit_claims": [
            {"claim_text": "7 years senior enterprise software development", "claimed_skill": "Software Engineering", "claimed_duration_years": 7.0, "claimed_seniority": "Senior"}
        ]
    },

    # 8. Keyword-Heavy Resume: Lists every buzzword in skills block, but zero project/work evidence for them (Tricks ATS, but exposed by TalentProof AI!)
    {
        "name": "Neha Gupta",
        "email": "neha.gupta@example.com",
        "phone": "+1-917-555-0108",
        "location": "New York, NY",
        "linkedin": "https://linkedin.com/in/nehagupta-tech",
        "github": "https://github.com/nehagupta",
        "portfolio": "",
        "summary": "Master Full Stack AI Architect. Expert in Python, FastAPI, React, TypeScript, PostgreSQL, Docker, AWS, Kubernetes, LLM APIs, LangChain, PyTorch, GraphQL, Redis, Terraform, CI/CD.",
        "total_experience_years": 3.2,
        "educations": [
            {
                "degree": "B.S. in Information Systems",
                "institution": "New York University",
                "graduation_year": "2022",
                "field": "Information Systems",
                "gpa": "3.5"
            }
        ],
        "experiences": [
            {
                "company": "Alpha Trend Media",
                "role": "Web Developer",
                "start_date": "2022",
                "end_date": "Present",
                "duration_years": 3.2,
                "responsibilities": [
                    "Updated WordPress content and HTML/CSS styling for company blog.",
                    "Configured Google Analytics tags and assisted marketing department with landing pages.",
                    "Wrote occasional Python helper scripts to clean CSV spreadsheets."
                ],
                "achievements": ["Redesigned marketing home page."],
                "technologies": ["HTML", "CSS", "Python"]
            }
        ],
        "skills": [
            {"name": "Python", "category": "technical", "years_of_experience": 3.0, "proficiency_claimed": "advanced"},
            {"name": "FastAPI", "category": "framework", "years_of_experience": 3.0, "proficiency_claimed": "expert"},
            {"name": "React", "category": "framework", "years_of_experience": 3.0, "proficiency_claimed": "expert"},
            {"name": "TypeScript", "category": "technical", "years_of_experience": 3.0, "proficiency_claimed": "expert"},
            {"name": "PostgreSQL", "category": "database", "years_of_experience": 3.0, "proficiency_claimed": "expert"},
            {"name": "Docker", "category": "technical", "years_of_experience": 3.0, "proficiency_claimed": "expert"},
            {"name": "AWS", "category": "cloud", "years_of_experience": 3.0, "proficiency_claimed": "expert"},
            {"name": "LLM APIs", "category": "technical", "years_of_experience": 3.0, "proficiency_claimed": "expert"},
            {"name": "Kubernetes", "category": "technical", "years_of_experience": 3.0, "proficiency_claimed": "expert"}
        ],
        "projects": [
            {
                "title": "Marketing Blog Redesign",
                "description": "Styled WordPress template with CSS for corporate marketing site.",
                "technologies": ["HTML", "CSS"],
                "contribution": "Web designer",
                "results_metrics": "Live website"
            }
        ],
        "certifications": [],
        "explicit_claims": [
            {"claim_text": "Expert in FastAPI, React, TypeScript, PostgreSQL, Docker, AWS, and LLM APIs", "claimed_skill": "Full Stack AI", "claimed_duration_years": 3.0, "claimed_seniority": "Senior"}
        ]
    }
]
