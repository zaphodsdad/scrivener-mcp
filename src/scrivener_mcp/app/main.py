"""Web app for Scrivener projects - works with any LLM."""

import json
import os
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..scrivener import ScrivenerProject
from ..server import find_scriv_folders, get_common_scrivener_locations

app = FastAPI(title="Scrivener Web App")

# Serve static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Config file path
CONFIG_FILE = Path.home() / ".scrivener-app.json"


def load_config() -> dict:
    """Load config from file."""
    default = {
        "provider": "openrouter",
        "api_key": os.environ.get("OPENROUTER_API_KEY", ""),
        "model": "anthropic/claude-sonnet-4-20250514",
        "base_url": "https://openrouter.ai/api/v1",
        "last_project": None,
    }
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                saved = json.load(f)
                default.update(saved)
        except Exception:
            pass
    return default


def save_config(config: dict):
    """Save config to file."""
    try:
        # Don't save sensitive data in plain text? For now, we do for convenience
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save config: {e}")


# Global state
_project: Optional[ScrivenerProject] = None
_llm_config = load_config()


# === Pydantic Models ===

class ProjectPath(BaseModel):
    path: str


class DocumentContent(BaseModel):
    identifier: str
    content: str


class SynopsisContent(BaseModel):
    identifier: str
    synopsis: str


class NotesContent(BaseModel):
    identifier: str
    notes: str


class NewDocument(BaseModel):
    title: str
    parent_path: str
    content: str = ""
    synopsis: str = ""


class ChatRequest(BaseModel):
    message: str
    context: str = ""  # Selected text or document content


class LLMConfig(BaseModel):
    provider: str = "openrouter"
    api_key: str = ""
    model: str = "anthropic/claude-sonnet-4-20250514"
    base_url: str = "https://openrouter.ai/api/v1"


# === Routes ===

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main app page."""
    index_path = static_dir / "index.html"
    return index_path.read_text()


@app.get("/api/projects")
async def list_projects(search_path: Optional[str] = None):
    """Find Scrivener projects."""
    projects = []

    if search_path:
        search_dir = Path(search_path).expanduser().resolve()
        if search_dir.exists():
            projects = find_scriv_folders(search_dir, max_depth=4)
    else:
        for location in get_common_scrivener_locations():
            projects.extend(find_scriv_folders(location, max_depth=3))

    return {
        "projects": [
            {"name": p.stem, "path": str(p)}
            for p in sorted(projects, key=lambda x: x.name.lower())
        ]
    }


@app.get("/api/browse")
async def browse_directory(path: Optional[str] = None):
    """Browse filesystem directories to find .scriv projects."""
    if not path:
        # Start at home directory
        browse_path = Path.home()
    else:
        browse_path = Path(path).expanduser().resolve()

    if not browse_path.exists():
        raise HTTPException(status_code=404, detail=f"Path not found: {path}")

    if not browse_path.is_dir():
        raise HTTPException(status_code=400, detail=f"Not a directory: {path}")

    items = []
    try:
        for item in sorted(browse_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            # Skip hidden files
            if item.name.startswith("."):
                continue

            if item.is_dir():
                is_scriv = item.suffix == ".scriv"
                items.append({
                    "name": item.name,
                    "path": str(item),
                    "is_dir": True,
                    "is_scriv": is_scriv,
                })
            # Skip regular files in browser
    except PermissionError:
        pass

    return {
        "current": str(browse_path),
        "parent": str(browse_path.parent) if browse_path.parent != browse_path else None,
        "items": items,
    }


@app.post("/api/project/open")
async def open_project(data: ProjectPath):
    """Open a Scrivener project."""
    global _project, _llm_config

    try:
        project_path = Path(data.path).expanduser().resolve()
        _project = ScrivenerProject(project_path)

        # Remember last project
        _llm_config["last_project"] = str(project_path)
        save_config(_llm_config)

        return {
            "name": _project.name,
            "path": str(_project.path),
            "is_locked": _project.is_locked,
            "total_items": sum(1 for _ in _project.all_items()),
            "text_items": sum(1 for item in _project.all_items() if item.is_text),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/project/status")
async def project_status():
    """Get current project status."""
    if not _project:
        return {"loaded": False}

    return {
        "loaded": True,
        "name": _project.name,
        "path": str(_project.path),
        "is_locked": _project.is_locked,
    }


@app.get("/api/binder")
async def get_binder():
    """Get the binder structure as JSON."""
    if not _project:
        raise HTTPException(status_code=400, detail="No project loaded")

    def item_to_dict(item):
        return {
            "uuid": item.uuid,
            "title": item.title,
            "path": item.path,
            "type": item.item_type,
            "is_folder": item.is_folder,
            "is_text": item.is_text,
            "include_in_compile": item.include_in_compile,
            "children": [item_to_dict(child) for child in item.children],
        }

    return {
        "items": [item_to_dict(item) for item in _project.binder_items]
    }


@app.get("/api/document/{identifier:path}")
async def read_document(identifier: str):
    """Read a document's content."""
    if not _project:
        raise HTTPException(status_code=400, detail="No project loaded")

    # Find by UUID, path, or title
    item = _project.find_by_uuid(identifier)
    if not item:
        item = _project.find_by_path(identifier)
    if not item:
        matches = _project.find_by_title(identifier, exact=False)
        item = matches[0] if matches else None

    if not item:
        raise HTTPException(status_code=404, detail=f"Document not found: {identifier}")

    if item.is_folder:
        return {
            "uuid": item.uuid,
            "title": item.title,
            "path": item.path,
            "is_folder": True,
            "word_count": _project.get_word_count(item, recursive=True),
        }

    content = _project.read_document(item)
    synopsis = _project.read_synopsis(item)
    notes = _project.read_notes(item)

    return {
        "uuid": item.uuid,
        "title": item.title,
        "path": item.path,
        "is_folder": False,
        "content": content,
        "synopsis": synopsis,
        "notes": notes,
        "word_count": _project.get_word_count(item),
        "include_in_compile": item.include_in_compile,
    }


@app.post("/api/document/write")
async def write_document(data: DocumentContent):
    """Write document content."""
    if not _project:
        raise HTTPException(status_code=400, detail="No project loaded")

    if _project.is_locked:
        raise HTTPException(
            status_code=423,
            detail="Project is open in Scrivener. Close Scrivener before writing."
        )

    item = _project.find_by_uuid(data.identifier)
    if not item:
        item = _project.find_by_path(data.identifier)
    if not item:
        matches = _project.find_by_title(data.identifier, exact=True)
        item = matches[0] if len(matches) == 1 else None

    if not item:
        raise HTTPException(status_code=404, detail=f"Document not found: {data.identifier}")

    try:
        old_count = _project.get_word_count(item)
        _project.write_document(item, data.content, create_snapshot=True)
        new_count = len(data.content.split())

        return {
            "success": True,
            "title": item.title,
            "old_word_count": old_count,
            "new_word_count": new_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/synopsis/write")
async def write_synopsis(data: SynopsisContent):
    """Write document synopsis."""
    if not _project:
        raise HTTPException(status_code=400, detail="No project loaded")

    if _project.is_locked:
        raise HTTPException(
            status_code=423,
            detail="Project is open in Scrivener. Close Scrivener before writing."
        )

    item = _project.find_by_uuid(data.identifier)
    if not item:
        item = _project.find_by_path(data.identifier)

    if not item:
        raise HTTPException(status_code=404, detail=f"Document not found: {data.identifier}")

    try:
        _project.write_synopsis(item, data.synopsis)
        return {"success": True, "title": item.title}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/notes/write")
async def write_notes(data: NotesContent):
    """Write document notes."""
    if not _project:
        raise HTTPException(status_code=400, detail="No project loaded")

    if _project.is_locked:
        raise HTTPException(
            status_code=423,
            detail="Project is open in Scrivener. Close Scrivener before writing."
        )

    item = _project.find_by_uuid(data.identifier)
    if not item:
        item = _project.find_by_path(data.identifier)

    if not item:
        raise HTTPException(status_code=404, detail=f"Document not found: {data.identifier}")

    try:
        _project.write_notes(item, data.notes)
        return {"success": True, "title": item.title}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/document/create")
async def create_document(data: NewDocument):
    """Create a new document."""
    if not _project:
        raise HTTPException(status_code=400, detail="No project loaded")

    if _project.is_locked:
        raise HTTPException(
            status_code=423,
            detail="Project is open in Scrivener. Close Scrivener before writing."
        )

    # Find parent folder
    parent = _project.find_by_path(data.parent_path)
    if not parent:
        matches = _project.find_by_title(data.parent_path, exact=False)
        matches = [m for m in matches if m.is_folder]
        parent = matches[0] if matches else None

    if not parent:
        raise HTTPException(status_code=404, detail=f"Parent folder not found: {data.parent_path}")

    try:
        new_item = _project.create_document(
            title=data.title,
            parent=parent,
            content=data.content,
            synopsis=data.synopsis,
        )
        return {
            "success": True,
            "uuid": new_item.uuid,
            "title": new_item.title,
            "path": new_item.path,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search")
async def search(query: str):
    """Search project content."""
    if not _project:
        raise HTTPException(status_code=400, detail="No project loaded")

    results = _project.search(query)

    return {
        "query": query,
        "results": [
            {
                "uuid": item.uuid,
                "title": item.title,
                "path": item.path,
                "matches": lines[:5],  # First 5 matches
            }
            for item, lines in results
        ]
    }


# === LLM Chat ===

@app.get("/api/llm/config")
async def get_llm_config():
    """Get current LLM configuration."""
    # Consider configured if: has API key OR is local provider (ollama/custom)
    is_configured = bool(_llm_config["api_key"]) or _llm_config["provider"] in ("ollama", "custom")

    return {
        "provider": _llm_config["provider"],
        "model": _llm_config["model"],
        "base_url": _llm_config["base_url"],
        "has_api_key": bool(_llm_config["api_key"]),
        "is_configured": is_configured,
        "last_project": _llm_config.get("last_project"),
    }


@app.get("/api/llm/models")
async def get_available_models():
    """Get available models from current provider (for Ollama)."""
    if _llm_config["provider"] != "ollama":
        return {"models": [], "error": "Only supported for Ollama"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{_llm_config['base_url']}/models",
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "models": [m["id"] for m in data.get("data", [])]
            }
    except Exception as e:
        return {"models": [], "error": str(e)}


@app.post("/api/llm/config")
async def set_llm_config(config: LLMConfig):
    """Update LLM configuration."""
    global _llm_config
    _llm_config["provider"] = config.provider
    _llm_config["model"] = config.model
    if config.api_key:
        _llm_config["api_key"] = config.api_key

    # Set base URL based on provider (or use custom)
    if config.base_url:
        _llm_config["base_url"] = config.base_url
    elif config.provider == "openrouter":
        _llm_config["base_url"] = "https://openrouter.ai/api/v1"
    elif config.provider == "anthropic":
        _llm_config["base_url"] = "https://api.anthropic.com/v1"
    elif config.provider == "openai":
        _llm_config["base_url"] = "https://api.openai.com/v1"
    elif config.provider == "ollama":
        _llm_config["base_url"] = "http://localhost:11434/v1"

    # Save to file
    save_config(_llm_config)

    return {"success": True}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Send a message to the LLM with optional context."""
    # Ollama doesn't require an API key
    if not _llm_config["api_key"] and _llm_config["provider"] not in ("ollama", "custom"):
        raise HTTPException(status_code=400, detail="No API key configured")

    # Build the prompt
    system_prompt = """You are a writing assistant helping with a Scrivener project.
You help with creative writing, editing, analysis, and answering questions about the manuscript.
Be concise but helpful. When suggesting edits, show the revised text clearly."""

    user_message = request.message
    if request.context:
        user_message = f"Context from the manuscript:\n\n{request.context}\n\n---\n\n{request.message}"

    try:
        async with httpx.AsyncClient() as client:
            if _llm_config["provider"] == "anthropic":
                # Direct Anthropic API
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": _llm_config["api_key"],
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": _llm_config["model"],
                        "max_tokens": 4096,
                        "system": system_prompt,
                        "messages": [{"role": "user", "content": user_message}],
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()
                return {"response": data["content"][0]["text"]}
            else:
                # OpenAI-compatible API (OpenRouter, OpenAI, Ollama, etc.)
                headers = {"Content-Type": "application/json"}
                if _llm_config["api_key"]:
                    headers["Authorization"] = f"Bearer {_llm_config['api_key']}"

                response = await client.post(
                    f"{_llm_config['base_url']}/chat/completions",
                    headers=headers,
                    json={
                        "model": _llm_config["model"],
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message},
                        ],
                    },
                    timeout=120.0,  # Longer timeout for local models
                )
                response.raise_for_status()
                data = response.json()
                return {"response": data["choices"][0]["message"]["content"]}

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run_app(host: str = "0.0.0.0", port: int = 8080):
    """Run the web app."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_app()
