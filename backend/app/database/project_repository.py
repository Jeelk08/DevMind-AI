from datetime import datetime, timezone

from app.database.connection import DatabaseConnection


class ProjectRepository:

    def __init__(
        self,
        database: DatabaseConnection,
    ):
        self.database = database

        self._create_table()

    def _create_table(self):
        with self.database.get_connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    repository_path TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS
                idx_projects_repository_path
                ON projects(repository_path)
                """
            )

            connection.commit()

    def create(
        self,
        project_id: str,
        name: str,
        repository_path: str,
    ):
        now = datetime.now(
            timezone.utc
        ).isoformat()

        with self.database.get_connection() as connection:
            connection.execute(
                """
                INSERT INTO projects (
                    id,
                    name,
                    repository_path,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    name,
                    repository_path,
                    now,
                    now,
                ),
            )

            connection.commit()


    def get_by_repository_path(
        self,
        repository_path: str,
    ):
        with self.database.get_connection() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM projects
                WHERE repository_path = ?
                """,
                (repository_path,),
            ).fetchone()

            return row

            
    def get_by_id(
        self,
        project_id: str,
    ):
        with self.database.get_connection() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM projects
                WHERE id = ?
                """,
                (project_id,),
            ).fetchone()

            return row

    def get_all(self):
        with self.database.get_connection() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM projects
                ORDER BY created_at
                """
            ).fetchall()

            return rows

    def delete(
        self,
        project_id: str,
    ):
        with self.database.get_connection() as connection:
            connection.execute(
                """
                DELETE FROM projects
                WHERE id = ?
                """,
                (project_id,),
            )

            connection.commit()