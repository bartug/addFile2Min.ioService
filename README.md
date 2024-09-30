This Python module is designed to handle the uploading of logo images extracted from a base64-encoded ZIP file to MinIO, while avoiding the re-upload of duplicate files. Each image is processed, converted to PNG format if necessary, and uploaded to the specified MinIO bucket. Before uploading, the function checks if a file with the same hash already exists in the storage, thereby preventing redundant uploads.

## Features
- Extracts files from a ZIP file (provided in base64 encoding).
- Checks for duplicate files using **MD5 hash** before uploading.
- Converts image files to PNG format if they are not already in PNG.
- Stores the PNG images in the MinIO object storage.
- Returns the MD5 hash of the files, skipping duplicate uploads.

  ## Requirements

Ensure that the following dependencies are installed before using the module:

```bash
pip install minio
pip install pillow
pip install imghdr
```
How It Works

 - Base64 Decoding: The base64-encoded ZIP file is decoded to its binary form.
 - Extracting Files from ZIP: The contents of the ZIP file are extracted, and each file is checked.
 - Hash Calculation: For each file, an MD5 hash is computed based on the file content. The hash is used to check whether the file already exists in MinIO.
 - Duplicate Check: If a file with the same hash already exists in the specified bucket, the upload is skipped, and the function returns the hash of the existing file.
 - Image Conversion: If the image file is not in PNG format, it is converted to PNG before uploading.
 - Uploading to MinIO: The file is uploaded with its hash as the filename (<md5_hash>.png) to MinIO.
 - Returning Hash: The function returns the MD5 hash of the uploaded file or the existing file in case of a duplicate.

Functions

 - check_slip_logos(logo_base64): Main function that handles the ZIP extraction, duplicate check, image conversion, and uploading process.
 - object_exists_in_minio(bucket_path, object_name): Checks whether an object already exists in the MinIO storage based on the bucket path and object name.
 - save_to_minio(file_name, content, bucket_path, tags): Saves a file to the specified bucket in MinIO with optional tags.

License

This project is licensed under the MIT License. See the LICENSE file for details.
This `README.md` should provide clear guidance on what the script does, how to install dependencies, and how to use the functions. Let me know if you need any further modifications!
