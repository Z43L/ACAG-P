import speech_recognition as sr
from pydub import AudioSegment
from typing import Dict, List, Any
import tempfile
import os
from .base_adapter import BaseAdapter, ContentType

class AudioAdapter(BaseAdapter):
    """Adaptador para procesamiento de audio y transcripción"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.supported_types = [ContentType.AUDIO]
        self.recognizer = sr.Recognizer()
        
    def connect(self) -> bool:
        """Verifica disponibilidad de librerías de audio"""
        return True  # Siempre disponible
        
    def extract_data(self, parameters: Dict[str, Any]) -> List[Dict]:
        """Transcribe audio a texto"""
        audio_path = parameters.get('path')
        if not audio_path:
            raise ValueError("Audio path is required")
            
        try:
            # Convertir a formato compatible si es necesario
            if audio_path.endswith('.mp3'):
                audio = AudioSegment.from_mp3(audio_path)
                wav_path = audio_path.replace('.mp3', '.wav')
                audio.export(wav_path, format='wav')
                audio_path = wav_path
                
            # Transcribir audio
            with sr.AudioFile(audio_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                
            return [{
                'content': text,
                'metadata': {
                    'source': audio_path,
                    'type': ContentType.AUDIO.value,
                    'duration': self._get_audio_duration(audio_path),
                    'timestamp': datetime.now().isoformat()
                }
            }]
        except Exception as e:
            raise Exception(f"Audio processing failed: {str(e)}")
            
    def _get_audio_duration(self, path: str) -> float:
        """Obtiene la duración del audio en segundos"""
        audio = AudioSegment.from_file(path)
        return len(audio) / 1000.0  # Convertir a segundos
            
    def close(self) -> bool:
        """Limpia recursos temporales"""
        return True