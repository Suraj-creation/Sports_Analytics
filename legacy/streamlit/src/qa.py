import streamlit as st
import datetime
from pathlib import Path
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

def load_llm():
    """Load LLM using the provider factory to avoid circular dependencies."""
    from core.llm_provider import LLMProviderFactory
    try:
        provider = LLMProviderFactory.create_provider()
        return provider._get_llm()
    except Exception as e:
        print(f"Failed to load LLM: {e}")
        # Fallback to original method if needed
        try:
            from app import load_llm as _load_llm
            return _load_llm()
        except:
            return None

def generate_qa_response(state):
    """Generates question and answer responses for sports analysis."""
    try:
        # Extract all necessary data from state
        player_names = state.get('player_names', 'the player(s)')
        semantics_analysis = state.get('semantics_analysis', 'No semantic analysis available.')
        retrieved_context = state.get('retrieved_context', 'No database context available.')
        question = state.get('question', '')
        highlight_rallies = state.get('highlight_rallies', [])
        sport_adapter = state.get('sport_adapter')

        # Get sport-specific information
        sport_name = sport_adapter.sport_name.title() if sport_adapter else "Sports"
        sport_terminology = sport_adapter.config.terminology if sport_adapter else {}

        # Get sport-specific Q&A prompt
        qa_prompt = None
        if sport_adapter and hasattr(sport_adapter.config, 'analysis'):
            qa_prompt = sport_adapter.config.analysis.get('qa_prompt')

        # Use generic prompt if no sport-specific one is available
        if not qa_prompt:
            qa_prompt = f"""You are an expert {sport_name.lower()} analyst answering questions about a {sport_name.lower()} match with deep technical knowledge and analytical insights.

Using the provided match data, performance analysis, and historical context, answer the user's question with:

1. **Technical Accuracy**: Provide precise, technically correct information about {sport_name.lower()} techniques, tactics, and rules
2. **Data-Driven Insights**: Reference specific rallies, shot types, and performance metrics from the match data
3. **Strategic Analysis**: Explain the tactical significance and decision-making behind specific plays
4. **Player Context**: Consider individual player styles, strengths, and historical performance
5. **Educational Value**: Help users understand {sport_name.lower()} concepts, techniques, and strategies

Available Match Data:
- Rally details with timestamps, shot types, and outcomes
- Player performance statistics and key metrics
- Technical analysis of shots, footwork, and court coverage
- Historical context and player background information

Question:
{{question}}

Match Data:
{{semantics_analysis}}

Historical Context:
{{retrieved_context}}
Player Names:
{{player_names}}

Provide a comprehensive, technically accurate answer that combines match-specific insights with general {sport_name.lower()} knowledge."""

        # Token limit safety
        safe_semantics = semantics_analysis[:2500] if semantics_analysis else "No semantic analysis available."
        safe_context = retrieved_context[:1000] if retrieved_context else "No database context available."
        safe_question = question[:500] if question else "No specific question provided - provide comprehensive analysis ready for follow-up questions."

        prompt_vars = {
            'semantics_analysis': safe_semantics,
            'enhanced_semantics': safe_semantics,
            'retrieved_context': safe_context,
            'question': safe_question,
            'player_names': player_names
        }

        # Generate response
        prompt = PromptTemplate.from_template(qa_prompt)
        llm = load_llm()

        if not llm:
            return {"generation": "LLM not available for Q&A response generation."}

        final_chain = prompt | llm | StrOutputParser()

        with st.spinner("Generating expert Q&A response with AI..."):
            try:
                generation = final_chain.invoke(prompt_vars)
                
                # Add follow-up prompt for Q&A if no specific question
                if not question:
                    generation += "\n\n🎯 **Analysis Complete!** You can now ask specific questions about this performance such as:\n"
                    generation += "- 'How effective were the smash shots?'\n"
                    generation += "- 'What were the key turning points?'\n"
                    generation += "- 'Which player dominated the net play?'\n"
                    generation += "- 'How did the players perform in crucial moments?'"
                
                # Add data insight if rallies were analyzed
                if highlight_rallies:
                    generation += f"\n\n📊 **Based on analysis of {len(highlight_rallies)} key rallies with detailed timestamp and performance data.**"

            except Exception as e:
                st.error(f"Q&A generation failed: {e}")
                generation = f"""💬 **Q&A Analysis for {player_names}**

**Question:** {question if question else 'General Analysis'}

**Based on available information:**
{safe_semantics if safe_semantics and 'No semantic analysis' not in safe_semantics else 'Semantic analysis was not available.'}

⚠️ **Note:** Full Q&A analysis couldn't be completed due to error: {str(e)}

**Fallback Response:**
The system has processed the available match data but encountered technical issues generating the detailed response. Please try rephrasing your question or ask about specific aspects like shot types, scores, or player techniques."""

        # Save results to files
        try:
            # Get project root from app module
            from app import PROJECT_ROOT
            output_dir = Path(PROJECT_ROOT) / 'output'
            output_dir.mkdir(exist_ok=True)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            player_safe = "".join(c if c.isalnum() else "_" for c in state.get('player_names', 'output'))

            if question:
                question_short = question[:30].replace(' ', '_')
                question_safe = "".join(c if c.isalnum() or c == '_' else '' for c in question_short)
                filename = f"{player_safe}_qa_{question_safe}_{timestamp}.txt"
            else:
                filename = f"{player_safe}_comprehensive_qa_{timestamp}.txt"

            output_path = output_dir / filename

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Player(s): {state.get('player_names', 'N/A')}\n")
                f.write(f"Task: Expert Q&A Analysis\n")
                f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                if question:
                    f.write(f"Question: {question}\n")
                if highlight_rallies:
                    f.write(f"Rally Data Points: {len(highlight_rallies)}\n")
                f.write("\n" + "="*50 + "\n\n")
                f.write(generation)

            st.success(f"Q&A analysis saved to: {filename}")
            
            # Provide download button
            st.download_button(
                label="📥 Download Q&A Analysis",
                data=generation,
                file_name=filename,
                mime="text/plain"
            )

        except Exception as e:
            st.warning(f"Could not save Q&A output file: {e}")

        return {"generation": generation}

    except Exception as e:
        st.error(f"Critical error during Q&A generation: {e}")
        return {"generation": f"Q&A analysis failed due to error: {str(e)}"}