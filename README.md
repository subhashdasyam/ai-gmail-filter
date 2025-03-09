# Gmail Unnecessary Email Filter

This project provides a modular Python application that connects to your Gmail account, analyzes your emails using a local Ollama LLM instance, and moves unnecessary emails to a separate label.

## Features

- **Gmail Integration**: Securely connects to your Gmail account using OAuth2
- **Smart Email Analysis**: Uses local Ollama API to evaluate email content
- **Customizable Filters**: Define what makes an email necessary or unnecessary
- **Label Management**: Creates and manages labels in your Gmail account
- **Detailed Logging**: Comprehensive logging for monitoring and debugging
- **Result Tracking**: Saves processing results for future reference

## Project Structure

```
gmail_filter/
├── main.py                 # Entry point
├── config.py               # Configuration settings
├── README.md               # Project documentation
├── requirements.txt        # Dependencies
├── modules/
│   ├── gmail/
│   │   ├── auth.py         # Gmail authentication
│   │   ├── email_ops.py    # Email operations
│   │   └── label_ops.py    # Label operations
│   └── llm/
│       ├── ollama.py       # Ollama integration
│       └── analyzer.py     # Email analysis logic
└── utils/
    ├── email_parser.py     # Email content parsing
    ├── logging_utils.py    # Logging setup
    └── file_utils.py       # File operations
```

## Prerequisites

- Python 3.7+
- Gmail account
- Google Cloud project with Gmail API enabled
- Ollama installed locally (https://ollama.ai)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/gmail-filter.git
   cd gmail-filter
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file by copying the example:
   ```
   cp .env.example .env
   ```

4. Edit the `.env` file to configure the application.

## Google API Setup

1. Create a Google Cloud Project:
   - Go to https://console.cloud.google.com/
   - Create a new project or select an existing one
   - Enable billing for the project (required for API usage)

2. Enable the Gmail API:
   - Go to https://console.cloud.google.com/apis/library
   - Search for "Gmail API" and select it
   - Click "Enable"

3. Create OAuth 2.0 credentials:
   - Go to https://console.cloud.google.com/apis/credentials
   - Click "Create Credentials" and select "OAuth client ID"
   - Select "Desktop app" as the application type
   - Name your credentials and click "Create"
   - Download the credentials JSON file
   - Rename it to "credentials.json" and place it in the project root directory

## Ollama Setup

1. Install Ollama from https://ollama.ai
2. Start the Ollama service
3. Pull the model you want to use:
   ```
   ollama pull llama2
   ```
   or any other model you prefer, like:
   ```
   ollama pull mistral
   ```
4. Ensure Ollama is running before starting the application

## Usage

Run the application:

```
python main.py
```

On first run, the script will open a browser window for you to authenticate with your Gmail account. After authentication, the script will:

1. Fetch emails from your inbox
2. Analyze each email using the local Ollama LLM
3. Move unnecessary emails to the "potential-unnecessary" label (or the label name you configured)
4. Save processing results to a file

## Configuration Options

You can customize the behavior of the application by editing the `.env` file:

- `MAX_EMAILS`: Maximum number of emails to process at once
- `OLLAMA_MODEL`: The LLM model to use for email analysis (must be pulled into Ollama first)
- `LABEL_NAME`: Name of the label for unnecessary emails
- `BODY_PREVIEW_LENGTH`: Length of email body to include in analysis
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

