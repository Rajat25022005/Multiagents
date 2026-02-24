"""
Neo4j graph memory: stores entities, relationships, and task context.
"""
from __future__ import annotations

import contextlib
from typing import Any

from neo4j import GraphDatabase, exceptions

from core.config import get_settings

settings = get_settings()


class Neo4jClient:
    _instance: Neo4jClient | None = None

    def __init__(self):
        self._driver = None

    @classmethod
    def get(cls) -> Neo4jClient:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def connect(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )

    def close(self):
        if self._driver:
            self._driver.close()
            self._driver = None

    @contextlib.contextmanager
    def session(self):
        self.connect()
        with self._driver.session() as s:
            yield s

    # ──────────────────────────────────────────────────────────────────────────

    def store_task(self, task_id: str, description: str, user_id: int):
        with self.session() as s:
            s.run(
                "MERGE (t:Task {id: $id}) "
                "SET t.description = $desc, t.user_id = $uid, t.created_at = timestamp()",
                id=task_id, desc=description, uid=user_id,
            )

    def store_result(self, task_id: str, result_summary: str):
        with self.session() as s:
            s.run(
                "MERGE (t:Task {id: $id}) "
                "SET t.result = $result, t.completed_at = timestamp()",
                id=task_id, result=result_summary,
            )

    def link_entities(self, task_id: str, entities: list[dict]):
        """Link named entities extracted from a task result to the task node."""
        with self.session() as s:
            for entity in entities:
                s.run(
                    "MERGE (e:Entity {name: $name, type: $type}) "
                    "WITH e "
                    "MATCH (t:Task {id: $tid}) "
                    "MERGE (t)-[:MENTIONS]->(e)",
                    name=entity.get("name", ""),
                    type=entity.get("type", "unknown"),
                    tid=task_id,
                )

    def get_related_tasks(self, task_description: str, limit: int = 5) -> list[dict]:
        """Full-text search for related past tasks (requires neo4j APOC)."""
        with self.session() as s:
            try:
                result = s.run(
                    "CALL apoc.index.search('Task', $query) YIELD node, weight "
                    "RETURN node.id AS id, node.description AS description, "
                    "node.result AS result, weight "
                    "ORDER BY weight DESC LIMIT $limit",
                    query=task_description, limit=limit,
                )
                return [dict(r) for r in result]
            except exceptions.ClientError:
                # APOC not available – fallback
                return []

    def get_entity_graph(self, entity_name: str) -> list[dict]:
        with self.session() as s:
            result = s.run(
                "MATCH (e:Entity {name: $name})<-[:MENTIONS]-(t:Task) "
                "RETURN t.id AS task_id, t.description AS description LIMIT 10",
                name=entity_name,
            )
            return [dict(r) for r in result]
