from flask import Flask, request, jsonify, send_from_directory, send_file, abort
from flask_cors import CORS, cross_origin
import os
import base64
import mimetypes

from infrastructure.providers.app_container import AppContainer
from infrastructure.providers.llm_provider import LLMProvider
from infrastructure.providers.assistant_provider import AssistantProvider
from infrastructure.providers.service_provider import ServiceProvider
from infrastructure.providers.db_provider import DBProvider
from infrastructure.providers.repository_provider import RepositoryProvider
from infrastructure.providers.client_provider import ClientProvider
from ui.routes.routes import register_routes
from infrastructure.config.config import get_env
from threading import Thread

app = Flask(__name__)

frontend_url = get_env("APP_FRONTED_URL")

# Configurar CORS con la URL del frontend
CORS(app, origins=[frontend_url], resources={r"/*": {"origins": frontend_url}})
app.config["CORS_HEADERS"] = "Content-Type"

# Providers de la aplicación
providers = [
    LLMProvider(),
    AssistantProvider(),
    ServiceProvider(),
    DBProvider(),
    RepositoryProvider(),
    ClientProvider(),
]

container = AppContainer(providers)
container.initialize_services()

register_routes(app, container)

def messages_expiration_listener():
    listener_service = container.make("messages_expiration_listener_service")
    listener_service.execute()

if __name__ == "__main__":
    # # 🔁 Iniciar hilo antes de correr Flask.
    thread = Thread(target=messages_expiration_listener, daemon=True)
    thread.start()
    print("🧵 Redis messages expiration listener corriendo en segundo plano...")

    # app.run(debug=False)
    app.run(host="0.0.0.0", port=5000, debug=False)
    
# @app.route("/wompi-webhook-test", methods=["POST"])
# def receivedEvent():
#     worksheet = getInteresadasWorksheet()
#     # OBSERVAR LOS QUE LLEGAN SIN ENTRAR POR EL CHAT.
#     try:
#         body = request.get_json()

#         if (
#             body["event"] == "transaction.updated"
#             and body["data"]["transaction"]["status"] == "APPROVED"
#         ):
#             insertUpdateValue(
#                 worksheet,
#                 find_row_by="EMAIL",
#                 search_value=body["data"]["transaction"]["customer_email"],
#                 insert_column_name="ESTADO PAGO",
#                 value=body["data"]["transaction"]["status"],
#             )

#             insertUpdateValue(
#                 worksheet,
#                 find_row_by="EMAIL",
#                 search_value=body["data"]["transaction"]["customer_email"],
#                 insert_column_name="TRANSACTION_ID",
#                 value=body["data"]["transaction"]["id"],
#             )

#             headers_interesadas = getHeaders(worksheet)

#             row_data_interesadas = findRowByValue(
#                 worksheet, "EMAIL", body["data"]["transaction"]["customer_email"]
#             )

#             worksheet = getConsultasWorksheet()

#             headers__sheet_consultas = getHeaders(worksheet)

#             row_data_sheet_consultas = GoogleSheetsService.combinar_datos(
#                 row_data_interesadas, headers_interesadas, headers__sheet_consultas
#             )  # Combinar datos de las hojas de INTERSADAS -> CONSULTAS

#             print("NEW ROW DATA")
#             print(row_data_sheet_consultas)

#             insertUpdateRow(
#                 worksheet, "ID", row_data_sheet_consultas[0], row_data_sheet_consultas
#             )

#             insertUpdateValue(
#                 worksheet=worksheet,
#                 find_row_by="ID",
#                 search_value=row_data_sheet_consultas[0],
#                 insert_column_name="SOPORTE",
#                 value=body["data"]["transaction"]["id"],
#             )

#             insertUpdateValue(
#                 worksheet=worksheet,
#                 find_row_by="ID",
#                 search_value=row_data_sheet_consultas[0],
#                 insert_column_name="COSTO",
#                 value=str(AppFunctions.costo_consulta),
#             )

#             insertUpdateValue(
#                 worksheet=worksheet,
#                 find_row_by="ID",
#                 search_value=row_data_sheet_consultas[0],
#                 insert_column_name="VALOR PAGADO",
#                 value=str(body["data"]["transaction"]["amount_in_cents"]),
#             )

#             insertUpdateValue(
#                 worksheet=worksheet,
#                 find_row_by="ID",
#                 search_value=row_data_sheet_consultas[0],
#                 insert_column_name="CREATED_AT",
#                 value=str(body["sent_at"]),
#             )

#         return [{"status": 200}]
#     except Exception as exception:
#         print(exception)
#         return exception


# @app.route("/comprobantes/<string:comprobante_id>", methods=["GET"])
# def get_comprobante(comprobante_id):

#     comprobante_path = os.path.join(
#         os.path.dirname(__file__), "storage", f"{comprobante_id}.jpeg"
#     )

#     if not os.path.exists(comprobante_path):
#         abort(404)

#     with open(comprobante_path, "rb") as f:
#         comprobante_data = f.read()

#     mimetype, _ = mimetypes.guess_type(comprobante_path)

#     return send_file(
#         comprobante_path,
#         mimetype=mimetype,
#         as_attachment=False,  # Abrir directamente en el navegador
#     )