# Define data structures (optional type hints for clarity)
from typing import Optional

class SensorData:
    def __init__(self, sensor_id: str, temperature: float, humidity: float, co2: Optional[float] = None):
        self.sensor_id = sensor_id
        self.temperature = temperature
        self.humidity = humidity
        self.co2 = co2

class VisionRequest:
    def __init__(self, image_url: str):
        self.image_url = image_url
