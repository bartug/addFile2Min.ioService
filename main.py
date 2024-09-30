import os
import hashlib
from minio import Minio
import io
import base64
import zipfile
import imghdr
from PIL import Image
from fastapi import FastAPI, HTTPException
from minio.error import S3Error
from urllib3 import PoolManager, Timeout
from urllib.parse import urlparse
import uvicorn
from logger import log

app = FastAPI(
    title="Belge İşleme Servisi",
    description="Gelen zip dosyasını açar, içindeki dosyaları kontrol edip PNG'ye çevirir ve MinIO'ya yükler.",
    version="1.0.0",
)

MINIO_BUCKET = os.getenv("MINIO_BUCKET", "your-bucketname")
MINIO_ACCESS = os.getenv("MINIO_ACCESS_KEY", "your-accesskey")
MINIO_SECRET = os.getenv("MINIO_SECRET_KEY", "your-secretkey")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "your-miniodomain")

# get hostname
o = urlparse(MINIO_ENDPOINT)
MINIO_ENDPOINT = o.hostname
client = Minio(endpoint=MINIO_ENDPOINT, access_key=MINIO_ACCESS, secret_key=MINIO_SECRET, secure=True,
               http_client=PoolManager(timeout=Timeout(connect=1.0, read=3.0)))


async def process_zip_file(logo_base64):
    zip_data = base64.b64decode(logo_base64)
    zip_md5_hash = hashlib.md5(zip_data).hexdigest()

    object_name = f"{zip_md5_hash}.png"
    bucket_path = "logo"

    # Eğer bu hashli dosya MinIO'da varsa, hash'i döneceğiz
    if await object_exists_in_minio(bucket_path, object_name):
        log.info(f"ZIP {zip_md5_hash} already exists in MinIO.")
        return zip_md5_hash


    with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_ref:
        file_names = zip_ref.namelist()

        for file_name in file_names:
            with zip_ref.open(file_name) as image_file:
                image_bytes = image_file.read()

                # Dcheck filetype
                image_type = imghdr.what(None, h=image_bytes)
                if image_type in ['png', 'jpeg', 'jpg', 'bmp']:
                    # get hash
                    file_hash = hashlib.md5(image_bytes).hexdigest()
                    object_name = f"{file_hash}.png"

                    # if its exist control
                    if await object_exists_in_minio(bucket_path, object_name):
                        log.info(f"File {file_name} with hash {file_hash} already exists in MinIO.")
                        return file_hash

                    # convert to png
                    if image_type != 'png':
                        image = Image.open(io.BytesIO(image_bytes))
                        png_buffer = io.BytesIO()
                        image.save(png_buffer, format="PNG")
                        image_bytes = png_buffer.getvalue()


                    await save_to_minio(object_name, image_bytes, bucket_path, None)

    return zip_md5_hash


async def object_exists_in_minio(bucket_path, object_name):
    try:
        client.stat_object(bucket_name=MINIO_BUCKET, object_name=f"{bucket_path}/{object_name}")
        log.info(f"Object '{object_name}' already exists in MinIO.")
        return True
    except S3Error:
        return False


async def save_to_minio(file_name, content, bucket_path, tags):
    client.put_object(
        bucket_name=MINIO_BUCKET,
        object_name=f"{bucket_path}/{file_name}",
        data=io.BytesIO(content),
        length=len(content),
        content_type='image/png',
        tags=tags
    )
    log.info(f"{file_name} uploaded to MinIO at {bucket_path}.")



@app.post("/upload-zip")
async def upload_zip(request: dict):
    try:
        zip_base64 = request.get('zip_base64')
        if not zip_base64:
            raise HTTPException(status_code=400, detail="Base64 zip verisi eksik.")

        result = await process_zip_file(zip_base64)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hata: {e}")


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
