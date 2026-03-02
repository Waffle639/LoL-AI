"""
Webhook de Stripe.
POST /webhooks/stripe  Genera la API key y crea la cuenta del usuario tras el pago.
"""

from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, APIKey, CreditTransaction, User
from app.auth import create_user_and_api_key
from datetime import datetime
import stripe
import os
import logging
import traceback

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


def _get_email_from_session(session) -> str:
    """Extrae el email de los customer_details de la sesion de Stripe (v10 compatible)."""
    cd = session.get("customer_details") or {}
    if hasattr(cd, "email"):
        return cd.email or "unknown"
    if hasattr(cd, "get"):
        return cd.get("email") or "unknown"
    return "unknown"


@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload        = await request.body()
    sig_header     = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        logger.warning(f"Webhook firma invalida o error de parseo: {e}")
        raise HTTPException(status_code=400, detail="Firma invalida")

    # Pago unico completado
    if event["type"] == "checkout.session.completed":
        session    = event["data"]["object"]
        metadata   = dict(session.get("metadata") or {})
        plan       = metadata.get("plan", "starter")
        credits    = int(metadata.get("credits", 20))
        pay_status = getattr(session, "payment_status", None) or session.get("payment_status")

        if pay_status not in ("paid", "no_payment_required"):
            return {"status": "ignored", "reason": "pago no completado"}

        db: Session = SessionLocal()
        try:
            create_user_and_api_key(
                db                = db,
                pending_id        = metadata.get("pending_id"),
                customer_id       = session.get("customer"),
                email_fallback    = _get_email_from_session(session),
                plan              = plan,
                credits           = credits,
                stripe_session_id = session["id"],
            )
        except Exception as e:
            db.rollback()
            tb = traceback.format_exc()
            logger.error(f"Error procesando checkout.session.completed: {e}\n{tb}")
            print(f"[WEBHOOK ERROR] {e}\n{tb}", flush=True)
            raise HTTPException(status_code=500, detail=f"Error interno: {e}")
        finally:
            db.close()

    # Renovacion mensual (suscripcion)
    elif event["type"] == "invoice.paid":
        invoice         = event["data"]["object"]
        subscription_id = invoice.get("subscription")
        customer_id     = invoice.get("customer")

        if not subscription_id or invoice.get("billing_reason") == "subscription_create":
            return {"status": "ignored", "reason": "primer invoice, ya procesado"}

        db: Session = SessionLocal()
        try:
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if not user:
                logger.warning(f"invoice.paid: no se encontro usuario para customer {customer_id}")
                return {"status": "ignored"}

            key_obj = db.query(APIKey).filter(
                APIKey.user_id == user.id, APIKey.is_active == True
            ).first()
            if key_obj:
                key_obj.credits   += 50
                key_obj.updated_at = datetime.utcnow()
                db.add(CreditTransaction(
                    api_key           = key_obj.key,
                    amount            = 50,
                    description       = "Renovacion mensual",
                    stripe_session_id = subscription_id,
                ))
                db.commit()
                logger.info(f"Renovacion mensual: +50 creditos para {user.email}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error procesando invoice.paid: {e}")
        finally:
            db.close()

    return {"status": "ok"}
