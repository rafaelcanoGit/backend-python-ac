from domain.assistants.interfaces.llm_assistant_interface import LlmAssistantInterface
from langchain.llms.base import LLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool, tool
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage
from typing import List
from domain.whatsapp.entities.langraph_state import LangGraphState
from domain.whatsapp.entities.chat_state import ChatState


class ExecutiveAssistant(LlmAssistantInterface):

    def __init__(
        self,
    ) -> None:
        self.prompt_template = None
        # Initialize the Assistant rules.
        self.initialize_assistant()

    def initialize_assistant(self) -> None:
        "Initialize the ExecutiveAssistant with necessary prompt_template."

        self.prompt_template = ChatPromptTemplate(
            [
                # Identidad y rol
                (
                    "system",
                    "* Identidad y rol:\n"
                    "* Eres Bella Sofía, 30 años, asistente virtual comercial del Dr. Andrés Cánchica en Medellín, Colombia.\n",
                ),
                # Personalidad
                (
                    "system",
                    "* Personalidad:\n"
                    "* Eres Amable, empática y profesional; inspiras confianza con respuestas breves y directas (usa el mínimo de tokens posible).\n",
                ),
                # Servicios
                (
                    "system",
                    "* Servicios:\n"
                    "  1. Consulta/Valoración\n"
                    "  2. Cirugía estética\n"
                    "  3. Cirugía reconstructiva\n"
                    "  4. Mínimamente invasivos (Botox, ácido hialurónico)",
                ),
                # Comportamiento
                (
                    "system",
                    "* Comportamiento:\n"
                    "* Tu objetivo principal es guiar al usuario para gestionar una consulta con el Dr. Andrés Cánchica. Toda la conversación debe estar orientada a llevarlo paso a paso hasta confirmar una fecha de consulta o valoración con su respectivo pago.\n"
                    "* *Conduce la conversación siguiendo este flujo:* \n"
                    "  1. Preséntate y pregunta siempre: '¿Con quién tengo el gusto de hablar?'\n"
                    "  2. Identifica con claridad el interés del usuario (consulta/valoración o cirugía). Confírmalo con él antes de avanzar.\n"
                    "  3. Aplica los pasos correspondientes según el interés identificado (usa las 'Condiciones y pasos según interés').\n"
                    "* Importante: haz solo una pregunta a la vez, no te saltes ningún paso, mantén un tono neutral y no emitas juicios.\n",
                ),
                # Condiciones
                (
                    "system",
                    "* Condiciones y pasos según interés:\n"
                    "**IMPORTANTE:** Este flujo determina cómo debe continuar la conversación. Avanza paso a paso según el interés del usuario:\n"
                    "  • Si el usuario tiene interés en una *Valoración o Consulta*:\n"
                    "     Paso 1. Confirma si desea consulta *virtual* ó *presencial*.\n"
                    "     Paso 2. Ofrece las fechas disponibles para consulta. (usando la tool `get_available_slots`)\n"
                    "     Paso 3. Cuando elija una fecha (ej. '9:00AM-10:00AM 02-Octubre 2025'), confírmala textualmente. Ejemplo: 'Te confirmo que elegiste la fecha...'. Luego continúa.\n"
                    "     Paso 4. Realiza todas las preguntas pre-consulta una a una, en orden. **No te saltes ninguna.**\n"
                    "     Paso 5. Una vez respondidas todas las preguntas pre-consulta, programa la pre-agenda (usando la tool `schedule_pre_consultation`).\n"
                    "     Paso 6. Confirma si desea proceder con el pago y pregunta su método preferido: *Transferencia Bancolombia* o *Link de pago*.\n"
                    "     Paso 7. Envía el método de pago elegido.\n"
                    "     Paso 8. Solicita y comprueba el comprobante de pago.\n"
                    "  • Si el usuario tiene interés en una *Cirugía*: Debes informarle que es necesario realizar una valoración previa.\n",
                ),
                # Preguntas previas
                (
                    "system",
                    "* Preguntas Pre-consulta (realízalas una por una) **en este orden y sin omitir ninguna**:\n"
                    "1. ¿Cuál es tu nombre completo y correo electrónico?\n"
                    "2. Documento de identidad y fecha de nacimiento.\n"
                    "3. Cirugía de interés.\n",
                ),
                # FAQs
                (
                    "system",
                    "* FAQs:\n"
                    "  • ¿Valoración virtual? Sí, mismo costo.\n"
                    "  • ¿Valoración presencial? Sí, en Medellín.\n"
                    "  • Pagos nacionales? Transferencia Bancolombia.\n"
                    "  • Pagos fuera del país? Compartimos link de pago.\n"
                    "  • Duración consulta? 45–60 min.\n"
                    "  • Costo valoración? 300 000 COP (se abona si hay cirugía). \n"
                    "  • ¿Qué incluye valoración? Evaluación de tu caso según la cirugía de interés, y respuesta a tus preguntas.\n"
                    "  • ¿Precios cirugía? Depende de la cirugía y tu caso, se define en la valoración.\n",
                ),
                # Observaciones finales
                (
                    "system",
                    "* Observaciones:\n"
                    "  • Puedes usar un lenguaje cercano o coloquial, siempre manteniendo el profesionalismo y respeto.\n"
                    "  • Si ya identificaste al usuario (nombre e intención), continúa con el flujo sin repetir preguntas innecesarias.\n"
                    "  • Si el usuario ya indicó una fecha de consulta (ejemplo: '9:00AM-10:00AM 02-Octubre 2025'), confírmala y avanza al siguiente paso sin repetir la oferta de fechas.\n"
                    "  • Si el usuario ya completó todos los pasos, incluyendo el pago, confirma la cita, agradece su confianza y finaliza la conversación de manera amable.\n"
                    "  • Si el usuario decide NO realizar el pago en este momento, recuérdale que debe hacerlo con al menos 24 horas de anticipación a la consulta, de lo contrario la cita será cancelada automáticamente.\n"
                    "  • No estás autorizado a dar precios de cirugías, ni siquiera aproximados. Debes explicar que el valor depende de la evaluación personalizada que se realiza durante la valoración.\n"
                    "  • Si al momento de programar la consulta en el horario seleccionado por el usuario y este horario ya no está disponible y el usuario desea elegir otro horario, debes volver al Paso 2: Ofrece las fechas disponibles para consulta. (usando la tool `get_available_slots`). Cuando el usuario vuelva a elegir una nueva fecha ya NO hacemos las preguntas pre-consulta sino que continuamos al Paso 5. programa la pre-agenda (usando la tool `schedule_pre_consultation`).\n",
                ),
                # Variables de contexto
                ("system", "* Responde en el lenguaje: {language}.\n"),
                ("system", "* Teléfono Usuario: {user_phone}.\n"),
                (
                    "system",
                    "* Memorias de conversación entre tú y el usuario relevantes recuperadas: {memories}.\n",
                ),
                # Mensaje del usuario
                ("user", "Mensaje Usuario: {user_message}"),
            ]
        )

    def invoke(self, *args, **kwargs) -> dict:
        """
        Invoke the LLM assistant with a given prompt.
        """
        try:
            print("🔔 Invoking the Executive Assistant...", "\n")
            if not self.prompt_template:
                raise Exception(
                    "Prompt template not initialized. Call initialize_assistant first."
                )

            builder_state = kwargs.get("builder_state")
            langraph_state = kwargs.get("langraph_state")
            user_phone = kwargs.get("user_phone", "")
            user_message = kwargs.get("user_message", "")

            graph = self.create_chat_state_graph(builder_state, langraph_state)

            state_obj = ChatState(
                prompt_template=self.prompt_template,
                user_phone=user_phone,
                user_message=user_message,
            )

            response = graph.invoke(state_obj)

            return response
        except Exception as e:
            print(f"An error occurred while invoking the assistant: {e}", "\n")
            return [
                {
                    "format_type": "error",
                    "response": {
                        "message": f"An error occurred while invoking the assistant: {str(e)}",
                    },
                }
            ]

    # ========== Create the chat state graph for LangGraph ==========
    def create_chat_state_graph(
        self, builder_state: StateGraph, langraph_state: LangGraphState
    ) -> StateGraph:
        """
        Creates and returns a state graph for chat processing.
        Only adds nodes if the graph is not compiled and nodes don't exist.
        """
        if (
            not hasattr(builder_state, "state_type")
            or builder_state.state_type != ChatState
        ):
            raise TypeError("builder_state must be configured with ChatState type")

        # Check if the graph is already compiled
        if hasattr(builder_state, "_compiled") and builder_state._compiled is not None:
            print("✅ El grafo ya está compilado, retornando versión existente")
            return builder_state._compiled

        # Check if nodes already exist before adding them
        existing_nodes = (
            builder_state.nodes.keys() if hasattr(builder_state, "nodes") else []
        )

        # Add nodes only if they don't exist and graph is not compiled
        if "recuperar_memorias" not in existing_nodes:
            print("➕ Agregando nodo 'recuperar_memorias'")
            builder_state.add_node(
                "recuperar_memorias", langraph_state.retrieve_memories
            )
        else:
            print("⏩ Nodo 'recuperar_memorias' ya existe")

        if "generar_respuesta" not in existing_nodes:
            print("➕ Agregando nodo 'generar_respuesta'")
            builder_state.add_node(
                "generar_respuesta", langraph_state.generate_response
            )
        else:
            print("⏩ Nodo 'generar_respuesta' ya existe")

        if "guardar_memoria" not in existing_nodes:
            print("➕ Agregando nodo 'guardar_memoria'")
            builder_state.add_node("guardar_memoria", langraph_state.save_memory)
        else:
            print("⏩ Nodo 'guardar_memoria' ya existe")

        # Set the entry point only if not set
        if (
            not hasattr(builder_state, "entry_point")
            or builder_state.entry_point is None
        ):
            print("📍 Estableciendo punto de entrada")
            builder_state.set_entry_point("recuperar_memorias")
        else:
            print(f"⏩ Punto de entrada ya establecido: {builder_state.entry_point}")

        # Define edges between nodes only if not already defined
        existing_edges = getattr(builder_state, "_edges", [])

        recuperar_to_generar = ("recuperar_memorias", "generar_respuesta")
        generar_to_guardar = ("generar_respuesta", "guardar_memoria")
        guardar_to_end = ("guardar_memoria", END)

        if recuperar_to_generar not in existing_edges:
            print("🔗 Agregando arista: recuperar_memorias → generar_respuesta")
            builder_state.add_edge(*recuperar_to_generar)
        else:
            print("⏩ Arista recuperar_memorias → generar_respuesta ya existe")

        if generar_to_guardar not in existing_edges:
            print("🔗 Agregando arista: generar_respuesta → guardar_memoria")
            builder_state.add_edge(*generar_to_guardar)
        else:
            print("⏩ Arista generar_respuesta → guardar_memoria ya existe")

        if guardar_to_end not in existing_edges:
            print("🔗 Agregando arista: guardar_memoria → END")
            builder_state.add_edge(*guardar_to_end)
        else:
            print("⏩ Arista guardar_memoria → END ya existe")

        # Compile and return the graph only if not compiled
        if not getattr(builder_state, "_compiled", None):
            print("⚙️ Compilando grafo...")
            compiled_graph = builder_state.compile()
            builder_state._compiled = compiled_graph
            print("Grafo LangGraph creado con éxito. ✅", "\n")
            return compiled_graph
        else:
            print("✅ El grafo ya está compilado, retornando versión existente")
            return builder_state._compiled
