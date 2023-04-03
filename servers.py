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


@app.get("/cwd")
async def cwd():
    allpaths = { 
    "current_directory": current_directory,
    "current_path": current_path,
    }
    return(allpaths)


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











from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import Union


@app.get("/reports/{path:path}")
@app.get("/reports/")
async def get_files(request: Request, path: Union[str, None] = None):
    abs_path = Path(FolderPath) / path if path else Path(FolderPath)
    file_list = []
    for f in abs_path.iterdir():
        file_stat = f.stat()
        file_obj = {
            "name": f.name,
            "fIcon": "bi bi-folder-fill" if f.is_dir() else getIconClassForFilename(f.name),
            "relPath": str(f.relative_to(Path(FolderPath))).replace("\\", "/"),
            "mTime": getTimeStampString(file_stat.st_mtime),
            "size": getReadableByteSize(file_stat.st_size),
        }
        if f.is_dir():
            file_obj["hasFiles"] = any(f.is_file() for f in f.iterdir())
        file_list.append(file_obj)
    return JSONResponse(content=file_list)


@app.post('/reports/')
async def get_files(request: Request):
    data = await request.json()
    req_path = data['path']

    abs_path = Path(FolderPath) / req_path

    def f_obj_from_scan(x):
        file_stat = x.stat()
        # return file information for rendering
        return {
            "name": x.name,
            "fIcon": "bi bi-folder-fill" if x.is_dir() else getIconClassForFilename(x.name),
            "relPath": str(x.relative_to(Path(FolderPath))).replace("\\", "/"),
            "mTime": getTimeStampString(file_stat.st_mtime),
            "size": getReadableByteSize(file_stat.st_size),
        }

    file_list = [f_obj_from_scan(f) for f in abs_path.iterdir()]

    return JSONResponse(content=file_list)


@app.post('/files-display/{item}')
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
            subdirectory_path = "";
        
          $.ajax({
          url: '/reports/' + subdirectory_path,
          //url: '/reports/',
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
                      "    <td scope='row'>"+num+"</td>"+
                      "    <td>"+
                      "        <a href='http://127.0.0.1:8000/files-display/"+item.relPath+"' >"+
                      "            <span><i class='"+item.fIcon+"' style='margin-right:0.3em'></i></span>"+
                      "        </a>"+
                      "    </td>"+
                      "    <th> "+item.name+" </th>"+
                      "    <th> "+item.mTime+" </th>"+
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
            subdirectory_path = "";
        
          $.ajax({
          url: '/reports/' + subdirectory_path,
          //url: '/reports/',
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
                      "    <td scope='row'>"+num+"</td>"+
                      "    <td>"+
                      "        <a href='http://127.0.0.1:8000/files-display/"+item.relPath+"' >"+
                      "            <span><i class='"+item.fIcon+"' style='margin-right:0.3em'></i></span>"+
                      "        </a>"+
                      "    </td>"+
                      "    <th> "+item.name+" </th>"+
                      "    <th> "+item.mTime+" </th>"+
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


