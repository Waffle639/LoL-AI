"""Billing endpoints 100% JSON para frontend SPA."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db, APIKey, CreditTransaction, User, PendingRegistration
from app.auth import get_api_key, create_user_and_api_key, hash_key, hash_password
from pydantic import BaseModel, EmailStr
import stripe
import os
import secrets
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/billing", tags=["billing"])


class RegisterBillingRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    plan: str = "starter"

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


@router.get("/checkout")
def checkout_info():
    return {
        "message": "Use POST /billing/register para crear una sesión de checkout",
        "plans": list(PACKS.keys()),
    }


@router.post("/register")
def register_submit(payload: RegisterBillingRequest, db: Session = Depends(get_db)):
    """Valida el payload, guarda registro pendiente y crea checkout de Stripe."""
    username = payload.username.strip()
    email = payload.email.strip().lower()
    password = payload.password.strip()
    plan = payload.plan

    if len(username) < 3:
        raise HTTPException(status_code=400, detail="El nombre de usuario debe tener al menos 3 caracteres.")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres.")
    if plan not in PACKS:
        raise HTTPException(status_code=400, detail="Plan no válido.")

    existing = db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="El email o el nombre de usuario ya están registrados.")

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
        raise HTTPException(status_code=503, detail=f"El plan {pack_info['name']} no está disponible ahora mismo.")

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
            success_url = f"{base_url}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url  = f"{base_url}/billing/cancel",
        )
        session_kwargs["line_items"] = [{"price": price_id, "quantity": 1}]
        if pack_info["mode"] == "subscription":
            session_kwargs["subscription_data"] = {"metadata": {"pending_id": pending_id}}

        stripe_session = stripe.checkout.Session.create(**session_kwargs)
        return {
            "checkout_url": stripe_session.url,
            "plan": plan,
            "credits": pack_info["credits"],
        }

    except stripe.error.StripeError as e:
        db.delete(pending)
        db.commit()
        raise HTTPException(status_code=502, detail=str(e))


# ==================== CANCEL ====================

@router.get("/cancel")
def cancel():
    return {"status": "cancelled", "message": "Pago cancelado por el usuario"}


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
