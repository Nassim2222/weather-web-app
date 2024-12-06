import azure.functions as func
import requests
import json
import os
from azure.storage.blob import BlobServiceClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Récupérer les paramètres d'environnement
        api_key = os.getenv('b41cc283acef48e357433dd5b463d282')
        blob_connection_string = os.getenv('DefaultEndpointsProtocol=https;AccountName=weatherstoragecloud;AccountKey=VlNADm8lnYbGypRznVymoKV955CgZsoWdAn6WAOJ/ZEVdlRiodhS3y+OedDDtwqMcoXHqrHHmTm3+ASt/MWPeQ==;EndpointSuffix=core.windows.net')
        container_name = "weather-data"

        # Récupérer le nom de la ville depuis la requête
        city = req.params.get('city')
        if not city:
            return func.HttpResponse(
                "Please provide a city in the query string, e.g., ?city=Paris",
                status_code=400
            )

        # Appeler l'API météo
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        response = requests.get(url)

        # Vérifier si l'appel API est réussi
        if response.status_code != 200:
            return func.HttpResponse(
                f"Failed to fetch weather data for {city}. Please check the city name or API key.",
                status_code=response.status_code
            )

        weather_data = response.json()

        # Sauvegarder les données dans Azure Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"{city}-weather.json")

        blob_client.upload_blob(json.dumps(weather_data), overwrite=True)

        return func.HttpResponse(
            f"Weather data for {city} has been successfully stored in Azure Blob Storage.",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            f"An error occurred: {str(e)}",
            status_code=500
        )
