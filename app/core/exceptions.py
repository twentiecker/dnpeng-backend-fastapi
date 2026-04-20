from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = err["loc"][-1]
        err_type = err["type"]
        if err_type == "float_parsing":
            msg = f"{field} harus berupa angka"
        elif err_type == "missing":
            msg = f"{field} wajib diisi"
        else:
            msg = err["msg"]
        errors.append({"field": field, "message": msg})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"success": False, "errors": errors},
    )
