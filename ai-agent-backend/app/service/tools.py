def get_weather(city: str):
    # Mock weather data for now; this can be replaced with a real API call later.
    return {"city": city, "forecast": "sunny", "temperature_c": 24}


def get_users():
    # Mock user list for demonstration.
    return [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"},
    ]
