import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def parent_directory(path: str) -> str:
    return os.path.abspath(os.path.join(path, os.pardir))

@app.get("/files-display/{path:path}")
@app.get("/files-display/")
async def display_files(request: Request, path: str = ""):
    full_path = os.path.abspath(os.path.join( path))
    print(full_path)

    if not os.path.exists(full_path):
        return {"message": "Path does not exist."}

    if not os.path.isdir(full_path):
        return {"message": "Path is not a directory."}

    files = os.listdir(full_path)
    files_info = []

    for file in files:
        file_info = {}
        file_path = os.path.join(full_path, file)
        file_info["name"] = file
        file_info["size"] = os.path.getsize(file_path)
        file_info["mtime"] = os.path.getmtime(file_path)
        if os.path.isdir(file_path):
            file_info["type"] = "directory"
        else:
            file_info["type"] = "file"
        files_info.append(file_info)


    print("path", path)
    print("files", files_info)


    return templates.TemplateResponse("files.html.j2", {"request": request, "path": path, "files": files_info},)


# @app.get("/files-display2/{path:path}")
# @app.get("/files-display2/")
# async def display_files(request: Request, path: str = ""):
#     full_path = os.path.abspath(os.path.join( path))

#     if not os.path.exists(full_path):
#         return {"message": "Path does not exist."}

#     if not os.path.isdir(full_path):
#         return {"message": "Path is not a directory."}

#     files = os.listdir(full_path)
#     files_info = []

#     for file in files:
#         file_info = {}
#         file_path = os.path.join(full_path, file)
#         file_info["name"] = file
#         file_info["size"] = os.path.getsize(file_path)
#         file_info["mtime"] = os.path.getmtime(file_path)
#         if os.path.isdir(file_path):
#             file_info["type"] = "directory"
#         else:
#             file_info["type"] = "file"
#         files_info.append(file_info)

#     return templates.TemplateResponse("files.html.j2", {"request": request, "path": path, "files": files_info},)


# @app.get("/download/{path:path}/{file_name}")
# async def download_file(path: str, file_name: str):
#     file_path = path + "/" + file_name
#     return FileResponse(file_path)