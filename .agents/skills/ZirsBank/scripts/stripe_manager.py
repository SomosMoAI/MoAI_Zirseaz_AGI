#!/usr/bin/env python3
"""
ZirsBank - Stripe Manager
Módulo central para gestionar pagos con Stripe.
Uso: python stripe_manager.py --action <accion> [parametros]
Acciones: charge, subscription, webhook, report
"""

import os
import json
import sys
from datetime import datetime

class StripeManager:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("STRIPE_SECRET_KEY")
        self.stripe_available = False
        
        if self.api_key:
            try:
                import stripe
                stripe.api_key = self.api_key
                self.stripe_available = True
                print("✅ Stripe conectado correctamente")
            except ImportError:
                print("⚠️  stripe no instalado. Usando modo simulación.")
        else:
            print("⚠️  No hay STRIPE_SECRET_KEY. Modo simulación.")
    
    def create_charge(self, amount, currency="usd", source=None, description=""):
        """Crear un cargo simple (sin 3D Secure)"""
        if self.stripe_available:
            import stripe
            try:
                charge = stripe.Charge.create(
                    amount=int(amount * 100),  # centavos
                    currency=currency.lower(),
                    source=source,
                    description=description
                )
                return {"success": True, "charge_id": charge.id, "status": charge.status}
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            return {"success": True, "charge_id": "sim_123", "status": "succeeded", "mode": "SIMULATION"}
    
    def create_subscription(self, customer_email, price_id, payment_method=None):
        """Crear suscripción para un cliente existente o nuevo"""
        if self.stripe_available:
            import stripe
            try:
                # Buscar cliente por email o crear
                customers = stripe.Customer.list(email=customer_email).data
                if customers:
                    customer = customers[0]
                else:
                    customer = stripe.Customer.create(email=customer_email)
                
                # Crear suscripción
                subscription = stripe.Subscription.create(
                    customer=customer.id,
                    items=[{"price": price_id}],
                    payment_behavior="default_incomplete",
                    expand=["latest_invoice.payment_intent"]
                )
                return {
                    "success": True,
                    "subscription_id": subscription.id,
                    "client_secret": subscription.latest_invoice.payment_intent.client_secret
                }
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            return {"success": True, "subscription_id": "sub_sim_456", "mode": "SIMULATION"}
    
    def handle_webhook(self, payload, sig_header, endpoint_secret):
        """Manejar webhooks entrantes de Stripe"""
        if self.stripe_available:
            import stripe
            try:
                event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
                return {"success": True, "event_type": event.type, "data": event.data.object}
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            return {"success": True, "event_type": "simulated", "data": {}}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ZirsBank - Stripe Manager")
    parser.add_argument("--action", required=True, choices=["charge", "subscription", "webhook", "report"])
    parser.add_argument("--amount", type=float, default=10.0)
    parser.add_argument("--email", default="cliente@ejemplo.com")
    parser.add_argument("--price-id", default="price_123")
    args = parser.parse_args()
    
    manager = StripeManager()
    
    if args.action == "charge":
        result = manager.create_charge(args.amount)
        print(json.dumps(result, indent=2))
    elif args.action == "subscription":
        result = manager.create_subscription(args.email, args.price_id)
        print(json.dumps(result, indent=2))
    elif args.action == "webhook":
        print("Esperando payload de webhook... (simulado)")