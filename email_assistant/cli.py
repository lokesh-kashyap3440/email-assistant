import re, typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from email_assistant.config import get_settings, save_settings
from email_assistant.fetcher import create_fetcher
from email_assistant.processor import EmailProcessor
from email_assistant.provider import OpenCodeAPI
from email_assistant.gmail_auth import get_service, authenticate

app = typer.Typer(help="AI-powered email assistant - summarize, categorize, and action your inbox")
console = Console()

CATEGORY_COLORS = {
    "billing": "red",
    "newsletter": "blue",
    "security": "yellow",
    "ai-tool": "magenta",
    "personal": "green",
    "social": "cyan",
    "alert": "red",
    "forum": "blue",
    "promotion": "blue",
    "other": "white",
}

URGENCY_LABEL = {
    "urgent": "[red]!![/red]",
    "important": "[yellow]![/yellow]",
    "normal": "",
    "low": "[dim].[/dim]",
}


@app.callback()
def callback():
    pass


@app.command()
def inbox(
    count: int = typer.Option(10, "--count", "-n", help="Number of emails to fetch"),
    unread_only: bool = typer.Option(False, "--unread", "-u", help="Only unread emails"),
):
    """Fetch and analyze your recent inbox emails."""
    if not _ensure_opencode():
        return

    try:
        fetcher = create_fetcher()
    except Exception as e:
        console.print(f"[red]X {e}[/red]")
        return

    query = "is:unread" if unread_only else ""
    with console.status("[bold green]Fetching emails..."):
        try:
            emails = fetcher.fetch(max_results=count, query=query)
        except RuntimeError as e:
            console.print(f"[red]X {e}[/red]")
            return

    if not emails:
        console.print("[yellow]No emails found.")
        return

    processor = EmailProcessor()
    with console.status("[bold green]Analyzing emails with AI..."):
        try:
            results = processor.process(emails)
        except Exception as e:
            console.print(f"[red]X LLM error: {e}[/red]")
            _plain_display(emails)
            return

    _display_results(emails, results)


@app.command()
def summarize(
    count: int = typer.Option(10, "--count", "-n", help="Number of emails to show"),
):
    """Quick summary of recent emails (no AI analysis)."""
    try:
        fetcher = create_fetcher()
    except Exception as e:
        console.print(f"[red]X {e}[/red]")
        return

    with console.status("[bold green]Fetching emails..."):
        try:
            emails = fetcher.fetch(max_results=count)
        except RuntimeError as e:
            console.print(f"[red]X {e}[/red]")
            return

    if not emails:
        console.print("[yellow]No emails found.")
        return

    _plain_display(emails)


@app.command()
def config(
    host: str = typer.Option(None, "--host", help="OpenCode server host"),
    port: int = typer.Option(None, "--port", "-p", help="OpenCode server port"),
    password: str = typer.Option(None, "--password", help="OpenCode server password"),
    backend: str = typer.Option(None, "--backend", help="Email backend: composio or gmail_api"),
    composio_key: str = typer.Option(None, "--composio-key", help="Set Composio API key", hidden=True),
):
    """Configure the email assistant."""
    s = get_settings()
    if host:
        s["opencode_host"] = host
    if port:
        s["opencode_port"] = port
    if password is not None:
        s["opencode_password"] = password
    if composio_key:
        s["composio_key"] = composio_key
        if not s.get("backend") or s["backend"] == "gmail_api":
            s["backend"] = "composio"
    if backend:
        if backend not in ("composio", "gmail_api"):
            console.print("[red]Backend must be 'composio' or 'gmail_api'[/red]")
            return
        s["backend"] = backend
    save_settings(s)

    table = Table(title="Settings", box=box.ROUNDED)
    table.add_column("Key", style="bold cyan")
    table.add_column("Value")
    for k, v in sorted(s.items()):
        display = v[:20] + "..." if k == "composio_key" and len(v) > 20 else v
        table.add_row(k, str(display))
    console.print(table)


@app.command()
def setup(
    creds: str = typer.Option(None, "--creds", help="Path to Gmail API credentials.json"),
    composio_key: str = typer.Option(None, "--composio-key", help="Composio API key"),
):
    """One-time setup: auth + test connection."""
    console.print("[bold]== Email Assistant Setup ==[/bold]\n")

    s = get_settings()

    if composio_key:
        s["backend"] = "composio"
        s["composio_key"] = composio_key
        save_settings(s)
        console.print("[bold green]OK[/bold green] Composio key saved")
    elif creds:
        s["backend"] = "gmail_api"
        save_settings(s)
        from email_assistant.gmail_auth import authenticate as gmail_auth
        if not gmail_auth(creds):
            return
    else:
        console.print("[yellow]Provide either:[/yellow]")
        console.print("  --composio-key KEY    (use Composio)")
        console.print("  --creds path/to.json  (use Gmail API)")
        return

    if not _ensure_opencode():
        return

    backend = s.get("backend", "gmail_api")
    console.print(f"[bold green]OK[/bold green] Backend: {backend}")
    console.print(f"[bold green]OK[/bold green] OpenCode: connected")
    console.print("\nTry: [cyan]email-assistant inbox[/cyan]")


def _ensure_opencode() -> bool:
    api = OpenCodeAPI()
    if api.check():
        return True
    s = get_settings()
    host = s.get("opencode_host", "127.0.0.1")
    port = s.get("opencode_port", 4096)
    console.print(f"[red]X OpenCode server not running at {host}:{port}[/red]")
    console.print("  Start: [yellow]opencode serve[/yellow]")
    if host == "127.0.0.1":
        console.print("  Or if remote: [yellow]email-assistant config --host <ip> --port <port>[/yellow]")
    return False


def _plain_display(emails: list) -> None:
    for e in emails:
        t = e.datetime
        time_str = t.strftime("%b %d %H:%M") if t else e.timestamp[:10]
        tag = "[red][IMP][/red]" if e.is_important else ""
        console.print(f"{tag} [bold]{e.subject}[/bold]")
        console.print(f"   [dim]{e.sender} - {time_str}[/dim]")
        console.print(f"   {e.body_preview[:150]}")
        console.print()


_RE_REMOVE = re.compile(r"[^\x00-\x7F]+")

def _sanitize(text: str | None) -> str:
    if not text:
        return ""
    return _RE_REMOVE.sub("", text).strip()

def _display_results(emails: list, results: list[dict]) -> None:
    result_map = {r["id"]: r for r in results}

    for e in emails:
        r = result_map.get(e.id, {})
        cat = r.get("category", "other")
        urgency = r.get("urgency", "normal")
        summary = _sanitize(r.get("summary"))
        action = _sanitize(r.get("action_item"))
        reply = _sanitize(r.get("suggested_reply"))

        color = CATEGORY_COLORS.get(cat, "white")
        cat_tag = f"[{color}]{cat.upper()}[/{color}]"
        urgency_tag = URGENCY_LABEL.get(urgency, "")

        t = e.datetime
        time_str = t.strftime("%b %d %H:%M") if t else e.timestamp[:10]

        body = f"[dim]{e.sender} - {time_str}[/dim]\n\n{summary}"
        if action:
            body += f"\n\n[bold red]> Action:[/bold red] {action}"
        if reply:
            body += f"\n[bold green]> Reply:[/bold green] [italic]{reply}[/italic]"

        console.print(Panel(
            body,
            title=f"  {urgency_tag} {e.subject}  {cat_tag}",
            border_style=color if color != "white" else "dim",
            padding=(1, 2),
        ))
        console.print()


def main():
    app()
