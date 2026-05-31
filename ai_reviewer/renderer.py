import sys
from contextlib import contextmanager
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich.theme import Theme

# Reconfigure stdout/stderr to UTF-8 if possible
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Check if the output stream supports UTF-8 characters
def _supports_utf8() -> bool:
    try:
        encoding = getattr(sys.stdout, "encoding", None)
        if encoding and "utf" in encoding.lower():
            return True
        "⚡".encode(encoding or "ascii")
        return True
    except Exception:
        return False

UTF8_SUPPORTED = _supports_utf8()

# Define visual indicators with fallback representations
CHAR_FLASH = "⚡" if UTF8_SUPPORTED else "**"
CHAR_WARNING = "⚠️" if UTF8_SUPPORTED else "[!]"
CHAR_SUCCESS = "✔" if UTF8_SUPPORTED else "[+]"
CHAR_INFO = "ℹ" if UTF8_SUPPORTED else "[i]"
CHAR_REPORT = "📊" if UTF8_SUPPORTED else "==="

# Define a custom color theme for professional aesthetics
CUSTOM_THEME = Theme({
    "info": "cyan bold",
    "warning": "yellow bold",
    "error": "red bold",
    "success": "green bold",
    "accent": "magenta bold",
    "header": "reverse blue bold",
})

# Instantiate the console with the theme
console = Console(theme=CUSTOM_THEME)

class Renderer:
    """Manages the visual rendering of inputs, outputs, errors, and progress in the terminal."""

    @staticmethod
    def print_banner():
        """Displays a beautiful title banner for the CLI tool."""
        banner_text = Text()
        banner_text.append(f"{CHAR_FLASH} AI CODE REVIEWER {CHAR_FLASH}\n", style="accent")
        banner_text.append("Your local terminal assistant for automated code reviews", style="italic white")
        
        console.print()
        console.print(
            Panel(
                banner_text,
                border_style="bright_blue",
                title="[bold cyan]Code Critic CLI[/bold cyan]",
                subtitle="v1.0.0",
                subtitle_align="right",
                expand=False
            )
        )
        console.print()

    @staticmethod
    def print_warning(message: str):
        """Displays a warning alert panel."""
        console.print(
            Panel(
                f"[yellow]{CHAR_WARNING}  {message}[/yellow]",
                border_style="yellow",
                title="[yellow bold]Warning[/yellow bold]",
                title_align="left"
            )
        )
        console.print()

    @staticmethod
    def print_error(message: str):
        """Displays an error alert panel."""
        console.print(
            Panel(
                f"[red]Error: {message}[/red]",
                border_style="red",
                title="[red bold]Error[/red bold]",
                title_align="left"
            )
        )
        console.print()

    @staticmethod
    def print_success(message: str):
        """Displays a success message with green text."""
        console.print(f"[success]{CHAR_SUCCESS}[/success] {message}")

    @staticmethod
    def print_info(message: str):
        """Displays an informational status message."""
        console.print(f"[info]{CHAR_INFO}[/info] {message}")

    @staticmethod
    @contextmanager
    def show_spinner(status_text: str = "Processing..."):
        """
        A context manager that displays a loading spinner with text.
        """
        # Fallback to simple print if stdin/stdout are redirected or UTF8 not fully supported
        with console.status(f"[bold magenta]{status_text}[/bold magenta]", spinner="dots") as status:
            yield status

    @staticmethod
    def print_report(markdown_content: str, title: str, file_path: str):
        """
        Renders markdown reports beautifully directly in the terminal.
        """
        markdown_obj = Markdown(markdown_content, code_theme="monokai")
        
        console.print()
        console.print(
            Panel(
                markdown_obj,
                border_style="bright_blue",
                title=f"[bold green]{CHAR_REPORT} {title} Report: {file_path}[/bold green]",
                title_align="center",
                padding=(1, 2)
            )
        )
        console.print()

    @staticmethod
    def print_score_panel(score_info: dict):
        """
        Displays a beautiful, visually appealing panel containing the Code Health Score summary.
        """
        status = score_info["status"]
        if status == "Excellent":
            status_style = "green bold"
            border_style = "green"
            score_color = "green"
        elif status == "Good":
            status_style = "cyan bold"
            border_style = "cyan"
            score_color = "cyan"
        else: # Needs Improvement
            status_style = "red bold"
            border_style = "red"
            score_color = "red"
            
        panel_text = Text()
        panel_text.append("Code Health Score: ", style="bold white")
        panel_text.append(f"{score_info['score_str']}\n\n", style=f"bold {score_color}")
        
        panel_text.append("Critical Issues: ", style="white")
        panel_text.append(f"{score_info['critical']}\n", style="bold red")
        panel_text.append("Warnings: ", style="white")
        panel_text.append(f"{score_info['warning']}\n", style="bold yellow")
        panel_text.append("Suggestions: ", style="white")
        panel_text.append(f"{score_info['suggestion']}\n\n", style="bold blue")
        
        panel_text.append("Status: ", style="bold white")
        panel_text.append(f"{status}", style=status_style)
        
        console.print()
        console.print(
            Panel(
                panel_text,
                border_style=border_style,
                title="[bold]Code Health Summary[/bold]",
                title_align="left",
                expand=False,
                padding=(1, 4)
            )
        )

