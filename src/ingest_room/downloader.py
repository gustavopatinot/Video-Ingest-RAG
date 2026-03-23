import logging
from pathlib import Path
from typing import Optional, Dict, Any
import yt_dlp

# Configuración básica de logging para monitoreo en Colab
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VideoDownloader:
    """
    Clase encargada de gestionar la descarga de videos y extracción de audio
    desde plataformas compatibles (ej. YouTube) utilizando yt-dlp.
    """

    def __init__(self, output_dir: str = "/content/data/raw"):
        """
        Inicializa el descargador con un directorio de salida específico.

        Args:
            output_dir (str): Ruta temporal en Colab donde se guardarán los audios.
        """
        self.output_dir = Path(output_dir)
        # Crea el directorio si no existe
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_youtube_audio(self, video_url: str) -> Optional[str]:
        """
        Descarga el mejor audio disponible de un video de YouTube y lo convierte a MP3.

        Args:
            video_url (str): URL del video de YouTube a procesar.

        Returns:
            Optional[str]: La ruta absoluta del archivo de audio descargado (.mp3),
                           o None si ocurre un error durante el proceso.
        """
        # Opciones de configuración para yt-dlp
        ydl_opts: Dict[str, Any] = {
            'format': 'bestaudio/best',
            'outtmpl': f'{self.output_dir}/%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True
        }

        try:
            logger.info(f"Iniciando extracción de audio para: {video_url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extrae información y descarga
                info_dict = ydl.extract_info(video_url, download=True)
                video_id = info_dict.get('id', 'unknown')
                expected_file = self.output_dir / f"{video_id}.mp3"

                if expected_file.exists():
                    logger.info(f"Extracción exitosa. Archivo guardado en: {expected_file}")
                    return str(expected_file)
                else:
                    logger.error("Error: El archivo no se encontró en el directorio tras la descarga.")
                    return None

        except yt_dlp.utils.DownloadError as e:
            logger.error(f"Error de red o de yt-dlp al procesar el video: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado durante la ejecución: {e}")
            return None