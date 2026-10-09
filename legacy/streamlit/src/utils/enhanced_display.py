"""
Enhanced Display Module for Highlights with Video Integration
This module provides an updated display_highlights_in_streamlit function
that supports video embedding with AI narration.
"""

import streamlit as st
import os
from typing import List, Dict
from utils.video_highlight_processor import extract_and_narrate_highlight


def display_highlights_in_streamlit(generation: str, selected_highlights: List[Dict], 
                                    player_names: str, sport_name: str = "Sports", 
                                    video_url: str = None):
    """
    Display highlights content in Streamlit web interface with proper formatting.
    If video_url is provided, embed video clips with AI narration for each highlight.
    
    Args:
        generation: Generated text content
        selected_highlights: List of highlight dictionaries
        player_names: Player names string
        sport_name: Name of the sport
        video_url: Optional path to video file
    """
    try:
        # Display main title
        st.title(f"🎬 {sport_name.title()} Match Highlights")
        st.subheader(f"📊 {player_names} Match Highlights")
        
        # Check if video URL is provided and accessible
        video_available = False
        video_path = None
        if video_url:
            video_path = os.path.normpath(video_url.strip('"\''))
            if os.path.exists(video_path) and os.access(video_path, os.R_OK):
                video_available = True
                st.info(f"📹 Video highlights will be displayed with AI narration")
            else:
                st.warning(f"Video file not accessible. Showing text highlights only.")
        
        for i, highlight in enumerate(selected_highlights, 1):
            start_time = highlight.get('start_time', '00:00')
            end_time = highlight.get('end_time', '00:00')
            duration = highlight.get('duration', 0)
            win_player = highlight.get('win_point_player', 'Player')
            ai_reasoning = highlight.get('ai_reasoning', '')
            
            # Create expandable section for each highlight (first one expanded by default)
            with st.expander(f"🎯 Highlight {i}: {start_time} - {end_time}", expanded=(i == 1)):
                # Display basic info
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Duration:** {duration} seconds")
                with col2:
                    st.write(f"**Winner:** {win_player}")
                
                st.divider()
                
                # If video is available, extract and display video clip with AI narration
                if video_available and video_path:
                    try:
                        with st.spinner(f"Creating video clip {i} with AI narration..."):
                            video_clip_path = extract_and_narrate_highlight(
                                video_path=video_path,
                                start_time=start_time,
                                end_time=end_time,
                                ai_narration=ai_reasoning if ai_reasoning and ai_reasoning != "AI analysis unavailable" else None,
                                highlight_index=i,
                                player_names=player_names
                            )
                        
                        if video_clip_path and os.path.exists(video_clip_path):
                            # Display video clip
                            st.video(video_clip_path)
                            st.caption("🔊 Video with AI narration audio")
                        else:
                            st.warning("Could not create video clip for this highlight")
                            # Fallback to text display
                            display_text_highlight_info(highlight)
                    except Exception as e:
                        st.error(f"Error creating video clip: {str(e)}")
                        display_text_highlight_info(highlight)
                else:
                    # Display text-based highlight info
                    display_text_highlight_info(highlight)
                
                # Always display AI analysis regardless of video availability
                display_ai_analysis(highlight)
        
        return True
        
    except Exception as e:
        st.error(f"Error displaying highlights: {str(e)}")
        return False


def display_text_highlight_info(highlight: Dict):
    """Helper function to display text-based highlight information."""
    # Display shots/actions if available
    ball_types = highlight.get('ball_types', '')
    if ball_types:
        st.write(f"**Key Actions:** {ball_types}")


def display_ai_analysis(highlight: Dict):
    """Helper function to display AI analysis for highlights."""
    ai_reasoning = highlight.get('ai_reasoning', '')
    if ai_reasoning and ai_reasoning != "AI analysis unavailable":
        st.write("**🤖 AI Analysis:**")
        st.info(ai_reasoning)
    else:
        st.write("**🤖 AI Analysis:**")
        st.warning("AI analysis not available for this highlight")
