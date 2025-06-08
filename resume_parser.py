import re
import json
import spacy
import docx2txt
import PyPDF2
import io
import phonenumbers
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from email_validator import validate_email, EmailNotValidError

# Load English language model for NER
nlp = spacy.load("en_core_web_sm")

class ResumeParser:
    def __init__(self):
        self.skills = [
            'python', 'java', 'c++', 'javascript', 'html', 'css', 'sql', 'mongodb',
            'aws', 'docker', 'kubernetes', 'machine learning', 'deep learning',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'django',
            'flask', 'react', 'angular', 'vue', 'node.js', 'git', 'github', 'gitlab',
            'jenkins', 'ci/cd', 'rest api', 'graphql', 'postgresql', 'mysql', 'nosql',
            'data analysis', 'data visualization', 'tableau', 'power bi', 'excel'
        ]
        self.education_keywords = [
            'education', 'academic background', 'academics', 'qualifications',
            'bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'b.e.', 'm.e.',
            'b.sc', 'm.sc', 'bca', 'mca', 'b.arch', 'm.arch', 'b.com', 'm.com'
        ]
        self.experience_keywords = [
            'experience', 'employment', 'work history', 'work experience',
            'professional experience', 'career history', 'employment history'
        ]
        self.project_keywords = [
            'projects', 'personal projects', 'academic projects', 'project experience'
        ]

    def extract_text_from_pdf(self, file) -> str:
        """Extract text from PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""

    def extract_text_from_docx(self, file) -> str:
        """Extract text from DOCX file."""
        try:
            return docx2txt.process(file)
        except Exception as e:
            print(f"Error reading DOCX: {e}")
            return ""

    def extract_contact_info(self, text: str) -> Dict:
        """Extract contact information from text."""
        contact = {}
        
        # Extract email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        if emails:
            try:
                valid = validate_email(emails[0])
                contact['email'] = valid.email
            except EmailNotValidError:
                pass
        
        # Extract phone numbers
        for match in phonenumbers.PhoneNumberMatcher(text, "US"):
            if phonenumbers.is_valid_number(match.number):
                contact['phone'] = phonenumbers.format_number(
                    match.number, phonenumbers.PhoneNumberFormat.E164)
                break
        
        # Extract name (simple approach - first line with title case)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines[:5]:  # Check first 5 lines for name
            if line.istitle() and len(line.split()) in (2, 3):
                contact['name'] = line
                break
        
        return contact

    def extract_education(self, text: str) -> List[Dict]:
        """Extract education information."""
        education = []
        lines = [line.strip() for line in text.split('\n')]
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in self.education_keywords):
                # Look for degree and university in following lines
                for j in range(i, min(i + 10, len(lines))):
                    if any(word in lines[j].lower() for word in ['bachelor', 'master', 'phd', 'b.tech', 'm.tech']):
                        edu = {
                            'degree': lines[j],
                            'institution': lines[j+1] if j+1 < len(lines) else '',
                            'year': re.search(r'\d{4}', lines[j+2] if j+2 < len(lines) else '').group() if re.search(r'\d{4}', lines[j+2] if j+2 < len(lines) else '') else ''
                        }
                        education.append(edu)
        return education

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text."""
        found_skills = set()
        text_lower = text.lower()
        
        # Check for exact matches
        for skill in self.skills:
            if skill in text_lower:
                found_skills.add(skill)
        
        # Use NER to find other skills
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'TECH']:
                found_skills.add(ent.text.lower())
        
        return sorted(list(found_skills))

    def extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience."""
        experience = []
        lines = [line.strip() for line in text.split('\n')]
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in self.experience_keywords):
                # Look for job positions in following lines
                for j in range(i, min(i + 20, len(lines))):
                    if ' at ' in lines[j] or ' @ ' in lines[j]:
                        parts = re.split(r' at | @ ', lines[j], 1)
                        if len(parts) == 2:
                            exp = {
                                'position': parts[0].strip(),
                                'company': parts[1].strip(),
                                'duration': lines[j+1] if j+1 < len(lines) and re.search(r'\d{4}', lines[j+1]) else ''
                            }
                            experience.append(exp)
        return experience

    def extract_projects(self, text: str) -> List[Dict]:
        """Extract projects information."""
        projects = []
        lines = [line.strip() for line in text.split('\n')]
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in self.project_keywords):
                # Look for project details in following lines
                j = i + 1
                while j < len(lines) and not any(keyword in lines[j].lower() for keyword in self.experience_keywords + self.education_keywords):
                    if lines[j] and lines[j][0].isupper() and not lines[j].endswith(':'):
                        project = {
                            'name': lines[j],
                            'description': lines[j+1] if j+1 < len(lines) else ''
                        }
                        projects.append(project)
                        j += 2
                    else:
                        j += 1
        return projects

    def calculate_skill_match(self, resume_skills: List[str], job_description: str) -> Dict:
        """Calculate skill match percentage."""
        if not job_description:
            return {'match_percentage': 0, 'missing_skills': [], 'found_skills': []}
        
        # Extract skills from job description
        job_skills = set()
        for skill in self.skills:
            if skill in job_description.lower():
                job_skills.add(skill)
        
        if not job_skills:
            return {'match_percentage': 0, 'missing_skills': [], 'found_skills': []}
        
        # Calculate match
        resume_skills_set = set(resume_skills)
        matched_skills = resume_skills_set.intersection(job_skills)
        missing_skills = job_skills - resume_skills_set
        
        match_percentage = (len(matched_skills) / len(job_skills)) * 100
        
        return {
            'match_percentage': round(match_percentage, 2),
            'missing_skills': sorted(list(missing_skills)),
            'found_skills': sorted(list(matched_skills))
        }

    def parse_resume(self, file, job_description: str = "") -> Dict:
        """Parse resume and return structured data."""
        filename = file.name.lower()
        
        # Extract text based on file type
        if filename.endswith('.pdf'):
            text = self.extract_text_from_pdf(file)
        elif filename.endswith(('.doc', '.docx')):
            text = self.extract_text_from_docx(file)
        else:
            text = ""
        
        # Extract information
        contact_info = self.extract_contact_info(text)
        education = self.extract_education(text)
        skills = self.extract_skills(text)
        experience = self.extract_experience(text)
        projects = self.extract_projects(text)
        
        # Calculate skill match if job description is provided
        skill_match = self.calculate_skill_match(skills, job_description.lower()) if job_description else {}
        
        return {
            'filename': file.name,
            'contact_info': contact_info,
            'education': education,
            'skills': skills,
            'experience': experience,
            'projects': projects,
            'skill_match': skill_match,
            'raw_text': text[:1000] + '...'  # Store first 1000 chars for reference
        }
