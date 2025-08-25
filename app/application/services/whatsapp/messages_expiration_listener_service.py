from application.interfaces.service_interface import ServiceInterface
from infrastructure.interfaces.db_connection_interface import DBConnectionInterface
import re as regex
from domain.whatsapp.helpers.wp_helper import get_message_format
from domain.whatsapp.entities.langraph_state import LangGraphState
from langgraph.graph import StateGraph
from domain.whatsapp.interfaces.whatsapp_repository_interface import (
    WhatsappRepositoryInterface,
)


class MessagesExpirationListenerService(ServiceInterface):

    def __init__(
        self,
        redis_connection: DBConnectionInterface,
        conversation_service: ServiceInterface,
        send_message_service: ServiceInterface,
        builder_state: StateGraph,
        langraph_state: LangGraphState,
        whatsapp_repository: WhatsappRepositoryInterface,
    ) -> None:
        self.redis_connection = redis_connection
        self.conversation_service = conversation_service
        self.send_message_service = send_message_service
        self.builder_state = builder_state
        self.langraph_state = langraph_state
        self.whatsapp_repository = whatsapp_repository

        self.init_redis_connection()
        self.pubsub = self.redis_connection.get_connection().pubsub()
        self.subscribe_to_expired_events()

    def start_listener(self) -> None:
        print("🟢 Escuchando expiraciones en Redis...", "\n")

        for message in self.pubsub.listen():
            if message["type"] != "pmessage":
                continue

            expired_key = message["data"].decode()
            print(f"🔔 Clave expirada: {expired_key}", "\n")

            match = regex.match(r"whatsapp:timer:(.+)", expired_key)

            if not match:
                continue

            phone_number = match.group(1)
            list_key = f"whatsapp:buffer:{phone_number}"
            print(
                f"🔍 Procesando mensajes acumulados para el usuario: {list_key}", "\n"
            )

            # Verificamos si el usuario existe en la base de datos.
            user = self.whatsapp_repository.get_contact_by_number(phone_number)
            if user:
                print(
                    f"User to respond format_message found: ✅ {user['phone_number']}",
                    "\n",
                )

            # Get messages from Redis list
            messages = self.get_messages_from_redis(list_key, phone_number)

            # Obtenemos los mensajes acumulados para el número de teléfono.
            accumulated_messages = self.get_accumulated_messages(
                phone_number, messages
            )

            if accumulated_messages:
                print(f"🫙 Storing user messages... {phone_number}", "\n")
                self.save_messages_user(phone_number, user, messages)

                # Ejecutamos conversación (IA)
                response_content = self.conversation_service.execute(
                    self.builder_state,
                    self.langraph_state,
                    phone_number,
                    accumulated_messages,
                )

                print(
                    f"🤖 Response content para {phone_number}: {response_content}",
                    "\n",
                )

                format_messages = []
                for response in response_content["responses"]:
                    print(
                        "🔗 Formateando mensaje para WhatsApp...",
                        response,
                        "\n",
                    )
                    # Formatear el mensaje para enviar por WhatsApp
                    format_message = get_message_format(
                        format_type=response["format_type"],
                        phone_number=phone_number,
                        response=response["response"],
                    )

                    # Save assistant response in the database
                    self.whatsapp_repository.save_message(
                        user, "ASSISTANT", response["response"]
                    )

                    format_messages.append(format_message)

                print(
                    f"📩 Mensajes formateados para {phone_number}: {format_messages}",
                    "\n",
                )
                print("=" * 50, "\n")
                for format_message in format_messages:
                    print(
                        f"🔗 Enviando mensaje vía WhatsApp a:  {phone_number}: {format_message}",
                        "\n",
                    )
                    # === send response via whatsapp ===
                    self.send_message_service.execute(
                        phone_number=phone_number,
                        format_message=format_message,
                    )

                # Limpiar la lista después de procesar
                self.redis_connection.get_connection().delete(list_key)

    def get_messages_from_redis(self, list_key, phone_number):
        """
        Obtiene los mensajes acumulados de Redis para un número de teléfono.
        """
        messages = self.redis_connection.get_connection().lrange(list_key, 0, -1)
        messages = [message.decode() for message in messages]
        print(f"📝 Mensajes acumulados para {phone_number}: {messages}", "\n")
        return messages

    def get_accumulated_messages(self, phone_number, messages) -> str:
        """
        Obtiene todos los mensajes acumulados para un número de teléfono.
        Returns:
            str: El mensaje combinado si hay mensajes, de lo contrario None.
        """
        if messages:
            accumulated_messages = " ".join(messages)
            print(
                f"🧠 Procesando mensajes de {phone_number}: {accumulated_messages}",
                "\n",
            )
            return accumulated_messages

        return None

    def save_messages_user(self, phone_number, user, messages) -> None:
        """
        Save user messages to the database.
        """
        print(f"🔍 Mensajes a almacenar en DB para {phone_number}: {messages}", "\n")

        if messages:
            for message in messages:

                self.whatsapp_repository.save_message(
                    user,
                    "USER",
                    {
                        "message": message,
                    },
                )

    def execute(self) -> None:
        """
        Execute the service to listen for message expirations for a specific user.
        """
        """
        Start the listener for message expirations.
        """
        self.start_listener()

    def validate(self, *args, **kwargs):
        """
        Validate the service parameters.
        """
        return super().validate(*args, **kwargs)

    def init_redis_connection(self) -> None:
        try:
            if not self.redis_connection.is_connected():
                self.redis_connection.connect()
                print("🔗 Conectando a Redis...")
        except Exception as e:
            print(f"❌ Error al conectar a Redis: {e}")
            raise e

        print("🔗 Conexión a Redis establecida correctamente.")

    def subscribe_to_expired_events(self) -> None:
        print("🔔 Suscribiéndose a eventos de expiración de claves en Redis...", "\n")
        self.pubsub.psubscribe("__keyevent@0__:expired")
