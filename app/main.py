from fastapi import FastAPI, APIRouter, Query, HTTPException, status, Request, Depends, Form
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi import FastAPI, UploadFile, File
from pathlib import Path
import os
from os import getcwd, remove
import datetime as dt
from typing import Optional
from typing import Union

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/invoice-create")
def invoice_create(request: Request,
    renter_name: str = Form(...),
    prefix: str = Form(...), 
    rent: float = Form(...), 
    water: float = Form(...), 
    refuse: float = Form(...), 
    sewage: float = Form(...),
    other: float = Form(...),
    outstanding: float = Form(...),
    due: str = Form(...),
):

    renter_name = renter_name
    item1 = "rent"
    item2 = "water"
    item3 = "refuse"
    item4 = "sewage"
    item5 = "other"
    item6 = "outstanding"

    subtotal1 = rent
    subtotal2 = water
    subtotal3 = refuse
    subtotal4 = sewage
    subtotal5 = other
    subtotal6 = outstanding
    due_date = due

    total = subtotal1 + subtotal2 + subtotal3 + subtotal4 + subtotal5 + subtotal6

    today_date = datetime.today().strftime("%d %b, %Y")
    month = datetime.today().strftime("%B")
    year = datetime.today().strftime("%Y")

    # get invoice number
    from sqlalchemy import desc
    
    last_invoice = db.query(models.Invoices).order_by(desc(models.Invoices.invoice_number)).first()
    if last_invoice:
        last_invoice_number = last_invoice.invoice_number
        next_invoice_number = int(last_invoice_number) + 1
        
    else:
        last_invoice = 1
        next_invoice_number = last_invoice

    # include bank account must fit prop
    prefix = prefix
    if prefix == 34 or 341 or 342 or 155 or 1551 or 47:
        account_no = "1910 337 943"
    elif prefix == 32  or 321:
        account_no = '1003 401 449'
    else: # prefix == 10
        account_no = '1910 325 821'

    context = {'renter_name': renter_name, "next_invoice_number": next_invoice_number,
               'today_date': today_date, 'month': due_date, "prefix": prefix,
               "account_no": account_no, 'total': f'R {total:.2f}',
               'item1': item1, 'subtotal1': f'R {subtotal1:.2f}', # rent
               'item2': item2, 'subtotal2': f'R {subtotal2:.2f}', # water
               'item3': item3, 'subtotal3': f'R {subtotal3:.2f}', # refuse
               'item4': item4, 'subtotal4': f'R {subtotal4:.2f}', # sewage
               'item5': item5, 'subtotal5': f'R {subtotal5:.2f}', # other
               'item6': item6, 'subtotal6': f'R {subtotal6:.2f}'  # outstanding
               }

    template_loader = jinja2.FileSystemLoader('app/templates/invoices')
    template_env = jinja2.Environment(loader=template_loader)
    html_template = 'invoicepdf.html'
    
    css_template = 'app/templates/invoices/invoice.css'
    
    invoice_folder = 'invoices/'

    template = template_env.get_template(html_template)
    output_text = template.render(context)
    # Install
    # apt-get install wkhtmltopdf
    # Find directory
    # which wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
    output_pdf = invoice_folder+renter_name+'_'+month+'_'+year+'_invoice.pdf'
    pdfkit.from_string(output_text, output_pdf, configuration=config, css=css_template)

    return {"message": output_pdf}


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


@app.get("/files/{path:path}")
@app.get("/files/")
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



@app.get('/files/{path:path}')
def get_file_content(path: str, response: Response):
    # Get the full path of the requested file
    full_path = os.path.join('path', path)

    # Check if the file exists and is a file (not a directory)
    if not os.path.isfile(full_path):
        response.status_code = 404
        return {'detail': f'File not found: {path}'}

    # Read the contents of the file
    with open(full_path, 'r') as f:
        content = f.read()

    # Return the file contents as plain text
    return content


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

