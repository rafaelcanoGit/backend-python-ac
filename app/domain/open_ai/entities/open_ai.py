from langchain.llms.base import LLM
from typing import List, Optional, Dict, Any
from pydantic import Field

# Override de la clase LLM de langchain para crear un modelo personalizado
class OpenAI(LLM):
    """Wrapper around OpenAI's GPT-3.5-turbo and GPT-4 models."""

    model_name: str = Field(default="gpt-4o")
    temperature: float = Field(default=0.0)

    @property
    def _llm_type(self) -> str:
        return "openai"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"model_name": self.model_name, "temperature": self.temperature}

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response = f"Procesando el prompt: {prompt}"
        if stop:
            for stop_word in stop:
                response = response.split(stop_word)[0]
        return response


# Instanciar la clase OpenAI
custom_llm = OpenAI(model_name="gpt-4o", temperature=0.7)
response = custom_llm.invoke("Hola, ¿cómo estás?")
print(response)
