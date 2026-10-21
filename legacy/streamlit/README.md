# Sports Video Analysis System

An AI-powered sports video analysis application that generates highlights, summaries, and provides Q&A capabilities for sports content using advanced language models and computer vision.

## Features

- **Video Highlight Generation**: Automatically extracts and creates highlight videos from sports footage
- **Embedded Video Clips**: View highlights directly in the web interface with synchronized AI narration
- **Interactive Q&A**: Answer questions about sports content using RAG (Retrieval-Augmented Generation)
- **Multi-Modal Analysis**: Processes video, audio, and text data
- **Sports-Specific Processing**: Optimized for various sports with specialized analysis modules
- **Video Embedding**: Each highlight shows as a video clip in the web interface
- **AI Narration**: Automatically generates voice-over narration for each highlight clip

### Prerequisites

- Python 3.8 or higher
- Git
- LM Studio (for local LLM inference)
- FFmpeg (for video processing)
- pyttsx3 (for text-to-speech conversion)

## Installation

### 1. Clone the Repository

{{ ... }}
```bash
git clone https://github.com/jayachandrad/SportsVideoAnalysis.git
cd SportsVideoAnalysis
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install pyttsx3
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

## LM Studio Setup (Local LLM)

### Download and Install LM Studio

1. **Download LM Studio**:
   - Visit [https://lmstudio.ai/](https://lmstudio.ai/)
   - Download the latest version for your operating system
   - Install the application

2. **Download Phi-3 Model**:
   - Open LM Studio
   - Go to the "Search" tab
   - Search for "phi-3" or "microsoft/phi-3"
   - Download the model:
     - `QuantFactory/Phi-3-mini-128k-instruct-GGUF` (2.7GB) - Fast, good for basic tasks

3. **Load and Run the Model**:
   - In LM Studio, go to "My Models" tab
   - Select the downloaded Phi-3 model
   - Click "Start Server"
   - Note the local server URL (default: http://localhost:1234)

4. **Configure the Application**:
   - Update your `.env` file to include:
   ```env
   LM_STUDIO_URL=http://localhost:1234
   LLM_MODEL=microsoft/Phi-3-mini-4k-instruct
   ```

## Usage

### Running the Application

1. **Start LM Studio Server**:
   - Ensure LM Studio is running with your Phi-3 model loaded
   - The server should be accessible at http://localhost:1234

2. **Run the Streamlit Application**:
   ```bash
   cd src
   streamlit run app.py
   ```

3. **Access the Application**:
   - Open your browser and go to `http://localhost:8501`
   - The application will load with the sports video analysis interface
   - Click on Admin Login & Login With THe Credentials "Admin" & "Admin"
   - Click on "Rebuild Database" Button

### Using the Application

1. **Upload Sports Video**:
   - Use the file uploader to select a sports video file
   - Or enter the full path to your video file in the "Match Video URL" field

2. **View Embedded Highlights**:
   - After processing, each highlight will show as an expandable section
   - Click any highlight to view the video clip with AI narration
   - First highlight auto-expands for immediate viewing
   - Supported formats: MP4, AVI, MOV

2. **Select Sport Type**:
   - Choose the appropriate sport from the dropdown menu
   - The system will load sport-specific analysis modules

3. **Generate Analysis**:
   - **Highlights**: Click to generate video highlights
   - **Summary**: Generate text summary of the sports event
   - **Q&A**: Ask questions about the content

4. **View Results**:
   - Check the `output/` directory for generated files
   - Video highlights, audio narrations, and PDF reports will be saved

### Input Data Structure

- Place sports-related text files in the `input/` directory
- These files are used for RAG (Retrieval-Augmented Generation)
- Examples: Player profiles, game rules, historical data

### Output Files

Generated outputs are saved in the `output/` directory:
- `*_highlights.mp4` - Video highlight clips
- `*_highlights.mp3` - Audio narrations
- `*.pdf` - Detailed analysis reports

## Configuration

### Model Selection

The application supports multiple LLM providers:
- **LM Studio** (Local): Phi-3, Llama, Mistral models
- **OpenAI**: GPT-3.5, GPT-4 models
- **HuggingFace**: Various open-source models

### Advanced Configuration

Edit the configuration files in the `src/config/` directory to customize:
- Model parameters (temperature, max tokens)
- Video processing settings
- Output formats and quality

## Troubleshooting

### Common Issues

1. **LM Studio Connection Error**:
   - Ensure LM Studio is running
   - Check the server URL in `.env` file
   - Verify the model is loaded and server is active

2. **Video Processing Errors**:
   - Install FFmpeg: `sudo apt-get install ffmpeg` (Linux) or `brew install ffmpeg` (macOS)
   - On Windows, download from https://ffmpeg.org/

3. **Memory Issues**:
   - Use smaller models like Phi-3-mini for systems with limited RAM
   - Close other applications when running analysis

4. **API Key Errors**:
   - Verify your HuggingFace API key is valid
   - Check rate limits for API calls

### Performance Tips

- Use GPU acceleration when available
- Process shorter video clips for faster analysis
- Use the RAG database for improved context awareness
- Consider using cloud-based models for better performance

## New Video Features

### Video Embedding
- Each highlight shows as a video clip in the web interface
- Exact timestamp matching from your source video
- First highlight auto-expands for immediate viewing

### AI Narration
- Automatically converts highlight analysis to speech
- Mixes with original audio (30% volume) for natural sound
- Clear, natural-sounding voice-over for each clip

### Performance Optimizations
- On-demand video generation (clips load when expanded)
- Caching of generated clips for faster access
- Graceful fallback to text if video processing fails

## Cleanup

After running the application, you can remove these files as they are no longer needed:
- `update_highlights_display.py` (one-time migration script)
- Any `.pyc` files in the project directories

## Project Structure

```
SportsVideoAnalysis/
├── src/                    # Main application code
│   ├── app.py             # Streamlit web application
│   ├── highlights.py      # Video highlight generation
│   ├── summarization.py   # Text summarization
│   ├── qa.py             # Question-answering system
│   ├── core/             # Core processing modules
│   ├── sports/           # Sport-specific modules
│   └── utils/            # Utility functions
├── input/                # Input data files
├── output/               # Generated outputs
├── rag_database/         # Vector database for RAG
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the repository
- Check the troubleshooting section above
- Ensure all prerequisites are properly installed

---

**Note**: This application requires significant computational resources. For best performance, use a system with a dedicated GPU and at least 16GB of RAM.
