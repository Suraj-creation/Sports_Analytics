"""
LLM Provider interface and cloud/local implementations.
Supports Azure OpenAI, OpenAI Direct, and local LM Studio.
"""
import os
from abc import ABC, abstractmethod
from typing import Any, Optional
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def _get_llm(self) -> Any:
        """Get the underlying LangChain LLM instance."""
        pass

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def invoke(self, prompt: str) -> Any:
        """Invoke the LLM with a prompt."""
        pass


class AzureOpenAIProvider(LLMProvider):
    """Azure OpenAI cloud provider implementation."""
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        deployment: Optional[str] = None,
        api_version: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        timeout: int = 60
    ):
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment = deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-mini")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self._llm = None
        
    def _get_llm(self):
        """Lazy-load AzureChatOpenAI instance."""
        if self._llm is None:
            from langchain_openai import AzureChatOpenAI
            self._llm = AzureChatOpenAI(
                azure_endpoint=self.endpoint,
                azure_deployment=self.deployment,
                openai_api_version=self.api_version,
                openai_api_key=self.api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout
            )
        return self._llm

    def generate_response(self, prompt: str) -> str:
        try:
            llm = self._get_llm()
            response = llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            print(f"[ERROR] Azure OpenAI response generation failed: {e}")
            return "Error generating response"

    def invoke(self, prompt: str) -> Any:
        try:
            llm = self._get_llm()
            return llm.invoke(prompt)
        except Exception as e:
            print(f"[ERROR] Azure OpenAI invoke failed: {e}")
            return None


class OpenAIProvider(LLMProvider):
    """Direct OpenAI API provider implementation."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        timeout: int = 60
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self._llm = None

    def _get_llm(self):
        """Lazy-load ChatOpenAI instance."""
        if self._llm is None:
            from langchain_openai import ChatOpenAI
            self._llm = ChatOpenAI(
                model=self.model,
                api_key=self.api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout
            )
        return self._llm

    def generate_response(self, prompt: str) -> str:
        try:
            llm = self._get_llm()
            response = llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            print(f"[ERROR] OpenAI response generation failed: {e}")
            return "Error generating response"

    def invoke(self, prompt: str) -> Any:
        try:
            llm = self._get_llm()
            return llm.invoke(prompt)
        except Exception as e:
            print(f"[ERROR] OpenAI invoke failed: {e}")
            return None


class LMStudioProvider(LLMProvider):
    """LM Studio local provider implementation."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:1234/v1", model: str = "phi-3-mini-128k-instruct"):
        self.base_url = os.getenv("LM_STUDIO_BASE_URL", base_url)
        self.model = os.getenv("LM_STUDIO_MODEL", model)
        self._llm = None
    
    def _get_llm(self):
        """Lazy load local ChatOpenAI instance."""
        if self._llm is None:
            from langchain_openai import ChatOpenAI
            self._llm = ChatOpenAI(
                model=self.model,
                base_url=self.base_url,
                api_key="lm-studio",
                temperature=0.3,
                max_tokens=2048,
                timeout=120
            )
        return self._llm
    
    def generate_response(self, prompt: str) -> str:
        try:
            llm = self._get_llm()
            response = llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            print(f"[ERROR] LM Studio response error: {e}")
            return "Error generating response"
    
    def invoke(self, prompt: str) -> Any:
        try:
            llm = self._get_llm()
            return llm.invoke(prompt)
        except Exception as e:
            print(f"[ERROR] LM Studio invoke error: {e}")
            return None


class LLMProviderFactory:
    """Factory for creating and accessing LLM providers."""
    
    @staticmethod
    def create_provider(provider_type: Optional[str] = None, **kwargs) -> LLMProvider:
        """Create an LLM provider instance based on type or environment configuration."""
        if provider_type is None:
            provider_type = os.getenv("LLM_PROVIDER", "azure_openai").lower()
            
        provider_type = provider_type.lower()
        if provider_type in ("azure", "azure_openai"):
            return AzureOpenAIProvider(**kwargs)
        elif provider_type in ("openai", "chatgpt"):
            return OpenAIProvider(**kwargs)
        elif provider_type in ("lm_studio", "local"):
            return LMStudioProvider(**kwargs)
        else:
            raise ValueError(f"Unknown provider type: {provider_type}. Expected 'azure_openai', 'openai', or 'lm_studio'.")
    
    @staticmethod
    def get_default_llm() -> Any:
        """Convenience method to retrieve the underlying LangChain LLM from configured provider."""
        provider = LLMProviderFactory.create_provider()
        return provider._get_llm()

    @staticmethod
    def create_from_config(config: dict) -> LLMProvider:
        """Create an LLM provider from configuration dictionary."""
        provider_type = config.get("type", os.getenv("LLM_PROVIDER", "azure_openai"))
        provider_config = config.get("config", {})
        return LLMProviderFactory.create_provider(provider_type, **provider_config)
