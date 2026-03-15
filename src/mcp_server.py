"""
Lumi Diary — MCP Server

Wraps all Lumi tool functions as MCP tools, exposing them to any
MCP-compatible client (Claude Desktop, Cursor, VS Code Copilot, etc.).

Run with:
    fastmcp run src/mcp_server.py
    # or
    python -m src.mcp_server
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.handlers import (
    export_lumi_scroll,
    manage_event,
    manage_fragment,
    manage_identity,
    record_group_fragment,
    render_lumi_canvas,
    save_meme,
    update_circle_dictionary,
)

PERSONA_PATH = Path(__file__).resolve().parent.parent / "SKILL.md"

mcp = FastMCP(
    "Lumi Diary",
    instructions=(
        "You are Lumi, a local-first memory guardian and cyber bestie. "
        "Use the provided tools to record life fragments, manage events, "
        "render interactive memory scrolls, and more. All data stays in "
        "the user's local Lumi_Vault/ directory."
    ),
)


def _json_result(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Prompt: full Lumi persona (clients can attach this to conversations)
# ---------------------------------------------------------------------------

@mcp.prompt()
def lumi_persona() -> str:
    """Full Lumi persona and behavioral protocol. Attach this to activate Lumi's personality."""
    if PERSONA_PATH.exists():
        raw = PERSONA_PATH.read_text(encoding="utf-8")
        parts = raw.split("system_prompt: |", 1)
        if len(parts) > 1:
            prompt_section = parts[1].split("\ntools:", 1)[0]
            lines = prompt_section.split("\n")
            return "\n".join(line[2:] if line.startswith("  ") else line for line in lines)
    return "You are Lumi, a local-first memory guardian."


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def tool_record_fragment(
    sender_name: str,
    content: str,
    story_node_id: str,
    interaction_type: str,
    context_type: str = "solo",
    media_path: str | None = None,
    event_name: str | None = None,
    emotion_tag: str | None = None,
    group_id: str | None = None,
    sender_id: str | None = None,
) -> str:
    """Record a life fragment into the local vault.

    Routes to Solo/Circles/Events based on context_type.
    Supports media attachments, emotion tags, and Rashomon stitching.
    """
    return _json_result(record_group_fragment(
        sender_name, content, story_node_id, interaction_type,
        context_type=context_type, media_path=media_path,
        event_name=event_name, emotion_tag=emotion_tag,
        group_id=group_id, sender_id=sender_id,
    ))


@mcp.tool()
def tool_manage_identity(
    action: str,
    display_name: str | None = None,
    account_id: str | None = None,
    original_name: str | None = None,
) -> str:
    """Manage owner profile and contacts in the identity registry.

    Actions: init_owner, get_owner, rename, lookup, list_contacts.
    """
    return _json_result(manage_identity(
        action, display_name=display_name,
        account_id=account_id, original_name=original_name,
    ))


@mcp.tool()
def tool_manage_event(
    action: str,
    event_name: str,
    group_id: str | None = None,
) -> str:
    """Start, stop, or query an event scroll.

    Actions: start, stop, query.
    Use group_id for namespace isolation across different groups.
    """
    return _json_result(manage_event(
        action, event_name, group_id=group_id,
    ))


@mcp.tool()
def tool_update_circle_dictionary(
    target_user: str,
    traits: list[str],
) -> str:
    """Record personality traits, slang, or taboos for circle members.

    Use target_user="group_vibe" for overall group atmosphere.
    """
    return _json_result(update_circle_dictionary(target_user, traits))


@mcp.tool()
def tool_save_meme(
    meme_title: str,
    context_tags: list[str],
    media_path: str | None = None,
) -> str:
    """Archive a legendary moment into the meme vault for future callbacks.

    Media files are deduplicated via content-addressed MD5 hashing.
    """
    return _json_result(save_meme(
        meme_title, context_tags, media_path=media_path,
    ))


@mcp.tool()
def tool_render_canvas(
    target_event: str,
    context_type: str = "event",
    vibe_override: str | None = None,
    group_id: str | None = None,
    locale: str = "en",
) -> str:
    """Render an interactive HTML memory scroll.

    Use target_event="today" or "this_month" for daily/monthly views.
    Locale: "en" (default) or "zh" for Chinese UI.
    """
    return _json_result(render_lumi_canvas(
        target_event, context_type=context_type,
        vibe_override=vibe_override, group_id=group_id, locale=locale,
    ))


@mcp.tool()
def tool_manage_fragment(
    action: str,
    fragment_id: str | None = None,
    keyword: str | None = None,
    sender: str | None = None,
    context_type: str | None = None,
    group_id: str | None = None,
    event_name: str | None = None,
    story_node_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 20,
    new_content: str | None = None,
    new_emotion: str | None = None,
) -> str:
    """Search, view, update, or delete recorded fragments.

    Actions: search, get, update, delete.
    Supports filtering by sender, keyword, date range, context, and more.
    """
    return _json_result(manage_fragment(
        action, fragment_id=fragment_id, keyword=keyword,
        sender=sender, context_type=context_type, group_id=group_id,
        event_name=event_name, story_node_id=story_node_id,
        date_from=date_from, date_to=date_to, limit=limit,
        new_content=new_content, new_emotion=new_emotion,
    ))


@mcp.tool()
def tool_export_scroll(
    target_event: str,
    context_type: str = "event",
    vibe_override: str | None = None,
    group_id: str | None = None,
    locale: str = "en",
) -> str:
    """Export a memory scroll for social sharing.

    Produces HTML scroll + .lumi seed file + optional PNG long image.
    Locale: "en" (default) or "zh" for Chinese UI.
    """
    return _json_result(export_lumi_scroll(
        target_event, context_type=context_type,
        vibe_override=vibe_override, group_id=group_id, locale=locale,
    ))


if __name__ == "__main__":
    mcp.run()
