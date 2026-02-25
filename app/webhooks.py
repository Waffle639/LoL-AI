"""
Webhook de Stripe.

POST /webhooks/stripe → Recibe eventos de Stripe y abona créditos automáticamente.

Eventos manejados:
  - checkout.session.completed → Pago exitoso, añadir créditos
"""

from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, APIKey, CreditTransaction
from datetime import datetime
import stripe
import os
import logging

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


@router.post("/stripe")
async def stripe_webhook(request: Request):
    """
    Endpoint que Stripe llama cuando ocurre un evento.
    Verifica la firma y procesa el evento.
    """
    payload     = await request.body()
    sig_header  = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    # Verificar firma — protege contra llamadas falsas
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except stripe.error.SignatureVerificationError:
        logger.warning("Webhook con firma inválida rechazado")
        raise HTTPException(status_code=400, detail="Firma inválida")
    except Exception as e:
        logger.error(f"Error procesando webhook: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    # ==================== EVENTOS ====================

    if event["type"] == "checkout.session.completed":
        session     = event["data"]["object"]
        metadata    = session.get("metadata", {})
        api_key     = metadata.get("api_key")
        pack        = metadata.get("pack", "unknown")
        credits_to_add = int(metadata.get("credits", 0))

        if not api_key or credits_to_add <= 0:
            logger.error(f"Webhook sin metadata válida: {metadata}")
            return {"status": "ignored", "reason": "metadata incompleta"}

        db: Session = SessionLocal()
        try:
            key_obj = db.query(APIKey).filter(APIKey.key == api_key).first()

            if not key_obj:
                logger.error(f"API Key no encontrada en webhook: {api_key[:8]}...")
                return {"status": "error", "reason": "api_key no encontrada"}

            # Abonar créditos
            key_obj.credits     += credits_to_add
            key_obj.updated_at  = datetime.utcnow()

            transaction = CreditTransaction(
                api_key=api_key,
                amount=credits_to_add,
                description=f"Recarga pack '{pack}' via Stripe",
                stripe_session_id=session["id"],
            )
            db.add(transaction)
            db.commit()

            logger.info(f"✅ +{credits_to_add} créditos abonados a {api_key[:8]}... (pack: {pack})")

        except Exception as e:
            db.rollback()
            logger.error(f"Error abonando créditos: {e}")
            raise HTTPException(status_code=500, detail="Error interno al abonar créditos")
        finally:
            db.close()

    else:
        logger.debug(f"Evento ignorado: {event['type']}")

    return {"status": "ok"}
