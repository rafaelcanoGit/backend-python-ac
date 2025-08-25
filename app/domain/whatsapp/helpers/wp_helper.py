from datetime import datetime, timedelta, timezone

meses_ingles_a_espanol = {
    "Jan": "Ene",
    "Feb": "Feb",
    "Mar": "Mar",
    "Apr": "Abr",
    "May": "May",
    "Jun": "Jun",
    "Jul": "Jul",
    "Aug": "Ago",
    "Sep": "Sep",
    "Oct": "Oct",
    "Nov": "Nov",
    "Dec": "Dic",
}

month_translation = {
    "Jan": "Enero",
    "Feb": "Febrero",
    "Mar": "Marzo",
    "Apr": "Abril",
    "May": "Mayo",
    "Jun": "Junio",
    "Jul": "Julio",
    "Aug": "Agosto",
    "Sep": "Septiembre",
    "Oct": "Octubre",
    "Nov": "Noviembre",
    "Dec": "Diciembre",
}


def get_data_user(body):
    entry = (body["entry"])[0]
    changes = (entry["changes"])[0]
    value = changes["value"]
    data = (value["messages"])[0]
    return data


def get_message_user(type_message, data):
    if type_message == "text":
        return (data["text"])["body"]
    elif type_message == "image":
        return data["image"]["caption"]
    elif type_message == "interactive":
        interactive_object = data["interactive"]
        interactive_objectType = interactive_object["type"]
        return (interactive_object[interactive_objectType])["title"]
    else:
        return "Sin mensaje"


def get_number_user(data):
    return data["from"]


def text_message_format(number, response):
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "text",
        "text": {"preview_url": False, "body": response["message"]},
    }


def image_message_format(number, response):
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "image",
        "image": {"link": response["link"]},
    }


def audio_message_format(number, response):
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "audio",
        "audio": {"link": response["link"]},
    }


def video_message_format(number, response):
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "video",
        "video": {
            "link": response["link"],
            "caption": response["caption"],
        },
    }


def document_message_format(number, response):
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "document",
        "document": {
            "link": response["link"],
            "caption": response["caption"],
        },
    }


def sticker_message_format(number, response):
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "sticker",
        "sticker": {"link": response["link"]},
    }


def location_message_format(number, response):
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "location",
        "location": {
            "latitude": response["latitude"],
            "longitude": response["longitude"],
            "name": response["name"],
            "address": response["address"],
        },
    }


def buttons_message_format(number, response):  # Max 3 button options ['', '', '']
    structured_button_options = []

    for index, button_option in enumerate(response["button_options"]):
        structured_button_options.append(
            {
                "type": "reply",
                "reply": {
                    "id": index + 1,
                    "title": button_option,
                },
            }
        )
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": response["text_button"]},
            "action": {"buttons": structured_button_options},
        },
    }


def template_payment_method_transfer(number, response):
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "template",
        "template": {"name": "payment_method_transfer", "language": {"code": "es"}},
    }


def template_payment_method_link(number, response):
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "template",
        "template": {"name": "payment_method_link", "language": {"code": "es"}},
    }


def template_confirm_payment(number, response):
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "template",
        "template": {
            "name": "confirmar_pago_cita",
            "language": {"code": "es"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": response["fecha"]},
                        {"type": "text", "text": response["hora"]},
                    ],
                }
            ],
        },
    }

def reminder_consultation(number, response):
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "template",
        "template": {
            "name": "reminder_consultation",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": response["nombre_completo"]},
                        {"type": "text", "text": response["tipo_consulta"]},
                        {"type": "text", "text": response["fecha_consulta"]},
                        {"type": "text", "text": response["hora_inicio"]},
                    ],
                }
            ],
        },
    }


def list_message_format(
    number, response
):  # 'sections' should have 'title' and 'rows' and rows should have 'title', 'descripcion'
    structured_sections = []

    for index_section, section in enumerate(response["sections"]):

        structured_rows = []
        for index_row, row in enumerate(section["rows"]):
            structured_rows.append(
                {
                    "id": index_row + 1,
                    "title": row["title"],
                    "description": row["description"],
                }
            )

        structured_sections.append(
            {
                "title": section["title"],
                "rows": structured_rows,
            }
        )

    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": response["header"] if response["header"] else "",
            },
            "body": {"text": response["body"] if response["body"] else ""},
            "footer": {"text": response["footer"] if response["footer"] else ""},
            "action": {
                "button": response["button"] if response["button"] else "",
                "sections": structured_sections,
            },
        },
    }


message_format_map = {
    "text": text_message_format,
    "image": image_message_format,
    "audio": audio_message_format,
    "video": video_message_format,
    "document": document_message_format,
    "sticker": sticker_message_format,
    "location": location_message_format,
    "buttons": buttons_message_format,
    "list": list_message_format,
    "template_payment_method_transfer": template_payment_method_transfer,
    "template_payment_method_link": template_payment_method_link,
    "template_confirm_payment": template_confirm_payment,
    "reminder_consultation": reminder_consultation,
    "default": text_message_format,  # Default format if none matches
}


def get_message_format(format_type, phone_number, response):
    """
    Returns the appropriate message format function based on the type.
    """
    print(f"🔗 Formateando mensaje para WhatsApp del tipo: {format_type}", "\n")
    method = message_format_map.get(format_type)

    if method is None:
        raise ValueError(f"Unsupported message format type: {format_type}")

    return method(phone_number, response)


# Function to format available slots for WhatsApp messages.
def format_available_slots(results):
    "Formats available slots into a structured list for WhatsApp messages."
    sections = []
    total_rows = 0

    for index, result in enumerate(results):
        if total_rows >= 10:
            break

        if index < 10:
            rows = []
            for index_slot, available_slot in enumerate(result["available_slots"]):

                if total_rows >= 10:
                    break

                start_time = datetime.fromisoformat(available_slot["start_time"])
                end_time = datetime.fromisoformat(available_slot["end_time"])
                year = end_time.year

                start_time_str = start_time.strftime("%-I:%M%p")
                end_time_str = end_time.strftime("%-I:%M%p")
                available_time = f"{start_time_str}-{end_time_str}"

                rows.append(
                    {
                        "id": index_slot + 1,
                        "title": available_time,
                        "description": f"{start_time.strftime('%d')}-{month_translation[start_time.strftime('%b')]} {year}",
                    }
                )

                total_rows += 1

            date_obj = datetime.strptime(result["date"], "%Y-%m-%d")
            day_available = date_obj.strftime(
                f"%d de {meses_ingles_a_espanol[date_obj.strftime('%b')]}"
            )

            sections.append({"title": day_available, "rows": rows})
        else:
            break

    return sections
