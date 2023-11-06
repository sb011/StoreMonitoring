import cloudinary

"""
    This function uploads the file to cloudinary and returns the result

    Args:
        file_name (str): The name of the file to be uploaded

    Returns:
        upload_result (dict): The result of the upload
"""
def upload_file(file_name):
    cloudinary.config(
        cloud_name = "dgg7j9b5l",
        api_key = "314265242467722",
        api_secret = "O3qkLj4XZQ8YJ6jyqX4n0J6IyXU"
    )
    upload_result = None
    try:
        upload_result = cloudinary.uploader.upload(file_name)
    except:
        return {"Error": "File upload failed"}
    return upload_result
