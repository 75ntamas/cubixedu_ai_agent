"""
Main evaluation script for multi-turn agent testing
"""
import json
import os
import sys
from datetime import datetime
from typing import Dict, List
import requests
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from personas import get_all_scenarios
from evaluator import ToneEvaluator


class ChatAPI:
    """Interface to the Next.js chat API"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.chat_endpoint = f"{base_url}/api/chat"
    
    def send_message(self, messages: List[Dict[str, str]]) -> str:
        """
        Send messages to the chat API and get response
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            The assistant's response text
        """
        try:
            response = requests.post(
                self.chat_endpoint,
                json={"messages": messages},
                stream=True,
                timeout=60
            )
            
            if response.status_code != 200:
                return f"Error: API returned status {response.status_code}"
            
            # Collect the streamed response
            full_text = ""
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    # Server-Sent Events format: lines start with numbers like "0:"
                    if ':' in line and line[0].isdigit():
                        # Extract the text content after the colon
                        parts = line.split(':', 1)
                        if len(parts) > 1:
                            content = parts[1].strip()
                            # Remove quotes if present
                            if content.startswith('"') and content.endswith('"'):
                                content = content[1:-1]
                            # Unescape common characters
                            content = content.replace('\\n', '\n').replace('\\"', '"')
                            full_text += content
            
            return full_text if full_text else "No response received"
            
        except requests.exceptions.Timeout:
            return "Error: Request timed out"
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to API. Is the Next.js server running?"
        except Exception as e:
            return f"Error: {str(e)}"


def run_evaluation(
    iteration_name: str,
    output_dir: str,
    api_url: str = "http://localhost:3000"
) -> Dict:
    """
    Run full evaluation suite
    
    Args:
        iteration_name: Name of this iteration (e.g., 'baseline', 'iteration_1')
        output_dir: Directory to save results
        api_url: Base URL of the chat API
        
    Returns:
        Dict with evaluation results and summary
    """
    print(f"\n{'='*60}")
    print(f"Running Evaluation: {iteration_name}")
    print(f"{'='*60}\n")
    
    # Initialize components
    chat_api = ChatAPI(api_url)
    evaluator = ToneEvaluator()
    
    # Get all test scenarios
    scenarios = get_all_scenarios()
    
    # Results storage
    results = {
        "iteration_name": iteration_name,
        "timestamp": datetime.now().isoformat(),
        "api_url": api_url,
        "total_scenarios": len(scenarios),
        "scenarios": []
    }
    
    # Run each scenario
    for i, (persona, scenario) in enumerate(scenarios, 1):
        print(f"[{i}/{len(scenarios)}] Testing: {persona.name} - {scenario.goal}")
        
        # Send message to chat API
        assistant_response = chat_api.send_message(scenario.messages)
        
        # Extract user message for evaluation
        user_message = scenario.messages[0]["content"]
        
        # Evaluate tone
        print("  > Evaluating tone...")
        tone_eval = evaluator.evaluate_tone(user_message, assistant_response)
        
        # Format conversation for satisfaction evaluation
        conversation = f"User: {user_message}\n\nAssistant: {assistant_response}"
        
        # Evaluate user satisfaction
        print("  > Evaluating satisfaction...")
        satisfaction_eval = evaluator.evaluate_user_satisfaction(
            persona.name,
            persona.description,
            scenario.goal,
            conversation
        )
        
        # Store results
        scenario_result = {
            "scenario_number": i,
            "persona": {
                "name": persona.name,
                "description": persona.description,
                "characteristics": persona.characteristics
            },
            "goal": scenario.goal,
            "conversation": {
                "user_message": user_message,
                "assistant_response": assistant_response,
                "response_length": len(assistant_response)
            },
            "evaluation": {
                "tone": tone_eval,
                "satisfaction": satisfaction_eval
            }
        }
        
        results["scenarios"].append(scenario_result)
        
        print(f"  > Tone Score: {tone_eval['score']}/3")
        print(f"  > Satisfaction: {satisfaction_eval['satisfaction']}/5")
        print()
    
    # Calculate summary statistics
    tone_scores = [s["evaluation"]["tone"]["score"] for s in results["scenarios"] if s["evaluation"]["tone"]["score"] >= 0]
    satisfaction_scores = [s["evaluation"]["satisfaction"]["satisfaction"] for s in results["scenarios"] if s["evaluation"]["satisfaction"]["satisfaction"] >= 0]
    
    results["summary"] = {
        "average_tone_score": sum(tone_scores) / len(tone_scores) if tone_scores else 0,
        "average_satisfaction": sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0,
        "tone_scores_distribution": {
            "0": tone_scores.count(0),
            "1": tone_scores.count(1),
            "2": tone_scores.count(2),
            "3": tone_scores.count(3)
        },
        "satisfaction_distribution": {
            str(i): satisfaction_scores.count(i) for i in range(1, 6)
        },
        "total_valid_evaluations": len(tone_scores)
    }
    
    # Save results
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{iteration_name}_results.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Evaluation Complete: {iteration_name}")
    print(f"{'='*60}")
    print(f"Average Tone Score: {results['summary']['average_tone_score']:.2f}/3")
    print(f"Average Satisfaction: {results['summary']['average_satisfaction']:.2f}/5")
    print(f"Results saved to: {output_file}")
    print(f"{'='*60}\n")
    
    return results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run agent evaluation')
    parser.add_argument('--iteration', required=True, help='Iteration name (e.g., baseline, iteration_1)')
    parser.add_argument('--output-dir', default='evaluation/results', help='Output directory for results')
    parser.add_argument('--api-url', default='http://localhost:3000', help='Chat API base URL')
    
    args = parser.parse_args()
    
    # Check if API is accessible
    try:
        response = requests.get(args.api_url, timeout=5)
        print(f"[OK] API server is accessible at {args.api_url}")
    except:
        print(f"[WARNING] Could not connect to API at {args.api_url}")
        print("  Make sure the Next.js server is running (npm run dev)")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Run evaluation
    run_evaluation(args.iteration, args.output_dir, args.api_url)


if __name__ == "__main__":
    main()
