"""
Webhook de Stripe.
POST /webhooks/stripe → Genera la API key y crea la cuenta del usuario tras el pago.
"""

from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, APIKey, CreditTransaction, User, PendingRegistration
from datetime import datetime
import stripe
import os
import secrets
import hashlib
import logging

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload        = await request.body()
    sig_header     = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except stripe.error.SignatureVerificationError:
        logger.warning("Webhook con firma inválida")
        raise HTTPException(status_code=400, detail="Firma inválida")

    # ── Pago único completado ─────────────────────────────────────────────────
    if event["type"] == "checkout.session.completed":
        session  = event["data"]["object"]
        metadata = session.get("metadata", {})
        plan     = metadata.get("plan", "starter")
        credits  = int(metadata.get("credits", 20))

        if session.payment_status not in ("paid", "no_payment_required"):
            return {"status": "ignored", "reason": "pago no completado"}

        db: Session = SessionLocal()
        try:
            _create_user_and_key(db, session, metadata, plan, credits)
        except Exception as e:
            db.rollback()
            logger.error(f"Error procesando checkout.session.completed: {e}")
            raise HTTPException(status_code=500, detail="Error interno")
        finally:
            db.close()

    # ── Renovación mensual (suscripción) ─────────────────────────────────────
    elif event["type"] == "invoice.paid":
        invoice          = event["data"]["object"]
        subscription_id  = invoice.get("subscription")
        customer_id      = invoice.get("customer")

        if not subscription_id or invoice.get("billing_reason") == "subscription_create":
            # El primer invoice lo genera checkout.session.completed, no lo procesamos aquí
            return {"status": "ignored", "reason": "primer invoice, ya procesado"}

        db: Session = SessionLocal()
        try:
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if not user:
                logger.warning(f"invoice.paid: no se encontró usuario para customer {customer_id}")
                return {"status": "ignored"}

            key_obj = db.query(APIKey).filter(
                APIKey.user_id == user.id, APIKey.is_active == True
            ).first()
            if key_obj:
                key_obj.credits += 50  # recarga mensual
                key_obj.updated_at = datetime.utcnow()
                db.add(CreditTransaction(
                    api_key           = key_obj.key,
                    amount            = 50,
                    description       = "Renovación mensual",
                    stripe_session_id = subscription_id,
                ))
                db.commit()
                logger.info(f"✅ Renovación mensual: +50 créditos para {user.email}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error procesando invoice.paid: {e}")
        finally:
            db.close()

    return {"status": "ok"}


def _create_user_and_key(
    db: Session,
    session: dict,
    metadata: dict,
    plan: str,
    credits: int,
):
    """Crea el User (desde PendingRegistration) y su APIKey."""
    pending_id  = metadata.get("pending_id")
    customer_id = session.get("customer")

    # ── Buscar registro pendiente ─────────────────────────────────────────────
    pending = db.query(PendingRegistration).filter(
        PendingRegistration.id == pending_id
    ).first() if pending_id else None

    if pending:
        # Verificar que el usuario no se duplicó (webhook retry)
        if db.query(User).filter(User.email == pending.email).first():
            logger.warning(f"Usuario {pending.email} ya existe, ignorando retry")
            if pending:
                db.delete(pending)
                db.commit()
            return

        user = User(
            username           = pending.username,
            email              = pending.email,
            hashed_password    = pending.hashed_password,
            stripe_customer_id = customer_id,
            plan               = plan,
        )
        db.add(user)
        db.flush()   # obtener user.id sin commit
        email = pending.email
    else:
        # Flujo legacy (sin registro previo): usar email de Stripe
        email = session.get("customer_details", {}).get("email", "unknown")
        user  = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                username           = email.split("@")[0],
                email              = email,
                hashed_password    = "",
                stripe_customer_id = customer_id,
                plan               = plan,
            )
            db.add(user)
            db.flush()

    # ── Generar API Key ───────────────────────────────────────────────────────
    raw_key    = "lol_" + secrets.token_urlsafe(32)
    hashed     = hash_key(raw_key)
    key_prefix = raw_key[:16]

    key_obj = APIKey(
        key        = hashed,
        name       = user.username,
        credits    = credits,
        is_active  = True,
        user_id    = user.id,
        key_prefix = key_prefix,
        created_at = datetime.utcnow(),
    )
    db.add(key_obj)

    tx = CreditTransaction(
        api_key           = hashed,
        amount            = credits,
        description       = raw_key,          # raw key temporal; se borra al mostrarse en /success
        stripe_session_id = session["id"],
    )
    db.add(tx)

    if pending:
        db.delete(pending)

    db.commit()
    logger.info(f"✅ Cuenta creada: {email} | plan: {plan} | {credits} créditos")