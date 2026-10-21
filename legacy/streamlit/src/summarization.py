import streamlit as st
import datetime
import json
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

def parse_json_response(response_text):
    """Try to parse JSON response, fall back to plain text if fails."""
    # First, clean the response text
    cleaned_text = response_text.strip()
    
    # Remove any markdown code block markers if present
    if cleaned_text.startswith('```json'):
        cleaned_text = cleaned_text[7:]
    if cleaned_text.startswith('```'):
        cleaned_text = cleaned_text[3:]
    if cleaned_text.endswith('```'):
        cleaned_text = cleaned_text[:-3]
    cleaned_text = cleaned_text.strip()
    
    try:
        # Try to parse as JSON directly first
        result = json.loads(cleaned_text)
        # Ensure we have the expected structure
        if 'summary' in result:
            return {'summary': result['summary']}
        return result
    except json.JSONDecodeError:
        # If direct parse fails, try to extract JSON from the text
        try:
            start_idx = cleaned_text.find('{')
            end_idx = cleaned_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = cleaned_text[start_idx:end_idx]
                result = json.loads(json_str)
                if 'summary' in result:
                    return {'summary': result['summary']}
                return result
        except:
            pass
    
    # Fallback to plain text parsing
    return {'summary': cleaned_text}

def display_formatted_summary(summary_data):
    """Display the summary in a nicely formatted way."""
    st.subheader("📊 Match Summary")
    
    if isinstance(summary_data, dict):
        # Display the main summary paragraph
        if "summary" in summary_data:
            st.write(summary_data["summary"])
        elif "match_summary" in summary_data:  # Fallback for old format
            st.write(summary_data["match_summary"])
        else:
            st.write("No summary content available.")
    else:
        # Fallback for plain text
        st.write(summary_data)

def generate_summarization_response(state):
    """Generates performance summary for sports analysis."""
    try:
        # Extract all necessary data from state
        player_names = state.get('player_names', 'the player(s)')
        semantics_analysis = state.get('semantics_analysis', 'No semantic analysis available.')
        retrieved_context = state.get('retrieved_context', 'No database context available.')
        sport_adapter = state.get('sport_adapter')

        # Get sport-specific information
        sport_name = sport_adapter.sport_name.title() if sport_adapter else "Sports"
        sport_terminology = sport_adapter.config.terminology if sport_adapter else {}

        # Get sport-specific summarization prompt
        summarization_prompt = None
        if sport_adapter and hasattr(sport_adapter.config, 'analysis'):
            summarization_prompt = sport_adapter.config.analysis.get('summarization_prompt')

        # Use generic prompt if no sport-specific one is available
        if not summarization_prompt:
            summarization_prompt = f"""You are an expert {sport_name.lower()} analyst creating a concise yet comprehensive match summary.

MATCH DATA:
{{semantics_analysis}}

CONTEXT:
{{retrieved_context}}

Generate a single, well-structured paragraph (approximately 150-200 words) that captures the essence of the match. Focus on:
- Key moments and turning points
- Player performances and standout plays
- Tactical approaches and their effectiveness
- The overall flow and outcome of the match

Write in a clear, engaging narrative style suitable for sports enthusiasts. Avoid bullet points and section headers - just one cohesive paragraph that tells the story of the match.

Format your response as a JSON object with a single field called "summary". Example:
{{
  "summary": "[Your paragraph here]"
}}"""

        # Token limit safety
        safe_semantics = semantics_analysis[:2500] if semantics_analysis else "No semantic analysis available."
        safe_context = retrieved_context[:1000] if retrieved_context else "No database context available."

        prompt_vars = {
            'semantics_analysis': safe_semantics,
            'retrieved_context': safe_context
        }

        # Generate response
        prompt = PromptTemplate.from_template(summarization_prompt)
        llm = load_llm()

        if not llm:
            st.error("LLM not available for summarization.")
            return {"generation": "LLM not available for summarization."}

        final_chain = prompt | llm | StrOutputParser()

        with st.spinner("Generating match summary..."):
            try:
                # Get the raw generation
                raw_generation = final_chain.invoke(prompt_vars)
                
                # Parse the response
                parsed_summary = parse_json_response(raw_generation)
                
                # Extract and clean the summary text from the parsed response
                if isinstance(parsed_summary, dict):
                    # Try to get the summary from various possible keys
                    summary_text = parsed_summary.get('summary', 
                                                   parsed_summary.get('match_summary', 
                                                                   str(parsed_summary)))
                else:
                    summary_text = str(parsed_summary)
                
                # Clean up the summary text
                if summary_text:
                    # Remove JSON artifacts and unwanted patterns
                    cleanup_patterns = [
                        r'{\s*"summary"\s*:',  # Remove leading {"summary":
                        r'"\s*}\s*$',         # Remove trailing "}
                        r'^\s*"|\s*"$',       # Remove leading/trailing quotes
                        r'\\"',                # Remove escaped quotes
                    ]
                    
                    import re
                    for pattern in cleanup_patterns:
                        summary_text = re.sub(pattern, '', summary_text, flags=re.IGNORECASE)
                    
                    # Remove any remaining JSON control characters
                    summary_text = summary_text.strip().rstrip(',').strip()
                    
                    # Remove any remaining quotes if they don't make sense
                    if summary_text.startswith('"') and summary_text.endswith('"'):
                        summary_text = summary_text[1:-1].strip()
                
                # Display formatted summary with header
                st.success("✅ Match Summary Generated Successfully!")
                st.markdown("## 🏆 Match Summary")
                st.markdown("---")  # Add a horizontal line for separation
                st.write(summary_text)
                
                # Prepare text for file saving
                if isinstance(parsed_summary, dict):
                    # Clean up the summary text if it's a dictionary
                    match_summary = parsed_summary.get('match_summary', summary_text)
                    if match_summary and isinstance(match_summary, str):
                        match_summary = match_summary.replace('match_summary:', '').strip()
                    
                    # Get key stats and insights if available
                    key_stats = parsed_summary.get('key_statistics', [])
                    insights = parsed_summary.get('strategic_insights', [])
                    
                    # Use the summary text as fallback if match_summary is not available
                    generation_text = match_summary if match_summary else summary_text
                    
                    # Update parsed_summary with cleaned data
                    if isinstance(parsed_summary, dict):
                        parsed_summary.update({
                            'match_summary': match_summary,
                            'key_statistics': key_stats,
                            'strategic_insights': insights
                        })
                else:
                    generation_text = str(parsed_summary).replace('match_summary:', '').strip()

            except Exception as e:
                st.error(f"Summarization failed: {e}")
                error_msg = f"Error: {str(e)}"
                generation_text = error_msg
                parsed_summary = error_msg

        # Save results to files
        try:
            # Get project root from app module
            from app import PROJECT_ROOT
            output_dir = Path(PROJECT_ROOT) / 'output'
            output_dir.mkdir(exist_ok=True)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            player_safe = "".join(c if c.isalnum() else "_" for c in str(player_names))

            filename = f"{player_safe}_performance_summary_{timestamp}.txt"
            output_path = output_dir / filename  # Fix: Define output_path properly
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Player(s): {player_names}\n")
                f.write(f"Sport: {sport_name}\n")
                f.write("Task: Performance Summary Analysis\n")
                f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n" + "="*50 + "\n\n")
                f.write(generation_text)

            
            # Generate PDF and audio reports using utility modules
            try:
                from utils.pdf_generator import generate_pdf_report
                from utils.audio_generator import generate_audio_report
                
                # Determine if this is a highlights or summary task
                is_highlights_task = state.get('task') == 'highlights'
                
                # Generate PDF with appropriate title and content
                pdf_path = generate_pdf_report(
                    sport_name=sport_name,
                    player_names=player_names,
                    selected_highlights=[] if not is_highlights_task else state.get('highlight_rallies', []),
                    generation_text=generation_text,
                    is_summary=not is_highlights_task,  # Pass whether this is a summary
                    return_bytes=False,
                    output_dir=str(output_dir)
                )
                
                # Generate Audio with appropriate content
                audio_path = generate_audio_report(
                    sport_name=sport_name.lower(),
                    player_names=player_names,
                    selected_highlights=[] if not is_highlights_task else state.get('highlight_rallies', []),
                    generation_text=generation_text,
                    is_summary=not is_highlights_task,  # Pass whether this is a summary
                    return_bytes=False,
                    output_dir=str(output_dir)
                )
                
                    
            except Exception as e:
                st.warning(f"Could not generate PDF/Audio reports: {e}")

            # Create a clean output directory
            download_dir = output_dir / 'downloads'
            download_dir.mkdir(exist_ok=True)
            
            # Don't save text and JSON files separately anymore
            
            # Create a zip file containing PDF and audio assets
            import zipfile
            import os
            zip_path = download_dir / f"{Path(filename).stem}_assets.zip"
            has_assets = False
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                # Add PDF if exists
                if 'pdf_path' in locals() and pdf_path and os.path.exists(pdf_path):
                    zipf.write(pdf_path, arcname=os.path.basename(pdf_path))
                    has_assets = True
                # Add audio if exists
                if 'audio_path' in locals() and audio_path and os.path.exists(audio_path):
                    zipf.write(audio_path, arcname=os.path.basename(audio_path))
                    has_assets = True
            
            # Remove the zip if no assets were added
            if not has_assets and os.path.exists(zip_path):
                os.remove(zip_path)
                zip_path = None
            
            # Display download and action in two columns (consistent with highlights UI)
            with st.container():
                st.markdown("### Download Assets")
                col1, col2 = st.columns(2)
                with col1:
                    if zip_path and os.path.exists(zip_path):
                        with open(zip_path, 'rb') as f:
                            st.download_button(
                                label="📦 Download Match Assets (ZIP)",
                                data=f,
                                file_name=zip_path.name,
                                mime="application/zip",
                                use_container_width=True,
                                help="Download a ZIP file containing PDF and audio summaries"
                            )
                    else:
                        st.info("No downloadable assets available yet.")
                with col2:
                    if st.button("🔄 Process Another Match", use_container_width=True):
                        st.rerun()

        except Exception as e:
            st.warning(f"Could not save summary output file: {e}")

    except Exception as e:
        st.error(f"Critical error during summarization: {e}")
        return {"generation": f"Performance summary failed due to error: {str(e)}"}