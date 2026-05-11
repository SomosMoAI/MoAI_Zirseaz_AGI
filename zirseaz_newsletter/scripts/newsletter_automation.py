#!/usr/bin/env python3
"""Zirseaz Newsletter Engine — Pipeline completo de ingresos automatizados."""
import os,sys,json,time
from datetime import datetime

sys.path.insert(0,os.path.join(os.getcwd(),'skills_repo'))
sys.path.insert(0,os.path.join(os.getcwd(),'.agents','skills','zirseaz','skills_repo'))

PROJ_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class NewsEngine:
    def __init__(self):
        self.subs = []
        self.income = 0
        self._load()
    def _load(self):
        p = os.path.join(PROJ_DIR,'data.json')
        if os.path.exists(p):
            with open(p) as f:
                d = json.load(f)
                self.subs = d.get('subs',[])
                self.income = d.get('income',0)
        print(f"[NewsEngine] {len(self.subs)} subs | ${self.income} income")
    def _save(self):
        p = os.path.join(PROJ_DIR,'data.json')
        with open(p,'w') as f:
            json.dump({'subs':self.subs,'income':self.income,'updated':datetime.now().isoformat()},f,indent=2)
    def subscribe(self, email, plan='diario'):
        price = 15 if plan=='diario' else 5
        self.income += price
        self.subs.append({'email':email,'plan':plan,'since':datetime.now().isoformat()})
        self._save()
        try:
            from email_manager import send_email_to
            res = send_email_to("cuevasr.sebastian@gmail.com", f"💰 +${price} USD - {email}", f"Nuevo suscriptor {email} plan {plan}. Total: ${self.income}")
            print(f"[Subscribe] {res}")
        except Exception as e:
            print(f"[Subscribe] Error: {e}")
        return True
    def fetch_news(self):
        try:
            from search_skills import buscar_en_web
            res = []
            for q in ["AI news today 2026","inteligencia artificial hoy","AI business opportunities"]:
                r = buscar_en_web(q)
                if r: res.append(r[:300])
            return res or ["No se pudieron obtener noticias"]
        except: return ["Error fetching news"]
    def generate(self):
        news = self.fetch_news()
        lines = [f"# 🤖 Zirseaz AI Daily — {datetime.now().strftime('%d %B %Y')}\n"]
        lines.append("\n## 📰 Noticias del Día\n")
        for i,n in enumerate(news[:5],1):
            lines.append(f"{i}. {n[:200]}\n")
        lines.append(f"\n---\n*Generado por Zirseaz AGI | Subs: {len(self.subs)} | Ingresos: ${self.income}*")
        return ''.join(lines)
    def send_all(self):
        content = self.generate()
        try:
            from email_manager import send_email_to
            for s in self.subs:
                res = send_email_to(s['email'], f"🤖 Zirseaz Daily - {datetime.now().strftime('%d %b')}", content)
                if res.startswith("Exito"):
                    print(f"  ✓ {s['email']}")
                else:
                    print(f"  ✗ {s['email']}: {res}")
            send_email_to("cuevasr.sebastian@gmail.com", "📊 Reporte Diario", f"Enviado a {len(self.subs)} subs | ${self.income} generados")
        except Exception as e:
            print(f"Error sending: {e}")
    def report(self):
        return json.dumps({
            'subs':len(self.subs),
            'income':self.income,
            'mrr':len(self.subs)*12,
            'diario':sum(1 for s in self.subs if s['plan']=='diario'),
            'semanal':sum(1 for s in self.subs if s['plan']=='semanal'),
            'updated':datetime.now().isoformat()
        },indent=2)

if __name__=='__main__':
    import argparse
    e = NewsEngine()
    p = argparse.ArgumentParser()
    p.add_argument('--action',choices=['gen','send','report','sub'],default='report')
    p.add_argument('--email',default='')
    p.add_argument('--plan',choices=['diario','semanal'],default='diario')
    a = p.parse_args()
    if a.action=='gen': print(e.generate())
    elif a.action=='send': e.send_all()
    elif a.action=='sub' and a.email: e.subscribe(a.email,a.plan)
    else: print(e.report())
