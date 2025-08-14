"""Command-line interface for BondsAI - Dating App Personality Profiler."""

import asyncio
import sys
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.markdown import Markdown
from typer import Typer, Exit

from .core import DatingAssistant
from .config import config

app = Typer(
    name="bondsai",
    help="A charming AI personality profiler for dating app matching",
    add_completion=False,
)

console = Console()


def print_welcome() -> None:
    """Print welcome message."""
    welcome_text = Text()
    welcome_text.append("💕 Welcome to ", style="bold magenta")
    welcome_text.append("BondsAI", style="bold purple")
    welcome_text.append(" - Your Personal AI Matchmaker!", style="bold magenta")
    
    panel = Panel(
        welcome_text,
        border_style="magenta",
        padding=(1, 2),
    )
    console.print(panel)

def print_help() -> None:
    """Print help information."""
    help_text = """
[bold]Available Commands:[/bold]
• Just type your message to chat with your AI matchmaker
• [bold]/help[/bold] - Show this help message
• [bold]/clear[/bold] - Start a fresh conversation
• [bold]/info[/bold] - Show conversation info
• [bold]/quit[/bold] - Exit the application

[bold]What to expect:[/bold]
• Your AI will ask you thoughtful questions to get to know you
• Be yourself and share openly - this helps create better matches!
• The conversation will feel natural and engaging
• After 10-15 exchanges, you'll get a personality summary
    """
    
    panel = Panel(help_text, border_style="yellow", title="Help")
    console.print(panel)





def print_info(assistant: DatingAssistant) -> None:
    """Print conversation information."""
    summary = assistant.get_conversation_summary()
    
    info_text = f"""
[bold]Conversation Summary:[/bold]
• Messages exchanged: {summary['message_count']}
• Model: {summary['model']}
• Temperature: {summary['temperature']}
• Max Tokens: {summary['max_tokens']}
• Phase: {summary['conversation_phase']}

[bold]Personality Insights:[/bold]
{summary['personality_summary']}
    """
    
    panel = Panel(info_text, border_style="cyan", title="Info")
    console.print(panel)


async def chat_loop(assistant: DatingAssistant) -> None:
    """Main chat loop."""
    print_welcome()
    print_help()
    
    # Start the conversation
    initial_response = await assistant.chat()
    ai_text = Text()
    ai_text.append("💕 AI Matchmaker: ", style="bold magenta")
    ai_text.append(initial_response, style="white")
    
    panel = Panel(ai_text, border_style="magenta", padding=(0, 1))
    console.print(panel)
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold green]You[/bold green]")
            
            if user_input.lower() in ["/exit", "/quit"]:
                # Show personality summary before exiting
                profile = assistant.get_personality_profile()
                if profile != "Still getting to know this person...":
                    console.print("\n" + "="*80)
                    console.print("🎭 [bold]Your Personality Profile[/bold]")
                    console.print("="*80)
                    console.print(profile)
                    console.print("="*80)
                    console.print("[italic]This profile helps us find your perfect match! 💕[/italic]")
                    console.print("="*80)
                console.print("\n💕 Thanks for chatting! Your personality profile is ready for matching!")
                break
            elif user_input.lower() == "/help":
                print_help()
                continue

            elif user_input.lower() == "/clear":
                assistant.clear_history()
                console.print("🔄 Starting fresh! Let's get to know you again!")
                initial_response = await assistant.chat()
                ai_text = Text()
                ai_text.append("💕 AI Matchmaker: ", style="bold magenta")
                ai_text.append(initial_response, style="white")
                panel = Panel(ai_text, border_style="magenta", padding=(0, 1))
                console.print(panel)
                continue
            elif user_input.lower() == "/info":
                print_info(assistant)
                continue
            elif user_input.startswith("/"):
                console.print(f"❌ Unknown command: {user_input}")
                console.print("Type /help for available commands.")
                continue
            
            with Live(
                Spinner("dots", text="💕 BondsAI is thinking about your response..."),
                console=console,
                refresh_per_second=10,
            ):
                response = await assistant.chat(user_input)
            
            ai_text = Text()
            ai_text.append("💕 AI Matchmaker: ", style="bold magenta")
            ai_text.append(response, style="white")
            
            panel = Panel(ai_text, border_style="magenta", padding=(0, 1))
            console.print(panel)
            
            
        except KeyboardInterrupt:
            # Show personality summary before exiting
            profile = assistant.get_personality_profile()
            if profile != "Still getting to know this person...":
                console.print("\n" + "="*80)
                console.print("🎭 [bold]Your Personality Profile[/bold]")
                console.print("="*80)
                console.print(profile)
                console.print("="*80)
                console.print("[italic]This profile helps us find your perfect match! 💕[/italic]")
                console.print("="*80)
            console.print("\n💕 Thanks for chatting! Your personality profile is ready for matching!")
            break
        except Exception as e:
            console.print(f"❌ Error: {str(e)}", style="red")


@app.command()
def main() -> None:
    """Main entry point for BondsAI Dating App."""
    try:
        config.validate()
        
        assistant = DatingAssistant()
        
        asyncio.run(chat_loop(assistant))
        
    except ValueError as e:
        console.print(f"❌ Configuration Error: {str(e)}", style="red")
        console.print("Please check your .env file and ensure OPENAI_API_KEY is set.")
        raise Exit(1)
    except Exception as e:
        console.print(f"❌ Unexpected Error: {str(e)}", style="red")
        raise Exit(1)


if __name__ == "__main__":
    app()
