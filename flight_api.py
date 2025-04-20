import requests
from config import TRAVELPAYOUTS_TOKEN, MARKER
import logging

logger = logging.getLogger(__name__)

# Build booking link
def build_affiliate_link(origin, destination, date=None):
    link = f"https://www.aviasales.com/search/{origin.lower()}{destination.lower()}1"
    if date:
        link += f"?departure_at={date}"
    link += f"&marker={MARKER}"
    return link

# Real-time flight fetch
def get_flight_data(origin, destination, depart_date=None, direct_only=False):
    base_url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
    params = {
        "origin": origin,
        "destination": destination,
        "token": TRAVELPAYOUTS_TOKEN,
        "currency": "usd",
        "unique": "true"
    }
    if depart_date:
        params["departure_at"] = depart_date

    try:
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            return f"⚠️ Error fetching flights: {response.status_code}"

        flights = response.json().get("data", [])
        if direct_only:
            flights = [f for f in flights if f.get("transfers", 1) == 0]

        if not flights:
            return "❌ No matching flights found."

        top_flights = sorted(flights, key=lambda x: x.get("price", 999999))[:3]

        message = f"✈️ *Top flights from {origin} to {destination}*\n\n"
        for flight in top_flights:
            airline = flight.get("airline", "Unknown").upper()
            price = flight.get("price", "N/A")
            date = flight.get("departure_at", "")[:10]
            stops = flight.get("transfers", 0)
            link = build_affiliate_link(origin, destination, date)

            message += (
                f"*{airline}* – ${price} on {date} "
                f"({'Non-stop' if stops == 0 else f'{stops} stop(s)'})\n"
                f"[Book Now]({link})\n\n"
            )
        return message

    except Exception as e:
        logger.error(f"[ERROR] Exception fetching flights: {e}")
        return f"⚠️ Error fetching flights: {e}"

# Static 10 hot routes
def get_top_deals():
    routes = [
        ("JFK", "LON"),
        ("LAX", "PAR"),
        ("NYC", "DXB"),
        ("ORD", "AMS"),
        ("SFO", "ROM"),
        ("BOS", "BER"),
        ("MIA", "MAD"),
        ("SEA", "BCN"),
        ("ATL", "IST"),
        ("DFW", "CAI"),
    ]

    message = "🔥 *Top 10 Hot Flight Deals:*\n\n"
    for origin, destination in routes:
        try:
            result = get_flight_data(origin, destination)
            message += result + "\n"
        except Exception as e:
            logger.error(f"[DEAL ERROR] {origin}-{destination}: {e}")
            continue

    return message
