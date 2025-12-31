#!/usr/bin/env python3
"""
Editor Agent - Quality-Enforcing Recursive Research System

Architecture:
- Editor Agent: Supervises quality, rejects subpar work, creates refinement plans
- Worker Agents: Execute searches and analysis
- Recursive refinement until quality threshold met or budget exhausted

User specifies: Number of LLM calls (budget)
System ensures: High-quality output through recursive improvement
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
from research_agent import HNDatabase


class WorkerAgent:
    """Worker agent that executes specific research tasks."""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.db = HNDatabase()
    
    def call_llm(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 4000) -> str:
        """Call LLM API."""
        print(f"     🤖 Calling LLM... ", end='', flush=True)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        print("✓")
        return response.json()['choices'][0]['message']['content']
    
    def search_and_analyze(self, task: Dict) -> Dict:
        """Execute a search task and analyze results."""
        print(f"\n  🔨 Worker Task: {task['description']}")
        print(f"     Keywords: {', '.join(task['keywords'][:3])}")
        
        # Execute search
        print(f"     🔍 Searching HN archive...", end='', flush=True)
        results = self.db.search_by_keywords(
            keywords=task['keywords'],
            item_type=task.get('type'),
            min_score=task.get('min_score'),
            limit=task.get('limit', 20),
            max_shards=1637
        )
        
        print(f" ✓ Found: {len(results)} posts")
        
        if not results:
            return {
                'success': False,
                'task': task,
                'results': [],
                'analysis': {'insights': [], 'quotes': [], 'issues': ['No results found']}
            }
        
        # Get full content
        posts = []
        for r in results[:15]:
            item = self.db.get_item_by_id(r['id'], max_shards=200)
            if item:
                posts.append(item)
        
        # Format for analysis
        posts_data = []
        for post in posts:
            text = post.get('text', '')
            if text:
                text = text.replace('&#34;', '"').replace('&#39;', "'")
                text = text.replace('&lt;', '<').replace('&gt;', '>')
                text = text[:1000]  # Truncate
            
            posts_data.append({
                'id': post['id'],
                'type': post['type'],
                'date': post.get('timestamp', ''),
                'author': post.get('by', ''),
                'score': post.get('score'),
                'title': post.get('title', ''),
                'content': text
            })
        
        # Analyze with LLM
        analysis_prompt = f"""Analyze these HackerNews posts for: {task['goal']}

Posts ({len(posts_data)}):
{json.dumps(posts_data, indent=2)}

Extract:
1. Key insights (3-5 main points)
2. Important quotes with attribution (post ID, author)
3. Patterns or themes
4. Any issues or gaps in the data

JSON format:
{{
  "insights": ["...", "..."],
  "quotes": [{{"post_id": "...", "author": "...", "text": "..."}}],
  "patterns": ["...", "..."],
  "issues": ["..."]
}}"""

        messages = [{"role": "user", "content": analysis_prompt}]
        response = self.call_llm(messages, temperature=0.3, max_tokens=2000)
        
        try:
            if "```json" in response:
                analysis = json.loads(response.split("```json")[1].split("```")[0].strip())
            elif "```" in response:
                analysis = json.loads(response.split("```")[1].split("```")[0].strip())
            else:
                analysis = json.loads(response.strip())
        except:
            analysis = {'insights': ['Analysis failed'], 'quotes': [], 'patterns': [], 'issues': ['Parse error']}
        
        return {
            'success': True,
            'task': task,
            'results': posts,
            'analysis': analysis
        }
    
    def synthesize_section(self, task: Dict, findings: List[Dict]) -> str:
        """Synthesize findings into a narrative section."""
        print(f"\n  ✍️  Worker: Synthesizing '{task['section_title']}'")
        print(f"     Using {len(findings)} research findings")
        
        # Collect all relevant data
        all_insights = []
        all_quotes = []
        all_posts = []
        
        for finding in findings:
            if finding['success']:
                all_insights.extend(finding['analysis'].get('insights', []))
                all_quotes.extend(finding['analysis'].get('quotes', []))
                all_posts.extend(finding['results'][:10])
        
        # Format posts with full content
        posts_full = []
        for post in all_posts[:20]:
            text = post.get('text', '')
            if text:
                text = text.replace('&#34;', '"').replace('&#39;', "'")
                text = text.replace('&lt;', '<').replace('&gt;', '>')
            
            posts_full.append({
                'id': post['id'],
                'type': post['type'],
                'date': post.get('timestamp', ''),
                'author': post.get('by', ''),
                'score': post.get('score'),
                'title': post.get('title', ''),
                'content': text
            })
        
        synthesis_prompt = f"""Write a comprehensive section for a research report.

Section: {task['section_title']}
Requirements: {task['requirements']}

Available Data:
- Insights: {json.dumps(all_insights, indent=2)}
- Quotes: {json.dumps(all_quotes, indent=2)}
- Full Posts: {json.dumps(posts_full, indent=2)}

Write 800-1200 words covering:
{task['requirements']}

Use:
- 5+ direct quotes with attribution (Post #ID, author name)
- Specific examples from the data
- Clear narrative flow
- Technical depth where appropriate

Start directly with content (no "Introduction:" labels)."""

        messages = [{"role": "user", "content": synthesis_prompt}]
        section = self.call_llm(messages, temperature=0.7, max_tokens=3000)
        
        return section


class EditorAgent:
    """
    Editor/Supervisor Agent - Enforces quality through recursive refinement.
    
    Responsibilities:
    1. Create research plan
    2. Assign tasks to workers
    3. Evaluate quality of work
    4. Reject subpar work and create refinement plans
    5. Recursively improve until quality met or budget exhausted
    """
    
    def __init__(self, api_key: str, model: str, max_calls: int):
        self.api_key = api_key
        self.model = model
        self.max_calls = max_calls
        self.calls_used = 0
        self.worker = WorkerAgent(api_key, model)
        
        # Quality thresholds
        self.min_quality_score = 7.0
        self.min_quote_count = 10
        self.min_word_count = 3000
    
    def call_llm(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 4000) -> str:
        """Call LLM and track budget."""
        if self.calls_used >= self.max_calls:
            raise Exception(f"❌ Budget exhausted: {self.calls_used}/{self.max_calls} calls used")
        
        # Show progress
        progress = (self.calls_used / self.max_calls) * 100
        bar_length = 20
        filled = int(bar_length * self.calls_used / self.max_calls)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"     💰 [{bar}] {self.calls_used}/{self.max_calls} calls ({progress:.0f}%)", end='', flush=True)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        
        self.calls_used += 1
        print(f" → {self.calls_used}/{self.max_calls}")
        
        return response.json()['choices'][0]['message']['content']
    
    def create_master_plan(self, question: str) -> Dict:
        """Create comprehensive research plan."""
        print("\n" + "="*80)
        print("📋 EDITOR: Creating Master Research Plan")
        print("="*80)
        
        planning_prompt = f"""As research editor, create a comprehensive plan for: "{question}"

Create a structured plan with:

1. Research Objectives (3-5 specific goals)
2. Search Tasks (5-8 targeted searches)
   - Each with: description, keywords, filters, goal
3. Report Sections (4-6 major sections)
   - Each with: title, requirements, word count target

Quality Requirements:
- Minimum 10 direct quotes with attribution
- Minimum 3000 words
- Clear narrative arc
- Technical depth with explanations
- Community voice and personality

Format as JSON:
{{
  "objectives": ["...", "..."],
  "search_tasks": [
    {{
      "description": "...",
      "keywords": ["...", "..."],
      "type": null,
      "min_score": null,
      "limit": 20,
      "goal": "..."
    }}
  ],
  "report_sections": [
    {{
      "title": "...",
      "requirements": "...",
      "word_count": 800
    }}
  ]
}}"""

        messages = [{"role": "user", "content": planning_prompt}]
        response = self.call_llm(messages, temperature=0.3, max_tokens=3000)
        
        try:
            if "```json" in response:
                plan = json.loads(response.split("```json")[1].split("```")[0].strip())
            elif "```" in response:
                plan = json.loads(response.split("```")[1].split("```")[0].strip())
            else:
                plan = json.loads(response.strip())
            
            print(f"\n✅ Plan Created:")
            print(f"   Objectives: {len(plan['objectives'])}")
            print(f"   Search Tasks: {len(plan['search_tasks'])}")
            print(f"   Report Sections: {len(plan['report_sections'])}")
            
            return plan
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Plan parsing failed: {e}")
            # Fallback minimal plan
            return {
                "objectives": ["Understand the topic", "Find key discussions"],
                "search_tasks": [{
                    "description": "General search",
                    "keywords": question.split()[:3],
                    "type": None,
                    "min_score": None,
                    "limit": 20,
                    "goal": "Find relevant posts"
                }],
                "report_sections": [{
                    "title": "Overview",
                    "requirements": "Summarize findings",
                    "word_count": 1000
                }]
            }
    
    def evaluate_work(self, work: Any, work_type: str, context: str) -> Dict:
        """
        Critically evaluate quality of work product.
        Returns: {score, issues, suggestions, acceptable}
        """
        print(f"\n  🔍 EDITOR: Evaluating {work_type}")
        print(f"     Context: {context[:60]}...")
        
        if work_type == "search_results":
            evaluation_prompt = f"""Evaluate the quality of these search results.

Context: {context}
Results: {json.dumps(work, indent=2)}

Evaluate:
1. Relevance - Do results match the goal?
2. Quality - Are posts substantive and informative?
3. Coverage - Adequate number of results?
4. Gaps - What's missing?

Score 1-10 and provide specific issues and suggestions.

JSON:
{{
  "score": 7,
  "issues": ["...", "..."],
  "suggestions": ["...", "..."],
  "acceptable": true
}}"""
        
        elif work_type == "section":
            # Count quotes and words
            quote_count = work.count("Post #") + work.count("#HN")
            word_count = len(work.split())
            
            evaluation_prompt = f"""Evaluate this report section for publication quality.

Section:
{work[:2000]}... ({word_count} words)

Detected: {quote_count} quotes, {word_count} words

Evaluate:
1. Quality (7-10 = good, 4-6 = needs work, 1-3 = unacceptable)
2. Narrative flow and engagement
3. Quote usage (need 3+ per section)
4. Technical depth
5. Specificity vs generalization

Be CRITICAL. If it's generic or lacks depth, score low.

JSON:
{{
  "score": 7.5,
  "issues": ["Too few quotes", "Lacks specific examples"],
  "suggestions": ["Add 2 more quotes", "Include specific post examples"],
  "acceptable": true,
  "quote_count": {quote_count},
  "word_count": {word_count}
}}"""
        
        elif work_type == "full_report":
            quote_count = work.count("Post #") + work.count("#")
            word_count = len(work.split())
            
            evaluation_prompt = f"""Evaluate this complete research report for publication quality.

Report Preview:
{work[:3000]}...

Stats: {word_count} words, ~{quote_count} quotes detected

Evaluate against requirements:
- Minimum 10 quotes with attribution ✓/✗
- Minimum 3000 words ✓/✗
- Clear narrative arc ✓/✗
- Technical depth ✓/✗
- Community personality ✓/✗
- Engaging writing ✓/✗

Score 1-10 (be CRITICAL):
- 9-10: Excellent, publish-ready
- 7-8: Good, minor improvements
- 5-6: Needs significant work
- 1-4: Unacceptable, major rewrite

JSON:
{{
  "score": 7.5,
  "meets_requirements": {{
    "quotes": true,
    "word_count": true,
    "narrative": true,
    "technical_depth": false,
    "personality": true
  }},
  "issues": ["Lacks technical depth", "Some sections too generic"],
  "suggestions": ["Add more technical explanations", "Include specific examples"],
  "acceptable": true
}}"""
        
        else:
            return {"score": 5, "issues": ["Unknown work type"], "suggestions": [], "acceptable": False}
        
        messages = [{"role": "user", "content": evaluation_prompt}]
        response = self.call_llm(messages, temperature=0.2, max_tokens=1000)
        
        try:
            if "```json" in response:
                evaluation = json.loads(response.split("```json")[1].split("```")[0].strip())
            elif "```" in response:
                evaluation = json.loads(response.split("```")[1].split("```")[0].strip())
            else:
                evaluation = json.loads(response.strip())
            
            print(f"     📊 Score: {evaluation['score']}/10 {'✅' if evaluation.get('acceptable') else '❌'}")
            
            if evaluation.get('issues'):
                print(f"     ⚠️  Issues: {evaluation['issues'][0][:80]}")
                if len(evaluation['issues']) > 1:
                    print(f"              + {len(evaluation['issues'])-1} more")
            
            return evaluation
            
        except json.JSONDecodeError:
            return {"score": 5, "issues": ["Evaluation parse failed"], "suggestions": [], "acceptable": True}
    
    def create_refinement_plan(self, evaluation: Dict, work_type: str) -> List[Dict]:
        """Create specific tasks to address quality issues."""
        print(f"\n🔄 EDITOR: Creating Refinement Plan")
        
        refinement_prompt = f"""Based on this quality evaluation, create specific refinement tasks.

Work Type: {work_type}
Evaluation: {json.dumps(evaluation, indent=2)}

Create 2-4 specific tasks to address issues. For each task:
- What to do
- Why it's needed
- How to accomplish it

JSON:
[
  {{
    "type": "additional_search" | "enhance_section" | "add_quotes",
    "description": "...",
    "specifics": {{...}}
  }}
]"""

        messages = [{"role": "user", "content": refinement_prompt}]
        response = self.call_llm(messages, temperature=0.4, max_tokens=1500)
        
        try:
            if "```json" in response:
                tasks = json.loads(response.split("```json")[1].split("```")[0].strip())
            elif "```" in response:
                tasks = json.loads(response.split("```")[1].split("```")[0].strip())
            else:
                tasks = json.loads(response.strip())
            
            if not isinstance(tasks, list):
                tasks = [tasks]
            
            print(f"   Created {len(tasks)} refinement tasks")
            for task in tasks:
                print(f"   - {task.get('type')}: {task.get('description', '')[:60]}...")
            
            return tasks
            
        except json.JSONDecodeError:
            return []
    
    def execute_refinement(self, task: Dict, existing_data: Any) -> Any:
        """Execute a refinement task."""
        print(f"\n  🔧 Executing: {task['type']}")
        
        if task['type'] == 'additional_search':
            # Worker does new search
            search_task = {
                'description': task['description'],
                'keywords': task['specifics'].get('keywords', []),
                'type': task['specifics'].get('type'),
                'min_score': task['specifics'].get('min_score'),
                'limit': 20,
                'goal': task['specifics'].get('goal', '')
            }
            result = self.worker.search_and_analyze(search_task)
            return result
        
        elif task['type'] == 'enhance_section':
            # Re-synthesize with additional requirements
            section_task = {
                'section_title': task['specifics'].get('section', 'Section'),
                'requirements': task['description']
            }
            enhanced = self.worker.synthesize_section(section_task, existing_data)
            return enhanced
        
        elif task['type'] == 'add_quotes':
            # Extract more quotes from existing data
            if isinstance(existing_data, list):
                posts = []
                for item in existing_data:
                    if isinstance(item, dict) and 'results' in item:
                        posts.extend(item['results'])
                
                # Create quote extraction task
                posts_subset = posts[:20]
                posts_data = []
                for post in posts_subset:
                    text = post.get('text', '')
                    if text:
                        text = text.replace('&#34;', '"').replace('&#39;', "'")[:1000]
                    posts_data.append({
                        'id': post['id'],
                        'author': post.get('by'),
                        'content': text
                    })
                
                extraction_prompt = f"""Extract 5 compelling quotes from these posts.

Posts: {json.dumps(posts_data, indent=2)}

For each quote:
- Select insightful, specific statements
- Include full context
- Attribute with Post #ID and author

JSON:
[
  {{"post_id": "...", "author": "...", "quote": "..."}}
]"""

                messages = [{"role": "user", "content": extraction_prompt}]
                response = self.call_llm(messages, temperature=0.4, max_tokens=1500)
                
                try:
                    if "```json" in response:
                        quotes = json.loads(response.split("```json")[1].split("```")[0].strip())
                    elif "```" in response:
                        quotes = json.loads(response.split("```")[1].split("```")[0].strip())
                    else:
                        quotes = json.loads(response.strip())
                    return quotes
                except:
                    return []
        
        return None
    
    def research_with_quality_control(self, question: str) -> str:
        """
        Main loop: Recursive research with quality enforcement.
        """
        print("\n" + "="*80)
        print("🎯 EDITOR AGENT - QUALITY-ENFORCED RESEARCH")
        print("="*80)
        print(f"\nQuestion: {question}")
        print(f"Budget: {self.max_calls} LLM calls")
        print(f"Model: {self.model}")
        
        # Phase 1: Planning
        plan = self.create_master_plan(question)
        
        # Phase 2: Execute search tasks
        print("\n" + "="*80)
        print("🔍 PHASE 2: RESEARCH EXECUTION")
        print("="*80)
        
        all_findings = []
        tasks_to_execute = plan['search_tasks'].copy()
        
        iteration = 0
        while tasks_to_execute and self.calls_used < self.max_calls - 5:  # Reserve calls
            iteration += 1
            print(f"\n--- Research Iteration {iteration} ---")
            
            # Execute batch of tasks
            batch = tasks_to_execute[:3]
            tasks_to_execute = tasks_to_execute[3:]
            
            for task in batch:
                if self.calls_used >= self.max_calls - 5:
                    break
                
                # Worker executes
                result = self.worker.search_and_analyze(task)
                
                # Editor evaluates
                evaluation = self.evaluate_work(
                    result['analysis'],
                    'search_results',
                    task['description']
                )
                
                if evaluation['acceptable']:
                    all_findings.append(result)
                else:
                    # Create refinement plan
                    if self.calls_used < self.max_calls - 3:
                        refinements = self.create_refinement_plan(evaluation, 'search_results')
                        if refinements:
                            # Add refinement tasks
                            for ref_task in refinements[:2]:
                                if ref_task.get('type') == 'additional_search':
                                    tasks_to_execute.append(ref_task.get('specifics', {}))
        
        print(f"\n✅ Research complete: {len(all_findings)} high-quality findings")
        
        # Phase 3: Synthesis with quality control
        print("\n" + "="*80)
        print("✍️  PHASE 3: SYNTHESIS WITH QUALITY CONTROL")
        print("="*80)
        
        sections = []
        for section_spec in plan['report_sections']:
            if self.calls_used >= self.max_calls - 3:
                print("\n⚠️  Budget low - using remaining findings as-is")
                break
            
            print(f"\n📝 Synthesizing: {section_spec['title']}")
            
            # Worker synthesizes
            section = self.worker.synthesize_section(
                {**section_spec, 'section_title': section_spec['title']},
                all_findings
            )
            
            # Editor evaluates
            evaluation = self.evaluate_work(section, 'section', section_spec['title'])
            
            if not evaluation['acceptable'] and self.calls_used < self.max_calls - 2:
                print("   ❌ Section rejected - refining...")
                
                # One refinement attempt
                refinements = self.create_refinement_plan(evaluation, 'section')
                if refinements:
                    enhanced = self.execute_refinement(refinements[0], all_findings)
                    if enhanced:
                        section = enhanced
            
            sections.append(f"## {section_spec['title']}\n\n{section}")
        
        # Assemble report
        report = "\n\n".join(sections)
        
        # Phase 4: Final quality check
        print("\n" + "="*80)
        print("🎓 PHASE 4: FINAL QUALITY CHECK")
        print("="*80)
        
        final_eval = self.evaluate_work(report, 'full_report', question)
        
        if final_eval['score'] < self.min_quality_score and self.calls_used < self.max_calls - 1:
            print("\n⚠️  Report below quality threshold - attempting final enhancement...")
            
            # One final enhancement pass
            refinements = self.create_refinement_plan(final_eval, 'full_report')
            if refinements and self.calls_used < self.max_calls:
                # Try to enhance the weakest section
                enhancement_prompt = f"""Enhance this research report based on feedback.

Current Report:
{report[:2000]}...

Issues: {json.dumps(final_eval.get('issues', []))}
Suggestions: {json.dumps(final_eval.get('suggestions', []))}

Rewrite to address issues while maintaining existing strengths.
Add more quotes, examples, and depth where needed."""

                messages = [{"role": "user", "content": enhancement_prompt}]
                try:
                    enhanced_report = self.call_llm(messages, temperature=0.7, max_tokens=8000)
                    report = enhanced_report
                    print("   ✅ Report enhanced")
                except:
                    print("   ⚠️  Enhancement failed - using original")
        
        print(f"\n✅ Final Score: {final_eval['score']}/10")
        print(f"   Budget Used: {self.calls_used}/{self.max_calls} calls")
        print(f"   Word Count: ~{len(report.split())} words")
        
        return report


def load_api_key():
    """Load API key."""
    api_key = os.environ.get('OPENROUTER_API_KEY') or os.environ.get('OPEN_ROUTER_KEY')
    
    if not api_key:
        env_path = Path('.env')
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('OPEN_ROUTER_KEY=') or line.startswith('OPENROUTER_API_KEY='):
                        api_key = line.split('=', 1)[1].strip('"\'')
                        break
    
    return api_key


def main():
    parser = argparse.ArgumentParser(
        description='Editor Agent - Quality-Enforced Recursive Research',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 20 LLM calls budget
  python3 editor_agent.py "analog computers" -o report.md --calls 20
  
  # 30 calls for more thorough research
  python3 editor_agent.py "startup advice" -o advice.md --calls 30
  
  # Budget mode (10 calls)
  python3 editor_agent.py "rust programming" -o rust.md --calls 10
        """
    )
    
    parser.add_argument('question', help='Research question')
    parser.add_argument('-o', '--output', required=True, help='Output markdown file')
    parser.add_argument('--calls', type=int, required=True,
                       help='LLM call budget (recommended: 15-30)')
    parser.add_argument('--model', default='anthropic/claude-3.5-sonnet',
                       help='LLM model (default: claude-3.5-sonnet)')
    parser.add_argument('--min-quality', type=float, default=7.0,
                       help='Minimum quality score (default: 7.0)')
    
    args = parser.parse_args()
    
    # Validate budget
    if args.calls < 10:
        print("⚠️  Warning: Less than 10 calls may produce subpar results")
    if args.calls > 50:
        print("⚠️  Warning: More than 50 calls may be unnecessary")
    
    # Load API key
    api_key = load_api_key()
    if not api_key:
        print("❌ Error: OpenRouter API key not found")
        return 1
    
    # Create editor agent
    editor = EditorAgent(api_key, args.model, args.calls)
    editor.min_quality_score = args.min_quality
    
    # Execute research with quality control
    try:
        report = editor.research_with_quality_control(args.question)
        
        # Add metadata
        metadata = f"""# {args.question.title()} - Quality-Controlled Research Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Research Question:** {args.question}  
**Model:** {args.model}  
**LLM Calls Used:** {editor.calls_used}/{args.calls}  
**Quality System:** Editor Agent with Recursive Refinement  
**Word Count:** ~{len(report.split())} words  

---

"""
        
        # Save
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(metadata + report, encoding='utf-8')
        
        print(f"\n✅ Report saved to: {args.output}")
        print(f"   Calls used: {editor.calls_used}/{args.calls}")
        print(f"   Efficiency: {(editor.calls_used/args.calls)*100:.1f}%")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())

