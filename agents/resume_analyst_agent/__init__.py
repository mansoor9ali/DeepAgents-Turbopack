"""
Resume Analyst Agent Package

Professional resume analysis agent with PII protection middleware.
Evaluates and provides improvement suggestions for resumes across diverse industries.

Features:
- Resume parsing and extraction
- Skill and experience analysis
- Job requirement matching
- Improvement suggestions
- PII redaction (email, credit card, URL)

Usage:
    from agents.resume_analyst_agent import resume_analyst_agent

    result = await resume_analyst_agent.ainvoke({
        "messages": [HumanMessage("Analyze the resume at path/to/resume.pdf")]
    })

Author: DeepAgents-Turbopack
"""

from .resume_analyst_agent import (
    # Agent instance
    resume_analyst_agent,

    # Tools
    read_resume,
    extract_information,
    generate_summary,
    calculate_experience_years,
    match_job_requirements,
    suggest_improvements,

    # Configuration
    system_prompt,
    MODEL_NAME,
)

__all__ = [
    # Agent
    "resume_analyst_agent",

    # Tools
    "read_resume",
    "extract_information",
    "generate_summary",
    "calculate_experience_years",
    "match_job_requirements",
    "suggest_improvements",

    # Config
    "system_prompt",
    "MODEL_NAME",
]
