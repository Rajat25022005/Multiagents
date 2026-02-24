"""
Planner Agent – breaks a task into structured subtasks using Instructor + Pydantic.
Falls back to JSON parsing if Instructor isn't available.
"""
from __future__ import annotations

import json
import re

from pydantic import BaseModel, Field

from core.llm_router import LLMRouter


class SubTask(BaseModel):
    task_id: str = Field(description="Short unique ID like 'step_1'")
    description: str = Field(description="What to do in this subtask")
    agent_type: str = Field(
        default="executor",
        description="Which agent: executor | react | code | search | summarizer",
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="task_ids that must complete before this one",
    )
    priority: int = Field(default=1, description="1=high, 2=medium, 3=low")


class Plan(BaseModel):
    objective: str = Field(description="One-sentence restatement of the goal")
    subtasks: list[SubTask]
    estimated_complexity: str = Field(
        default="medium",
        description="simple | medium | complex",
    )


PLANNER_SYSTEM = """You are a master planning agent. Given a task, decompose it into 2-6 concrete subtasks.

Rules:
- Each subtask must be actionable and specific
- Identify dependencies between subtasks (no circular deps)
- Choose the right agent_type for each step:
  • executor   – general reasoning / writing
  • react      – tasks needing tool use (web search, run code, read files)
  • code       – generate and run Python/JS code
  • search     – web research and summarization
  • summarizer – aggregate and synthesize results

Respond ONLY with valid JSON matching the Plan schema. No prose."""


class PlannerAgent:
    def __init__(self, router: LLMRouter):
        self.router = router

    def create_plan(self, task: str, context: str = "") -> Plan:
        prompt = task
        if context:
            prompt = f"Context from memory:\n{context}\n\nTask: {task}"

        # Try Instructor for guaranteed structured output
        try:
            import instructor
            from openai import OpenAI
            from core.config import get_settings
            settings = get_settings()
            if settings.llm_provider == "openai" and settings.openai_api_key:
                client = instructor.from_openai(OpenAI(api_key=settings.openai_api_key))
                return client.chat.completions.create(
                    model=self.router.model,
                    response_model=Plan,
                    messages=[
                        {"role": "system", "content": PLANNER_SYSTEM},
                        {"role": "user", "content": prompt},
                    ],
                )
        except Exception:
            pass

        # Fallback: parse JSON from LLM response
        response = self.router.chat(
            messages=[{"role": "user", "content": prompt}],
            system=PLANNER_SYSTEM,
            temperature=0.2,
            trace_name="planner",
        )
        return self._parse_plan(response.content, task)

    def _parse_plan(self, raw: str, fallback_task: str) -> Plan:
        # Strip markdown fences
        cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("```").strip()
        try:
            data = json.loads(cleaned)
            return Plan(**data)
        except Exception:
            # Last resort: single-step plan
            return Plan(
                objective=fallback_task,
                subtasks=[
                    SubTask(
                        task_id="step_1",
                        description=fallback_task,
                        agent_type="executor",
                    )
                ],
                estimated_complexity="simple",
            )
