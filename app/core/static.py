from fastapi.staticfiles import StaticFiles


def setup_static(app):
    app.mount("/files", StaticFiles(directory="public/files"), name="files")
    # app.mount("/images", StaticFiles(directory="public/images"), name="images")
