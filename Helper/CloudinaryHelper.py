import cloudinary

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
