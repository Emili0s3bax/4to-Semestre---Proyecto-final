import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# ==============================================================================
# Configuración del Entorno AWS para el Usuario: zahid_cloud_developer
# Bucket de destino: uide-publify-hub-prod-s3
# Prefijo lógico: pins-multimedia/
# ==============================================================================

BUCKET_NAME = "uide-publify-hub-prod-s3"
S3_PREFIX = "pins-multimedia/"

def get_s3_client():
    
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    session_token = os.getenv("AWS_SESSION_TOKEN")  # <-- AGREGA ESTA LÍNEA AQUÍ
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
    
    return boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        aws_session_token=session_token,
        region_name=region
    )

def upload_file_to_s3(file_bytes: bytes, filename: str, content_type: str) -> str:
    """
    Sube un objeto (archivo) a AWS S3 utilizando la operación put_object (PutObject).
    Guarda el recurso bajo el prefijo 'pins-multimedia/' dentro del bucket.
    Retorna la URL del recurso en la nube para su consumo.
    """
    s3_client = get_s3_client()
    s3_key = f"{S3_PREFIX}{filename}"
    
    # Subir el archivo mediante la operación put_object (PutObject)
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=file_bytes,
        ContentType=content_type,
        ACL="public-read"  # Permite acceso público de lectura para el consumo en el frontend
    )
    
    # Obtener región activa para construir el endpoint regional correcto
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
    
    # Construir la URL pública de AWS S3 con endpoint regional (evita redirecciones 307)
    url = f"https://{BUCKET_NAME}.s3.{region}.amazonaws.com/{s3_key}"
    return url
