#!/usr/bin/env python3
"""
Agentic Research System - Self-Conversation Pattern
LLM controls everything, Python just executes actions.

Design Goal: <2% Python execution time, 98% LLM latency.
"""

import os
import json
import time
import re
import argparse
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv
import requests

from tools import search_hn, get_post_by_id, get_thread, get_stats, save_report
from prompts import get_system_prompt, get_force_completion_prompt


class AgenticResearcher:
    """
    Agentic research system using self-conversation pattern.
    LLM decides all actions, Python only executes and tracks budget.
    """
    
    def __init__(self, api_key: str, model: str = "anthropic/claude-3.5-sonnet", 
                 max_calls: int = 20, min_quality: float = 7.0):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.max_calls = max_calls
        self.min_quality = min_quality
        
        # Conversation state
        self.conversation: List[Dict] = []
        self.calls_used = 0
        
        # Performance tracking
        self.llm_time = 0.0
        self.python_time = 0.0
        self.search_time = 0.0
        
        # Research tracking
        self.actions_taken = []
        self.searches_performed = 0
        self.posts_found = 0
    
    def research(self, question: str, output_file: Optional[str] = None) -> str:
        """
        Main research loop - LLM controls everything.
        
        Args:
            question: Research question
            output_file: Optional output file path
        
        Returns:
            Final report as markdown string
        """
        print(f"\n{'='*80}")
        print(f"🔬 AGENTIC RESEARCH SYSTEM")
        print(f"{'='*80}")
        print(f"Question: {question}")
        print(f"Budget: {self.max_calls} LLM calls")
        print(f"Model: {self.model}")
        print(f"{'='*80}\n")
        
        # Initialize conversation with system prompt
        self.conversation.append({
            "role": "system",
            "content": get_system_prompt()
        })
        
        # Add user question with budget
        self.conversation.append({
            "role": "user",
            "content": f"Question: {question}\nBudget: {self.calls_used}/{self.max_calls} calls"
        })
        
        # Main agentic loop - LLM controls everything
        report = None
        loop_start = time.time()  # Track total elapsed time
        
        while self.calls_used < self.max_calls:
            # Progress indicator
            print(f"\n{'─'*80}")
            print(f"📊 Progress: {self.calls_used}/{self.max_calls} calls | "
                  f"🔍 {self.searches_performed} searches | "
                  f"📄 {self.posts_found} posts found")
            print(f"{'─'*80}\n")
            
            # Call LLM (this is where 98% of time should be spent)
            llm_start = time.time()
            response = self._call_llm()
            self.llm_time += time.time() - llm_start
            self.calls_used += 1
            
            print(f"💭 LLM Call {self.calls_used}: {self.llm_time:.2f}s (LLM time so far)")
            
            # Parse action (Python does minimal parsing)
            python_start = time.time()
            action = self._parse_action(response)
            self.python_time += time.time() - python_start
            
            # Check if done
            if action["type"] == "DONE":
                report = action.get("report", "")
                print(f"\n✅ Research complete!")
                break
            
            # Execute action (Python just executes, doesn't decide)
            python_start = time.time()
            observation = self._execute_action(action)
            self.python_time += time.time() - python_start
            
            # Add to conversation
            self.conversation.append({
                "role": "assistant",
                "content": response
            })
            self.conversation.append({
                "role": "user",
                "content": f"Observation: {json.dumps(observation, indent=2)}\n\n"
                          f"Budget: {self.calls_used}/{self.max_calls} calls"
            })
        
        # Budget exhausted - force completion
        if report is None:
            print(f"\n⚠️  Budget exhausted! Forcing completion...\n")
            report = self._force_completion()
        
        # Performance summary
        total_elapsed = time.time() - loop_start
        pure_python = self.python_time - self.search_time  # Python logic excluding search I/O
        python_pct = (pure_python / total_elapsed * 100) if total_elapsed > 0 else 0
        search_pct = (self.search_time / total_elapsed * 100) if total_elapsed > 0 else 0
        llm_pct = (self.llm_time / total_elapsed * 100) if total_elapsed > 0 else 0
        
        print(f"\n{'='*80}")
        print(f"📊 PERFORMANCE SUMMARY")
        print(f"{'='*80}")
        print(f"Total time:    {total_elapsed:.2f}s")
        print(f"LLM time:      {self.llm_time:.2f}s ({llm_pct:.1f}%)")
        print(f"Search I/O:    {self.search_time:.2f}s ({search_pct:.1f}%)")
        print(f"Python logic:  {pure_python:.3f}s ({python_pct:.1f}%)")
        print(f"Calls used:    {self.calls_used}/{self.max_calls}")
        print(f"Searches:      {self.searches_performed}")
        print(f"Posts found:   {self.posts_found}")
        print(f"Avg per call:  {total_elapsed/self.calls_used:.2f}s")
        print(f"{'='*80}\n")
        
        if python_pct > 2.0:
            print(f"⚠️  Python logic is {python_pct:.1f}% (goal: <2%)")
        else:
            print(f"✅ Python logic is {python_pct:.1f}% (goal: <2%)")
        
        # Save if output file specified
        if output_file and report:
            result = save_report(report, output_file)
            print(f"\n💾 Report saved: {result['path']} ({result['size']} bytes)")
        
        return report
    
    def _call_llm(self) -> str:
        """Call LLM with current conversation state"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": self.conversation,
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        response = requests.post(self.base_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        return content
    
    def _parse_action(self, response: str) -> Dict:
        """
        Parse LLM response into action dict.
        Minimal parsing - just extract structure.
        """
        # Extract ACTION line
        action_match = re.search(r'ACTION:\s*(\w+)', response, re.IGNORECASE)
        if not action_match:
            # No action found - treat as thinking/intermediate response
            return {"type": "CONTINUE", "content": response}
        
        action_type = action_match.group(1).upper()
        
        # Parse based on action type
        if action_type in ["SEARCH", "REFINE_SEARCH"]:
            # Extract keywords
            keywords_match = re.search(r'Keywords:\s*\[(.*?)\]', response, re.IGNORECASE | re.DOTALL)
            if keywords_match:
                keywords_str = keywords_match.group(1)
                # Split by comma and clean
                keywords = [k.strip().strip('"').strip("'") for k in keywords_str.split(',')]
                keywords = [k for k in keywords if k]  # Remove empty
            else:
                keywords = []
            
            return {
                "type": "SEARCH",
                "keywords": keywords,
                "raw_response": response
            }
        
        elif action_type == "SYNTHESIZE":
            # Extract section and content
            section_match = re.search(r'Section:\s*\[(.*?)\]', response, re.IGNORECASE)
            content_match = re.search(r'Content:\s*\[(.*)\]', response, re.IGNORECASE | re.DOTALL)
            
            section = section_match.group(1).strip() if section_match else "Unknown Section"
            content = content_match.group(1).strip() if content_match else response
            
            return {
                "type": "SYNTHESIZE",
                "section": section,
                "content": content,
                "raw_response": response
            }
        
        elif action_type == "DONE":
            # Extract report
            report_match = re.search(r'Report:\s*\[(.*)\]', response, re.IGNORECASE | re.DOTALL)
            if report_match:
                report = report_match.group(1).strip()
            else:
                # Sometimes LLM puts report after DONE without brackets
                report = response[action_match.end():].strip()
            
            return {
                "type": "DONE",
                "report": report,
                "raw_response": response
            }
        
        else:
            # Unknown action - treat as continue
            return {"type": "CONTINUE", "content": response}
    
    def _execute_action(self, action: Dict) -> Dict:
        """
        Execute action using tools.
        Python just executes - no decisions.
        """
        action_type = action["type"]
        self.actions_taken.append(action_type)
        
        if action_type == "SEARCH":
            keywords = action.get("keywords", [])
            print(f"🔍 SEARCH: {keywords}")
            
            # Execute search tool (track search time separately)
            search_start = time.time()
            result = search_hn(keywords, limit=50, max_shards=1637)
            search_elapsed = time.time() - search_start
            self.search_time += search_elapsed
            
            self.searches_performed += 1
            self.posts_found += result["found"]
            
            print(f"   ✓ Found {result['found']} posts ({search_elapsed:.2f}s)")
            
            # Return observation (truncate posts for context window)
            return {
                "action": "SEARCH",
                "keywords": keywords,
                "found": result["found"],
                "posts": result["posts"][:20],  # Limit to 20 for context
                "note": f"Showing first 20 of {result['found']} posts. Each post has: id, title, text, score, by, url, time"
            }
        
        elif action_type == "SYNTHESIZE":
            section = action.get("section", "Unknown")
            content = action.get("content", "")
            print(f"✍️  SYNTHESIZE: {section} ({len(content)} chars)")
            
            # No execution needed - just acknowledge
            return {
                "action": "SYNTHESIZE",
                "section": section,
                "status": "acknowledged",
                "note": "Section noted. Continue research or finalize report."
            }
        
        elif action_type == "CONTINUE":
            # Just thinking/intermediate response
            print(f"💭 CONTINUE: LLM is thinking...")
            return {
                "action": "CONTINUE",
                "note": "Continue with next action"
            }
        
        else:
            # Unknown action
            print(f"⚠️  Unknown action: {action_type}")
            return {
                "action": "UNKNOWN",
                "note": f"Action '{action_type}' not recognized. Available: SEARCH, SYNTHESIZE, DONE"
            }
    
    def _force_completion(self) -> str:
        """Force completion when budget exhausted"""
        self.conversation.append({
            "role": "user",
            "content": get_force_completion_prompt()
        })
        
        llm_start = time.time()
        response = self._call_llm()
        self.llm_time += time.time() - llm_start
        self.calls_used += 1
        
        # Extract report
        action = self._parse_action(response)
        if action["type"] == "DONE":
            return action.get("report", response)
        else:
            # LLM didn't follow instructions, return raw response
            return response


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(description="Agentic HackerNews Research System")
    parser.add_argument("question", help="Research question")
    parser.add_argument("-o", "--output", help="Output file path", default=None)
    parser.add_argument("--calls", type=int, default=20, help="Maximum LLM calls (default: 20)")
    parser.add_argument("--model", default="anthropic/claude-3.5-sonnet", 
                       help="Model to use (default: claude-3.5-sonnet)")
    parser.add_argument("--min-quality", type=float, default=7.0,
                       help="Minimum quality score (default: 7.0)")
    
    args = parser.parse_args()
    
    # Load API key - try .env file first, then environment
    try:
        load_dotenv()
    except:
        pass  # .env file may not exist or be readable
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found")
        print("   Set it in .env file or as environment variable")
        return 1
    
    # Create researcher
    researcher = AgenticResearcher(
        api_key=api_key,
        model=args.model,
        max_calls=args.calls,
        min_quality=args.min_quality
    )
    
    # Run research
    try:
        report = researcher.research(args.question, args.output)
        
        if not args.output:
            print(f"\n{'='*80}")
            print("📄 FINAL REPORT")
            print(f"{'='*80}\n")
            print(report)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Research interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

