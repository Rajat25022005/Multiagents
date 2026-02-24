"""
ReAct Agent – Reason + Act loop with tool use.
Agents think, call tools, observe results, and iterate until done.
"""
from __future__ import annotations

import os
from typing import Callable

from core.llm_router import LLMRouter

REACT_SYSTEM = """You are an autonomous ReAct agent. You reason step by step and use tools to complete tasks.

Format your responses EXACTLY as:
THINK: <your reasoning about what to do next>
ACTION: <tool_name>
INPUT: <tool input, either plain text or JSON>

When you have enough information to answer, output:
THINK: <final reasoning>
FINAL: <your complete answer>

Available tools:
- search_web(query)       – search the internet
- read_file(path)         – read a file from disk
- write_file(path, content) – write content to a file (JSON input: {"path": "...", "content": "..."})
- run_python(code)        – execute Python code in sandbox
- list_files(directory)   – list files in a directory
- http_get(url)           – fetch a URL and return its content

Important:
- Always verify information with tools before making claims
- If a tool fails, try an alternative approach
- Keep answers concise and factual
- You have a maximum of {max_steps} steps"""


class ReActAgent:
    def __init__(
        self,
        router: LLMRouter,
        max_steps: int = 12,
        on_step: Callable | None = None,
    ):
        self.router = router
        self.max_steps = max_steps
        self.on_step = on_step  # callback(step_num, think, action, observation)
        self._tools = self._build_tools()

    def _build_tools(self) -> dict[str, Callable]:
        from actions.code_executor import SandboxExecutor
        from actions.web_scraper import WebScraper

        sandbox = SandboxExecutor()
        scraper = WebScraper()

        def _write_file(inp: str):
            import json as _json
            try:
                data = _json.loads(inp)
                path, content = data["path"], data["content"]
            except Exception:
                return "Error: write_file needs JSON input: {\"path\": \"...\", \"content\": \"...\"}"
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return f"Written {len(content)} chars to {path}"

        return {
            "search_web": lambda q: scraper.search(q),
            "read_file": lambda p: open(p).read() if os.path.exists(p) else "File not found",
            "write_file": _write_file,
            "run_python": lambda code: str(sandbox.run_python(code)),
            "list_files": lambda d: str(os.listdir(d)) if os.path.exists(d) else "Directory not found",
            "http_get": lambda url: scraper.fetch(url),
        }

    def run(self, task: str) -> str:
        system = REACT_SYSTEM.format(max_steps=self.max_steps)
        messages = [{"role": "user", "content": task}]

        for step in range(self.max_steps):
            response = self.router.chat(
                messages=messages,
                system=system,
                temperature=0.3,
                trace_name=f"react_step_{step}",
            )
            content = response.content
            messages.append({"role": "assistant", "content": content})

            # Check for FINAL answer
            if "FINAL:" in content:
                return content.split("FINAL:", 1)[-1].strip()

            # Parse and execute action
            if "ACTION:" in content:
                try:
                    action_line = content.split("ACTION:", 1)[-1].split("\n")[0].strip()
                    input_line = content.split("INPUT:", 1)[-1].split("\n")[0].strip() if "INPUT:" in content else ""

                    tool_fn = self._tools.get(action_line)
                    if tool_fn:
                        try:
                            observation = str(tool_fn(input_line))[:2000]  # cap length
                        except Exception as e:
                            observation = f"Tool error: {e}"
                    else:
                        observation = f"Unknown tool '{action_line}'. Available: {list(self._tools.keys())}"

                    think = content.split("THINK:", 1)[-1].split("ACTION:")[0].strip() if "THINK:" in content else ""
                    if self.on_step:
                        self.on_step(step, think, action_line, observation)

                    messages.append({"role": "user", "content": f"OBSERVATION: {observation}"})
                except Exception as e:
                    messages.append({"role": "user", "content": f"OBSERVATION: Error parsing action: {e}"})
            else:
                # No action, treat full response as final
                return content

        return "Maximum steps reached without completing task."
