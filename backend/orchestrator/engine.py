"""
Orchestrator Engine – coordinates planning, parallel execution, and finalization.
Supports both async streaming (SSE) and sync batch execution (Celery).
"""
from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import AsyncGenerator, Callable

from agents.executor import CodeAgent, ExecutorAgent, FinalizerAgent
from agents.planner import Plan, PlannerAgent, SubTask
from agents.react_agent import ReActAgent
from agents.vector_memory import VectorMemory
from core.llm_router import LLMRouter
from core.neo4j_client import Neo4jClient


class OrchestratorEngine:
    def __init__(self, provider: str | None = None, model: str | None = None):
        self.router = LLMRouter(provider=provider, model=model)
        self.planner = PlannerAgent(self.router)
        self.executor = ExecutorAgent(self.router)
        self.finalizer = FinalizerAgent(self.router)
        self.memory = VectorMemory.get()
        self.neo4j = Neo4jClient.get()

    # ──────────────────────────────────────────────────────────────────────────
    # Async streaming (SSE endpoint)
    # ──────────────────────────────────────────────────────────────────────────

    async def execute_streaming(
        self,
        task: str,
        task_db_id: int,
        user_id: int,
    ) -> AsyncGenerator[dict, None]:
        yield {"stage": "memory", "message": "🔍 Searching memory for similar tasks..."}

        # Memory context
        similar = self.memory.search_similar(task, n_results=3, user_id=user_id)
        context = ""
        if similar:
            context = "Similar past tasks:\n" + "\n".join(
                f"- {s['content'][:200]}" for s in similar
            )
            yield {"stage": "memory", "found": len(similar), "context_preview": context[:300]}

        yield {"stage": "planning", "message": "🧠 Planning your task..."}

        # Plan
        plan = await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.planner.create_plan(task, context)
        )
        yield {
            "stage": "plan",
            "objective": plan.objective,
            "complexity": plan.estimated_complexity,
            "subtasks": [
                {"id": s.task_id, "description": s.description, "agent": s.agent_type}
                for s in plan.subtasks
            ],
        }

        # Neo4j store
        try:
            self.neo4j.store_task(str(task_db_id), task, user_id)
        except Exception:
            pass

        # Execute subtasks with dependency resolution
        results: dict[str, str] = {}
        files_created: list[str] = []
        remaining = list(plan.subtasks)

        with ThreadPoolExecutor(max_workers=4) as pool:
            while remaining:
                # Find ready subtasks (dependencies satisfied)
                ready = [t for t in remaining if all(dep in results for dep in t.dependencies)]
                if not ready:
                    yield {"stage": "error", "message": "Circular dependency detected"}
                    break

                # Emit "starting" events
                for subtask in ready:
                    yield {
                        "stage": "executing",
                        "task_id": subtask.task_id,
                        "description": subtask.description,
                        "agent": subtask.agent_type,
                    }

                # Execute ready tasks in parallel
                futures = {
                    pool.submit(self._execute_subtask, subtask, results, files_created): subtask
                    for subtask in ready
                }
                for future in as_completed(futures):
                    subtask = futures[future]
                    try:
                        result = future.result()
                        results[subtask.task_id] = result
                        yield {
                            "stage": "result",
                            "task_id": subtask.task_id,
                            "output": result[:500] + ("..." if len(result) > 500 else ""),
                        }
                    except Exception as e:
                        results[subtask.task_id] = f"Error: {e}"
                        yield {"stage": "error", "task_id": subtask.task_id, "error": str(e)}

                remaining = [t for t in remaining if t.task_id not in results]

        # Finalize
        yield {"stage": "finalizing", "message": "✍️ Synthesizing results..."}
        final = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.finalizer.finalize(task, results, files_created),
        )

        # Store in memory
        try:
            self.memory.store_task_result(task, final[:800], task_db_id, user_id, files_created)
            self.neo4j.store_result(str(task_db_id), final[:500])
        except Exception:
            pass

        yield {
            "stage": "done",
            "message": "✅ Task complete",
            "result": final,
            "files": files_created,
            "subtask_results": results,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Sync batch execution (Celery)
    # ──────────────────────────────────────────────────────────────────────────

    async def execute(
        self,
        task: str,
        user_id: int,
        task_db_id: int = 0,
        on_stage: Callable | None = None,
    ) -> dict:
        def _stage(s):
            if on_stage:
                try:
                    on_stage(s)
                except Exception:
                    pass

        _stage("planning")
        similar = self.memory.search_similar(task, n_results=3, user_id=user_id)
        context = "\n".join(s["content"][:200] for s in similar) if similar else ""
        plan = self.planner.create_plan(task, context)

        try:
            self.neo4j.store_task(str(task_db_id), task, user_id)
        except Exception:
            pass

        _stage("executing")
        results: dict[str, str] = {}
        files_created: list[str] = []
        remaining = list(plan.subtasks)

        with ThreadPoolExecutor(max_workers=4) as pool:
            while remaining:
                ready = [t for t in remaining if all(dep in results for dep in t.dependencies)]
                if not ready:
                    break
                futures = {
                    pool.submit(self._execute_subtask, t, results, files_created): t
                    for t in ready
                }
                for future in as_completed(futures):
                    subtask = futures[future]
                    try:
                        results[subtask.task_id] = future.result()
                    except Exception as e:
                        results[subtask.task_id] = f"Error: {e}"
                remaining = [t for t in remaining if t.task_id not in results]

        _stage("finalizing")
        final = self.finalizer.finalize(task, results, files_created)

        try:
            self.memory.store_task_result(task, final[:800], task_db_id, user_id, files_created)
            self.neo4j.store_result(str(task_db_id), final[:500])
        except Exception:
            pass

        return {
            "result": final,
            "files": files_created,
            "plan": plan.objective,
            "subtask_results": results,
        }

    # ──────────────────────────────────────────────────────────────────────────

    def _execute_subtask(
        self, subtask: SubTask, context_results: dict, files_created: list
    ) -> str:
        context = ""
        if subtask.dependencies:
            context = "Results from previous steps:\n" + "\n".join(
                f"[{dep}]: {context_results.get(dep, 'pending')[:400]}"
                for dep in subtask.dependencies
            )

        agent_type = subtask.agent_type

        if agent_type == "react":
            agent = ReActAgent(router=self.router)
            return agent.run(subtask.description)

        elif agent_type == "code":
            agent = CodeAgent(router=self.router)
            result = agent.generate_and_run(subtask.description)
            if result["success"]:
                return f"Code executed successfully.\nOutput:\n{result['execution']['stdout']}\n\nCode:\n```python\n{result['code']}\n```"
            else:
                return f"Code generated (execution failed):\n```python\n{result['code']}\n```\nError: {result['execution']['stderr']}"

        elif agent_type == "search":
            from actions.web_scraper import WebScraper
            scraper = WebScraper()
            search_results = scraper.search(subtask.description)
            # Summarize search results
            response = self.router.chat(
                messages=[{"role": "user", "content": f"Summarize these search results for: {subtask.description}\n\n{search_results}"}],
                temperature=0.3,
                trace_name="search_summarizer",
            )
            return response.content

        else:
            # Default: executor
            return self.executor.execute(subtask.description, context)
