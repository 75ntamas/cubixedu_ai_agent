"""
Evaluator with LLM-as-a-Judge for tone assessment
"""
import os
import re
from typing import Dict
from openai import OpenAI


class ToneEvaluator:
    """LLM-as-a-Judge evaluator for tone/friendliness assessment"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the tone evaluator
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
    
    def evaluate_tone(self, user_message: str, assistant_response: str) -> Dict:
        """
        Evaluate the tone/friendliness of an assistant response
        
        Args:
            user_message: The user's question/message
            assistant_response: The assistant's response
            
        Returns:
            Dict with 'score' (0-3) and 'reasoning'
        """
        prompt = f"""Evaluate the TONE/FRIENDLINESS of the following AI assistant response on a 0-3 scale.

USER QUESTION:
{user_message}

AI ASSISTANT RESPONSE:
{assistant_response}

EVALUATION SCALE:
0 - Robotic, cold, overly formal. No friendliness or warmth.
1 - Somewhat friendly, but still stiff or too official. Lacks naturalness.
2 - Friendly and direct, but could be warmer or more personal.
3 - Warm, friendly, natural tone. Like advice from a good friend.

CONSIDER the following:
- Does it use natural, everyday expressions?
- Is there warmth and empathy?
- Can you feel that it wants to help, or does it just provide functionality?
- Is it overly formal or natural?
- Is it friendly or robotic?

Provide ONLY a score (0-3) and brief 1-2 sentence reasoning!

FORMAT:
Score: X
Reasoning: ...
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3  # Low temperature for consistent evaluation
            )
            
            result_text = response.choices[0].message.content
            
            # Parse the response
            score_match = re.search(r'Score:\s*(\d)', result_text)
            reasoning_match = re.search(r'Reasoning:\s*(.+)', result_text, re.DOTALL)
            
            if score_match and reasoning_match:
                score = int(score_match.group(1))
                reasoning = reasoning_match.group(1).strip()
                
                return {
                    "score": min(max(score, 0), 3),  # Clamp to 0-3
                    "reasoning": reasoning
                }
            else:
                # Fallback parsing
                return {
                    "score": -1,
                    "reasoning": f"Failed to parse: {result_text}"
                }
                
        except Exception as e:
            return {
                "score": -1,
                "reasoning": f"Error during evaluation: {str(e)}"
            }
    
    def evaluate_user_satisfaction(
        self, 
        persona_name: str,
        persona_description: str,
        goal: str,
        conversation: str
    ) -> Dict:
        """
        Simulate user satisfaction rating
        
        Args:
            persona_name: Name of the persona
            persona_description: Description of the persona
            goal: The goal the user had
            conversation: Full conversation history
            
        Returns:
            Dict with 'satisfaction' (1-5) and 'reasoning'
        """
        prompt = f"""You are a user who asked for cooking help from an AI assistant.

YOUR PERSONA: {persona_name} - {persona_description}
YOUR GOAL WAS: {goal}

CONVERSATION:
{conversation}

QUESTION: How satisfied are you with this conversation? (1-5 scale)
1 - Very dissatisfied (didn't get what I was looking for)
2 - Dissatisfied (only partially helped)
3 - Neutral (it was okay but could be better)
4 - Satisfied (got a good answer)
5 - Very satisfied (exactly what I was looking for!)

Provide a score and brief 1-2 sentence reasoning from your persona's perspective!

FORMAT:
Satisfaction: X
Reasoning: ...
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            
            result_text = response.choices[0].message.content
            
            # Parse the response
            satisfaction_match = re.search(r'Satisfaction:\s*(\d)', result_text)
            reasoning_match = re.search(r'Reasoning:\s*(.+)', result_text, re.DOTALL)
            
            if satisfaction_match and reasoning_match:
                satisfaction = int(satisfaction_match.group(1))
                reasoning = reasoning_match.group(1).strip()
                
                return {
                    "satisfaction": min(max(satisfaction, 1), 5),  # Clamp to 1-5
                    "reasoning": reasoning
                }
            else:
                return {
                    "satisfaction": -1,
                    "reasoning": f"Failed to parse: {result_text}"
                }
                
        except Exception as e:
            return {
                "satisfaction": -1,
                "reasoning": f"Error during evaluation: {str(e)}"
            }
