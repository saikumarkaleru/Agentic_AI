
# ------------------------------
# SERVER SIDE (MCP Server)
# ------------------------------

import sqlite3
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sqlite-demo")
# Create database/table once

def init_db():
    conn = sqlite3.connect("demo.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            profession TEXT
        )
        """
    )

    conn.commit()
    conn.close()


@mcp.tool()
def add_data(name: str, age: int, profession: str) -> bool:
    """Add a person record into SQLite."""

    conn = sqlite3.connect("demo.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO people (name, age, profession)
        VALUES (?, ?, ?)
        """,
        (name, age, profession),
    )

    conn.commit()
    conn.close()

    return True


@mcp.tool()
def read_data() -> list:
    """Fetch all people records from SQLite."""

    conn = sqlite3.connect("demo.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, age, profession FROM people")
    results = cursor.fetchall()

    conn.close()

    return results


if __name__ == "__main__":
    init_db()
    print("Starting MCP server...")
    print("Run this file as the MCP server process.")
    mcp.run(transport="sse")
    # Example:
    # python server.py
    # or transport depending on FastMCP setup

