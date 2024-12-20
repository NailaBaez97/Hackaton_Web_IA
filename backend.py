from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests

app = FastAPI()



# Modelo para la entrada
class UserInput(BaseModel):
    text: str

# Ruta para renderizar el frontend
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("frontend.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)

# Ruta para generar el GIF
@app.post("/generate-gif")
async def generate_gif(user_input: UserInput):
    try:
        # Paso 1: Solicitud a la API de OpenAI
        openai_response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": f"Describe this feeling in one word: {user_input.text}"}
                ]
            }
        ).json()

        ai_description = openai_response['choices'][0]['message']['content']

        # Paso 2: Solicitud a la API de Giphy
        giphy_response = requests.get(
            f"https://api.giphy.com/v1/gifs/search",
            params={
                "api_key": GIPHY_API_KEY,
                "q": ai_description,
                "limit": 1
            }
        ).json()

        gif_url = giphy_response['data'][0]['images']['original']['url']

        # Paso 3: Retornar el URL del GIF al frontend
        return JSONResponse(content={"gif_url": gif_url}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
