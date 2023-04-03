from fastapi import FastAPI
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import os
import datetime as dt
from typing import Optional
from typing import Union
from fastapi.responses import FileResponse
from os import getcwd, remove
from fastapi.responses import JSONResponse
from fastapi import FastAPI, UploadFile, File

app = FastAPI()


current_directory = os.getcwd()
current_path = os.path.abspath(os.getcwd())
FolderPath = os.getcwd()


@app.get("/cwd")
async def cwd():
    allpaths = { 
    "current_directory": current_directory,
    "current_path": current_path,
    }
    return(allpaths)

# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    with open(file.filename, 'wb') as image:
        content = await file.read()
        image.write(content)
        image.close()
    return JSONResponse(content={"filename": file.filename},
status_code=200)


@app.get("/download/{name_file}")
def download_file(name_file: str):
    return FileResponse(path=getcwd() + "/" + name_file, media_type='application/octet-stream', filename=name_file)


# @app.post("/directory")
# async def download_post(request: Request,):
#     absPath = Path(current_path)
#     def fObjFromScan(x):
#         fileStat = x.stat()
#         # return file information for rendering
#         return {'name': x.name,
#                 'fIcon': "bi bi-folder-fill" if x.is_dir() else getIconClassForFilename(x.name),
#                 'relPath': str(x.relative_to(Path(FolderPath))).replace("\\", "/"),
#                 'mTime': getTimeStampString(fileStat.st_mtime),
#                 'size': getReadableByteSize(fileStat.st_size)}
#     fileList = [fObjFromScan(f) for f in absPath.iterdir()]
#     return(fileList)
    # return templates.TemplateResponse("directory.html", {"request": request, "dirPath": str(absPath), "fileList": fileList})


@app.get("/file/{name_file}")
def get_file(name_file: str):
    return FileResponse(path=getcwd() + "/" + name_file)


@app.delete("/delete/file/{name_file}")
def delete_file(name_file: str):
    try:
        remove(getcwd() + "/" + name_file)
        return JSONResponse(content={
            "removed": True
            }, status_code=200)   
    except FileNotFoundError:
        return JSONResponse(content={
            "removed": False,
            "error_message": "File not found"
        }, status_code=404)


FolderPath = os.getcwd()

def getReadableByteSize(num, suffix="B") -> str:
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Y", suffix)

def getTimeStampString(tSec: float) -> str:
    tObj = dt.datetime.fromtimestamp(tSec)
    tStr = dt.datetime.strftime(tObj, "%Y-%m-%d %H:%M:%S")
    return tStr

def getIconClassForFilename(fName):
    fileExt = Path(fName).suffix
    fileExt = fileExt[1:] if fileExt.startswith(".") else fileExt
    fileTypes = ["aac","ai","bmp","cs","css","csv","doc","docx","exe",
                 "gif","heic","html","java","jpg","js","json","jsx",
                 "key","m4p","md","mdx","mov","mp3","mp4","otf","pdf",
                 "php","png","pptx","psd","py","raw","rb","sass","scss",
                 "sh","sql","svg","tiff","tsx","ttf","txt","wav","woff",
                 "xlsx","xml","yml",
                ]
    
    fileIconClass = f"bi bi-filetype-{fileExt}" if fileExt in fileTypes else "bi bi-file-earmark"
    return fileIconClass


@app.get("/directory")
async def download_post(request: Request, path: Union[str, None] = FolderPath):
    absPath = Path(FolderPath) / path
    def fObjFromScan(x):
        fileStat = x.stat()
        # return file information for rendering
        return {
            "name": x.name,
            "fIcon": "bi bi-folder-fill" if x.is_dir() else getIconClassForFilename(x.name),
            "relPath": str(x.relative_to(Path(FolderPath))).replace("\\", "/"),
            "mTime": getTimeStampString(fileStat.st_mtime),
            "size": getReadableByteSize(fileStat.st_size),
        }
    fileList = [fObjFromScan(f) for f in absPath.iterdir()]
    return JSONResponse(content=fileList)


# @app.post("/directory")
# async def download_post(request: Request, path: Union[str, None] = FolderPath):
#     absPath = Path(FolderPath) / path
#     def fObjFromScan(x):
#         fileStat = x.stat()
#         # return file information for rendering
#         return {
#             "name": x.name,
#             "fIcon": "bi bi-folder-fill" if x.is_dir() else getIconClassForFilename(x.name),
#             "relPath": str(x.relative_to(Path(FolderPath))).replace("\\", "/"),
#             "mTime": getTimeStampString(fileStat.st_mtime),
#             "size": getReadableByteSize(fileStat.st_size),
#         }
#     fileList = [fObjFromScan(f) for f in absPath.iterdir()]
#     return JSONResponse(content=fileList)


@app.get('/files-display')
def displayfiles():
    html_content = """
    <html>
        <body>
            <div id='directory' class='table table-striped table-responsive'></div>
        </body>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
        
        <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap-icons@1.9.1/font/bootstrap-icons.css'>
        <style>
            table {table-layout:fixed; width:100%;}
            table td, th {word-wrap:break-word;}
            th {text-align: left;}
        </style>
        <script>
          $.ajax({
          url: '/directory/',
          type: 'GET',
          success: function(response) {
              $('#directory').append(
                  "<table>"+
                  "<tbody>"
              );

              $.each(response, function(i, item) {
                  num = i + 1;
                  $('#directory').append(
                      "<tr>"+
                      //"    <td scope='row'>"+num+"</td>"+
                      "    <td>"+
                      "        <a href='' target='blank'>"+
                      "            <span><i class='"+item.icon+"' style='margin-right:0.3em'></i></span>"+
                      "        </a>"+
                      "    </td>"+
                      "    <th> "+item.name+" </th>"+
                      "    <th> "+item.time+" </th>"+
                      "    <th> "+item.size+" </th>"+
                      "</tr>"
                  );
              });

              $('#directory').append(
                  "    </tbody>"+
                  "</table>"+
                  "<link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap-icons@1.9.1/font/bootstrap-icons.css'>"+
                  "<style>"+
                  "    table {table-layout:fixed; width:100%;}"+
                  "    table td, th {word-wrap:break-word;}"+
                  "    th {text-align: left;}"+
                  "</style>");
            }
          });
      </script>

      <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap-icons@1.9.1/font/bootstrap-icons.css'>

    </html>
    """
    
    return HTMLResponse(content=html_content, status_code=200)
