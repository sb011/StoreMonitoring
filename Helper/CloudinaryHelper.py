import cloudinary
import cloudinary.uploader

"""
    This function uploads the file to cloudinary and returns the result

    Args:
        file_name (str): The name of the file to be uploaded

    Returns:
        upload_result (dict): The result of the upload
"""
def upload_file(file_name):
    cloudinary.config(
        cloud_name = "dh96vxa5a",
        api_key = "578815199169335",
        api_secret = "8idcNXHGUqfQGU9GvSrMDKSYpck"
    )

    upload_result = None
    try:
        upload_result = cloudinary.uploader.upload(file_name, resource_type = "auto")
    except:
        return {"Error": "File upload failed"}
    
    return upload_result["url"]
