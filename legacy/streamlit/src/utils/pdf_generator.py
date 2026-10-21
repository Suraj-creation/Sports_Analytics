"""
PDF generation utility - sport-agnostic PDF report generation.
"""
import os
from typing import List, Dict, Optional
from pathlib import Path
from .text_processing import remove_emojis


def generate_pdf_report(
    sport_name: str,
    player_names: str, 
    selected_highlights: List[Dict] = None, 
    generation_text: str = "",
    is_summary: bool = False,
    return_bytes: bool = False,
    output_dir: Optional[str] = None
):
    """
    Generate a clean PDF report from the highlights text with no emojis and left alignment.
    
    Args:
        sport_name: Name of the sport (e.g., "Badminton", "Tennis")
        player_names: Names of the players for the title
        selected_highlights: List of highlight dictionaries (optional)
        generation_text: The text content to include in the PDF
        return_bytes: If True, returns the PDF as bytes instead of saving to file
        output_dir: Directory to save the PDF (optional)
        
    Returns:
        If return_bytes is True, returns the PDF as bytes. Otherwise, returns None.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.units import inch
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib import colors
        from io import BytesIO
        import datetime
        
        # Create a buffer to store PDF
        buffer = BytesIO()
        
        # Create the PDF object with left alignment
        doc = SimpleDocTemplate(buffer, 
                              pagesize=letter,
                              rightMargin=72, 
                              leftMargin=72,
                              topMargin=72, 
                              bottomMargin=72)
        
        # Set up styles with left alignment and clean fonts
        styles = getSampleStyleSheet()
        
        # Define custom style names to avoid conflicts
        custom_styles = {
            'Custom_Left': {
                'alignment': TA_LEFT,
                'fontSize': 11,
                'leading': 14,
                'fontName': 'Helvetica'
            },
            'Custom_Title': {
                'alignment': TA_LEFT,
                'fontSize': 16,
                'leading': 20,
                'spaceAfter': 20,
                'fontName': 'Helvetica-Bold'
            },
            'Custom_Heading2': {
                'alignment': TA_LEFT,
                'fontSize': 14,
                'leading': 16,
                'spaceAfter': 10,
                'fontName': 'Helvetica-Bold'
            }
        }
        
        # Add custom styles
        for style_name, style_attrs in custom_styles.items():
            if style_name not in styles:
                styles.add(ParagraphStyle(style_name, **style_attrs))
        
        # Use the custom styles directly
        left_style = styles['Custom_Left']
        title_style = styles['Custom_Title']
        heading2_style = styles['Custom_Heading2']
        
        # Create story (list of Flowable objects)
        story = []
        
        # Clean player names and title
        clean_player_names = remove_emojis(player_names)
        sport_title = sport_name.upper()
        
        # Title with clean formatting - sport-agnostic
        if is_summary:
            story.append(Paragraph(f"{sport_title} MATCH SUMMARY", title_style))
            story.append(Spacer(1, 5))
            story.append(Paragraph(clean_player_names, title_style))
            story.append(Spacer(1, 20))
            
            # Add generation text directly for summaries
            if generation_text:
                story.append(Paragraph("MATCH OVERVIEW", heading2_style))
                clean_generation = remove_emojis(generation_text)
                story.append(Paragraph(clean_generation, left_style))
                story.append(Spacer(1, 20))
        else:
            # Highlights-specific content
            story.append(Paragraph(f"{sport_title} MATCH HIGHLIGHTS", title_style))
            story.append(Spacer(1, 5))
            story.append(Paragraph(clean_player_names, title_style))        
            story.append(Spacer(1, 20))

            # Match Introduction for highlights
            story.append(Paragraph("MATCH INTRODUCTION", heading2_style))
            story.append(Paragraph("The match begins with player introductions and preparation.", left_style))
            story.append(Spacer(1, 20))
        
        # Highlights section
        if selected_highlights:
            story.append(Paragraph("HIGHLIGHTS", heading2_style))
            story.append(Spacer(1, 10))
            
            for i, rally in enumerate(selected_highlights, 1):
                start_time = rally.get('start_time', '00:00')
                end_time = rally.get('end_time', '00:00')
                win_player = rally.get('win_point_player', 'Unknown')
                ball_types = rally.get('ball_types', 'Unknown')
                
                # Capitalize ball types
                if ball_types and ball_types != 'Unknown':
                    ball_types = ', '.join([shot.strip().title() for shot in ball_types.split(',')])
                
                highlight_text = [
                    f"<b>HIGHLIGHT {i}: {start_time} - {end_time}</b>",
                    f"Player: {win_player}"
                ]
                
                # Add AI reasoning if available
                if 'ai_reasoning' in rally and rally['ai_reasoning'] not in ["", "AI analysis unavailable"]:
                    highlight_text.append(f"Analysis: {remove_emojis(rally['ai_reasoning'])}")
                
                # Add to story with consistent spacing
                story.append(Paragraph('<br/>'.join(highlight_text), left_style))
                story.append(Spacer(1, 12))
        
        # Note: DETAILED ANALYSIS section removed as per user request
        
        # Build PDF
        doc.build(story)
        
        # Get the PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        if return_bytes:
            return pdf_bytes
            
        # Save the PDF to a file if output_dir is provided
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            player_safe = "".join(c if c.isalnum() else "_" for c in player_names)
            pdf_filename = f"{player_safe}_{sport_name.lower()}_highlights_{timestamp}.pdf"
            pdf_path = os.path.join(output_dir, pdf_filename)
            
            with open(pdf_path, "wb") as pdf_file:
                pdf_file.write(pdf_bytes)
            
            return pdf_path
        
        return pdf_bytes
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        if return_bytes:
            return None
        return None
