import google.generativeai as genai
from openai import OpenAI
from ai_reviewer.config import Config, ConfigError

class AIClientError(Exception):
    """Custom exception raised when an API request fails."""
    pass

class AIClient:
    """Interacts with the selected AI model API to review/explain code."""

    def __init__(self):
        # 1. Determine provider & key
        try:
            self.provider = Config.get_provider()
            self.api_key = Config.get_api_key(self.provider)
            self.model_name = Config.get_model(self.provider)
        except ConfigError as e:
            raise AIClientError(f"Configuration configuration failed:\n{str(e)}")

        # 2. Initialize the corresponding client
        self.openai_client = None
        if self.provider == "openai":
            try:
                self.openai_client = OpenAI(api_key=self.api_key)
            except Exception as e:
                raise AIClientError(f"Failed to initialize OpenAI Client: {str(e)}")
        elif self.provider == "gemini":
            try:
                genai.configure(api_key=self.api_key)
            except Exception as e:
                raise AIClientError(f"Failed to initialize Google Gemini Client: {str(e)}")

    def generate_feedback(self, system_prompt: str, user_prompt: str) -> str:
        """
        Sends the system and user prompts to the AI provider and retrieves the response.
        
        Returns:
            The markdown-formatted text response from the model.
        """
        if self.provider == "gemini":
            return self._call_gemini(system_prompt, user_prompt)
        elif self.provider == "openai":
            return self._call_openai(system_prompt, user_prompt)
        else:
            raise AIClientError(f"Unsupported provider: {self.provider}")

    def _call_gemini(self, system_prompt: str, user_prompt: str) -> str:
        """Helper to invoke the Google Gemini API."""
        try:
            # Using google-generativeai SDK
            # Set system instruction and temperature
            generation_config = genai.types.GenerationConfig(
                temperature=0.2,  # Low temperature for analytical, consistent responses
            )
            
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt,
                generation_config=generation_config
            )
            
            response = model.generate_content(user_prompt)
            if not response.text:
                raise AIClientError("Received an empty response from Gemini API.")
            return response.text
        except Exception as e:
            raise AIClientError(
                f"Gemini API request failed: {str(e)}\n"
                "Please verify your GEMINI_API_KEY and network connection."
            )

    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Helper to invoke the OpenAI API."""
        if not self.openai_client:
            raise AIClientError("OpenAI client was not initialized properly.")
            
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Analytical consistency
            )
            
            content = response.choices[0].message.content
            if not content:
                raise AIClientError("Received an empty response from OpenAI API.")
            return content
        except Exception as e:
            raise AIClientError(
                f"OpenAI API request failed: {str(e)}\n"
                "Please verify your OPENAI_API_KEY and network connection."
            )
        
    def get_info_string(self) -> str:
        """Returns a string describing the current active provider and model."""
        return f"[bold cyan]{self.provider.upper()}[/bold cyan] (Model: [green]{self.model_name}[/green])"
