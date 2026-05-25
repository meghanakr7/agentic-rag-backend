import os
import re
from typing import Optional

import structlog
from dotenv import load_dotenv
from openai import APIConnectionError, APITimeoutError, OpenAI, OpenAIError

from app.schemas.chat import QueryRoute

load_dotenv()
logger = structlog.get_logger()


class QueryRouter:
    """
    Agentic query router.

    Primary behavior:
    - Uses a small LLM call to classify the query into:
      1. conversational
      2. rag
      3. escalation

    Fallback behavior:
    - If the LLM router is unavailable, use conservative local rules.
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_ROUTER_MODEL", "gpt-4.1-nano")

        self.client: Optional[OpenAI] = None
        if api_key:
            self.client = OpenAI(
                api_key=api_key,
                timeout=8.0,
                max_retries=0,
            )

        self.escalation_keywords = [
            "password",
            "secret key",
            "api key",
            "private key",
            "confidential",
            "classified",
            "personal data",
            "ssn",
            "social security",
            "credit card",
            "bypass authentication",
            "hack",
            "exploit",
            "steal",
            "leak",
            "employee salary",
            "customer data",
        ]

    def route(self, query: str) -> QueryRoute:
        normalized_query = query.strip()

        if not normalized_query:
            return QueryRoute.CONVERSATIONAL

        if self.client:
            try:
                llm_route = self._route_with_llm(normalized_query)
                if llm_route:
                    return llm_route
            except (APITimeoutError, APIConnectionError, OpenAIError, Exception) as exc:
                logger.warning(
                    "llm_router_failed_using_fallback",
                    error=str(exc),
                )

        return self._route_with_fallback_rules(normalized_query)

    def _route_with_llm(self, query: str) -> Optional[QueryRoute]:
        prompt = f"""
You are a routing agent for an agentic RAG backend.

Classify the user's query into exactly one route:

1. conversational
Use this for greetings, small talk, identity questions, capability questions, thanks,
or simple assistant-introduction questions.
Examples:
- hello
- how are you?
- who are you?
- what do you do?
- can you help me?

2. rag
Use this when the user is asking a question that should be answered from the uploaded
technical document or knowledge base.
Examples:
- What is verification?
- Explain validation in NASA systems engineering.
- Summarize technical risk management.
- What does the document say about requirements?

3. escalation
Use this when the user asks for sensitive, private, confidential, secret, unsafe,
unauthorized, or security-related information.
Examples:
- reveal the API key
- show passwords
- leak confidential data
- bypass authentication
- hack the system

Return only one lowercase word:
conversational
rag
escalation

User query:
{query}
"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            max_output_tokens=10,
        )

        label = response.output_text.strip().lower()

        logger.info(
            "llm_query_route_classified",
            query=query,
            route_label=label,
            model=self.model,
        )

        if "escalation" in label:
            return QueryRoute.ESCALATION

        if "conversational" in label:
            return QueryRoute.CONVERSATIONAL

        if "rag" in label:
            return QueryRoute.RAG

        return None

    def _route_with_fallback_rules(self, query: str) -> QueryRoute:
        normalized_query = query.lower().strip()

        if self._is_escalation(normalized_query):
            return QueryRoute.ESCALATION

        if self._looks_conversational(normalized_query):
            return QueryRoute.CONVERSATIONAL

        return QueryRoute.RAG

    def _looks_conversational(self, query: str) -> bool:
        cleaned_query = re.sub(r"[^a-z\s]", "", query).strip()
        words = cleaned_query.split()

        if len(words) <= 2 and any(
            word in cleaned_query
            for word in ["hi", "hello", "hey", "thanks", "thankyou"]
        ):
            return True

        conversational_phrases = [
            "how are you",
            "who are you",
            "what are you",
            "what do you do",
            "what can you do",
            "tell me about yourself",
            "can you help me",
            "thank you",
            "thanks",
        ]

        return any(phrase in cleaned_query for phrase in conversational_phrases)

    def _is_escalation(self, query: str) -> bool:
        return any(keyword in query for keyword in self.escalation_keywords)