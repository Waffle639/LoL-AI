"""
Endpoints de cuenta de usuario.

GET  /account/login      → Formulario de login
POST /account/login      → Valida credenciales y establece sesión
GET  /account/dashboard  → Panel del usuario (requiere sesión)
GET  /account/logout     → Cierra la sesión
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db, User, APIKey, CreditTransaction
from app.auth import verify_password
from app.template.template import html_login, html_dashboard

router = APIRouter(prefix="/account", tags=["account"])


# ==================== LOGIN ====================

@router.get("/login", response_class=HTMLResponse)
def login_page():
    return HTMLResponse(html_login())


@router.post("/login")
async def login_submit(request: Request, db: Session = Depends(get_db)):
    form     = await request.form()
    email    = form.get("email", "").strip().lower()
    password = form.get("password", "").strip()

    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.hashed_password):
        return HTMLResponse(html_login(error="Email o contraseña incorrectos."))

    if not user.is_active:
        return HTMLResponse(html_login(error="Cuenta desactivada. Contacta soporte."))

    request.session["user_id"] = user.id
    return RedirectResponse("/account/dashboard", status_code=303)


# ==================== DASHBOARD ====================

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/account/login", status_code=303)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        request.session.clear()
        return RedirectResponse("/account/login", status_code=303)

    key_obj = db.query(APIKey).filter(
        APIKey.user_id == user_id, APIKey.is_active == True
    ).first()

    credits    = key_obj.credits if key_obj else 0
    key_prefix = key_obj.key_prefix if key_obj else None

    # Intentar obtener la raw key si aún no se ha mostrado
    raw_key = None
    if key_obj:
        tx = db.query(CreditTransaction).filter(
            CreditTransaction.api_key == key_obj.key,
            CreditTransaction.description.like("lol_%"),
        ).first()
        raw_key = tx.description if tx else None

    return HTMLResponse(html_dashboard(
        username   = user.username,
        email      = user.email,
        plan       = user.plan,
        credits    = credits,
        key_prefix = key_prefix,
        raw_key    = raw_key,
    ))


# ==================== LOGOUT ====================

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/account/login", status_code=303)
