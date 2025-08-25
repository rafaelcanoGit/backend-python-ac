from flask import request, jsonify
from flask_cors import CORS, cross_origin
from domain.whatsapp.helpers.wp_helper import get_message_format


def register_routes(app, container):
    """
    Register all routes for the FastAPI application.
    """

    @app.route("/")
    def hello_world():
        return jsonify({"message": "Hello, World!", "status": 200}), 200

    @app.route("/welcome", methods=["GET"])
    def welcome():
        return jsonify({"message": "Welcome to the WhatsApp API", "status": 200}), 200

    @cross_origin()
    @app.route("/calendar/add_event", methods=["POST"])
    def add_calendar_event():
        """
        Endpoint to add a calendar event.
        """
        try:
            data = request.get_json()
            add_calendar_event_service = container.make("add_calendar_event_service")

            summary = data.get("summary")
            description = data.get("description")
            start = data.get("start")
            end = data.get("end")
            attendees = data.get("attendees", [])

            response = add_calendar_event_service.execute(
                summary=summary,
                description=description,
                start=start,
                end=end,
                attendees=attendees,
            )

            return response, 200

        except Exception as e:
            return jsonify({"message": str(e), "status": 500}), 500

    @cross_origin()
    @app.route("/whatsapp/contact/resume/information", methods=["POST"])
    def get_contact_resume_information():
        """
        Endpoint to get user resume information.
        """
        try:
            retreive_user_information_service = container.make(
                "retreive_user_information_service"
            )

            data = request.get_json()
            conversation = data.get("conversation", [])
            telefono = data.get("telefono", "0000000000")

            contact_resume_information = retreive_user_information_service.execute(
                conversation=conversation,
                telefono=telefono,
            )

            if not contact_resume_information:
                return (
                    jsonify(
                        {"message": "User resume information not found", "status": 404}
                    ),
                    404,
                )

            return (
                jsonify(
                    {
                        "contact_resume_information": contact_resume_information,
                        "status": 200,
                    }
                ),
                200,
            )
        except Exception as e:
            return jsonify({"message": str(e), "status": 500}), 500

    @cross_origin()
    @app.route("/whatsapp/send/message", methods=["POST"])
    def send_whatsapp_message():
        """
        Endpoint to send a message to a WhatsApp number.
        """
        try:
            send_message_service = container.make("send_message_service")

            data = request.get_json()

            if not isinstance(data, dict):
                return {"message": "Invalid JSON payload", "status": 400}, 400

            format_type = data.get("format_type", "text")
            phone_number = data.get("phone_number", "0000000000")
            message = data.get("message", "")

            format_message = get_message_format(
                format_type=format_type,
                phone_number=phone_number,
                response={"message": message},
            )

            response = send_message_service.execute(
                phone_number=phone_number,
                format_message=format_message,
            )

            return response, 200

        except Exception as e:
            return jsonify({"message": str(e), "status": 500}), 500

    # whatsapp/send/template/message
    @cross_origin()
    @app.route("/whatsapp/send/template/message", methods=["POST"])
    def send_whatsapp_template_message():
        """
        Endpoint to send a template message to a WhatsApp number.
        """
        try:
            send_message_service = container.make("send_message_service")

            data = request.get_json()

            if not isinstance(data, dict):
                return {"message": "Invalid JSON payload", "status": 400}, 400

            phone_number = data.get("phone_number", "0000000000")
            template_name = data.get("template_name", "")
            template_parameters = data.get("template_parameters", {})

            format_message = get_message_format(
                format_type=template_name,
                phone_number=phone_number,
                response=template_parameters,
            )

            response = send_message_service.execute(
                phone_number=phone_number,
                format_message=format_message,
            )

            return response, 200

        except Exception as e:
            return jsonify({"message": str(e), "status": 500}), 500

    # Endpoint for WhatsApp webhook =========================
    @app.route("/whatsapp", methods=["GET"])
    def verify_token():
        try:
            verify_token_service = container.make("verify_token_service")

            token = request.args.get("hub.verify_token")
            challenge = request.args.get("hub.challenge")

            return verify_token_service.execute(token, challenge)

        except Exception as e:
            return jsonify({"message": str(e), "status": 500}), 500

    @app.route("/webhook/whatsapp", methods=["POST"])
    def received_message():
        try:
            body = request.get_json()

            received_message_service = container.make("received_message_service")

            return received_message_service.execute(body)

        except Exception as e:
            return jsonify({"message": str(e), "status": 500}), 500

    # ==========================================================
    # Endpoint for Google Calendar Webhook =========================
    @app.route("/webhook/google-calendar", methods=["POST"])
    def webhook_google_calendar():
        # Google envía solo headers, sin body
        print("\n ===== Google Calendar Webhook Received =====")
        for k, v in request.headers.items():
            print(f"{k}: {v}")

        # Body vacío normalmente
        raw_data = request.data
        if raw_data:
            print("Body:", raw_data)
        else:
            print("Body: <empty>")

        return "OK", 200
