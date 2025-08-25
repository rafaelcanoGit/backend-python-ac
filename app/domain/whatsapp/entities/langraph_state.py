from langchain_community.vectorstores import VectorStore
from langchain.llms.base import LLM
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.documents import Document
from langchain_core.tools import Tool, tool
from langchain_core.prompts import ChatPromptTemplate
import uuid
from domain.whatsapp.entities.chat_state import ChatState
from infrastructure.interfaces.google_calendar_client_interface import (
    GoogleCalendarClientInterface,
)
from datetime import datetime, timedelta
from pydantic import create_model
from domain.whatsapp.interfaces.whatsapp_repository_interface import (
    WhatsappRepositoryInterface,
)


class LangGraphState:
    """Clase que contiene los nodos del gráfico de estados."""

    def __init__(
        self,
        llm: LLM,
        vectorstore: VectorStore,
        google_calendar_client: GoogleCalendarClientInterface,
        whatsapp_repository: WhatsappRepositoryInterface,
    ):
        self.llm = llm
        self.vectorstore = vectorstore
        self.google_calendar_client = google_calendar_client
        self.whatsapp_repository = whatsapp_repository

        # Inicializar herramientas.
        self.bind_llm_available_tools()

    # LLM Tools ==========
    def bind_llm_available_tools(self) -> None:
        """
        Bind available tools to the assistant.
        """
        print("🔨 Binding available tools for the Executive Assistant...", "\n")
        self.llm = self.llm.bind_tools(
            [
                Tool(
                    name="send_consulting_location",
                    func=self.send_consulting_location,
                    args_schema=create_model("EmptyArgs"),
                    description=(
                        "Invoca esta función **SÓLO cuando el usuario solicite explícitamente la ubicación del consultorio** "
                        "Del Dr. Andrés Cánchica (por ejemplo: '¿Dónde queda el consultorio?' o 'Ubicación, por favor').\n"
                        "La respuesta incluye un mensaje, coordenadas GPS y dirección física."
                    ),
                ),
                Tool(
                    name="get_available_slots",
                    func=self.get_available_slots,
                    args_schema=create_model("EmptyArgs"),
                    description=(
                        "Úsala *únicamente* en el **Paso 2** del flujo:\n"
                        "  El cual es: 2. Ofrece fechas de consulta disponibles.\n\n"
                        "▶️ Sólo cuando hayas confirmado que el usuario quiere reservar *consulta o valoración* (virtual o presencial) y estés listo para mostrarle opciones.\n"
                        "▶️ No la llames si el usuario aún no ha confirmado el tipo de consulta o si estás en cualquier otro paso."
                    ),
                ),
                Tool(
                    name="schedule_pre_consultation",
                    func=self.schedule_pre_consultation,
                    args_schema=create_model(
                        "ScheduleArgs",
                        full_name=(str, ...),
                        type_consultation=(str, ...),
                        user_phone=(str, ...),
                        start=(str, ...),
                        end=(str, ...),
                    ),
                    description=(
                        "Ejecuta esta función *inmediatamente después* de que el usuario haya respondido **todas** las preguntas pre-consulta:\n"
                        "  1. Nombre completo y email\n"
                        "  2. Documento de identidad y fecha de nacimiento\n"
                        "  3. Cirugía de interés\n\n"
                        "▶️ Sólo cuando la última pregunta ('Cirugía de interés') ya esté contestada.\n"
                        "▶️ No la llames si faltara alguna de las preguntas o si aún no se haya confirmado la fecha.\n\n"
                        "**Parámetros obligatorios:**\n"
                        "- `full_name`: nombre completo del paciente\n"
                        "- `type_consultation`: 'PRESENCIAL' o 'VIRTUAL'\n"
                        "- `user_phone`: número de contacto\n"
                        "- `start`: inicio (formato `'YYYY-MM-DDTHH:MM:SS'`, p.ej. `'2025-10-02T09:00:00'`)\n"
                        "- `end`: fin (mismo formato `'YYYY-MM-DDTHH:MM:SS'`, p.ej. `'2025-10-02T10:00:00'`)\n"
                    ),
                ),
                Tool(
                    name="send_payment_method_transfer",
                    func=self.send_payment_method_transfer,
                    args_schema=create_model("EmptyArgs"),
                    description=(
                        "Usa esta función **cuando estés en el paso #6 del flujo de reserva: 6.'Confirma y envía método de pago'**, "
                        "y el usuario haya elegido pagar por transferencia bancaria a Bancolombia.\n\n"
                        "Envía un mensaje con las instrucciones para completar la transferencia."
                    ),
                ),
                Tool(
                    name="send_payment_method_link",
                    func=self.send_payment_method_link,
                    args_schema=create_model("EmptyArgs"),
                    description=(
                        "Usa esta función **cuando estés en el paso #6 del flujo de reserva: 6.'Confirma y envía método de pago'**, "
                        "y el usuario indique que no tiene cuenta en Bancolombia o se encuentra fuera del país.\n\n"
                        "Envía las instrucciones necesarias para realizar el pago a través de link de pago."
                    ),
                ),
                Tool(
                    name="payment_received",
                    func=self.payment_received,
                    args_schema=create_model(
                        "PaymentReceivedArgs", user_phone=(str, ...)
                    ),
                    description=(
                        "Invoca esta función **cuando el usuario ha enviado el comprobante de pago (imagen) y se ha verificado su validez**. "
                        "Marca el pago como recibido y actualiza el estado del usuario en la base de datos.\n\n"
                        "**Requiere el siguiente dato obligatorio:**\n"
                        "- user_phone: número de teléfono del usuario que realizó el pago.\n\n"
                    ),
                ),
            ]
        )

    def send_consulting_location(self) -> dict:
        """
        Envía la ubicación del consultorio del Dr. Andrés Cánchica.

        El formato de respuesta incluye:
        - message: texto explicativo
        - latitude / longitude: coordenadas GPS
        - name: nombre del lugar
        - address: dirección completa
        """
        return {
            "format_type": "location",
            "response": {
                "message": "Te comparto la ubicación del consultorio del Dr. Andrés Cánchica: ...[Ubicación enviada]. 📍",
                "latitude": "6.197648678064593",
                "longitude": "-75.55816435480772",
                "name": "Consultorio Dr. Andrés Cánchica. El Tesoro, Torre Médica 2 Consultorio 1556.",
                "address": "Cra. 25a #1A Sur - 45, El Poblado, Medellín, Antioquia, Colombia",
            },
        }

    def get_available_slots(self) -> dict:
        """
        🔹 Devuelve los horarios disponibles del Dr. Andrés Cánchica para consulta o valoración médica.

        ✅ Esta función debe ser llamada **únicamente en el Paso 2 del flujo**, cuando:
            - Ya se confirmó que el usuario desea una consulta o valoración (no cirugía directa).
            - Ya eligió si será PRESENCIAL ó VIRTUAL.
            - El objetivo es mostrar las fechas y horas disponibles para agendar.

        ⚠️ No llamar esta función si el usuario aún no ha confirmado el tipo de consulta o si estás en otro paso.
        """
        return self.google_calendar_client.get_available_slots(
            "andrescanchica.consultorio@gmail.com"
        )

    def schedule_pre_consultation(
        self,
        full_name: str,
        type_consultation: str,
        user_phone: str,
        start: str,
        end: str,
    ) -> dict:
        """
        📅 Agenda una consulta o valoración médica con el Dr. Andrés Cánchica en Google Calendar.

        ✅ Esta función debe llamarse **solamente cuando se hayan completado TODAS las preguntas pre-consulta**, en el siguiente orden:
            1. Nombre completo y correo electrónico.
            2. Documento de identidad y fecha de nacimiento.
            3. Cirugía de interés.

        👉 Se requiere además que el usuario ya haya elegido fecha y hora previamente (Paso 3).

        ⚠️ No ejecutar esta función si falta alguna respuesta o si la cita no ha sido confirmada aún.

        📌 Requiere:
            - full_name (str): Nombre completo del paciente.
            - type_consultation (str): 'PRESENCIAL' o 'VIRTUAL'.
            - user_phone (str): Número de contacto.
            - start (str): Fecha/hora de inicio. Ej: '07-15T09:00:00'.
            - end (str): Fecha/hora de fin. Ej: '07-15T10:00:00'.
        """
        return self.google_calendar_client.schedule_pre_consultation(
            full_name=full_name,
            type_consultation=type_consultation,
            user_phone=user_phone,
            start=start,
            end=end,
        )

    def send_payment_method_transfer(self) -> dict:
        """
        Envía un mensaje con las instrucciones para realizar una transferencia bancaria a Bancolombia.

        Esta función debe usarse cuando el usuario:
        - Está en el paso #6 del flujo de reserva
        - Ha elegido pagar por transferencia
        - Tiene cuenta en Bancolombia
        """

        return {
            "format_type": "text",
            "response": {
                "message": (
                    "Aquí tienes las instrucciones para realizar el pago por transferencia bancaria a Bancolombia: \n\n"
                    "Banco: Bancolombia\n"
                    "Tipo de cuenta: Ahorros\n"
                    "Número: 10873049317\n"
                    "Titular: Dr. Andrés Cánchica Cano\n"
                    "Valor: $300.000 COP\n\n"
                    "Por favor envía el comprobante a este chat cuando realices la transferencia y procederemos a confirmar la cita."
                )
            },
        }

    def send_payment_method_link(self) -> dict:
        """
        Envía un mensaje con las instrucciones para realizar el pago a través de link de pago.

        Esta función debe usarse cuando el usuario:
        - No tiene cuenta en Bancolombia
        - O se encuentra fuera de Colombia
        """
        return {
            "format_type": "text",
            "response": {
                "message": (
                    "Aquí tienes las instrucciones para realizar el pago a través de link de pago: 💳\n\n"
                    "Link de pago: https://checkout.bold.co/payment/LNK_ALECEDBLFO\n\n"
                    "Por favor realiza el pago utilizando el enlace proporcionado y envía el comprobante a este chat para confirmar tu cita."
                )
            },
        }

    def payment_received(self, user_phone: str) -> dict:
        """
        Esta función se invoca cuando el usuario ha enviado el comprobante de pago (imagen) y se ha verificado su validez.
        Marca el pago como recibido y actualiza el estado del usuario en la base de datos.
        """
        user = self.whatsapp_repository.get_contact_by_number(user_phone)

        if not user:
            raise Exception("User not found in the database. ❌")

        self.whatsapp_repository.update_contact_by_id(
            user["id"], "status", "PAYMENT_RECEIVED"
        )

        return {
            "format_type": "text",
            "response": {
                "message": "¡Pago recibido! Tu cita ha sido confirmada. Nos vemos pronto. 🎉",
            },
        }

    # Methods LangGraph state managment ================================================
    def retrieve_memories(self, state: ChatState) -> ChatState:
        print("🔍 Recuperando recuerdos a largo plazo...", "\n")

        memories = self.recall_longterm_memories(
            {
                "user_message": state.user_message,
                "user_phone": state.user_phone,  # Pass explicitly
                "topic": self.infer_topic_from_message(state.user_message),
            }
        )

        state.memories = memories
        
        print(f"🧠 Recuerdos recuperados: {state.memories}", "\n")
        return state

    def generate_response(self, state: ChatState) -> ChatState:
        try:
            print("📝 Generando respuesta con LangGraphState...", "\n")
            prompt_template = state.prompt_template

            if not prompt_template:
                print(
                    "❗ No se encontró el template de prompt en el estado. Asegúrate de inicializarlo correctamente."
                )
                raise ValueError("Prompt template not found in state.")

            context = "\n".join(f"- {m}" for m in state.memories)
            prompt = prompt_template.invoke(
                {
                    "language": "Español",
                    "user_phone": state.user_phone,
                    "memories": context,
                    "user_message": state.user_message,
                }
            )
            print(f"📜 Prompt generado: {prompt}", "\n")
            state.response = self.llm.invoke(prompt)

            print(
                f"🤖 Respuesta generada por LLM desde LangraphState: {state.response}",
                "\n",
            )

            # Process tool calls or normal response.
            if isinstance(state.response, AIMessage) and state.response.tool_calls:
                print("🔧 Procesando tool_calls...", "\n")
                responses = self.process_tool_calls(state.response.tool_calls)
            else:
                print("🗣️ Respuesta normal:", state.response.content, "\n")
                responses = [
                    {
                        "format_type": "text",
                        "response": {"message": state.response.content},
                    }
                ]

            return {
                # "response": state.response,  # Raw LLM response
                "responses": responses,  # Processed responses
                "error": None,
            }
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            print(f"❗ {error_msg}", "\n")
            return {
                "error": error_msg,
                "responses": [
                    {"format_type": "error", "response": {"message": error_msg}}
                ],
            }

    def process_tool_calls(self, tool_calls):
        """
        Procesa las llamadas a herramientas especificadas en tool_calls.
        """
        responses = []
        for tool_call in tool_calls:
            function_name = tool_call["name"]
            args = tool_call["args"]

            print(f"Tool llamada: {function_name}", "\n")
            print(f"Argumentos recibidos: {args}", "\n")

            function = getattr(self, function_name, None)

            if function is None:
                raise ValueError(
                    f"La función '{function_name}' no existe en el asistente."
                )

            response_function = function(**args)
            responses.append(response_function)

        print("Respuestas de las tool_calls:", responses, "\n")
        return responses

    # Guardar nuevos recuerdos
    def save_memory(self, state: ChatState) -> ChatState:
        """
        Guarda la conversación completa (usuario + respuesta del asistente) como un solo bloque.
        """
        user_message = state.user_message.strip()
        user_phone = state.user_phone

        assistant_responses = " ".join(
            [response["response"]["message"] for response in state.responses]
        ).strip()

        if not user_message or not assistant_responses:
            print("🟨 Mensaje o respuesta vacía. No se guardó memoria.")
            print("User message:", user_message)
            print("Assistant responses:", assistant_responses, "\n")
            return state

        full_dialogue = f"user: {user_message} | assistant: {assistant_responses}"

        print(f"💾 Guardando full dialogo:\n{full_dialogue}\n")

        self.save_longterm_memory(
            {
                "role": "dialogue",
                "user_message": full_dialogue,
                "user_phone": user_phone,
                "topic": self.infer_topic_from_message(user_message),
                "timestamp": int(datetime.utcnow().timestamp()),
            }
        )

        print("✅ Memoria conversacional guardada exitosamente.\n")
        return state

    # ========== LangGraph Tools for Long-term Memory Management ==========

    def save_longterm_memory(self, input: dict) -> str:
        """
        Guarda un recuerdo en Chroma:
        - page_content: 'role: contenido'
        - metadata: incluye user_phone, timestamp, rol y opcionalmente tópico
        """
        user_message = input.get("user_message", "").strip()
        user_phone = input.get("user_phone", "").strip()
        role = input.get("role", "dialogue").strip()
        topic = input.get("topic", "").strip().lower()
        timestamp = input.get("timestamp", None)

        if not topic or len(topic.split()) > 4:
            topic = "general"

        if not user_phone or not user_message or not role:
            return "⚠️ No se proporcionó phone, mensaje o rol."

        content = f"{role}: {user_message}"

        # Create document with metadata
        doc = Document(
            page_content=content,
            id=str(uuid.uuid4()),
            metadata={
                "user_phone": user_phone,
                "timestamp": timestamp,
                "role": role,
                **({"topic": topic} if topic else {}),
            },
        )
        # Add document to vectorstore
        self.vectorstore.add_documents([doc])

        print(f"✅ Memoria guardada: [{timestamp}] {role} → {user_message}")
        return f"Memoria guardada para {user_phone} en {timestamp}."

    from datetime import datetime, timedelta

    def recall_longterm_memories(self, input: dict) -> set[str]:
        """
        Recupera los recuerdos más relevantes para user_phone.
        - Usa MM-R para diversidad
        - Filtra opcionalmente por topic y edad
        - Refuerza prioridad por recencia
        - Devuelve un set con los 15 recuerdos únicos más recientes
        """
        user_message = input.get("user_message", "").strip()
        user_phone = input.get("user_phone", "").strip()
        max_age_days = input.get("max_age_days", 7)  # Default to 7 days of recency
        topic_filter = input.get("topic", "").strip().lower()

        if not user_phone or not user_message:
            return set()

        metadata_filter = [{"user_phone": user_phone}]

        if topic_filter:
            metadata_filter.append({"topic": topic_filter})

        if max_age_days is not None:
            cutoff = datetime.utcnow() - timedelta(days=max_age_days)
            cutoff_timestamp = int(cutoff.timestamp())
            metadata_filter.append({"timestamp": {"$gte": cutoff_timestamp}})

        final_filter = {"$and": metadata_filter}
        print("🔍 Final filter", final_filter, "\n")

        # 🔍 Recuperar los 10 recuerdos más relevantes con MM-R y ordenarlos por recencia
        docs = self.vectorstore.max_marginal_relevance_search(
            query=user_message,
            k=10,
            fetch_k=30,
            filter=final_filter,
        )
        docs = sorted(docs, key=lambda d: d.metadata.get("timestamp", ""), reverse=True)
        results = docs

        # 🔍 Recuperar los 15 recuerdos más recientes del usuario (sin importar relevancia)
        user_docs = self.vectorstore.similarity_search(
            query="",
            k=100,
            filter={"user_phone": user_phone},
        )
        docs_with_timestamps = [doc for doc in user_docs if "timestamp" in doc.metadata]
        docs_with_timestamps.sort(key=lambda d: d.metadata["timestamp"], reverse=True)
        latest_15 = docs_with_timestamps[:15]

        # 🔗 Unir ambos conjuntos de recuerdos 10 + 15
        combined_docs = results + latest_15

        # 🧹 Eliminar duplicados por contenido
        unique_docs_dict = {}
        for doc in combined_docs:
            content = doc.page_content
            ts = doc.metadata.get("timestamp", 0)
            # Guardar solo la versión más reciente en caso de duplicado
            if (
                content not in unique_docs_dict
                or ts > unique_docs_dict[content]["timestamp"]
            ):
                unique_docs_dict[content] = {"timestamp": ts}

        # 🔢 Ordenar por timestamp descendente
        sorted_unique_docs = sorted(
            unique_docs_dict.items(), key=lambda x: x[1]["timestamp"], reverse=True
        )

        # Reverse the array
        sorted_unique_docs = sorted_unique_docs[::-1]

        # 🎯 Tomar solo los 15 más recientes
        top_15_recent_contents = [content for content, _ in sorted_unique_docs[:15]]

        print(
            f"🔍 Top 15 recuerdos únicos y recientes para {user_phone}: {top_15_recent_contents}",
            "\n",
        )

        return top_15_recent_contents

    def infer_topic_from_message(self, message: str) -> str:
        """
        Usa el LLM para inferir un tópico corto (1 a 3 palabras) que represente el contenido del mensaje.
        """

        prompt_template = ChatPromptTemplate(
            [
                (
                    "system",
                    "Eres un sistema de clasificación de temas para una asistente virtual médica. "
                    "Dado un mensaje de un usuario, tu tarea es identificar el tema central del mensaje en forma de una a tres palabras clave. "
                    "Sé específico pero conciso. No repitas el mensaje original. "
                    "No uses frases completas. No devuelvas respuestas genéricas como 'tema', 'mensaje', 'pregunta', etc."
                    "Usa palabras que podrían ayudar a categorizar el contenido en una base de datos o vector store. "
                    "Ejemplos: Mensaje: 'Quiero agendar una valoración con el doctor Andrés la próxima semana.' Tópico: valoración médica "
                    "Mensaje: '¿Dónde queda el consultorio?' Tópico: ubicación consultorio "
                    "Mensaje: 'Cuáles son los precios aproximados de una cirugía.' Tópico: precios cirugía",
                ),
                ("user", "Mensaje: {message}"),
                ("system", "Tópico: "),
            ]
        )
        prompt = prompt_template.invoke(
            {
                "message": message,
            }
        )
        response = self.llm.invoke(prompt)
        return response.content.strip().lower()
