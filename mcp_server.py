import os
from typing import Any

import httpx
from mcp.server import MCPServer
from mcp.types import ToolAnnotations


SCHEMESETU_API_URL = "https://msme-scheme-backend.vercel.app/api/ask"


mcp = MCPServer(
    "SchemeSetu",
    description=(
        "Search verified Indian government scheme documents "
        "for MSMEs and startups."
    ),
)


@mcp.tool(
    title="Find government schemes",
    description=(
        "Find potentially relevant Indian government schemes "
        "for an MSME or startup. Returns a grounded answer, "
        "citations, document titles, pages and official sources."
    ),
    annotations=ToolAnnotations(
        read_only_hint=True,
        open_world_hint=False,
    ),
    structured_output=True,
)
async def find_government_schemes(
    question: str,
) -> dict[str, Any]:
    """
    Search SchemeSetu using a detailed business profile.

    Include the business type, age, sector, state and required
    support whenever possible.
    """

    question = question.strip()

    if len(question) < 3:
        return {
            "error": (
                "Please provide a more detailed business "
                "profile or scheme question."
            )
        }

    timeout = httpx.Timeout(
        connect=20.0,
        read=200.0,
        write=30.0,
        pool=20.0,
    )

    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
        ) as client:
            response = await client.post(
                SCHEMESETU_API_URL,
                headers={
                    "Content-Type": "application/json"
                },
                json={
                    "question": question
                },
            )

        response.raise_for_status()
        data = response.json()

        return {
            "answer": data.get("answer", ""),
            "sources": data.get("sources", []),
            "notice": (
                "This is a potential scheme match. Confirm "
                "final eligibility on the official source."
            ),
        }

    except httpx.TimeoutException:
        return {
            "error": (
                "SchemeSetu took too long to answer. "
                "Please try again."
            )
        }

    except httpx.HTTPStatusError as error:
        return {
            "error": "SchemeSetu returned an API error.",
            "status_code": error.response.status_code,
        }

    except Exception as error:
        return {
            "error": (
                "The SchemeSetu MCP tool could not complete "
                "the request."
            ),
            "details": str(error),
        }


@mcp.resource(
    "schemesetu://about",
    name="About SchemeSetu",
    description=(
        "Information about the SchemeSetu RAG prototype."
    ),
    mime_type="text/plain",
)
def about_schemesetu() -> str:
    """Describe the SchemeSetu service."""

    return """
SchemeSetu is an independent educational prototype for
discovering Indian government schemes for MSMEs and startups.

It uses:
- Gemini query embeddings
- Supabase pgvector semantic search
- Cosine similarity
- Gemini grounded answer generation
- Official-document citations

SchemeSetu does not guarantee eligibility. Users must verify
application details on the official government source.
""".strip()


if __name__ == "__main__":
    # Local MCP transport. The MCP host launches this script.
    mcp.run(transport="stdio")

