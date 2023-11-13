<a href="https://cookbook.openai.com" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="/images/openai-cookbook-white.png" style="max-width: 100%; width: 400px; margin-bottom: 20px">
    <img alt="OpenAI Cookbook Logo" src="/images/openai-cookbook.png" width="400px">
  </picture>
</a>

<h3></h3>
 
> ✨ Navigate at [cookbook.openai.com](https://cookbook.openai.com)

# OpenAI Cookbook Web App Integration

This document outlines the integration of a simple web application with the OpenAI Cookbook repository. The web application allows users to interact with an AI assistant, send queries, and receive responses. It also includes the functionality to use a code interpreter tool.

## PLACE HOLDER: TODO as a kindness
 pip install -r requirements.txt 

## Features

- **AI Interaction Form**: Users can submit questions to the AI assistant.
- **Dynamic Assistant Configuration**: Users can set the assistant's name and instructions.
- **Code Interpreter**: An optional code interpreter tool can be enabled for processing code-related queries.

## ToDo

- **Add functionality to load in files**: Explore options for file input and processing within the web application.
- **Unit Testing**: Implement unit tests to ensure reliability and accuracy of the application.
- **Explore Integration with Memory and Storage Solutions**: Investigate how the application can integrate with services like Pinecone for enhanced memory and storage capabilities.

## Setup and Installation

1. **Clone the Repository**: Ensure you have a fork or clone of the OpenAI Cookbook repository.

2. **Install Dependencies**:
   ***CAUTION: ***
   - Flask: `pip install flask`
   - python-dotenv: `pip install python-dotenv`
   - OpenAI: `pip install openai`
   - Authorisation: `pip install Flask-HTTPAuth`



3. **Environment Variables**: Set up your `.env` file with the necessary API keys and configurations. (and check set to .gitignore)

## Running the Application

1. **Start the Flask Server**: Run `app.py` to start the Flask server.
2. **Access the Web App**: Open the provided local URL in your browser to interact with the application.

## Web Application Usage

- **Submitting Queries**: Enter your question in the 'Your question' field.
- **Setting Assistant Properties**:
  - *Assistant Name*: Optionally set a name for the assistant.
  - *Assistant Instructions*: Optionally provide specific instructions for the assistant.
- **Enabling Code Interpreter**: Check the 'Code Interpreter' box to enable the code interpreter tool for the query.

## Backend Functionality

- **Flask Server**: Handles HTTP requests and communicates with the OpenAI API.
- **AI Interaction**: The server processes user input, interacts with the OpenAI API, and returns the AI's response.
- **Code Interpreter**: When enabled, the server uses the code interpreter tool to process code-related queries and returns both the code and its output.

## Troubleshooting

- Ensure all dependencies are correctly installed.
- Check the Flask server logs for any errors or issues.
- Verify that the `.env` file is correctly set up with your API keys.

## Future Enhancements

- Improved error handling and user feedback.
- Additional customization options for the AI assistant.
- Enhanced UI/UX design for a better user experience.

