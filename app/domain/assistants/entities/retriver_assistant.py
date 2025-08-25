from domain.assistants.interfaces.llm_assistant_interface import LlmAssistantInterface
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.llms.base import LLM
from langchain_core.utils.json import parse_json_markdown
import json


class RetriverAssistant(LlmAssistantInterface):

    def __init__(self, llm: LLM) -> None:
        self.llm = llm
        self.prompt_template = None
        self.response_schemas = None
        self.initialize_assistant()

    def initialize_assistant(self) -> None:
        "Initialize the ExecutiveAssistant with necessary prompt_template."
        self.response_schemas = [
            ResponseSchema(
                name="user_info",
                type="object",
                description=(
                    """
                    Un objeto que contiene información del usuario con los siguientes atributos:
                    - tipo_documento (string): Tipo de documento. 'CC' por defecto.
                    - nro_documento (string): Número de documento.
                    - primer_nombre (string): Primer nombre.
                    - segundo_nombre (string): Segundo nombre.
                    - primer_apellido (string): Primer apellido.
                    - segundo_apellido (string): Segundo apellido.
                    - nombre_completo (string): Nombre completo.
                    - direccion (string): Dirección default: No registra.
                    - pais_id: (json): default { id: 19, codigo_pais: "+57", show_data: "Colombia"}
                    - telefono (string): Número de teléfono default: 0000000000.
                    - email (string): Correo electrónico default: noregistra@gmail.com.
                    - fecha_nacimiento (string): Fecha de nacimiento formato YYYY-MM-DD.
                    - fecha_consulta (string): Fecha programada para consulta. Formato YYYY-MM-DD.
                    - hora_inicio (string): ejemplo: "15:20:00". Hora de inicio de la consulta.
                    - hora_fin (string): ejemplo: "16:20:00". Hora de fin de la consulta.
                    - tipo_consulta (string): Tipo de consulta. PRESENCIAL ó VIRTUAL.
                    """
                ),
            )
        ]
        self.prompt_template = ChatPromptTemplate(
            [
                (
                    "system",
                    "Eres un asistente virtual que retrae información relevante de manera eficiente basado en unas conversaciones.",
                ),
                (
                    "system",
                    "### IMPORTANTE: \n {format_instructions}",
                ),
                (
                    "system",
                    "Devuelve la información en formato JSON, sin ningún otro texto adicional.",
                ),
                (
                    "system",
                    "El número de télefono del usuario es: {telefono}.",
                ),
                (
                    "user",
                    "Conversación: {conversation}",
                ),
            ]
        )

    def invoke(self, *args, **kwargs) -> dict:
        """
        Invoke the LLM assistant with a given prompt.
        """
        try:
            print("🔔 Invoking Retriver Assistant...", "\n")
            if not self.prompt_template:
                raise Exception(
                    "Prompt template not initialized. Call initialize_assistant first."
                )

            conversation = kwargs.get("conversation", "")
            telefono = kwargs.get("telefono", "0000000000")

            output_parser = StructuredOutputParser.from_response_schemas(
                self.response_schemas
            )
            format_instructions = output_parser.get_format_instructions()

            print("== Format Instructions ==", "\n")
            print(format_instructions, "\n")
            print("Conversation to process:", "\n")
            print(conversation, "\n")

            prompt = self.prompt_template.invoke(
                {
                    "format_instructions": format_instructions,
                    "conversation": " * "
                    + "\n * ".join(
                        json.dumps(c, ensure_ascii=False) for c in conversation
                    ),
                    "telefono": telefono,
                }
            )

            response = self.llm.invoke(prompt)
            json_response = parse_json_markdown(response.content)

            print("🔔 Response from Retriver Assistant in JSON mood:", "\n")
            print(json_response, "\n")

            return json_response

        except Exception as e:
            print(f"Error invoking Retriver Assistant: {e}", "\n")
            return {"error": str(e)}
