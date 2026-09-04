from datetime import datetime, timezone

from app.database.connection import DatabaseConnection


class ProjectRepository:

    def __init__(
        self,
        database: DatabaseConnection,
    ):
        self.database = database

        self._create_table()
        self._ensure_connected_column()

    def _create_table(self):
        with self.database.get_connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    repository_path TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    connected INTEGER NOT NULL DEFAULT 1
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
                    updated_at,
                    connected
                )
                VALUES (?, ?, ?, ?, ?, 1)
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

    def disconnect(
        self,
        project_id: str,
    ):
        with self.database.get_connection() as connection:
            connection.execute(
                """
                UPDATE projects
                SET connected = 0,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    datetime.now(
                        timezone.utc
                    ).isoformat(),
                    project_id,
                ),
            )

            connection.commit()

    def reconnect(
        self,
        project_id: str,
    ):
        with self.database.get_connection() as connection:
            connection.execute(
                """
                UPDATE projects
                SET connected = 1,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    datetime.now(
                        timezone.utc
                    ).isoformat(),
                    project_id,
                ),
            )

            connection.commit()

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

    def _ensure_connected_column(self) -> None:
        with self.database.get_connection() as connection:
            columns = connection.execute(
                "PRAGMA table_info(projects)"
            ).fetchall()

            column_names = {
                column[1]
                for column in columns
            }

            if "connected" not in column_names:
                connection.execute(
                    """
                    ALTER TABLE projects
                    ADD COLUMN connected
                    INTEGER NOT NULL DEFAULT 1
                    """
                )

                connection.commit()

    def disconnect(
        self,
        project_id: str,
    ):
        with self.database.get_connection() as connection:
            connection.execute(
                """
                UPDATE projects
                SET connected = 0
                WHERE id = ?
                """,
                (project_id,),
            )

            connection.commit()


    def reconnect(
        self,
        project_id: str,
    ):
        with self.database.get_connection() as connection:
            connection.execute(
                """
                UPDATE projects
                SET connected = 1
                WHERE id = ?
                """,
                (project_id,),
            )

            connection.commit()