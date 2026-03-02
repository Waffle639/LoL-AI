"""
Endpoints de billing con registro de cuenta.

GET  /billing/register   → Formulario de registro + elección de plan
POST /billing/register   → Procesa el formulario y redirige a Stripe
GET  /billing/success    → Muestra la API key tras el pago
GET  /billing/cancel     → Página de cancelación
GET  /billing/credits    → Consulta créditos (requiere X-API-Key)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db, APIKey, CreditTransaction, User, PendingRegistration
from app.auth import get_api_key, create_user_and_api_key, hash_key, hash_password
from app.template.template import _html_success, _html_error, _html_cancel, html_register
import stripe
import os
import secrets
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/billing", tags=["billing"])

PACKS = {
    "starter": {
        "credits":      20,
        "price_id_env": "STRIPE_PRICE_ID_STARTER",
        "name":         "Starter Pack",
        "mode":         "payment",
        "description":  "20 predicciones de partida",
        "price_label":  "Pago único",
    },
    "monthly": {
        "credits":      50,
        "price_id_env": "STRIPE_PRICE_ID_MONTHLY",
        "name":         "Monthly Pro",
        "mode":         "subscription",
        "description":  "50 predicciones al mes",
        "price_label":  "Suscripción mensual",
    },
}


# ==================== REGISTRO ====================

@router.get("/register", response_class=HTMLResponse)
def register_page():
    """Muestra el formulario de registro y selección de plan."""
    return HTMLResponse(html_register())


@router.get("/checkout")
def checkout_redirect():
    """Compatibilidad: redirige al nuevo flujo de registro."""
    return RedirectResponse("/billing/register", status_code=301)


@router.post("/register")
async def register_submit(request: Request, db: Session = Depends(get_db)):
    """Valida el formulario, guarda el registro pendiente y redirige a Stripe."""
    form     = await request.form()
    username = form.get("username", "").strip()
    email    = form.get("email", "").strip().lower()
    password = form.get("password", "").strip()
    plan     = form.get("plan", "starter")

    if not username or not email or not password:
        return HTMLResponse(html_register(error="Todos los campos son obligatorios."))
    if len(username) < 3:
        return HTMLResponse(html_register(error="El nombre de usuario debe tener al menos 3 caracteres."))
    if len(password) < 8:
        return HTMLResponse(html_register(error="La contraseña debe tener al menos 8 caracteres."))
    if plan not in PACKS:
        return HTMLResponse(html_register(error="Plan no válido."))

    existing = db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()
    if existing:
        return HTMLResponse(html_register(error="El email o el nombre de usuario ya están registrados."))

    pending_id = secrets.token_urlsafe(24)
    pending    = PendingRegistration(
        id              = pending_id,
        username        = username,
        email           = email,
        hashed_password = hash_password(password),
        plan            = plan,
    )
    db.add(pending)
    db.commit()

    pack_info = PACKS[plan]
    price_id  = os.getenv(pack_info["price_id_env"])

    if not price_id:
        db.delete(pending)
        db.commit()
        return HTMLResponse(html_register(error=f"El plan «{pack_info['name']}» no está disponible ahora mismo."))

    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")

    try:
        session_kwargs = dict(
            payment_method_types = ["card"],
            mode                 = pack_info["mode"],
            customer_email       = email,
            metadata             = {
                "pending_id": pending_id,
                "plan":       plan,
                "credits":    str(pack_info["credits"]),
            },
            success_url = f"{base_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url  = f"{base_url}/billing/cancel",
        )
        session_kwargs["line_items"] = [{"price": price_id, "quantity": 1}]
        if pack_info["mode"] == "subscription":
            session_kwargs["subscription_data"] = {"metadata": {"pending_id": pending_id}}

        stripe_session = stripe.checkout.Session.create(**session_kwargs)
        return RedirectResponse(stripe_session.url, status_code=303)

    except stripe.error.StripeError as e:
        db.delete(pending)
        db.commit()
        return HTMLResponse(html_register(error=str(e)))


# ==================== SUCCESS ====================

@router.get("/success", response_class=HTMLResponse)
def success(session_id: str = Query(...), db: Session = Depends(get_db)):
    """Página de éxito tras el pago. Muestra la API key generada por el webhook."""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError:
        return HTMLResponse(_html_error("Sesión de Stripe inválida."))

    if session.payment_status not in ("paid", "no_payment_required"):
        return HTMLResponse(_html_error(
            "El pago no se ha completado todavía. Espera unos segundos y recarga la página."
        ))

    tx = db.query(CreditTransaction).filter(
        CreditTransaction.stripe_session_id == session_id
    ).first()

    # Fallback: el webhook no ha llegado aún (habitual en local sin Stripe CLI activo)
    if not tx:
        logger.info(f"Webhook todavía no procesado para {session_id}. Ejecutando fallback.")
        try:
            metadata   = dict(session.metadata or {})
            plan       = metadata.get("plan", "starter")
            credits    = int(metadata.get("credits", PACKS.get(plan, PACKS["starter"])["credits"]))
            cd         = getattr(session, "customer_details", None)
            email_fb   = (getattr(cd, "email", None) or (cd.get("email") if hasattr(cd, "get") else None) or "unknown") if cd else "unknown"
            customer_id = getattr(session, "customer", None)

            create_user_and_api_key(
                db                = db,
                pending_id        = metadata.get("pending_id"),
                customer_id       = customer_id,
                email_fallback    = email_fb,
                plan              = plan,
                credits           = credits,
                stripe_session_id = session.id,
            )
        except Exception as exc:
            import traceback
            logger.error(f"Error en fallback /success: {exc}\n{traceback.format_exc()}")
            return HTMLResponse(_html_error(
                "Tu pago se ha procesado pero hubo un error generando la key. "
                "Contacta soporte o espera unos segundos y recarga."
            ))
        tx = db.query(CreditTransaction).filter(
            CreditTransaction.stripe_session_id == session_id
        ).first()
        if not tx:
            return HTMLResponse(_html_error(
                "Tu pago se ha procesado pero la key aún se está generando. "
                "Espera unos segundos y recarga la página."
            ))

    raw_key = tx.description if tx.description and tx.description.startswith("lol_") else None

    if not raw_key:
        return HTMLResponse(_html_error(
            "Key ya mostrada anteriormente. "
            "Accede a tu cuenta en <a href='/account/login' style='color:#0BC4E3'>/account/login</a> para ver tus créditos."
        ))

    plan    = session.metadata.get("plan", "starter") if session.metadata else "starter"
    credits = PACKS.get(plan, PACKS["starter"])["credits"]

    tx.description = f"{PACKS.get(plan, PACKS['starter'])['name']} — key mostrada"
    db.commit()

    return HTMLResponse(_html_success(raw_key, credits))


# ==================== CANCEL ====================

@router.get("/cancel", response_class=HTMLResponse)
def cancel():
    return HTMLResponse(_html_cancel())


# ==================== CREDITS ====================

@router.get("/credits")
def get_credits(api_key: str = Depends(get_api_key), db: Session = Depends(get_db)):
    """Consulta los créditos restantes de tu API Key."""
    hashed  = hash_key(api_key)
    key_obj = db.query(APIKey).filter(APIKey.key == hashed).first()

    if not key_obj:
        raise HTTPException(status_code=401, detail="API Key inválida")

    return {
        "name":              key_obj.name,
        "credits_remaining": key_obj.credits,
    }
