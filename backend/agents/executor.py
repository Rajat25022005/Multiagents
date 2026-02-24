"""
Executor Agent – handles general subtask execution.
Finalizer Agent – synthesizes all results into a coherent final answer.
"""
from __future__ import annotations

from core.llm_router import LLMRouter

EXECUTOR_SYSTEM = """You are an expert AI executor. You complete specific subtasks precisely and thoroughly.
- Provide detailed, accurate outputs
- If writing code, include working, complete implementations
- If analyzing, be thorough and structured
- Format output clearly with markdown when helpful"""

FINALIZER_SYSTEM = """You are a synthesis expert. Given a task and multiple subtask results, produce a 
comprehensive final answer that:
1. Addresses the original task completely
2. Integrates all relevant subtask results coherently  
3. Highlights key findings and actionable insights
4. Uses clear markdown formatting with headers, lists, code blocks where appropriate
5. Includes any generated files or code at the end"""

CODE_SYSTEM = """You are an expert programmer. Generate complete, working, production-quality code.
Always:
- Write complete files, not snippets
- Include error handling
- Add clear comments
- Follow best practices for the language
- Return ONLY the code, no prose explanation"""


class ExecutorAgent:
    def __init__(self, router: LLMRouter):
        self.router = router

    def execute(self, subtask: str, context: str = "") -> str:
        messages = [{"role": "user", "content": subtask}]
        if context:
            messages = [
                {"role": "user", "content": f"Context:\n{context}\n\nTask: {subtask}"}
            ]
        response = self.router.chat(
            messages=messages,
            system=EXECUTOR_SYSTEM,
            temperature=0.5,
            trace_name="executor",
        )
        return response.content


class CodeAgent:
    def __init__(self, router: LLMRouter):
        self.router = router

    def generate_and_run(self, task: str) -> dict:
        from actions.code_executor import SandboxExecutor

        # Generate code
        response = self.router.chat(
            messages=[{"role": "user", "content": f"Write Python code to: {task}"}],
            system=CODE_SYSTEM,
            temperature=0.2,
            trace_name="code_gen",
        )
        code = self._extract_code(response.content)

        # Run in sandbox
        sandbox = SandboxExecutor()
        execution_result = sandbox.run_python(code)

        return {
            "code": code,
            "execution": execution_result,
            "success": execution_result.get("exit_code", -1) == 0,
        }

    def _extract_code(self, text: str) -> str:
        import re
        # Try to find ```python ... ``` block
        match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()


class FinalizerAgent:
    def __init__(self, router: LLMRouter):
        self.router = router

    def finalize(
        self,
        original_task: str,
        subtask_results: dict[str, str],
        files_created: list[str] | None = None,
    ) -> str:
        results_text = "\n\n".join([
            f"### Subtask: {k}\n{v}" for k, v in subtask_results.items()
        ])
        files_text = f"\n\nFiles created: {', '.join(files_created)}" if files_created else ""

        prompt = (
            f"Original task: {original_task}\n\n"
            f"Subtask results:\n{results_text}"
            f"{files_text}\n\n"
            "Please synthesize these into a comprehensive final answer."
        )

        response = self.router.chat(
            messages=[{"role": "user", "content": prompt}],
            system=FINALIZER_SYSTEM,
            temperature=0.4,
            max_tokens=8192,
            trace_name="finalizer",
        )
        return response.content
