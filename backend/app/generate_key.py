"""
Genera API Keys manualmente.

Uso desde la raíz del proyecto:
    python -m app.generate_key generate --name "test" --credits 100
    python -m app.generate_key list
    python -m app.generate_key add-credits --key lol_xxx --credits 50
"""

import argparse
import secrets
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from app.core.database import SessionLocal, APIKey, CreditTransaction, User, create_tables
from app.auth import hash_password
from datetime import datetime

import hashlib

def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()

def generate_key(name, credits):
    create_tables()
    db = SessionLocal()
    raw_key = "lol_" + secrets.token_urlsafe(32)
    hashed  = hash_key(raw_key)

    email = f"{name}-{secrets.token_hex(4)}@local"
    user = User(
        username=name,
        email=email,
        hashed_password=hash_password(secrets.token_urlsafe(12)),
        credits=credits,
        is_active=True,
    )
    db.add(user)
    db.flush()

    db.add(APIKey(
        key=hashed,
        name=name,
        is_active=True,
        user_id=user.id,
        key_prefix=raw_key[:16],
        created_at=datetime.utcnow(),
    ))
    if credits > 0:
        db.add(CreditTransaction(
            user_id=user.id,
            api_key=hashed,
            amount=credits,
            description="Créditos iniciales",
        ))
    db.commit()
    db.close()
    print(f"\n Key generada!")
    print(f"   Nombre:   {name}")
    print(f"   Key:      {raw_key}   ← guárdala, no se puede recuperar")
    print(f"   Créditos: {credits}\n")


def list_keys():
    create_tables()
    db = SessionLocal()
    keys = db.query(APIKey).all()
    db.close()
    if not keys:
        print("No hay API Keys.")
        return
    print(f"\n{'Nombre':<20} {'Key':<16} {'Créditos':>10} {'Activa':>8}")
    print("-" * 60)
    for k in keys:
        credits = k.user.credits if k.user else 0
        print(f"{k.name:<20} {k.key[:12]}...  {credits:>10} {'✅' if k.is_active else '❌':>8}")


def add_credits(key_prefix, credits):
    db = SessionLocal()
    k = db.query(APIKey).filter(APIKey.key.startswith(key_prefix)).first()
    if not k:
        print(f"❌ Key no encontrada: {key_prefix}")
        db.close()
        return
    if not k.user_id:
        print("❌ La API key no tiene usuario asociado")
        db.close()
        return
    user = db.query(User).filter(User.id == k.user_id).first()
    if not user:
        print("❌ Usuario no encontrado")
        db.close()
        return
    user.credits += credits
    db.add(CreditTransaction(
        user_id=user.id,
        api_key=k.key,
        amount=credits,
        description="Créditos añadidos manualmente",
    ))
    db.commit()
    db.close()
    print(f" +{credits} créditos a '{k.name}'. Total: {user.credits}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")

    g = sub.add_parser("generate")
    g.add_argument("--name", required=True)
    g.add_argument("--credits", type=int, default=0)

    sub.add_parser("list")

    a = sub.add_parser("add-credits")
    a.add_argument("--key", required=True)
    a.add_argument("--credits", type=int, required=True)

    args = parser.parse_args()

    if args.cmd == "generate":     generate_key(args.name, args.credits)
    elif args.cmd == "list":       list_keys()
    elif args.cmd == "add-credits": add_credits(args.key, args.credits)
    else:                          parser.print_help()