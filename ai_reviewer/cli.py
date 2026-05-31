import argparse
import sys
import os
import warnings
import re
from typing import List, Optional

# Suppress all library-level warnings to ensure clean, focused CLI output
warnings.filterwarnings("ignore")

from ai_reviewer.renderer import Renderer
from ai_reviewer.file_handler import read_source_file, write_report_to_file, FileHandlerError
from ai_reviewer.prompt_manager import PromptManager
from ai_reviewer.ai_client import AIClient, AIClientError
from ai_reviewer.config import ConfigError

def run_command(command: str, file_path: str, output_path: Optional[str] = None, model_override: Optional[str] = None, provider_override: Optional[str] = None) -> int:
    """
    Executes the specified subcommand.
    
    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    # 1. Apply command line overrides to environment before initializing AIClient
    if provider_override:
        os.environ["AI_PROVIDER"] = provider_override
    if model_override:
        if provider_override:
            prov = provider_override.lower().strip()
        else:
            try:
                from ai_reviewer.config import Config
                prov = Config.get_provider()
            except Exception:
                prov = "gemini"
        
        if prov == "gemini":
            os.environ["GEMINI_MODEL"] = model_override
        elif prov == "openai":
            os.environ["OPENAI_MODEL"] = model_override

    # 2. Read and validate source file
    try:
        Renderer.print_info(f"Reading file: [yellow]{file_path}[/yellow]")
        code_content, language, warning_msg = read_source_file(file_path)
        
        if warning_msg:
            Renderer.print_warning(warning_msg)
        else:
            Renderer.print_success(f"Loaded file as [bold cyan]{language}[/bold cyan]")
            
    except FileHandlerError as e:
        Renderer.print_error(f"File Error: {str(e)}")
        return 1

    # 3. Initialize AI Client
    try:
        client = AIClient()
        Renderer.print_info(f"Using provider: {client.get_info_string()}")
    except AIClientError as e:
        Renderer.print_error(str(e))
        return 1

    # 4. Generate prompts
    filename = os.path.basename(file_path)
    prompts = PromptManager.get_prompts(command, language, filename, code_content)

    # 5. Fetch feedback with spinner
    try:
        spinner_msg = f"Analyzing {filename} with AI..."
        with Renderer.show_spinner(spinner_msg):
            feedback = client.generate_feedback(prompts["system"], prompts["user"])
    except AIClientError as e:
        Renderer.print_error(f"AI Client Error: {str(e)}")
        return 1

    # 6. Render the output
    if command == "review":
        critical_count = len(re.findall(r'\[Critical\]', feedback, re.IGNORECASE))
        warning_count = len(re.findall(r'\[Warning\]', feedback, re.IGNORECASE))
        suggestion_count = len(re.findall(r'\[Suggestion\]', feedback, re.IGNORECASE))
        
        deductions = (critical_count * 3.0) + (warning_count * 1.0) + (suggestion_count * 0.25)
        score = 10.0 - deductions
        score = max(0.0, min(10.0, score))
        
        if score.is_integer():
            score_str = f"{int(score)}/10"
        elif (score * 2).is_integer():
            score_str = f"{score:.1f}/10"
        else:
            score_str = f"{score:.2f}/10"
            
        if score >= 9.0:
            status = "Excellent"
        elif score >= 7.0:
            status = "Good"
        else:
            status = "Needs Improvement"
            
        score_info = {
            "score": score,
            "score_str": score_str,
            "critical": critical_count,
            "warning": warning_count,
            "suggestion": suggestion_count,
            "status": status
        }
        
        Renderer.print_score_panel(score_info)
        
        summary_md = (
            f"# Code Health Summary\n\n"
            f"* **Code Health Score:** {score_str}\n"
            f"* **Critical Issues:** {critical_count}\n"
            f"* **Warnings:** {warning_count}\n"
            f"* **Suggestions:** {suggestion_count}\n"
            f"* **Status:** {status}\n\n"
            f"---\n\n"
        )
        feedback = summary_md + feedback

    title_map = {
        "review": "Code Review",
        "explain": "Code Explanation",
        "complexity": "Complexity Analysis",
        "testgen": "Generated Test Cases"
    }
    title = title_map.get(command, "Report")
    
    Renderer.print_report(feedback, title, file_path)

    # 7. Export report if requested
    if output_path:
        try:
            saved_path = write_report_to_file(output_path, feedback)
            Renderer.print_success(f"Report exported successfully to: [bold underline]{saved_path.resolve()}[/bold underline]")
        except FileHandlerError as e:
            Renderer.print_error(str(e))
            return 1

    return 0

def main(args: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    # Print welcome banner
    Renderer.print_banner()

    parser = argparse.ArgumentParser(
        description="AI Code Critic - Command Line Static Analyzer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Global options
    parser.add_argument(
        "-p", "--provider",
        choices=["gemini", "openai"],
        help="Override the AI provider set in .env"
    )
    parser.add_argument(
        "-m", "--model",
        help="Override default LLM model name"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: review
    parser_review = subparsers.add_parser("review", help="Review code for bugs, quality, style, optimizations, and complexity")
    parser_review.add_argument("file", help="Path to the source code file to review")
    parser_review.add_argument("-o", "--output", help="Path to save the review report (markdown)")

    # Command: explain
    parser_explain = subparsers.add_parser("explain", help="Generate a clear, step-by-step logic explanation of the code")
    parser_explain.add_argument("file", help="Path to the source code file to explain")
    parser_explain.add_argument("-o", "--output", help="Path to save the explanation (markdown)")

    # Command: complexity
    parser_complexity = subparsers.add_parser("complexity", help="Analyze Big-O time/space complexity and suggest data structure optimizations")
    parser_complexity.add_argument("file", help="Path to the source code file to analyze")
    parser_complexity.add_argument("-o", "--output", help="Path to save the complexity report (markdown)")

    # Command: testgen
    parser_testgen = subparsers.add_parser("testgen", help="Analyze code and generate structured test cases automatically")
    parser_testgen.add_argument("file", help="Path to the source code file to generate tests for")
    parser_testgen.add_argument("-o", "--output", help="Path to save the generated test cases (markdown)")

    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 0

    return run_command(
        command=parsed_args.command,
        file_path=parsed_args.file,
        output_path=parsed_args.output,
        model_override=parsed_args.model,
        provider_override=parsed_args.provider
    )

if __name__ == "__main__":
    sys.exit(main())
