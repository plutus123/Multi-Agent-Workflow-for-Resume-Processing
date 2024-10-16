# tests/test_agents.py

import unittest
from agents import ResumeReaderAgent, ExtractorAgent, ValidatorAgent


class TestResumeReaderAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ResumeReaderAgent()

    def test_read_pdf(self):
        # Test with a sample PDF file
        try:
            resume_text = self.agent.read_pdf('sample_resume.pdf')
            self.assertIsInstance(resume_text, str)
            self.assertTrue(len(resume_text) > 0)
        except FileNotFoundError:
            self.skipTest("sample_resume.pdf not found.")

    def test_read_docx(self):
        # Test with a sample DOCX file
        try:
            resume_text = self.agent.read_docx('sample_resume.docx')
            self.assertIsInstance(resume_text, str)
            self.assertTrue(len(resume_text) > 0)
        except FileNotFoundError:
            self.skipTest("sample_resume.docx not found.")

    def test_read_unsupported_format(self):
        with self.assertRaises(ValueError):
            self.agent.read_resume('sample_resume.txt')


class TestExtractorAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ExtractorAgent()

    def test_extract_entities(self):
        sample_text = "John Doe\nEmail: john.doe@example.com\nPhone: 123-456-7890"
        extracted_data = self.agent.extract_entities(sample_text)
        self.assertIsInstance(extracted_data, dict)
        self.assertIn('Personal Information', extracted_data)


class TestValidatorAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ValidatorAgent()

    def test_validate_entities(self):
        extracted_data = {
            'Personal Information': {
                'Full Name': 'John Doe',
                'Email Address': 'john.doe@example.com',
                'Phone Number': '123-456-7890'
            },
            'Education': [
                {
                    'Degree': 'B.Sc. Computer Science',
                    'University/College Name': 'ABC University',
                    'Graduation Year': '2020'
                }
            ],
            'Work Experience': [],
            'Skills': {
                'Technical Skills': ['Python', 'JavaScript'],
                'Soft Skills': ['Communication', 'Teamwork']
            }
        }
        result = self.agent.validate_entities(extracted_data)
        self.assertFalse(result['valid'])
        self.assertIn('Work Experience information is missing.', result['errors'])


if __name__ == '__main__':
    unittest.main()
