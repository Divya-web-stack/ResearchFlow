import uuid
from typing import Any
from groq import Groq
from datetime import datetime


import os

from app.agents.agent import create_agent, registry
from app.agents.crew import ResearchBasedAgent
from app.memory.store import MemoryStore
from app.services.serper_search import SerperSearch
from app.utils.credibility import get_source_score

search_client = SerperSearch()
memory_store = MemoryStore()

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ==========================
# Research Agent
# ==========================
def research_execute(
    query: str,
    limit: int = 5,
    plan: dict | None = None,
    **kwargs: Any
) -> dict[str, Any]:

    tasks = plan.get("tasks", []) if plan else []

    search_query = query

    if "comparison_analysis" in tasks:
        search_query = (
            f"{query} comparison differences strengths weaknesses"
        )

    results = search_client.search(
        search_query,
        limit=limit
    )

    highlights = [
        f"Found result: {item.get('title', 'Unknown')}"
        for item in results
    ]

    return {
        "query": query,
        "search_query": search_query,
        "results": results,
        "highlights": highlights
    }


# ==========================
# Fact Checker Agent
# ==========================
def fact_checker_execute(
    research_results: dict[str, Any],
    **kwargs: Any
) -> dict[str, Any]:

    verifications = []

    for item in research_results.get("results", [])[:5]:

        url = item.get("url", "")

        score, level = get_source_score(url)


        print(
            f"URL={url} | SCORE={score} | LEVEL={level}"
)

        verifications.append(
            {
                "claim": item.get(
                    "title",
                    "Unknown result"
                ),
                "source": url,
                "credibility_score": score,
                "credibility_level": level,
                "note": (
                    f"Source classified as "
                    f"{level} credibility."
                )
            }
        )

    avg_score = 0

    if verifications:

        avg_score = round(
            sum(
                v["credibility_score"]
                for v in verifications
            ) / len(verifications),
            2
        )

    return {
        "query": research_results.get(
            "query",
            ""
        ),
        "verifications": verifications,
        "average_credibility": avg_score,
        "summary": (
            f"Verified {len(verifications)} sources. "
            f"Average credibility score: {avg_score}%."
        )
    }

def conversation_execute(
    query: str,
    chat_history=None,
    **kwargs
):

    if not chat_history:
        return {
            "original_query": query,
            "resolved_query": query
        }

    history_text = ""

    for msg in chat_history[-6:]:
        history_text += (
            f"{msg['role']}: {msg['content']}\n"
        )

    prompt = f"""
You are a conversation context resolver.

Conversation History:
{history_text}

Current User Question:
{query}

Rewrite the current question into a standalone question.

Return ONLY the rewritten question.
"""

    rewritten_query = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    ).choices[0].message.content.strip()

    return {
        "original_query": query,
        "resolved_query": rewritten_query
    }


def planner_execute(query: str, **kwargs):

    query_lower = query.lower()

    tasks = ["research", "verify", "summarize"]

    if "latest" in query_lower:
        tasks.insert(0, "find_recent_information")

    if "compare" in query_lower:
        tasks.append("comparison_analysis")

    return {
        "query": query,
        "tasks": tasks
    }

# ==========================
# Memory Retrieval Agent
# ==========================

# ==========================
# Writer Agent
# ==========================
def writer_execute(
    research_results: dict[str, Any],
    fact_check: dict[str, Any],
    **kwargs: Any
) -> dict[str, Any]:

    results = research_results.get("results", [])
    query = research_results.get("query", "")

    references = []
    source_text = ""

    credibility_text = ""

    for verification in fact_check.get(
        "verifications",
        []
    ):

        credibility_text += (
            f"\nSource: {verification.get('claim')}"
            f"\nCredibility Score: {verification.get('credibility_score')}"
            f"\nCredibility Level: {verification.get('credibility_level')}\n"
        )

    for idx, item in enumerate(results, start=1):

        title = item.get("title", "")
        snippet = item.get("snippet", "")
        url = item.get("url", "")

        source_text += f"""
Source {idx}

Title:
{title}

Snippet:
{snippet}

URL:
{url}

"""

        references.append(
            {
                "title": title,
                "url": url
            }
        )

    avg_credibility = fact_check.get(
        "average_credibility",
        0
    )

    prompt = f"""
You are a senior research analyst.

Research Topic:
{query}

Verified Sources:
{source_text}

Fact Checker Assessment:
{credibility_text}

Average Credibility Score:
{avg_credibility}

IMPORTANT:

- Prioritize sources with credibility scores above 85.
- Use lower credibility sources only as supporting evidence.
- If sources disagree, trust higher credibility sources.
- Do not simply summarize articles.
- Synthesize information from all sources.

Generate a professional research report using the following structure:

# Executive Summary

Provide a concise overview.

# Key Insights

Identify the most important findings.

# Applications / Use Cases

Describe practical and real-world applications.

# Challenges and Risks

Discuss limitations, concerns, and barriers.

# Research Gaps

Identify missing knowledge, unanswered questions,
or areas requiring further investigation.

# Recommendations for Hospitals / Organizations

Provide implementation recommendations.

# Recommendations for Researchers

Suggest future research directions.

# Recommendations for Policymakers

Provide governance and regulatory suggestions.

# Source Reliability Assessment

Discuss which sources were most reliable and why.

Mention the average credibility score.

# Conclusion

Summarize the overall findings.

Requirements:

- Professional report style.
- Use markdown formatting.
- Be analytical, not descriptive.
- Mention evidence quality.
- Explain trade-offs where relevant.
"""

    try:

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        report_text = (
            response
            .choices[0]
            .message
            .content
        )

    except Exception as e:

        report_text = f"""
# Report Generation Failed

Error:
{str(e)}

Please verify:
- GROQ_API_KEY is configured
- Internet connection is available
- Groq service is reachable
"""

    report_quality = {
        "sources_used": len(results),
        "average_credibility": avg_credibility,
        "research_depth": (
            "High"
            if len(results) >= 5
            else "Medium"
        )
    }

    references_markdown = "\n".join(
        [
            f"- [{ref['title']}]({ref['url']})"
            for ref in references
        ]
    )

    report_text += f"""

# References

{references_markdown}
"""

    return {
        "executive_summary": report_text[:500],
        "references": references,
        "fact_check_summary": fact_check.get(
            "summary",
            ""
        ),
        "report_quality": report_quality,
        "report": report_text
    }


def writer_execute_stream(
    research_results: dict[str, Any],
    fact_check: dict[str, Any],
    **kwargs: Any
):

    results = research_results.get("results", [])
    query = research_results.get("query", "")

    references = []
    source_text = ""
    credibility_text = ""

    for verification in fact_check.get(
        "verifications",
        []
    ):

        credibility_text += (
            f"\nSource: {verification.get('claim')}"
            f"\nCredibility Score: {verification.get('credibility_score')}"
            f"\nCredibility Level: {verification.get('credibility_level')}\n"
        )

    for idx, item in enumerate(results, start=1):

        title = item.get("title", "")
        snippet = item.get("snippet", "")
        url = item.get("url", "")

        source_text += f"""
Source {idx}

Title:
{title}

Snippet:
{snippet}

URL:
{url}

"""

        references.append(
            {
                "title": title,
                "url": url
            }
        )

    avg_credibility = fact_check.get(
        "average_credibility",
        0
    )

    prompt = f"""
You are a senior research analyst.

Research Topic:
{query}

Verified Sources:
{source_text}

Fact Checker Assessment:
{credibility_text}

Average Credibility Score:
{avg_credibility}

IMPORTANT:

- Prioritize sources with credibility scores above 85.
- Use lower credibility sources only as supporting evidence.
- If sources disagree, trust higher credibility sources.
- Do not simply summarize articles.
- Synthesize information from all sources.

Generate a professional research report using the following structure:

# Executive Summary

Provide a concise overview.

# Key Insights

Identify the most important findings.

# Applications / Use Cases

Describe practical and real-world applications.

# Challenges and Risks

Discuss limitations, concerns, and barriers.

# Research Gaps

Identify missing knowledge, unanswered questions,
or areas requiring further investigation.

# Recommendations for Hospitals / Organizations

Provide implementation recommendations.

# Recommendations for Researchers

Suggest future research directions.

# Recommendations for Policymakers

Provide governance and regulatory suggestions.

# Source Reliability Assessment

Discuss which sources were most reliable and why.

Mention the average credibility score.

# Conclusion

Summarize the overall findings.

Requirements:

- Professional report style.
- Use markdown formatting.
- Be analytical, not descriptive.
- Mention evidence quality.
- Explain trade-offs where relevant.
"""

    report_text = ""

    try:

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            stream=True
        )

        for chunk in response:

            token = (
                chunk
                .choices[0]
                .delta
                .content
            )

            if token:
                report_text += token
                yield {
                    "type": "token",
                    "content": token
                }

    except Exception as e:

        report_text = f"""
# Report Generation Failed

Error:
{str(e)}

Please verify:
- GROQ_API_KEY is configured
- Internet connection is available
- Groq service is reachable
"""

        yield {
            "type": "token",
            "content": report_text
        }

    references_markdown = "\n".join(
        [
            f"- [{ref['title']}]({ref['url']})"
            for ref in references
        ]
    )

    references_section = f"""

# References

{references_markdown}
"""

    report_text += references_section

    yield {
        "type": "token",
        "content": references_section
    }

    report_quality = {
        "sources_used": len(results),
        "average_credibility": avg_credibility,
        "research_depth": (
            "High"
            if len(results) >= 5
            else "Medium"
        )
    }

    yield {
        "type": "writer_result",
        "data": {
            "executive_summary": report_text[:500],
            "references": references,
            "fact_check_summary": fact_check.get(
                "summary",
                ""
            ),
            "report_quality": report_quality,
            "report": report_text
        }
    }

# ==========================
# Memory Agent
# ==========================
def memory_execute(
    query: str,
    research_results: dict[str, Any],
    summary: dict[str, Any],
    user_id: str | None = None,
    **kwargs: Any
) -> dict[str, Any]:

    memory_item = {
    "id": str(uuid.uuid4()),

    "user_id": user_id,

    "title": f"Research memory for: {query}",

    "content": summary.get(
        "report",
        ""
    ),

    "created_at": datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    ),

    "tags": [
        "research",
        "agent_workflow"
    ]
}
    
    memory_store.add_memory(
        memory_item
    )

    return {
        "stored": True,
        "memory_id": memory_item["id"],
        "title": memory_item["title"]
    }

def memory_retrieval_execute(
    query: str,
    user_id: str | None = None,
    **kwargs: Any
) -> dict[str, Any]:

    memories = (
        memory_store.list_memory_for_user(user_id)
        if user_id
        else []
    )

    return {
        "query": query,
        "related_memories": memories[-5:]
    }

def is_greeting_query(query: str) -> bool:

    normalized_query = query.strip().lower()

    greetings = {
        "hi",
        "hello",
        "hey",
        "greet",
        "greetings",
        "good morning",
        "good afternoon",
        "good evening"
    }

    return normalized_query in greetings


def greeting_response(query: str) -> dict[str, Any]:

    message = (
        "Hello! I am your research assistant. "
        "You can enter any topic, question, or comparison you want information on, "
        "and I will research sources, check credibility, and generate a structured report."
    )

    return {
        "query": query,
        "workflow": [
            "GreetingAgent"
        ],
        "conversation": {
            "original_query": query,
            "resolved_query": query
        },
        "memory_context": {
            "query": query,
            "related_memories": []
        },
        "plan": {
            "query": query,
            "tasks": [
                "greet_user"
            ]
        },
        "research": {
            "query": query,
            "search_query": "",
            "results": [],
            "highlights": []
        },
        "fact_check": {
            "query": query,
            "verifications": [],
            "average_credibility": 0,
            "summary": "No fact check needed for a greeting."
        },
        "report": {
            "executive_summary": message,
            "references": [],
            "fact_check_summary": "No fact check needed for a greeting.",
            "report_quality": {
                "sources_used": 0,
                "average_credibility": 0,
                "research_depth": "Not applicable"
            },
            "report": message
        },
        "memory": {
            "stored": False,
            "reason": "Greeting messages are not stored as research memory."
        }
    }


def manager_execute_stream(
    query: str,
    limit: int = 5,
    **kwargs: Any
):

    if is_greeting_query(query):

        response = greeting_response(query)

        yield {
            "type": "status",
            "agent": "GreetingAgent",
            "message": "Greeting detected."
        }
        yield {
            "type": "token",
            "content": response["report"]["report"]
        }
        yield {
            "type": "done",
            "data": response
        }
        return

    yield {
        "type": "status",
        "agent": "ConversationAgent",
        "message": "Resolving conversation context."
    }
    conversation_output = conversation_agent.execute(
        query=query,
        chat_history=kwargs.get("chat_history", [])
    )

    yield {
        "type": "status",
        "agent": "MemoryRetrievalAgent",
        "message": "Retrieving related memories."
    }
    memory_context = memory_retrieval_agent.execute(
        query=query,
        user_id=kwargs.get("user_id")
    )

    resolved_query = conversation_output["resolved_query"]

    yield {
        "type": "status",
        "agent": "PlannerAgent",
        "message": "Creating research plan."
    }
    plan_output = planner_agent.execute(
        query=query
    )

    yield {
        "type": "status",
        "agent": "ResearchAgent",
        "message": "Searching for sources."
    }
    research_output = research_agent.execute(
        query=resolved_query,
        plan=plan_output,
        limit=limit
    )

    yield {
        "type": "status",
        "agent": "FactCheckerAgent",
        "message": "Checking source credibility."
    }
    fact_check_output = fact_checker_agent.execute(
        research_results=research_output
    )

    yield {
        "type": "status",
        "agent": "WriterAgent",
        "message": "Writing the research report."
    }

    writer_output = {}

    for event in writer_execute_stream(
        research_results=research_output,
        fact_check=fact_check_output,
        memory_context=memory_context
    ):

        if event.get("type") == "writer_result":
            writer_output = event["data"]
            continue

        yield event

    yield {
        "type": "status",
        "agent": "MemoryAgent",
        "message": "Saving research memory."
    }
    memory_output = memory_agent.execute(
        query=query,
        research_results=research_output,
        summary=writer_output,
        user_id=kwargs.get("user_id"),
        average_credibility=fact_check_output.get(
            "average_credibility",
            0
        )
    )

    yield {
        "type": "done",
        "data": {
            "query": query,
            "workflow": [
                "ConversationAgent",
                "MemoryRetrievalAgent",
                "PlannerAgent",
                "ResearchAgent",
                "FactCheckerAgent",
                "WriterAgent",
                "MemoryAgent"
            ],
            "conversation": conversation_output,
            "memory_context": memory_context,
            "plan": plan_output,
            "research": research_output,
            "fact_check": fact_check_output,
            "report": writer_output,
            "memory": memory_output
        }
    }

# ==========================
# Manager Agent
# ==========================
def manager_execute(
    query: str,
    limit: int = 5,
    **kwargs: Any
) -> dict[str, Any]:
    
    print("KWARGS =", kwargs)

    if is_greeting_query(query):
        return greeting_response(query)
    
    conversation_output = conversation_agent.execute(
    query=query,
    chat_history=kwargs.get("chat_history", [])
)
    
    memory_context = memory_retrieval_agent.execute(
    query=query,
    user_id=kwargs.get("user_id")
)
    resolved_query = conversation_output["resolved_query"]

    
    plan_output = planner_agent.execute(
    query=query
)

    research_output = research_agent.execute(
    query=resolved_query,
    plan=plan_output,
    limit=limit
)

    fact_check_output = (
        fact_checker_agent.execute(
            research_results=research_output
        )
    )

    writer_output = writer_agent.execute(
    research_results=research_output,
    fact_check=fact_check_output,
    memory_context=memory_context
)

    memory_output = (
    memory_agent.execute(
        query=query,
        research_results=research_output,
        summary=writer_output,
        user_id=kwargs.get("user_id"),
        average_credibility=
        fact_check_output.get(
            "average_credibility",
            0
        )
    )
)

    return {
    "query": query,

    "workflow": [
        "ConversationAgent",
        "MemoryRetrievalAgent",
        "PlannerAgent",
        "ResearchAgent",
        "FactCheckerAgent",
        "WriterAgent",
        "MemoryAgent"
    ],

    "conversation": conversation_output,

    "memory_context": memory_context,


    "plan": plan_output,

    "research": research_output,

    "fact_check": fact_check_output,

    "report": writer_output,

    "memory": memory_output
}

# ==========================
# Agent Definitions
# ==========================
manager_agent = create_agent(
    name="ManagerAgent",
    role="Manager",
    description=(
        "Coordinate the research workflow."
    ),
    execute=manager_execute,
    tools=["workflow_planner"]
)

conversation_agent = create_agent(
    name="ConversationAgent",
    role="Conversation Manager",
    description="Maintain conversational context.",
    execute=conversation_execute,
    tools=["conversation_memory"]
)

planner_agent = create_agent(
    name="PlannerAgent",
    role="Planner",
    description="Analyze user query and create a research plan.",
    execute=planner_execute,
    tools=["task_planner"]
)
memory_retrieval_agent = create_agent(
    name="MemoryRetrievalAgent",
    role="Memory Retriever",
    description="Retrieve previous research memories.",
    execute=memory_retrieval_execute,
    tools=["memory_search"]
)

research_agent = create_agent(
    name="ResearchAgent",
    role="Research Specialist",
    description=(
        "Search and gather information."
    ),
    execute=research_execute,
    tools=["serper_search"]
)

fact_checker_agent = create_agent(
    name="FactCheckerAgent",
    role="Fact Checker",
    description=(
        "Validate information quality."
    ),
    execute=fact_checker_execute,
    tools=["verification_engine"]
)

writer_agent = create_agent(
    name="WriterAgent",
    role="Writer",
    description=(
        "Generate reports and summaries."
    ),
    execute=writer_execute,
    tools=["summary_generator"]
)

memory_agent = create_agent(
    name="MemoryAgent",
    role="Memory Manager",
    description=(
        "Store research history."
    ),
    execute=memory_execute,
    tools=["memory_store"]
)


# ==========================
# Crew
# ==========================
agent_crew = ResearchBasedAgent(
    name="CrewAI Agents",
   agents=[
    manager_agent,
    conversation_agent,
    planner_agent,
    memory_retrieval_agent,
    research_agent,
    fact_checker_agent,
    writer_agent,
    memory_agent
]
)


# ==========================
# Registry
# ==========================
registry.register(manager_agent)
registry.register(planner_agent)
registry.register(conversation_agent)
registry.register(memory_retrieval_agent)
registry.register(research_agent)
registry.register(fact_checker_agent)
registry.register(writer_agent)
registry.register(memory_agent)


if __name__ == "__main__":
    print(agent_crew)
