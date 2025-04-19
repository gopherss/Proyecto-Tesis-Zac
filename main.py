from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import cv2

app = FastAPI()

camera = cv2.VideoCapture(0)

# Carga el modelo Haar Cascade para detección de rostros
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            frame = cv2.flip(frame, 1)

            # Convierte a escala de grises para mejor rendimiento
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detecta rostros
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            # Dibuja un rectángulo sobre cada rostro detectado
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Codifica el frame
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

class StartPayload(BaseModel):
    start: str

class StopPayload(BaseModel):
    stop: str
    
@app.get("/")
def root():
    return {"message": "API de Monitoreo del Sueño Activa"}

@app.post("/start")
def handle_action(payload: StartPayload):
    return {"message": f"Acción '{payload.start}' Iniciar monitore"}

@app.post('/stop')
def handle_start(payload: StopPayload):
    return {"message": f"Acción '{payload.stop}' Detener Monitoreo"}
    

@app.get("/video")
def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")
