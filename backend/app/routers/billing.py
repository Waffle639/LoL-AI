"""Billing endpoints 100% JSON para frontend SPA."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from app.core.database import get_db, APIKey, CreditTransaction, User, PendingRegistration
from app.auth import get_current_user, hash_password
from pydantic import BaseModel, EmailStr, Field
import stripe
import os
import secrets
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/billing", tags=["billing"])


class RegisterBillingRequest(BaseModel):
    username: str = Field(..., description="Nombre de usuario")
    email: EmailStr = Field(..., description="Email de pago")
    password: str = Field(..., description="Contrasena (minimo 8 caracteres)")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "username": "summoner1",
                "email": "summoner1@lolai.com",
                "password": "Pass12345"
            }]
        }
    }


class PurchaseCreditsRequest(BaseModel):
    pack_id: str = Field(..., description="ID del pack de creditos")

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


CREDIT_PACKS = {
    "duelist": {
        "credits":      25,
        "price_id_env": "STRIPE_PRICE_ID_CREDITS_25",
        "name":         "Duelist Pack",
        "description":  "25 predicciones instantaneas",
        "price":        "€4.99",
        "per":          "≈ 0.20€ per credit",
        "featured":     False,
    },
    "elite": {
        "credits":      100,
        "price_id_env": "STRIPE_PRICE_ID_CREDITS_100",
        "name":         "Elite Pack",
        "description":  "100 predicciones instantaneas",
        "price":        "€14.99",
        "per":          "≈ 0.15€ per credit",
        "featured":     True,
    },
    "legend": {
        "credits":      500,
        "price_id_env": "STRIPE_PRICE_ID_CREDITS_500",
        "name":         "Legend Pack",
        "description":  "500 predicciones instantaneas",
        "price":        "€49.99",
        "per":          "≈ 0.10€ per credit",
        "featured":     False,
    },
}


def _serialize_credit_pack(pack_id: str, pack: dict) -> dict:
    return {
        "id": pack_id,
        "name": pack.get("name"),
        "description": pack.get("description"),
        "credits": pack.get("credits"),
        "price": pack.get("price"),
        "per": pack.get("per"),
        "featured": bool(pack.get("featured")),
    }


@router.get(
    "/checkout",
    summary="Ver planes",
    description="Muestra planes disponibles antes de crear el checkout.",
)
def checkout_info():
    return {
        "message": "Use POST /billing/register para crear una sesión de checkout",
        "packs": list(PACKS.keys()),
    }


@router.get(
    "/packs",
    summary="Listado de packs de creditos",
    description="Devuelve los packs disponibles para compra de creditos.",
)
def list_credit_packs():
    return {
        "packs": [_serialize_credit_pack(pid, pack) for pid, pack in CREDIT_PACKS.items()],
    }


@router.post(
    "/purchase",
    summary="Checkout de compra de creditos",
    description="Crea una sesion de checkout para comprar creditos.",
)
def purchase_credits(
    payload: PurchaseCreditsRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pack_id = payload.pack_id
    if pack_id not in CREDIT_PACKS:
        raise HTTPException(status_code=400, detail="Pack no valido")

    pack_info = CREDIT_PACKS[pack_id]
    price_id = os.getenv(pack_info["price_id_env"])
    if not price_id:
        raise HTTPException(status_code=503, detail=f"El pack {pack_info['name']} no esta disponible ahora mismo.")

    dashboard_url = os.getenv("FRONTEND_DASHBOARD_URL", "http://localhost:5174")

    customer_id = user.stripe_customer_id
    if not customer_id:
        try:
            customer = stripe.Customer.create(
                email=user.email,
                metadata={"user_id": str(user.id)},
            )
            customer_id = customer.id
            user.stripe_customer_id = customer_id
            db.commit()
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=502, detail=str(e))

    session_kwargs = dict(
        payment_method_types=["card"],
        mode="payment",
        metadata={
            "checkout_type": "topup",
            "user_id": str(user.id),
            "stripe_customer_id": customer_id or "",
            "pack_id": pack_id,
            "credits": str(pack_info["credits"]),
        },
        success_url=f"{dashboard_url}/billing?success=true&pack={pack_id}",
        cancel_url=f"{dashboard_url}/billing?canceled=true&pack={pack_id}",
    )

    if customer_id:
        session_kwargs["customer"] = customer_id
    else:
        session_kwargs["customer_email"] = user.email

    session_kwargs["line_items"] = [{"price": price_id, "quantity": 1}]

    try:
        stripe_session = stripe.checkout.Session.create(**session_kwargs)
        return {
            "checkout_url": stripe_session.url,
            "pack_id": pack_id,
            "credits": pack_info["credits"],
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post(
    "/register",
    summary="Registro con checkout",
    description="Crea registro pendiente y devuelve checkout_url de Stripe.",
)
def register_submit(payload: RegisterBillingRequest, db: Session = Depends(get_db)):
    """Valida el payload, guarda registro pendiente y crea checkout de Stripe."""
    username = payload.username.strip()
    email = payload.email.strip().lower()
    password = payload.password.strip()

    if len(username) < 3:
        raise HTTPException(status_code=400, detail="El nombre de usuario debe tener al menos 3 caracteres.")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres.")

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
    )
    db.add(pending)
    db.commit()

    pack_info = PACKS["starter"]
    price_id  = os.getenv(pack_info["price_id_env"])

    if not price_id:
        db.delete(pending)
        db.commit()
        raise HTTPException(status_code=503, detail=f"El pack {pack_info['name']} no está disponible ahora mismo.")

    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")

    try:
        session_kwargs = dict(
            payment_method_types = ["card"],
            mode                 = pack_info["mode"],
            customer_email       = email,
            metadata             = {
                "pending_id": pending_id,
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
            "credits": pack_info["credits"],
        }

    except stripe.error.StripeError as e:
        db.delete(pending)
        db.commit()
        raise HTTPException(status_code=502, detail=str(e))


# ==================== CANCEL ====================

@router.get(
    "/cancel",
    summary="Checkout cancelado",
    description="Resultado cuando el usuario cancela el pago en Stripe.",
)
def cancel():
    return {"status": "cancelled", "message": "Pago cancelado por el usuario"}


# ==================== CREDITS ====================

@router.get(
    "/credits",
    summary="Consultar creditos",
    description="Devuelve creditos restantes del usuario autenticado.",
)
def get_credits(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Consulta créditos autenticando por JWT o API key."""
    return {
        "name": user.username,
        "credits_remaining": user.credits,
    }


@router.get(
    "/summary",
    summary="Resumen de créditos",
    description="Totales de uso y compra de créditos del usuario autenticado.",
)
def get_credit_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_week = start_today - timedelta(days=start_today.weekday())

    tx_base = db.query(CreditTransaction).outerjoin(
        APIKey, CreditTransaction.api_key == APIKey.key
    ).filter(
        or_(
            CreditTransaction.user_id == user.id,
            (CreditTransaction.user_id.is_(None) & (APIKey.user_id == user.id)),
        )
    )

    def sum_amount(query) -> int:
        value = query.scalar()
        return int(value or 0)

    used_total = abs(sum_amount(
        tx_base.filter(CreditTransaction.amount < 0)
        .with_entities(func.sum(CreditTransaction.amount))
    ))
    used_today = abs(sum_amount(
        tx_base.filter(
            CreditTransaction.amount < 0,
            CreditTransaction.created_at >= start_today,
        ).with_entities(func.sum(CreditTransaction.amount))
    ))
    used_week = abs(sum_amount(
        tx_base.filter(
            CreditTransaction.amount < 0,
            CreditTransaction.created_at >= start_week,
        ).with_entities(func.sum(CreditTransaction.amount))
    ))
    bought_total = sum_amount(
        tx_base.filter(CreditTransaction.amount > 0)
        .with_entities(func.sum(CreditTransaction.amount))
    )

    return {
        "credits_remaining": user.credits,
        "used_today": used_today,
        "used_week": used_week,
        "used_total": used_total,
        "bought_total": bought_total,
    }
