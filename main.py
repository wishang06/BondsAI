#!/usr/bin/env python3
"""Main entry point for BondsAI - Dual Purpose AI Assistant."""

import asyncio
import sys
from src.bondsai.core import DatingAssistant
from src.bondsai.job_screening import JobScreeningAssistant


async def main():
    """Main application entry point."""
    print("=" * 60)
    print("🤖 Welcome to BondsAI - Your Dual Purpose AI Assistant!")
    print("=" * 60)
    
    # Show app selection menu
    print("\nPlease choose an application:")
    print("1. 💕 Dating App - AI Matchmaker")
    print("2. 💼 Job Screening - Quant Trading Assessment")
    print("3. ❌ Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            await run_dating_app()
            break
        elif choice == "2":
            await run_job_screening_app()
            break
        elif choice == "3":
            print("Goodbye! 👋")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


async def run_dating_app():
    """Run the dating app."""
    print("\n" + "=" * 60)
    print("💕 Welcome to BondsAI - Your Personal AI Matchmaker!")
    print("=" * 60)
    
    print("\n📋 Available Commands:")
    print("• Just type your message to chat with your AI matchmaker")
    print("• /help - Show this help message")
    print("• /clear - Start a fresh conversation")
    print("• /info - Show conversation info")
    print("• /quit - Exit the application")
    
    print("\n💡 What to expect:")
    print("• Your AI will ask you thoughtful questions to get to know you")
    print("• Be yourself and share openly - this helps create better matches!")
    print("• The conversation will feel natural and engaging")
    print("• After 10-15 exchanges, you'll get a personality summary")
    
    assistant = DatingAssistant()
    
    # Start the conversation automatically
    print("\n" + "-" * 60)
    initial_response = await assistant.chat()
    print("💕 AI Matchmaker:", initial_response)
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == "/quit":
                print("\n💕 Thanks for chatting! Your personality profile is ready for matching!")
                break
            elif user_input.lower() == "/help":
                print("\n📋 Available Commands:")
                print("• Just type your message to chat with your AI matchmaker")
                print("• /help - Show this help message")
                print("• /clear - Start a fresh conversation")
                print("• /info - Show conversation info")
                print("• /quit - Exit the application")
                continue
            elif user_input.lower() == "/clear":
                assistant.clear_history()
                print("Conversation cleared! Starting fresh...")
                # Start new conversation automatically
                print("\n" + "-" * 60)
                initial_response = await assistant.chat()
                print("💕 AI Matchmaker:", initial_response)
                print("-" * 60)
                continue
            elif user_input.lower() == "/info":
                summary = assistant.get_conversation_summary()
                print("\n" + "=" * 60)
                print("🎭 Your Personality Profile")
                print("=" * 60)
                print(summary["personality_summary"])
                print("=" * 60)
                print("This profile helps us find your perfect match! 💕")
                print("=" * 60)
                continue
            elif not user_input:
                continue
            
            print("⠋ 💕 BondsAI is thinking about your response...")
            response = await assistant.chat(user_input)
            
            print("-" * 60)
            print("💕 AI Matchmaker:", response)
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n\n💕 Thanks for chatting! Your personality profile is ready for matching!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")


async def run_job_screening_app():
    """Run the job screening app."""
    print("\n" + "=" * 60)
    print("💼 Welcome to BondsAI - Quantitative Trading Assessment!")
    print("=" * 60)
    
    print("\n📋 Available Commands:")
    print("• Just type your message to chat with the HR interviewer")
    print("• /help - Show this help message")
    print("• /clear - Start a fresh interview")
    print("• /info - Show interview progress")
    print("• /quit - Exit the application")
    
    print("\n💡 What to expect:")
    print("• Professional interview for Quantitative Trading position")
    print("• Questions about your background, skills, and experience")
    print("• Assessment of technical skills, behavioral traits, and cultural fit")
    print("• After 10-15 exchanges, you'll receive a detailed assessment report")
    
    assistant = JobScreeningAssistant()
    
    # Start the conversation automatically
    print("\n" + "-" * 60)
    initial_response = await assistant.chat()
    print("💼 HR Interviewer:", initial_response)
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == "/quit":
                print("\n💼 Thanks for your time! Your assessment has been completed.")
                break
            elif user_input.lower() == "/help":
                print("\n📋 Available Commands:")
                print("• Just type your message to chat with the HR interviewer")
                print("• /help - Show this help message")
                print("• /clear - Start a fresh interview")
                print("• /info - Show interview progress")
                print("• /quit - Exit the application")
                continue
            elif user_input.lower() == "/clear":
                assistant.clear_history()
                print("Interview cleared! Starting fresh...")
                # Start new conversation automatically
                print("\n" + "-" * 60)
                initial_response = await assistant.chat()
                print("💼 HR Interviewer:", initial_response)
                print("-" * 60)
                continue
            elif user_input.lower() == "/info":
                print(f"\nInterview Progress: {assistant.candidate.conversation_count} exchanges completed")
                if assistant.candidate.conversation_count >= 10:
                    print("Assessment ready to generate!")
                else:
                    print(f"Need {10 - assistant.candidate.conversation_count} more exchanges for assessment")
                continue
            elif not user_input:
                continue
            
            print("⠋ 💼 HR is thinking about your response...")
            response = await assistant.chat(user_input)
            
            print("-" * 60)
            print("💼 HR Interviewer:", response)
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n\n💼 Thanks for your time! Your assessment has been completed.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
