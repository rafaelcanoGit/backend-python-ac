from datetime import datetime, timedelta, timezone
from domain.whatsapp.helpers.wp_helper import format_available_slots


def review_available_slot_on_consult_days(busy_periods, consult_days):
    "Review available slots on consult days based on busy periods."

    available_slots = []
    for consult_day in consult_days:
        current_time = datetime.fromisoformat(consult_day["start"])
        while current_time < datetime.fromisoformat(consult_day["end"]):

            slot_end_time = current_time + timedelta(hours=1)

            is_available = True
            for busy_start, busy_end in busy_periods:
                if current_time < busy_end and slot_end_time > busy_start:
                    is_available = False
                    break

            if is_available:
                available_slots.append(
                    {
                        "start_time": current_time.isoformat(),
                        "end_time": slot_end_time.isoformat(),
                    }
                )

            current_time += timedelta(hours=1)

    return available_slots


def group_availables_slots_by_days(available_slots):
    "Group available slots by day and format them for response."

    grouped_data = {}
    for item in available_slots:
        date = datetime.fromisoformat(item["start_time"]).date().isoformat()
        if date not in grouped_data:
            grouped_data[date] = []
        grouped_data[date].append(item)

    results = [
        {"date": key, "available_slots": value} for key, value in grouped_data.items()
    ]

    results = format_available_slots(results)

    return {
        "format_type": "list",
        "response": {
            "message": "Aquí tienes los horarios disponibles para tu valoración (Escoge el que más te convenga):... [Horarios entregados en formato de lista]",
            "header": None,
            "body": "Las fechas y horarios disponibles para valoración son:",
            "footer": "Elige una opción",
            "button": "VER HORARIOS",
            "sections": results,
        },
    }
