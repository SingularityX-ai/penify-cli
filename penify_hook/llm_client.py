import json
import os
from typing import Dict, Optional, List, Any, Union
import litellm

class LLMClient:
    """
    Client for interacting with LLM models using LiteLLM.
    """
    
    def __init__(self, model: str = None, api_base: str = None, api_key: str = None):
        """
        Initialize the LLM client.
        
        Args:
            model: LLM model to use (e.g., "gpt-4", "ollama/llama2", etc.)
            api_base: Base URL for API requests (e.g., "http://localhost:11434" for Ollama)
            api_key: API key for the LLM service
        """
        self.model = model
        self.api_base = api_base
        self.api_key = api_key
        
        # Configure litellm if parameters are provided
        if api_base:
            os.environ["OPENAI_API_BASE"] = api_base
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
    
    def generate_commit_summary(self, diff: str, message: str, repo_details: Dict) -> Dict:
        """
        Generate a commit summary using the LLM.
        
        Args:
            diff: Git diff of changes
            message: User-provided commit message or instructions
            repo_details: Details about the repository
            
        Returns:
            Dict with title and description for the commit
        """
        if not self.model:
            raise ValueError("LLM model not configured. Please provide a model when initializing LLMClient.")
        
        # Limit diff size to avoid token limits
        max_diff_chars = 10000
        if len(diff) > max_diff_chars:
            diff = diff[:max_diff_chars] + f"\n... (diff truncated, total {len(diff)} characters)"
        
        # Create prompt for the LLM
        prompt = f"""
        Based on the Git diff below, generate a concise and descriptive commit summary.
        
        Repository: {repo_details.get('organization_name')}/{repo_details.get('repo_name')}
        Hosted on: {repo_details.get('vendor', 'Unknown')}
        
        User instructions: {message}
        
        Git diff:
        ```
        {diff}
        ```
        
        Please provide:
        1. A short, focused commit title (50-72 characters)
        2. A more detailed description of the changes
        
        Format your response as valid JSON with 'title' and 'description' keys.
        """
        
        try:
            # Call the LLM using litellm
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON from the response
            try:
                # Try to parse the entire content as JSON
                result = json.loads(content)
                if not isinstance(result, dict) or 'title' not in result or 'description' not in result:
                    raise ValueError("Invalid JSON structure")
                    
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from the content
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                else:
                    # Last resort: extract title and description directly
                    lines = content.split('\n')
                    title = next((line for line in lines if line.strip()), "Generated commit").strip()
                    description = "\n".join(line for line in lines[1:] if line.strip())
                    result = {
                        "title": title,
                        "description": description
                    }
            
            return result
            
        except Exception as e:
            # Fallback to a basic summary if LLM fails
            print(f"Error generating commit summary with LLM: {e}")
            return {
                "title": "Update code",
                "description": f"Changes were made to the repository.\n\nUser message: {message}"
            }
