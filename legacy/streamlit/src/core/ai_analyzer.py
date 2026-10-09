"""
Sport-agnostic AI analysis module for rally analysis.
"""
from typing import Dict, Any
from .llm_provider import LLMProvider


def analyze_rally_with_ai(rally: Dict, sport_adapter: Any, llm_provider: LLMProvider) -> Dict:
    """Analyze a rally using AI to enhance the excitement score."""
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    
    try:
        # Get sport-specific highlights prompt from config
        config = sport_adapter.config
        prompt_template = getattr(config, 'highlights_prompt', None)
        
        # If config doesn't have the highlights prompt, try to get from analysis section
        if not prompt_template and hasattr(config, 'analysis'):
            prompt_template = config.analysis.get('highlights_prompt', None)
        
        # Fallback to generic prompt if sport-specific one not found
        if not prompt_template:
            sport_name = getattr(sport_adapter, 'sport_name', 'sport')
            prompt_template = f"""
Analyze this {sport_name} rally and explain why it deserves to be a highlight in exactly 120 words or less.
Focus on what made this rally exciting and spectacular for viewers.

Consider these factors:
- Shot variety and complexity
- Player movement and court coverage
- Rally length and intensity
- Technical brilliance (perfect placement, power, timing)
- Dramatic moments
- Entertainment value for spectators

Rally Data:
{{rally_data}}

Return a JSON with:
- score: number from 0-10 (excitement level)
- reasoning: explain in 60 words why this rally is highlight-worthy
- highlight_worthy: boolean
"""
        
        # Format rally data for the prompt
        rally_data = "\n".join(f"{k}: {v}" for k, v in rally.items())
        
        # Create the chain
        prompt = ChatPromptTemplate.from_template(prompt_template)
        llm = llm_provider._get_llm()  # Get the actual LLM instance
        chain = prompt | llm | JsonOutputParser()
        
        # Get AI analysis
        result = chain.invoke({"rally_data": rally_data})
        
        # Update rally with AI analysis
        rally['ai_score'] = float(result.get('score', 0))
        rally['ai_reasoning'] = result.get('reasoning', '')
        rally['highlight_worthy'] = result.get('highlight_worthy', False)
        
    except Exception as e:
        print(f"AI analysis failed: {e}")
        # Fallback to original score if AI fails
        rally['ai_score'] = rally.get('excitement_score', 0) / 10  # Scale 0-10
        rally['ai_reasoning'] = "AI analysis unavailable"
        rally['highlight_worthy'] = rally.get('excitement_score', 0) > 5
    
    return rally
