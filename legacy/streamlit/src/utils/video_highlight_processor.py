"""
Video Highlight Processor Module
Handles extraction of video segments and addition of AI narration
"""

import os
import datetime
import subprocess
import traceback
import pyttsx3
from pathlib import Path
from typing import Dict


def parse_timestamp(timestamp_str: str) -> int:
    """Convert timestamp string to seconds."""
    try:
        parts = str(timestamp_str).strip().split(':')
        if len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        else:
            return 0
    except:
        return 0


def extract_and_narrate_highlight(video_path: str, start_time: str, end_time: str, 
                                   ai_narration: str, highlight_index: int, 
                                   player_names: str) -> str:
    """
    Extract a video segment and overlay AI narration audio.
    
    Args:
        video_path: Path to the original video file
        start_time: Start time in format MM:SS or HH:MM:SS
        end_time: End time in format MM:SS or HH:MM:SS
        ai_narration: AI analysis text to convert to speech
        highlight_index: Index of the highlight (for unique filename)
        player_names: Player names for context
    
    Returns:
        Path to the processed video clip with narration
    """
    try:
        # Create output directory for clips
        from app import PROJECT_ROOT
        output_dir = Path(PROJECT_ROOT) / 'output' / 'highlight_clips'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        player_safe = "".join(c if c.isalnum() else "_" for c in player_names)
        
        # Temporary files
        temp_video_path = output_dir / f"temp_clip_{highlight_index}_{timestamp}.mp4"
        audio_narration_path = output_dir / f"temp_narration_{highlight_index}_{timestamp}.mp3"
        final_video_path = output_dir / f"{player_safe}_highlight_{highlight_index}_{timestamp}.mp4"
        
        print(f"[DEBUG] Extracting video segment: {start_time} to {end_time}")
        
        # Step 1: Extract video segment (with original audio for now)
        extract_success = extract_video_segment(
            input_video=video_path,
            start_time=start_time,
            end_time=end_time,
            output_path=str(temp_video_path)
        )
        
        if not extract_success or not os.path.exists(temp_video_path):
            print(f"[ERROR] Failed to extract video segment")
            return None
        
        # Step 2: Generate AI narration audio if provided
        narration_audio_exists = False
        if ai_narration:
            narration_audio_exists = generate_narration_audio(
                text=ai_narration,
                output_path=str(audio_narration_path)
            )
        
        # Step 3: Process video based on narration availability
        if narration_audio_exists and os.path.exists(audio_narration_path):
            print(f"[DEBUG] Muting original audio and adding AI narration")
            combine_success = combine_video_with_narration(
                video_path=str(temp_video_path),
                audio_path=str(audio_narration_path),
                output_path=str(final_video_path)
            )
            
            # Clean up temporary files
            try:
                if os.path.exists(temp_video_path):
                    os.remove(temp_video_path)
                if os.path.exists(audio_narration_path):
                    os.remove(audio_narration_path)
            except:
                pass
            
            if combine_success and os.path.exists(final_video_path):
                return str(final_video_path)
            else:
                # If combination failed, return muted video without narration
                if os.path.exists(temp_video_path):
                    mute_success = create_muted_video(str(temp_video_path), str(final_video_path))
                    if mute_success:
                        try:
                            os.remove(temp_video_path)
                        except:
                            pass
                        return str(final_video_path)
                return None
        else:
            # No narration available, create muted video
            print(f"[DEBUG] No narration available, creating muted video")
            mute_success = create_muted_video(str(temp_video_path), str(final_video_path))
            if mute_success:
                try:
                    os.remove(temp_video_path)
                except:
                    pass
                return str(final_video_path)
            else:
                # Fallback: return video with original audio
                os.rename(temp_video_path, final_video_path)
                return str(final_video_path)
    
    except Exception as e:
        print(f"[ERROR] Error in extract_and_narrate_highlight: {str(e)}")
        traceback.print_exc()
        return None


def extract_video_segment(input_video: str, start_time: str, end_time: str, output_path: str) -> bool:
    """
    Extract a video segment using FFmpeg.
    
    Args:
        input_video: Path to input video
        start_time: Start time (MM:SS or HH:MM:SS)
        end_time: End time (MM:SS or HH:MM:SS)
        output_path: Path for output video segment
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Calculate duration
        start_seconds = parse_timestamp(start_time)
        end_seconds = parse_timestamp(end_time)
        duration = end_seconds - start_seconds
        
        if duration <= 0:
            print(f"[ERROR] Invalid duration: {duration}")
            return False
        
        # FFmpeg command to extract segment
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output file
            '-ss', str(start_seconds),  # Start time
            '-i', input_video,  # Input file
            '-t', str(duration),  # Duration
            '-c:v', 'libx264',  # Video codec
            '-c:a', 'aac',  # Audio codec
            '-strict', 'experimental',
            '-preset', 'fast',
            output_path
        ]
        
        print(f"[DEBUG] Running FFmpeg command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path):
            print(f"[SUCCESS] Video segment extracted: {output_path}")
            return True
        else:
            print(f"[ERROR] FFmpeg failed: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"[ERROR] Error extracting video segment: {str(e)}")
        return False


def generate_narration_audio(text: str, output_path: str) -> bool:
    """
    Generate high-quality audio narration from text using pyttsx3 with better voice settings.
    
    Args:
        text: Text to convert to speech
        output_path: Path for output audio file (will be converted to MP3)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"[DEBUG] Generating high-quality narration audio")
        
        # Create temp WAV file (pyttsx3 works better with WAV)
        temp_wav = os.path.splitext(output_path)[0] + '.wav'
        
        # Initialize TTS engine with better settings
        engine = pyttsx3.init()
        
        # Configure voice properties
        voices = engine.getProperty('voices')
        
        # Try to find a good voice (prefer female voices as they're often clearer)
        preferred_voices = [v for v in voices if 'female' in v.name.lower() or 'zira' in v.name.lower()]
        if preferred_voices:
            engine.setProperty('voice', preferred_voices[0].id)
        elif len(voices) > 1:
            engine.setProperty('voice', voices[1].id)  # Fallback to second voice
        
        # Optimize speech parameters
        engine.setProperty('rate', 160)  # Slightly faster than normal (default is ~200)
        engine.setProperty('volume', 1.0)  # Max volume
        
        # Save to WAV first for better quality
        engine.save_to_file(text, temp_wav)
        engine.runAndWait()
        
        if not os.path.exists(temp_wav) or os.path.getsize(temp_wav) == 0:
            print(f"[ERROR] Failed to generate WAV narration")
            return False
            
        # Convert to MP3 with ffmpeg for better quality and compression
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output
            '-i', temp_wav,  # Input WAV
            '-codec:a', 'libmp3lame',  # Use LAME MP3 encoder
            '-qscale:a', '2',  # Quality (2 = high quality, smaller file)
            '-ar', '44100',  # Sample rate (CD quality)
            '-ac', '2',  # Stereo
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up temp WAV file
        try:
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
        except:
            pass
        
        if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"[SUCCESS] High-quality narration audio generated: {output_path}")
            return True
        else:
            print(f"[ERROR] Failed to generate MP3 narration: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"[ERROR] Error generating narration audio: {str(e)}")
        return False


def combine_video_with_narration(video_path: str, audio_path: str, output_path: str) -> bool:
    """
    Combine video with narration audio, ensuring audio matches video duration.
    Process:
    1. Get video duration
    2. Stretch/speed up narration audio to match video duration
    3. Combine video with processed audio
    
    Args:
        video_path: Path to input video
        audio_path: Path to narration audio
        output_path: Path for output video with narration
    
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"[DEBUG] Combining video with narration (matching audio to video duration)")
        
        # Create temp directory
        temp_dir = os.path.dirname(output_path)
        temp_audio = os.path.join(temp_dir, f"temp_narration_adjusted_{os.path.basename(audio_path)}")
        
        # Get video duration using ffprobe
        cmd_get_duration = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        
        print("[DEBUG] Getting video duration...")
        result = subprocess.run(cmd_get_duration, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] Failed to get video duration: {result.stderr}")
            return False
            
        try:
            video_duration = float(result.stdout.strip())
            print(f"[DEBUG] Video duration: {video_duration} seconds")
        except ValueError:
            print(f"[ERROR] Could not parse video duration: {result.stdout}")
            return False
        
        # Process audio to match video duration
        print("[DEBUG] Adjusting narration audio to match video duration...")
        cmd_process_audio = [
            'ffmpeg',
            '-y',
            '-i', audio_path,
            '-af', f'atempo=1.0,asetpts=N/SR/TB',  # Prepare for duration adjustment
            '-f', 'mp3',
            temp_audio
        ]
        
        result = subprocess.run(cmd_process_audio, capture_output=True, text=True)
        if result.returncode != 0 or not os.path.exists(temp_audio):
            print(f"[ERROR] Failed to process narration audio: {result.stderr}")
            return False
            
        # Get narration audio duration
        cmd_get_audio_duration = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            temp_audio
        ]
        
        result = subprocess.run(cmd_get_audio_duration, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] Failed to get audio duration: {result.stderr}")
            return False
            
        try:
            audio_duration = float(result.stdout.strip())
            print(f"[DEBUG] Narration audio duration: {audio_duration} seconds")
        except ValueError:
            print(f"[ERROR] Could not parse audio duration: {result.stdout}")
            return False
            
        # Calculate speed factor (if narration is longer than video, speed it up)
        speed_factor = audio_duration / video_duration
        
        # If narration is too short, add silence at the end
        if speed_factor < 1.0:
            silence_duration = video_duration - audio_duration
            cmd_add_silence = [
                'ffmpeg',
                '-y',
                '-i', temp_audio,
                '-f', 'lavfi',
                '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100',
                '-filter_complex', f'[0:a]apad=whole_dur={video_duration}[a1];[1:a]atrim=duration={silence_duration},volume=0[a2];[a1][a2]amix=inputs=2:duration=longest',
                '-c:a', 'libmp3lame',
                '-q:a', '2',
                temp_audio + '.silenced.mp3'
            ]
            result = subprocess.run(cmd_add_silence, capture_output=True, text=True)
            if result.returncode == 0 and os.path.exists(temp_audio + '.silenced.mp3'):
                os.replace(temp_audio + '.silenced.mp3', temp_audio)
        # If narration is too long, speed it up (with pitch correction)
        elif speed_factor > 1.0:
            cmd_speed_up = [
                'ffmpeg',
                '-y',
                '-i', temp_audio,
                '-filter:a', f'atempo={speed_factor}',
                '-c:a', 'libmp3lame',
                '-q:a', '2',
                temp_audio + '.spedup.mp3'
            ]
            result = subprocess.run(cmd_speed_up, capture_output=True, text=True)
            if result.returncode == 0 and os.path.exists(temp_audio + '.spedup.mp3'):
                os.replace(temp_audio + '.spedup.mp3', temp_audio)
        
        # Combine video with processed audio
        print("[DEBUG] Combining video with adjusted narration...")
        cmd_combine = [
            'ffmpeg',
            '-y',
            '-i', video_path,  # Input video
            '-i', temp_audio,  # Processed narration audio
            '-map', '0:v',    # Video from first input
            '-map', '1:a',    # Audio from second input
            '-c:v', 'copy',   # Copy video stream
            '-c:a', 'aac',    # Encode audio as AAC
            '-shortest',      # Match to shortest stream (should be same duration now)
            '-movflags', '+faststart',  # Enable streaming
            output_path
        ]
        
        result = subprocess.run(cmd_combine, capture_output=True, text=True)
        
        # Clean up temporary files
        try:
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
        except:
            pass
        
        if result.returncode == 0 and os.path.exists(output_path):
            print(f"[SUCCESS] Video combined with narration (duration matched): {output_path}")
            return True
        else:
            print(f"[ERROR] FFmpeg failed: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"[ERROR] Error combining video with narration: {str(e)}")
        return False


def create_muted_video(video_path: str, output_path: str) -> bool:
    """
    Create a video with no audio (muted).
    
    Args:
        video_path: Path to input video
        output_path: Path for output muted video
    
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"[DEBUG] Creating muted video")
        
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output file
            '-i', video_path,  # Input video
            '-map', '0:v',  # Video only (no audio)
            '-c:v', 'copy',  # Copy video codec
            '-an',  # No audio
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path):
            print(f"[SUCCESS] Muted video created: {output_path}")
            return True
        else:
            print(f"[ERROR] Muting failed: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"[ERROR] Error creating muted video: {str(e)}")
        return False


def replace_audio_entirely(video_path: str, audio_path: str, output_path: str) -> bool:
    """
    Replace video audio entirely with narration (fallback method).
    
    Args:
        video_path: Path to input video
        audio_path: Path to narration audio
        output_path: Path for output video
    
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"[DEBUG] Replacing audio entirely (fallback)")
        
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output file
            '-i', video_path,  # Input video
            '-i', audio_path,  # Input audio
            '-map', '0:v',  # Video from first input
            '-map', '1:a',  # Audio from second input
            '-c:v', 'copy',  # Copy video codec
            '-c:a', 'aac',  # Audio codec
            '-shortest',  # Finish when shortest input ends
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path):
            print(f"[SUCCESS] Audio replaced: {output_path}")
            return True
        else:
            print(f"[ERROR] Audio replacement failed: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"[ERROR] Error replacing audio: {str(e)}")
        return False
