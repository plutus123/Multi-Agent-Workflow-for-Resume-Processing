# agents.py

import os
import PyPDF2
import docx
import json
from typing import List, Dict, Any
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


class ResumeReaderAgent:
    """Agent to read and process resumes."""

    def __init__(self):
        pass

    def read_pdf(self, file_path: str) -> str:
        """Reads text from a PDF file."""
        with open(file_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
        return text

    def read_docx(self, file_path: str) -> str:
        """Reads text from a DOCX file."""
        doc = docx.Document(file_path)
        text = '\n'.join([para.text for para in doc.paragraphs])
        return text

    def read_resume(self, file_path: str) -> str:
        """Determines file type and reads the resume."""
        if file_path.endswith('.pdf'):
            return self.read_pdf(file_path)
        elif file_path.endswith('.docx'):
            return self.read_docx(file_path)
        else:
            raise ValueError('Unsupported file format')


class ExtractorAgent:
    """Agent to extract entities from resume text."""

    def __init__(self):
        self.chat_llm = ChatOpenAI(
            model_name='gpt-3.5-turbo',
            temperature=0,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
            verbose=True
        )

    def extract_entities(self, resume_text: str) -> Dict[str, Any]:
        """Extracts entities from resume text using LLM."""
        prompt = PromptTemplate(
            input_variables=['resume_text'],
            template='''
Please extract the following information from the resume text below:

1. Personal Information:
   - Full Name
   - Email Address
   - Phone Number
   - Address (if available)
   - LinkedIn URL
   - GitHub URL
2. Education (list all):
   - Degree
   - Major
   - University/College Name
   - Graduation Year
3. Work Experience (list all jobs):
   - Job Title
   - Company Name
   - Start Date
   - End Date
   - Responsibilities and Achievements
4. Skills:
   - List of technical skills
   - List of soft skills
5. Certifications (if any):
   - Certification Name
   - Issuing Organization
   - Issue Date

Provide the extracted information in JSON format.

Resume Text:
{resume_text}
'''
        )

        chain = LLMChain(llm=self.chat_llm, prompt=prompt)

        response = chain.run(resume_text=resume_text)

        try:
            extracted_data = json.loads(response)
        except json.JSONDecodeError:
            print("Error parsing JSON output from LLM.")
            extracted_data = {}
        return extracted_data


class ValidatorAgent:
    """Agent to validate extracted entities."""

    def __init__(self):
        pass

    def validate_entities(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validates the extracted data for completeness."""
        errors = []

        # Validate Personal Information
        personal_info = extracted_data.get('Personal Information', {})
        if not personal_info.get('Full Name'):
            errors.append('Full Name is missing in Personal Information.')
        if not personal_info.get('Email Address'):
            errors.append('Email Address is missing in Personal Information.')

        # Validate Education
        education = extracted_data.get('Education', [])
        if not education:
            errors.append('Education information is missing.')
        else:
            for idx, edu in enumerate(education):
                if not edu.get('Degree'):
                    errors.append(f'Degree is missing in Education entry {idx + 1}.')
                if not edu.get('University/College Name'):
                    errors.append(f'University/College Name is missing in Education entry {idx + 1}.')

        # Validate Work Experience
        work_experience = extracted_data.get('Work Experience', [])
        if not work_experience:
            errors.append('Work Experience information is missing.')

        # Validate Skills
        skills = extracted_data.get('Skills', {})
        if not skills.get('Technical Skills'):
            errors.append('Technical Skills are missing in Skills.')

        return {'valid': not errors, 'errors': errors}

