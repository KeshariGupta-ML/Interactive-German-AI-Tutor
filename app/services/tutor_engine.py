import google.api_core.exceptions as google_exceptions
from typing import List, Tuple, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


class TutorResponse(BaseModel):
    german_reply: str = Field(description="The response spoken to the student in simple, clear A1 German.")
    english_translation: str = Field(description="A helpful translation or hint in English of your german_reply.")
    corrections_found: Optional[str] = Field(
        description="Grammar/spelling corrections or English-to-German transition guidance.")
    detected_vocabulary: List[str] = Field(description="List of 2-4 core vocabulary words used in this turn.")


class GermanTutorEngine:
    """Manages the AI Tutor execution using dynamically provided user API keys."""

    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.3):
        self.model_name = model_name
        self.temperature = temperature
        self.prompt_template = self._build_prompt_template()

    def _build_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", (
                "You are 'Lukas', an encouraging, patient personal German A1 AI Tutor.\n"
                "Keep your sentences short, simple, and strictly at an A1 level.\n"
                "You must communicate through a structured JSON response layout.\n\n"

                "CRITICAL LANGUAGE RULES FOR YOUR FIELDS:\n"
                "1. 'german_reply': ALWAYS write this entirely in simple A1 German. This is what you speak to the student.\n"
                "2. 'english_translation': ALWAYS provide a clean English translation of your own 'german_reply'.\n"

                "3. 'corrections_found' (THE GRAMMAR FIXES):\n"
                "   - ALWAYS WRITE THIS FIELD ENTIRELY IN ENGLISH so the beginner student can understand your teaching.\n"
                "   - If the student responds in English, explain how to say it properly in German.\n"
                "   - If the student makes a German grammar or spelling mistake (e.g., writing 'ich Essen' instead of 'Ich esse'), "
                "break down the rule clearly in English.\n"
                "   - Example explanation: \"Great effort! You wrote 'ich Essen', but in German, verbs are conjugated based on the subject. "
                "For 'ich' (I), the verb 'essen' drops the '-n' to become 'esse'. Also, unlike nouns, verbs are not capitalized unless they start a sentence: 'Ich esse'.\"\n"
                "   - If their input was flawless German, leave this field blank.\n\n"

                "4. ALWAYS output data that perfectly matches the required structural fields."
            )),
            ("placeholder", "{chat_history}"),
            ("user", "{student_input}")
        ])

    def generate_response(self, student_input: str, chat_history: List[Tuple[str, str]], user_api_key: str):
        """
        Executes the tutor response using the specific user's API key.
        Returns a tuple: (TutorResponse object or None, Error Message string or None)
        """
        if not user_api_key or user_api_key.strip() == "":
            return None, "API Key is missing. Please add your Gemini API key in your profile settings."

        try:
            # 1. Dynamically initialize the model using the user's key
            llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=user_api_key,
                temperature=self.temperature
            )

            # 2. Bind structure and build the runtime chain
            structured_llm = llm.with_structured_output(TutorResponse)
            chain = self.prompt_template | structured_llm

            # 3. Invoke the API
            result = chain.invoke({
                "chat_history": chat_history,
                "student_input": student_input
            })

            return result, None

        # 4. Handle specific Gemini API errors explicitly
        except google_exceptions.InvalidArgument as e:
            return None, "Your Gemini API Key appears to be invalid or expired. Please check your profile settings."

        except google_exceptions.ResourceExhausted as e:
            return None, "Your Gemini API quota has been exhausted or rate-limited. Please check your Google AI Studio billing status."

        except google_exceptions.InternalServerError as e:
            return None, "Google's AI servers are temporarily overloaded. Please try sending your message again in a moment."

        except Exception as e:
            return None, f"An unexpected error occurred while connecting to your AI engine: {str(e)}"