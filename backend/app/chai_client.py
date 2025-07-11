import aiohttp
import asyncio
import logging
from typing import Dict, List, Optional
import backoff
from datetime import datetime

logger = logging.getLogger(__name__)


class ChaiAPIClient:
    """Async client for interacting with CHAI's chat API"""

    def __init__(self, api_key: str):
        self.base_url = "http://guanaco-submitter.guanaco-backend.k2.chaiverse.com"
        self.endpoint = "/endpoints/onsite/chat"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=30)

        # Default safety prompt
        self.safety_prompt = """You are a helpful, harmless, and honest AI friend. 
        Always respond in a safe and appropriate manner. Be respectful and considerate in your responses.
        """

    async def initialize(self):
        """Initialize the aiohttp session"""
        if not self.session:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=self.timeout
            )
            logger.info("CHAI API client session initialized")

    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("CHAI API client session closed")

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=60
    )
    async def send_message(
            self,
            data: Dict,
            user_message: Optional[str] = None
    ) -> Dict:
        """
        Send a message to the CHAI API with retry logic

        Args:
            data: Dictionary containing prompt, bot_name, user_name, chat_history
            user_message: Optional current user message to append to history

        Returns:
            Dictionary with the API response
        """
        if not self.session:
            await self.initialize()

        # Prepare the request data
        request_data = {
            "memory": data.get("memory", ""),
            "prompt": self._prepare_prompt(data.get("prompt", "")),
            "bot_name": data.get("bot_name", "Assistant"),
            "user_name": data.get("user_name", "User"),
            "chat_history": data.get("chat_history", [])
        }

        # If user_message is provided, append it to chat history
        if user_message:
            request_data["chat_history"].append({
                "sender": request_data["user_name"],
                "message": user_message
            })

        logger.info(f"Sending request to CHAI API for bot: {request_data['bot_name']}")

        try:
            async with self.session.post(
                    f"{self.base_url}{self.endpoint}",
                    headers=self.headers,
                    json=request_data
            ) as response:
                response.raise_for_status()
                result = await response.json()

                # Extract the bot's response
                bot_response = result.get("model_output", result.get("response", result.get("message", "")))

                logger.info(f"Received response from CHAI API: {len(bot_response)} chars")

                return {
                    "response": bot_response,
                    "bot_name": request_data["bot_name"],
                    "timestamp": datetime.utcnow().isoformat()
                }

        except aiohttp.ClientResponseError as e:
            logger.error(f"CHAI API error: {e.status} - {e.message}")
            if e.status == 401:
                raise Exception("Invalid API key")
            elif e.status == 429:
                raise Exception("Rate limit exceeded")
            else:
                raise Exception(f"API error: {e.message}")
        except Exception as e:
            logger.error(f"Unexpected error calling CHAI API: {e}")
            raise

    def _prepare_prompt(self, custom_prompt: str) -> str:
        """Prepare the prompt with safety instructions"""
        if custom_prompt:
            return f"{self.safety_prompt}\n\n{custom_prompt}"
        return self.safety_prompt

    def create_personality_prompt(
            self,
            personality_type: str,
            custom_traits: Optional[List[str]] = None
    ) -> str:
        """Create a personality-specific prompt for human personas"""

        base_prompts = {
            "friendly": "You are a warm, outgoing person who loves meeting new people. You're naturally cheerful, use casual language, and genuinely enjoy conversations. You share personal experiences and ask engaging questions about others' lives.",
            "professional": "You are a successful professional with strong communication skills. You speak with confidence and clarity, share insights from your career, and maintain appropriate boundaries while being personable.",
            "creative": "You are an artistic and imaginative person who sees the world differently. You love discussing ideas, sharing creative projects, and inspiring others to think outside the box. You often reference art, music, or literature.",
            "analytical": "You are a logical thinker who enjoys analyzing situations and solving problems. You appreciate data and facts, ask thoughtful questions, and like to understand how things work. You're naturally curious about systems and patterns.",
            "empathetic": "You are a deeply caring person who connects emotionally with others. You're a great listener, validate feelings, and offer genuine support. You share your own vulnerabilities and create safe spaces for others.",
            "humorous": "You are naturally funny and love making people laugh. You use appropriate humor, share amusing stories from your life, and can lighten the mood in any conversation. You're quick-witted but never mean-spirited.",
            "adventurous": "You are someone who loves new experiences and exploring the world. You're always planning your next trip, trying new activities, and encouraging others to step out of their comfort zones. You share exciting stories from your adventures.",
            "intellectual": "You are well-read and enjoy deep discussions about ideas, philosophy, science, and culture. You love learning and sharing knowledge, but in a conversational way that doesn't feel preachy. You ask thought-provoking questions."
        }

        prompt = base_prompts.get(
            personality_type,
            "You are a helpful AI friend."
        )

        if custom_traits:
            traits_str = ", ".join(custom_traits)
            prompt += f"\n\nAdditional traits: {traits_str}"

        return f"{self.safety_prompt}\n\n{prompt}"