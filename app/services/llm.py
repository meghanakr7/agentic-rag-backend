import os
from typing import List

import structlog
from dotenv import load_dotenv
from openai import APIConnectionError, APITimeoutError, OpenAI, OpenAIError

logger = structlog.get_logger()

load_dotenv()


class LLMService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing. Please set it in your .env file.")

        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.client = OpenAI(
            api_key=api_key,
            timeout=20.0,
            max_retries=1,
        )

    def generate_answer(self, query: str, context_chunks: List[str]) -> str:
        context = "\n\n---\n\n".join(context_chunks)

        prompt = f"""
You are an aerospace systems engineering assistant.

Answer the user's question using only the provided context from the uploaded document.

Rules:
- Do not invent facts.
- If the context does not contain enough information, say that the uploaded document does not provide enough information.
- Keep the answer clear, professional, and interview-demo friendly.
- Keep the answer under 180 words unless the user asks for a detailed explanation.
- Mention the source document only when useful.

User question:
{query}

Retrieved context:
{context}
"""

        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                max_output_tokens=400,
            )

            answer = response.output_text.strip()

            logger.info(
                "llm_answer_generated",
                model=self.model,
                answer_length=len(answer),
            )

            return answer

        except APITimeoutError as exc:
            logger.error("llm_timeout", error=str(exc))
            return (
                "The language model request timed out. "
                "Please try again in a moment."
            )

        except APIConnectionError as exc:
            logger.error("llm_connection_error", error=str(exc))
            return (
                "The language model service could not be reached. "
                "Please check your network connection and try again."
            )

        except OpenAIError as exc:
            logger.error("llm_api_error", error=str(exc))
            return (
                "The language model service returned an error. "
                "Please try again later."
            )