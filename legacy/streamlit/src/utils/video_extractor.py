#!/usr/bin/env python3
"""
Video Highlights Extractor using FFmpeg - FIXED VERSION
Extracts timestamped segments and creates highlights compilation with captions
Fixed issues with video playback getting stuck and improved smoothness
"""

import re
import os
import subprocess
import tempfile
import json
from pathlib import Path

def parse_timestamps_from_file(text_file_path):
    """
    Parse timestamps and descriptions from the text file
    Returns list of tuples: (start_time, end_time, description)
    """
    segments = []
    
    with open(text_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    print(f"Total lines in file: {len(lines)}")
    
    # More flexible pattern to match timestamps
    timestamp_pattern = r'\[(\d{1,2}:\d{2})\s*[-–—]\s*(\d{1,2}:\d{2})\]'
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
            
        # Look for timestamp pattern
        match = re.search(timestamp_pattern, line)
        if match:
            start_time = match.group(1)
            end_time = match.group(2)
            
            # Get description - could be on same line or next lines
            description_parts = []
            
            # Check if there's description on the same line after the timestamp
            remaining_line = line[match.end():].strip()
            if remaining_line:
                description_parts.append(remaining_line)
            
            # Look for continuation on next lines until we hit another timestamp or empty line
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                
                # Stop if we hit another timestamp or empty line
                if not next_line or re.search(timestamp_pattern, next_line):
                    break
                    
                description_parts.append(next_line)
                j += 1
            
            # Combine description parts and sanitize for console output
            description = ' '.join(description_parts).strip()
            
            if description:  # Only add if we have a description
                # Format time to ensure MM:SS format
                start_time = format_time(start_time)
                end_time = format_time(end_time)
                
                # Sanitize description for console output (remove or replace special characters)
                safe_description = ''.join(c if ord(c) < 128 else ' ' for c in description)
                
                segments.append((start_time, end_time, description))
                print(f"Found segment: [{start_time} - {end_time}] {safe_description[:50]}...")
            
            i = j  # Skip to after the description
        else:
            i += 1
    
    print(f"Successfully parsed {len(segments)} segments")
    return segments

def format_time(time_str):
    """Ensure time is in MM:SS format"""
    parts = time_str.split(':')
    if len(parts) == 2:
        minutes = int(parts[0])
        seconds = int(parts[1])
        return f"{minutes:02d}:{seconds:02d}"
    return time_str

def time_to_seconds(time_str):
    """Convert MM:SS format to seconds"""
    try:
        minutes, seconds = map(int, time_str.split(':'))
        return minutes * 60 + seconds
    except:
        print(f"Warning: Could not parse time: {time_str}")
        return 0

def seconds_to_time(seconds):
    """Convert seconds to MM:SS format"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def wrap_text(text, max_length=40):
    """
    Wrap text into multiple lines for better caption display
    """
    words = text.split()
    if not words:
        return text
    
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        # If adding this word would exceed max length, start new line
        if current_length + len(word) + 1 > max_length and current_line:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            current_line.append(word)
            current_length += len(word) + 1
    
    # Add remaining words
    if current_line:
        lines.append(' '.join(current_line))
    
    # Join with line breaks (max 2 lines for readability)
    return '\\n'.join(lines[:2])

def check_ffmpeg():
    """Check if ffmpeg is available"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_video_info(video_path):
    """Get video duration, dimensions, and frame rate using ffprobe"""
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', '-show_streams', video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        
        # Get video stream info
        video_stream = next(s for s in info['streams'] if s['codec_type'] == 'video')
        duration = float(info['format']['duration'])
        width = int(video_stream['width'])
        height = int(video_stream['height'])
        
        # Get frame rate
        fps_str = video_stream.get('r_frame_rate', '30/1')
        fps_num, fps_den = map(int, fps_str.split('/'))
        fps = fps_num / fps_den if fps_den != 0 else 30
        
        return duration, width, height, fps
    except Exception as e:
        print(f"Error getting video info: {e}")
        return None, None, None, None

def extract_segment(video_path, start_time, end_time, output_path):
    """Extract a video segment using ffmpeg with proper re-encoding for consistency"""
    cmd = [
        'ffmpeg', '-i', video_path,
        '-ss', start_time,
        '-to', end_time,
        '-c:v', 'libx264',  # Re-encode video for consistency
        '-c:a', 'aac',      # Re-encode audio for consistency
        '-preset', 'fast',   # Balance between speed and quality
        '-crf', '23',       # Good quality setting
        '-r', '30',         # Standardize frame rate
        '-avoid_negative_ts', 'make_zero',
        '-fflags', '+genpts',  # Generate presentation timestamps
        '-y', output_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, check=True, text=True, encoding='utf-8')
        print(f"[OK] Extracted segment: {start_time} - {end_time}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to extract segment: {start_time} - {end_time}")
        print(f"Error: {e.stderr if e.stderr else str(e)}")
        return False

def create_blank_screen(duration, width, height, output_path, color='black'):
    """Create a high-quality blank screen with smooth fade in/out"""
    # Create a fade filter for smooth transitions
    fade_duration = min(1.0, duration / 3)  # Fade duration up to 1 second
    
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', f'color=c={color}:s={width}x{height}:d={duration+2}:r=60',  # Higher frame rate for smoother fades
        '-vf', f'fade=in:0:{int(30*fade_duration)},fade=out:st={duration-fade_duration}:d={fade_duration}',
        '-c:v', 'libx264',
        '-preset', 'slow',  # Slower preset for better quality
        '-crf', '18',      # Higher quality
        '-x264-params', 'ref=6:bframes=8:b-adapt=2',  # Better motion estimation
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        '-t', str(duration),
        '-y', output_path
    ]
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to create blank screen: {e.stderr if e.stderr else str(e)}")
        return False

def create_caption_image(text, output_path, width=1920, height=1080, bg_color='black', text_color='white'):
    """Create an image with centered text for captions with proper text wrapping"""
    from PIL import Image, ImageDraw, ImageFont
    import textwrap
    import os
    
    # Create a blank image with the specified background color
    image = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)
    
    # Use a default font with better sizing
    try:
        font_size = max(32, min(width // 25, height // 15))
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # Wrap text to fit the screen width
    max_chars_per_line = width // (font_size // 2)
    wrapped_lines = textwrap.wrap(text, width=max_chars_per_line)
    
    # Calculate total text height
    line_height = font_size + 10
    total_text_height = len(wrapped_lines) * line_height
    
    # Start position (centered vertically)
    start_y = (height - total_text_height) // 2
    
    # Draw each line centered horizontally
    for i, line in enumerate(wrapped_lines):
        # Get text dimensions using textbbox (newer PIL method)
        try:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
        except AttributeError:
            # Fallback for older PIL versions
            text_width, _ = draw.textsize(line, font=font)
        
        x_position = (width - text_width) // 2
        y_position = start_y + (i * line_height)
        
        # Add text shadow for better visibility
        shadow_offset = 2
        draw.text((x_position + shadow_offset, y_position + shadow_offset), line, 
                 fill='black', font=font)
        draw.text((x_position, y_position), line, fill=text_color, font=font)
    
    # Save the image
    image.save(output_path, 'PNG')
    return output_path

def add_caption_to_segment(input_path, caption_text, output_path, width, height, next_caption=None):
    """Add clean, readable captions to video segment with 10-second transition screen - OPTIMIZED"""
    import re
    import tempfile
    import os
    import shutil
    from concurrent.futures import ThreadPoolExecutor
    
    # Clean and prepare caption text
    clean_caption = re.sub(r'[^\w\s.,!?\-]', ' ', str(caption_text))  # Keep basic punctuation
    clean_caption = ' '.join(clean_caption.split())  # Normalize whitespace
    
    if not clean_caption.strip():
        print("[WARNING] Empty caption text, using default caption")
        clean_caption = "Match Highlight"
    
    # Prepare next caption for transition
    if next_caption:
        next_clean = re.sub(r'[^\w\s.,!?\-]', ' ', str(next_caption))
        next_clean = ' '.join(next_clean.split())
        transition_text = f"Coming Up Next: {next_clean[:100]}..."
    else:
        transition_text = "End of Highlights"
        
    # Create a temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Normalize paths to use forward slashes for FFmpeg
        temp_dir = temp_dir.replace('\\', '/')
        input_path = input_path.replace('\\', '/')
        output_path = output_path.replace('\\', '/')
        
        # Get video duration first
        duration_cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_path
        ]
        try:
            duration = float(subprocess.run(duration_cmd, capture_output=True, text=True).stdout.strip())
        except:
            duration = 5.0  # Default duration if we can't determine it
        
        # Use optimized parallel processing for image creation and video processing
        def create_caption_image_task():
            caption_img = os.path.join(temp_dir, 'caption.png').replace('\\', '/')
            create_caption_image(clean_caption, caption_img, width, height//4, 'rgba(0,0,0,128)', 'white')
            return caption_img
        
        def create_transition_image_task():
            transition_img = os.path.join(temp_dir, 'transition.png').replace('\\', '/')
            create_caption_image(transition_text, transition_img, width, height, 'black', 'yellow')
            return transition_img
        
        # Process both images concurrently for faster execution
        with ThreadPoolExecutor(max_workers=3) as executor:
            caption_future = executor.submit(create_caption_image_task)
            transition_future = executor.submit(create_transition_image_task)
            
            # Get results
            caption_img = caption_future.result()
            transition_img = transition_future.result()

        # Create captioned video with overlay at bottom
        captioned_path = os.path.join(temp_dir, 'captioned.mp4').replace('\\', '/')
        
        # Build optimized FFmpeg command with caption overlay at bottom
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-i', caption_img,
            # Optimized video filters: overlay caption at bottom
            '-filter_complex', (
                f'[1:v]scale={width}:{height//6}[caption];'
                f'[0:v][caption]overlay=0:H-h:enable=\'between(t,0.5,{duration-0.5})\'[v]'
            ),
            '-map', '[v]',
            '-map', '0:a',
            # Optimized video encoding settings for faster processing
            '-c:v', 'libx264',
            '-preset', 'ultrafast',  # Fastest preset for speed
            '-crf', '23',  # Balanced quality/speed
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            # Audio settings
            '-c:a', 'copy',  # Copy audio without re-encoding for speed
            '-y', captioned_path
        ]
        
        try:
            # Run the caption overlay command
            subprocess.run(cmd, capture_output=True, check=True, text=True, encoding='utf-8')
            print(f"[OK] Added caption: {clean_caption[:50]}...")
            
            # Create 10-second transition video with upcoming caption
            transition_vid = os.path.join(temp_dir, 'transition.mp4').replace('\\', '/')
            transition_cmd = [
                'ffmpeg',
                '-loop', '1',
                '-i', transition_img,
                '-t', '10',  # 10 seconds as requested
                '-vf', 'fade=in:0:30,fade=out:270:30',  # Fade in/out for 1 second each
                '-c:v', 'libx264',
                '-preset', 'ultrafast',  # Fastest preset for speed
                '-pix_fmt', 'yuv420p',
                '-r', '30',
                '-y', transition_vid
            ]
            
            # Create transition video (no need for parallel processing here as it's already fast)
            subprocess.run(transition_cmd, capture_output=True, check=True, text=True, encoding='utf-8')
            
            # Concatenate the captioned segment and transition
            filelist_path = os.path.join(temp_dir, 'filelist.txt').replace('\\', '/')
            with open(filelist_path, 'w') as f:
                f.write(f"file '{captioned_path}'\nfile '{transition_vid}'\n")
            
            concat_cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', filelist_path,
                '-c', 'copy',
                '-movflags', '+faststart',
                '-y', output_path
            ]
            
            subprocess.run(concat_cmd, capture_output=True, check=True, text=True, encoding='utf-8')
            print("[OK] Added 10-second transition after segment")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to process segment: {e.stderr if e.stderr else str(e)}")
            # Fallback to copying the input file without changes
            try:
                subprocess.run(['ffmpeg', '-i', input_path, '-c', 'copy', '-y', output_path], 
                             capture_output=True, check=True, text=True, encoding='utf-8')
                return True
            except subprocess.CalledProcessError as e2:
                print(f"[CRITICAL] Complete processing failure: {e2.stderr if e2.stderr else str(e2)}")
                return False

def create_transition_clip(caption_text, output_path, width, height, fps=30, duration=3):
    """Create a black screen transition with upcoming caption"""
    font_size = max(24, width // 40)
    # Remove any non-ASCII characters from caption
    safe_caption = ''.join(c if ord(c) < 128 else ' ' for c in caption_text)
    wrapped_caption = wrap_text(safe_caption, 50)  # Longer lines for transitions
    
    # Simple escaping for ffmpeg filter
    caption_escaped = (wrapped_caption
                      .replace("\\", "\\\\")
                      .replace("'", "\\'")
                      .replace(":", "\\:")
                      .replace("|", "\\|")
                      .replace("[", "\\[")
                      .replace("]", "\\]"))
    
    # Create a black background with text
    text_filter = (
        f"color=c=black:s={width}x{height}:d={duration}:"
        f"[bg];"
        f"[bg]drawtext=text='{caption_escaped}':"
        f"fontsize={font_size}:"
        f"fontcolor=white:"
        f"bordercolor=black:"
        f"borderw=2:"
        f"x=(w-text_w)/2:"
        f"y=(h-text_h)/2:"
        f"box=1:boxcolor=black@0.5:boxborderw=10"
    )
    
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', text_filter,
        '-c:v', 'libx264',
        '-t', str(duration),
        '-r', str(fps),
        '-pix_fmt', 'yuv420p',
        '-y', output_path
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True, text=True, encoding='utf-8')
        print("[OK] Created transition clip")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[WARNING] Could not create transition: {e.stderr if e.stderr else str(e)}")
        # Create a simple black frame as fallback
        try:
            subprocess.run([
                'ffmpeg',
                '-f', 'lavfi',
                '-i', f'color=c=black:s={width}x{height}:d={duration}',
                '-c:v', 'libx264',
                '-t', str(duration),
                '-r', str(fps),
                '-y', output_path
            ], capture_output=True, check=True, text=True, encoding='utf-8')
            return True
        except subprocess.CalledProcessError as e2:
            print(f"[ERROR] Failed to create fallback transition: {e2.stderr if e2.stderr else str(e2)}")
            return False

def create_highlights_compilation(video_path, text_file_path, output_path="highlights.mp4"):
    """Create highlights compilation with captions and transitions - IMPROVED VERSION"""
    
    print("Starting highlights compilation...")
    print(f"Input video: {video_path}")
    print(f"Text file: {text_file_path}")
    print(f"Output path: {output_path}")
    
    # Check if input video exists
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        return None
    
    # Check if text file exists
    if not os.path.exists(text_file_path):
        print(f"Error: Text file not found: {text_file_path}")
        return None
    
    # Check if ffmpeg is available
    if not check_ffmpeg():
        print("Error: ffmpeg is not installed or not in PATH")
        print("Install FFmpeg from https://ffmpeg.org/download.html")
        return None
    
    # Get video info including fps
    duration, width, height, fps = get_video_info(video_path)
    if duration is None:
        print("Error: Could not get video information")
        return None
    
    print(f"Video info: {duration:.2f}s, {width}x{height}, {fps:.2f}fps")
    
    # Parse segments
    segments = parse_timestamps_from_file(text_file_path)
    if not segments:
        print("No segments found in text file!")
        return None
        
    print(f"Found {len(segments)} segments to process")
    
    # Create temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        segment_files = []
        successful_segments = 0
        
        # Process each segment with parallel processing
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        def process_segment(i, start_time, end_time, description, next_description=None):
            """Process a single segment with extraction and captioning"""
            print(f"\nProcessing segment {i}/{len(segments)}: {start_time} - {end_time}")
            print(f"Description: {description[:100]}...")
            
            # Check if timestamps are valid
            start_seconds = time_to_seconds(start_time)
            end_seconds = time_to_seconds(end_time)
            
            if start_seconds >= duration:
                print(f"Warning: Segment {i} starts after video ends ({start_seconds}s >= {duration}s). Adjusting to last 10 seconds...")
                # Adjust to extract the last 10 seconds of video instead of skipping
                start_seconds = max(0, duration - 10)
                end_seconds = duration - 0.1
                start_time = seconds_to_time(start_seconds)
                end_time = seconds_to_time(end_seconds)
                
            if end_seconds > duration:
                print(f"Warning: Segment {i} exceeds video duration. Adjusting...")
                end_seconds = duration - 0.1
                end_time = seconds_to_time(end_seconds)
            
            if start_seconds >= end_seconds:
                print(f"Warning: Invalid time range for segment {i} ({start_seconds}s >= {end_seconds}s). Creating 5-second segment...")
                # Create a 5-second segment instead of skipping
                if start_seconds + 5 <= duration:
                    end_seconds = start_seconds + 5
                else:
                    start_seconds = max(0, duration - 5)
                    end_seconds = duration - 0.1
                start_time = seconds_to_time(start_seconds)
                end_time = seconds_to_time(end_seconds)
            
            try:
                # Extract segment with proper re-encoding
                temp_segment = os.path.join(temp_dir, f"segment_{i:02d}_raw.mp4")
                if not extract_segment(video_path, start_time, end_time, temp_segment):
                    print(f"Failed to extract segment {i}, but continuing with other segments...")
                    return None
                
                # Add caption with next caption for transition
                temp_captioned = os.path.join(temp_dir, f"segment_{i:02d}_captioned.mp4")
                if add_caption_to_segment(temp_segment, description, temp_captioned, width, height, next_description):
                    return temp_captioned
                else:
                    return None
                
            except Exception as e:
                print(f"Error processing segment {i}: {e}")
                print(f"Segment details: {start_time}-{end_time}, Description: {description[:100]}...")
                # Don't return None, let other segments continue processing
                return None
        
        # Process segments with optimized parallel execution (increased workers for faster processing)
        processed_files = []
        max_workers = min(len(segments), 4)  # Use up to 4 workers or number of segments
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all segment processing tasks
            future_to_segment = {}
            for i, (start_time, end_time, description) in enumerate(segments, 1):
                # Get next segment description for transition
                next_desc = segments[i][2] if i < len(segments) else None
                
                future = executor.submit(process_segment, i, start_time, end_time, description, next_desc)
                future_to_segment[future] = i
            
            # Collect results in order
            results = [None] * len(segments)
            for future in as_completed(future_to_segment):
                segment_idx = future_to_segment[future]
                try:
                    result = future.result()
                    results[segment_idx - 1] = result
                except Exception as e:
                    print(f"Error in segment {segment_idx}: {e}")
            
            # Add successful results to segment_files in order
            for result in results:
                if result:
                    processed_files.append(result)
                    successful_segments += 1
        
        segment_files = processed_files
        if not segment_files:
            print("No segments were successfully processed!")
            return None
            
        print(f"\nSuccessfully processed {successful_segments} segments with {len(segment_files)} total clips")
        
        # Create file list for concatenation
        filelist_path = os.path.join(temp_dir, "filelist.txt")
        with open(filelist_path, 'w') as f:
            for segment_file in segment_files:
                f.write(f"file '{segment_file}'\n")
        
        print(f"Created file list with {len(segment_files)} clips")
        
        # Concatenate all segments with proper settings
        print("Creating final highlights compilation...")
        cmd = [
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', filelist_path,
            '-c:v', 'libx264',     # Re-encode for consistency
            '-c:a', 'aac',         # Re-encode audio
            '-preset', 'fast',     # Good balance of speed/quality
            '-crf', '23',          # Good quality
            '-r', '30',            # Standardize frame rate
            '-fflags', '+genpts',  # Generate proper timestamps
            '-movflags', '+faststart',  # Optimize for web playback
            '-y', output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, check=True, text=True)
            print(f"Success! Highlights saved to: {output_path}")
            
            # Get final video info
            final_duration, _, _, _ = get_video_info(output_path)
            if final_duration:
                print(f"Final video duration: {final_duration:.2f} seconds")
            
            # Return the output path on success
            return output_path
                
        except subprocess.CalledProcessError as e:
            print(f"Error creating final compilation: {e}")
            if e.stderr:
                print(f"FFmpeg error: {e.stderr}")
            return None

def test_parsing(text_content):
    """Test function to verify parsing works with sample input"""
    print("Testing timestamp parsing...")
    
    # Write test content to temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(text_content)
        temp_file = f.name
    
    try:
        segments = parse_timestamps_from_file(temp_file)
        print(f"Parsing test complete: Found {len(segments)} segments")
        for i, (start, end, desc) in enumerate(segments, 1):
            print(f"  {i:2d}. [{start} - {end}] {desc}")
        return segments
    finally:
        os.unlink(temp_file)