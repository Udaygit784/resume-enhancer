# Simple Resume Parser

A lightweight and efficient Streamlit application to extract key information from resumes in PDF format. This tool focuses on extracting essential information like contact details, skills, and work experience without the complexity of advanced NLP processing.

## Features

- Extract contact information (name, email, phone)
- Identify skills from a predefined list
- Parse work experience (job titles, companies, and durations)
- Simple and intuitive user interface
- Fast processing with caching for better performance
- No external API keys or services required
- Export data to CSV/Excel

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   streamlit run app.py
   ```
2. Open your browser and navigate to `http://localhost:8501`
3. Upload a PDF resume using the file uploader
4. View the extracted information

## Dependencies

- Streamlit
- PyPDF2
- python-magic (for file type validation)
- python-dotenv (for environment variables)
- pandas (for data handling)

## License

MIT
