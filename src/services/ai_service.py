from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from loguru import logger
import re

class LightweightAIService:
    """Lightweight AI service using FLAN-T5 for resource-constrained systems"""
    
    def __init__(self):
        self.model_name = "google/flan-t5-large"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        logger.info(f"Loaded {self.model_name} model successfully")

    def generate_summary(self, text: str) -> str:
        """Generic text generation"""
        if not isinstance(text, str):
            raise TypeError("Text input must be a string.")
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        outputs = self.model.generate(**inputs, max_length=200)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def enhance_with_ai(self, text_or_dict):
        """
        Enhance text or structured resume data using AI summarization.
        Accepts either plain text or dict input.
        """
        logger.info("Enhancing text using FLAN-T5 lightweight model...")

        # ✅ Handle dict input (structured resume)
        if isinstance(text_or_dict, dict):
            # Merge text fields (skills, experience, education, etc.) for summarization
            combined_text = ""
            if "summary" in text_or_dict and isinstance(text_or_dict["summary"], str):
                combined_text += text_or_dict["summary"] + "\n"
            if "experience" in text_or_dict:
                combined_text += " ".join(
                    [str(exp) for exp in text_or_dict["experience"]]
                ) + "\n"
            if "education" in text_or_dict:
                combined_text += " ".join(
                    [str(edu) for edu in text_or_dict["education"]]
                ) + "\n"
            if "skills" in text_or_dict:
                combined_text += "Skills: " + ", ".join(text_or_dict["skills"]) + "\n"

            text = (
                combined_text
                if combined_text.strip()
                else "This resume contains structured information but no text summary."
            )
        elif isinstance(text_or_dict, str):
            text = text_or_dict
        else:
            raise TypeError(
                "enhance_with_ai() expects either a string or a dictionary input."
            )

        # Generate enhanced summary
        prompt = f"Summarize this candidate profile concisely: {text}"
        enhanced_summary = self.generate_summary(prompt)

        return {"enhancedSummary": enhanced_summary}

    def parse_resume(self, text: str, *args, **kwargs):
        """
        Lightweight resume parsing — extracts basic info from resume text.
        Handles extra unused arguments gracefully.
        """
        summary = self.generate_summary(
            f"Extract name, email, skills, education, and experience from: {text}"
        )

        # Basic regex extraction (fallback)
        name = re.search(r"Name[:\s]*([A-Za-z\s]+)", text)
        email = re.search(r"[\w\.-]+@[\w\.-]+", text)
        skills = re.findall(
            r"(Python|Java|C\+\+|Machine Learning|FastAPI|Django|SQL)", text, re.I
        )

        # Return consistent structure
        return {
            "personalInfo": {
                "name": name.group(1).strip() if name else "Not found",
                "contact": {"email": email.group(0) if email else "Not found"},
            },
            "skills": list(set(skills)) if skills else [],
            "experience": [],
            "education": [],
            "summary": summary,
        }


# ✅ Global instance for import
ai_service = LightweightAIService()
