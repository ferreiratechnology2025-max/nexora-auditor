"""
factory_manager.py — Nexora Site Factory
==========================================
Clona a estrutura de Landing Page da AXON para novos nichos,
adaptando conteúdo, paleta de cores e copywriting.

Foco: Venda + Captura de Lead (sem lógica de auditoria).
Saída: startups/{slug}/index.html + style.css prontos para deploy.

Uso:
    python core/factory_manager.py --niche saude
    python core/factory_manager.py --niche imobiliario
    python core/factory_manager.py --niche financas
    python core/factory_manager.py --custom  # modo interativo

    # Listar nichos disponíveis:
    python core/factory_manager.py --list
"""

import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── Paths ─────────────────────────────────────────────────────────────────────
_ROOT      = Path(__file__).resolve().parents[1]
_TEMPLATE  = _ROOT / "startups" / "axon"
_OUTPUT    = _ROOT / "startups"


# =============================================================================
# NICHE CONFIG — Define a identidade visual e de conteúdo de cada nicho
# =============================================================================

@dataclass
class NicheConfig:
    slug: str                    # identificador: "saude", "imobiliario"
    brand_name: str              # "MEDIX", "PROPIX", etc.
    brand_accent: str            # letra colorida no logo ("IX", "ON", etc.)
    tagline: str                 # Hero title principal
    subtagline: str              # Subtítulo do hero
    hero_sub: str                # Parágrafo de apoio do hero

    # Acento primário e seu glow (iOS palette)
    accent_primary: str = "#0a84ff"
    accent_glow: str    = "rgba(10,132,255,0.35)"
    accent_subtle: str  = "rgba(10,132,255,0.12)"

    # Seção de problemas (4 cards)
    problems: list[dict] = field(default_factory=list)

    # Features / capacidades (6 cards)
    features: list[dict] = field(default_factory=list)

    # Métricas (3 valores)
    metrics: list[dict] = field(default_factory=list)

    # Steps "Como funciona" (4 passos)
    steps: list[dict] = field(default_factory=list)

    # Waitlist CTA
    waitlist_title: str = "Entre na Lista de Espera."
    waitlist_desc: str  = "Acesso antecipado. Vagas limitadas."
    waitlist_cta: str   = "Garantir meu acesso antecipado"

    # Footer
    footer_company: str = ""
    copyright_year: str = "2026"

    # Badge no hero
    hero_badge: str = "Lançamento em Breve"

    # Endpoint da API
    api_endpoint: str = "/api/waitlist"

    # Infraestrutura / deploy
    port:   int = 5008
    domain: str = ""
    target: str = ""
    status: str = "draft"   # draft | awaiting_activation | live

    def __post_init__(self):
        if not self.footer_company:
            self.footer_company = f"{self.brand_name} Technologies"


# =============================================================================
# CATÁLOGO DE NICHOS PRÉ-CONFIGURADOS
# =============================================================================

NICHES: dict[str, NicheConfig] = {

    # ── SAÚDE ─────────────────────────────────────────────────────────────────
    "saude": NicheConfig(
        slug="saude",
        brand_name="MEDIX",
        brand_accent="IX",
        tagline="MEDIX.\nGestão de Clínica\npara a Era da IA.",
        subtagline="Agendamento, prontuário e faturamento em uma plataforma.",
        hero_sub=(
            "Clínicas que usam MEDIX <strong>reduzem faltas em 60%</strong> "
            "e dobram a capacidade de atendimento sem contratar mais equipe."
        ),
        accent_primary="#30d158",
        accent_glow="rgba(48,209,88,0.35)",
        accent_subtle="rgba(48,209,88,0.12)",
        hero_badge="Gestão Clínica · IA de Elite",
        problems=[
            {"icon": "📅", "title": "Agenda Desorganizada",
             "desc": "Faltas, encaixes e remarcações consomem horas do dia. Sem automação, a recepção vive apagando incêndio."},
            {"icon": "📋", "title": "Prontuário no Papel",
             "desc": "Informações perdidas, histórico fragmentado e risco de erros clínicos por falta de dados integrados."},
            {"icon": "💸", "title": "Faturamento Perdido",
             "desc": "Procedimentos não cobrados, glosas de convênio e relatórios financeiros inexatos custam até 20% do faturamento."},
            {"icon": "📊", "title": "Sem Visibilidade",
             "desc": "Sem dashboard, o gestor toma decisões no escuro — sem saber quais médicos, dias e procedimentos geram mais resultado."},
        ],
        features=[
            {"icon": "🗓️", "title": "Agendamento Inteligente",
             "desc": "IA que preenche encaixes automaticamente, envia lembretes e reduz faltas em até 60%."},
            {"icon": "📝", "title": "Prontuário Digital",
             "desc": "Histórico completo por paciente, prescrições digitais, exames integrados e assinatura eletrônica."},
            {"icon": "💳", "title": "Faturamento Automático",
             "desc": "TISS, TUSS e CBHPM integrados. Envio de lotes para convênios com um clique."},
            {"icon": "📊", "title": "Dashboard Executivo",
             "desc": "Métricas de produtividade por médico, taxa de ocupação, ticket médio e projeção de receita."},
            {"icon": "📱", "title": "App para Pacientes",
             "desc": "Portal do paciente para agendar, ver resultados e pagar — reduz ligações para a recepção."},
            {"icon": "🔒", "title": "LGPD Nativo",
             "desc": "Dados criptografados, consentimento registrado e auditoria de acesso — conformidade total com a LGPD."},
        ],
        metrics=[
            {"value": "60", "unit": "%", "label": "de redução em faltas e cancelamentos"},
            {"value": "2×",  "unit": "",  "label": "mais atendimentos sem aumentar equipe"},
            {"value": "20",  "unit": "%", "label": "de receita recuperada com faturamento automático"},
        ],
        steps=[
            {"title": "Cadastre sua clínica",
             "desc": "Importamos sua agenda e histórico de pacientes. Setup completo em menos de 1 hora."},
            {"title": "Configure os fluxos",
             "desc": "Defina regras de agendamento, convênios aceitos, alertas e modelos de prontuário."},
            {"title": "Automatize o atendimento",
             "desc": "Confirmações, lembretes e cobranças rodam sozinhos. Sua equipe foca no que importa."},
            {"title": "Monitore em tempo real",
             "desc": "Dashboard atualizado ao vivo. Tome decisões baseadas em dados — não em intuição."},
        ],
        waitlist_title="Sua clínica merece tecnologia de elite.",
        waitlist_desc="Junte-se a centenas de médicos que já estão na lista. Acesso antecipado com 40% de desconto no primeiro ano.",
        waitlist_cta="Quero acesso antecipado ao MEDIX",
        footer_company="Medix Health Technologies",
    ),

    # ── IMOBILIÁRIO ───────────────────────────────────────────────────────────
    "imobiliario": NicheConfig(
        slug="imobiliario",
        brand_name="PROPIX",
        brand_accent="IX",
        tagline="PROPIX.\nVenda mais Imóveis\ncom IA.",
        subtagline="Do lead ao contrato assinado — sem perder oportunidades.",
        hero_sub=(
            "Imobiliárias que usam PROPIX <strong>fecham 3× mais negócios</strong> "
            "e reduzem o ciclo de venda de 90 dias para menos de 30."
        ),
        accent_primary="#ff9f0a",
        accent_glow="rgba(255,159,10,0.35)",
        accent_subtle="rgba(255,159,10,0.12)",
        hero_badge="CRM Imobiliário · IA de Elite",
        problems=[
            {"icon": "🔥", "title": "Leads Desperdicados",
             "desc": "Portais geram centenas de contatos que somem no WhatsApp. Sem CRM, o corretor esquece e o cliente compra no concorrente."},
            {"icon": "📂", "title": "Carteira Desorganizada",
             "desc": "Imóveis cadastrados em planilhas, fotos em WhatsApp e contratos em papel. Caos que custa vendas."},
            {"icon": "⏰", "title": "Follow-up Manual",
             "desc": "Cada lembrete, cada visita, cada proposta depende da memória do corretor. Uma hora de descuido e o negócio vai embora."},
            {"icon": "📉", "title": "Gestão sem Dados",
             "desc": "Sem métricas, o gestor não sabe quais imóveis giram mais, quais corretores convertem ou qual canal traz leads qualificados."},
        ],
        features=[
            {"icon": "🧲", "title": "CRM com IA",
             "desc": "Captura automática de leads de portais, WhatsApp e Instagram. Qualificação por IA com score de probabilidade de compra."},
            {"icon": "🏘️", "title": "Carteira Digital",
             "desc": "Catálogo profissional com tour virtual 360°, plantas interativas e integração automática com ZAP, OLX e Viva Real."},
            {"icon": "🤖", "title": "Follow-up Automático",
             "desc": "Sequências de mensagens inteligentes no WhatsApp, e-mail e SMS — sem o corretor digitar nada."},
            {"icon": "📋", "title": "Propostas em 1 Clique",
             "desc": "Gere propostas profissionais e contratos prontos para assinar digitalmente — do template ao PDF assinado em minutos."},
            {"icon": "📊", "title": "Dashboard de Conversão",
             "desc": "Taxa de conversão por canal, tempo médio de fechamento, ranking de corretores e previsão de receita."},
            {"icon": "🔗", "title": "Integração Total",
             "desc": "Conecta com portais, cartório digital, financeiras parceiras e ferramentas de marketing — tudo em um lugar."},
        ],
        metrics=[
            {"value": "3×",  "unit": "",  "label": "mais negócios fechados com o mesmo time"},
            {"value": "30",  "unit": "d", "label": "ciclo médio de venda (vs 90 dias no mercado)"},
            {"value": "40",  "unit": "%", "label": "de leads que seriam perdidos, recuperados pela IA"},
        ],
        steps=[
            {"title": "Importe sua carteira",
             "desc": "Conecte seus portais e importe imóveis e leads existentes. Pronto em minutos, sem retrabalho."},
            {"title": "Distribua para os corretores",
             "desc": "Regras de distribuição automática por região, perfil e disponibilidade. Cada lead com o corretor certo."},
            {"title": "A IA nutre os leads",
             "desc": "Sequências automáticas de contato, agendamento de visitas e envio de propostas — sem intervenção manual."},
            {"title": "Feche e acompanhe",
             "desc": "Assinatura digital, repasse de comissões e histórico completo. Do lead ao pós-venda, tudo registrado."},
        ],
        waitlist_title="Sua imobiliária no próximo nível.",
        waitlist_desc="Acesso antecipado para imobiliárias selecionadas. Onboarding gratuito e 3 meses sem mensalidade.",
        waitlist_cta="Quero transformar minha imobiliária",
        footer_company="Propix Real Estate Technologies",
    ),

    # ── FINANCAS ──────────────────────────────────────────────────────────────
    "financas": NicheConfig(
        slug="financas",
        brand_name="FINIX",
        brand_accent="IX",
        tagline="FINIX.\nControle Financeiro\npara PMEs de Elite.",
        subtagline="DRE, fluxo de caixa e projeções — em tempo real, sem contador.",
        hero_sub=(
            "Empresas que usam FINIX <strong>eliminam surpresas no caixa</strong> "
            "e tomam decisões 10× mais rápido com IA financeira integrada."
        ),
        accent_primary="#bf5af2",
        accent_glow="rgba(191,90,242,0.35)",
        accent_subtle="rgba(191,90,242,0.12)",
        hero_badge="Gestão Financeira · IA de Elite",
        problems=[
            {"icon": "😰", "title": "Surpresas no Caixa",
             "desc": "Sem projeção de fluxo de caixa, empresas quebram mesmo lucrando. O problema não é vender — é saber quando o dinheiro entra."},
            {"icon": "📊", "title": "DRE no Excel",
             "desc": "Demonstrativos feitos manualmente, sempre atrasados e cheios de erros. Decisões baseadas em dados de 30 dias atrás."},
            {"icon": "🧾", "title": "Conciliação Manual",
             "desc": "Horas reconciliando extrato bancário com lançamentos. Tempo que deveria ir para o negócio vai para planilha."},
            {"icon": "🤷", "title": "Sem Visibilidade de Margem",
             "desc": "Você sabe quanto vendeu, mas não sabe quanto lucrou. Precificação no chute é receita de prejuízo."},
        ],
        features=[
            {"icon": "💸", "title": "Fluxo de Caixa em Tempo Real",
             "desc": "Conecte seus bancos via Open Finance. Entradas e saídas atualizadas automaticamente, com projeção de 90 dias."},
            {"icon": "📈", "title": "DRE Automatizado",
             "desc": "Demonstrativo de resultado gerado automaticamente a partir dos lançamentos. Atualizado ao minuto, sem contador."},
            {"icon": "🤖", "title": "Conciliacao com IA",
             "desc": "A IA categoriza e concilia lançamentos bancários automaticamente. Reduz horas de trabalho a segundos."},
            {"icon": "🎯", "title": "Precificacao Inteligente",
             "desc": "Calcule o ponto de equilíbrio, margem por produto e preço mínimo para cada SKU — em segundos."},
            {"icon": "🔮", "title": "Projecao e Cenarios",
             "desc": "Simule cenários de crescimento, crise ou expansão. Tome decisões com base em dados, não em intuição."},
            {"icon": "📤", "title": "Relatorios para Investidores",
             "desc": "Gere relatórios profissionais em PDF para sócios, bancos e investidores com um clique."},
        ],
        metrics=[
            {"value": "10×", "unit": "",  "label": "mais rápido para fechar o mês contábil"},
            {"value": "98",  "unit": "%", "label": "de precisão na conciliação automática"},
            {"value": "40",  "unit": "h", "label": "economizadas por mês em tarefas manuais"},
        ],
        steps=[
            {"title": "Conecte seus bancos",
             "desc": "Open Finance com os principais bancos do Brasil. Autorize uma vez, dados fluem automaticamente."},
            {"title": "Importe o historico",
             "desc": "Carregue extratos e planilhas antigas. A IA categoriza tudo e monta seu histórico financeiro."},
            {"title": "Configure o plano de contas",
             "desc": "Adapte às categorias do seu negócio. O FINIX aprende com seus lançamentos e fica mais preciso ao longo do tempo."},
            {"title": "Tome decisoes com dados",
             "desc": "Dashboard ao vivo, alertas proativos e relatórios automáticos. Foco no negócio, não nas planilhas."},
        ],
        waitlist_title="Chega de surpresas financeiras.",
        waitlist_desc="Lista de espera aberta para PMEs. Primeiros 100 clientes com onboarding dedicado e 6 meses gratuitos.",
        waitlist_cta="Quero controle financeiro de elite",
        footer_company="Finix Financial Technologies",
    ),

    # ── EDUCACAO ──────────────────────────────────────────────────────────────
    "educacao": NicheConfig(
        slug="educacao",
        brand_name="EDUNIX",
        brand_accent="NIX",
        tagline="EDUNIX.\nEnsino Online\npara a Era da IA.",
        subtagline="Crie, venda e gerencie cursos com IA — sem técnico, sem complexidade.",
        hero_sub=(
            "Criadores que usam EDUNIX <strong>lançam cursos em 48h</strong> "
            "e aumentam a taxa de conclusão dos alunos em 3× com IA adaptativa."
        ),
        accent_primary="#ffd60a",
        accent_glow="rgba(255,214,10,0.35)",
        accent_subtle="rgba(255,214,10,0.12)",
        hero_badge="EAD · IA de Elite",
        problems=[
            {"icon": "🕐", "title": "Lançamento Demorado",
             "desc": "Configurar plataforma, gravar aulas, montar área de membros e integrar pagamento leva semanas. Ideias que morrem antes de nascer."},
            {"icon": "😴", "title": "Alunos Desengajados",
             "desc": "Sem personalização, os alunos abandonam o curso em menos de 30 dias. Taxa de conclusão abaixo de 15% é comum."},
            {"icon": "💰", "title": "Pagamento Fragmentado",
             "desc": "Gateway, área de membros e e-mail marketing em ferramentas diferentes. Cada integração que quebra custa vendas."},
            {"icon": "📉", "title": "Sem Analytics de Aprendizado",
             "desc": "Você sabe quantos compraram, mas não sabe onde os alunos travam, desistem ou têm dúvidas recorrentes."},
        ],
        features=[
            {"icon": "⚡", "title": "Launch em 48h",
             "desc": "Do upload do conteúdo à página de vendas ativa em menos de 48 horas. Sem código, sem designer."},
            {"icon": "🧠", "title": "IA Adaptativa",
             "desc": "A IA identifica alunos em risco de abandono e envia nudges personalizados no momento certo."},
            {"icon": "💳", "title": "Checkout Nativo",
             "desc": "Pix, cartão parcelado e boleto integrados. Recuperação de carrinho automática e upsell pós-compra."},
            {"icon": "📊", "title": "Analytics de Aprendizado",
             "desc": "Heatmap de engajamento por aula, taxa de conclusão por módulo e pontos de abandono identificados pela IA."},
            {"icon": "🏆", "title": "Gamificacao",
             "desc": "Certificados automatizados, rankings, badges e desafios — alunos que aprendem mais, indicam mais."},
            {"icon": "📱", "title": "App Nativo",
             "desc": "Seus alunos estudam offline no celular. Notificações push aumentam o retorno em 40%."},
        ],
        metrics=[
            {"value": "48", "unit": "h", "label": "do upload ao curso publicado e vendendo"},
            {"value": "3×", "unit": "",  "label": "mais taxa de conclusão com IA adaptativa"},
            {"value": "40", "unit": "%", "label": "de aumento nas vendas com checkout nativo"},
        ],
        steps=[
            {"title": "Carregue seu conteúdo",
             "desc": "Upload de vídeos, PDFs e áudios. A IA estrutura em módulos e gera descrições automaticamente."},
            {"title": "Personalize sua escola",
             "desc": "Logo, cores e domínio próprio. Área de membros profissional sem precisar de designer."},
            {"title": "Ative as vendas",
             "desc": "Página de vendas, checkout e e-mail de boas-vindas configurados em minutos."},
            {"title": "Acompanhe e otimize",
             "desc": "Analytics de aprendizado em tempo real. A IA sugere melhorias com base no comportamento dos alunos."},
        ],
        waitlist_title="Lance seu curso nos próximos 48h.",
        waitlist_desc="Acesso antecipado para criadores selecionados. Primeiro mês gratuito + onboarding dedicado.",
        waitlist_cta="Quero lançar meu curso agora",
        footer_company="Edunix Education Technologies",
    ),

    # ── AUDITOR ───────────────────────────────────────────────────────────────
    "auditor": NicheConfig(
        slug="auditor",
        brand_name="AUDITX",
        brand_accent="IX",
        tagline="AUDITX.\nAuditoria de Código\ncom Auto-Correção.",
        subtagline="Detectamos vulnerabilidades, corrigimos e entregamos o laudo.",
        hero_sub=(
            "Envie seu projeto e receba em minutos um <strong>health score completo</strong>, "
            "patches prontos para aplicar e um laudo profissional para compliance."
        ),
        accent_primary="#ff453a",
        accent_glow="rgba(255,69,58,0.35)",
        accent_subtle="rgba(255,69,58,0.12)",
        hero_badge="Segurança · IA de Elite",
        problems=[
            {"icon": "🕳️", "title": "Vulnerabilidades Ocultas",
             "desc": "SQL Injection, XSS e auth fraca vivem no código sem que ninguém perceba — até o dia que custam caro."},
            {"icon": "⏳", "title": "Auditoria Manual é Lenta",
             "desc": "Reviews manuais levam dias ou semanas e dependem de especialistas escassos e caros."},
            {"icon": "📉", "title": "Sem Visibilidade de Risco",
             "desc": "Sem métricas objetivas, é impossível saber se o código está melhorando ou piorando a cada sprint."},
            {"icon": "📑", "title": "Compliance sem Laudo",
             "desc": "Fintechs, SaaS e empresas reguladas precisam de relatórios formais que nenhuma ferramenta interna gera."},
        ],
        features=[
            {"icon": "🐍", "title": "Multi-linguagem",
             "desc": "Suporta Python, JavaScript, PHP, Java e mais. Análise profunda independente da stack do projeto."},
            {"icon": "📦", "title": "Upload Flexível",
             "desc": "Envie um ZIP ou cole o link do GitHub. Sem instalação, sem configuração de ambiente local."},
            {"icon": "🔍", "title": "Detecção Avançada",
             "desc": "Identificamos SQL Injection, XSS, autenticação fraca e dezenas de outros vetores de ataque conhecidos."},
            {"icon": "🔧", "title": "Auto-Correção com Patch",
             "desc": "Geramos diffs prontos para aplicar. Corrija vulnerabilidades com um clique, sem reescrever código."},
            {"icon": "📊", "title": "Health Score Evolutivo",
             "desc": "Pontuação de segurança antes e depois da correção. Acompanhe a evolução do código ao longo do tempo."},
            {"icon": "📋", "title": "Laudo Profissional",
             "desc": "Relatório completo em PDF pronto para apresentar a clientes, investidores e equipes de compliance."},
        ],
        metrics=[
            {"value": "200+", "unit": "",  "label": "tipos de vulnerabilidades detectadas automaticamente"},
            {"value": "5",    "unit": "min", "label": "para auditoria completa de um projeto médio"},
            {"value": "90",   "unit": "%", "label": "de redução de risco com auto-correção aplicada"},
        ],
        steps=[
            {"title": "Envie seu projeto",
             "desc": "Upload de ZIP ou link do GitHub. Suportamos mono-repos, submódulos e projetos multi-linguagem."},
            {"title": "A IA audita o código",
             "desc": "Varredura completa em busca de vulnerabilidades, más práticas e pontos de falha críticos."},
            {"title": "Receba o patch e o laudo",
             "desc": "Diffs prontos para aplicar e relatório profissional gerado automaticamente em minutos."},
            {"title": "Monitore o Health Score",
             "desc": "Acompanhe a evolução da segurança do projeto a cada commit. IA aprende com seu histórico."},
        ],
        waitlist_title="Seu código merece uma auditoria de elite.",
        waitlist_desc="Acesso antecipado para startups e fintechs selecionadas. Primeira auditoria gratuita.",
        waitlist_cta="Auditar meu código agora",
        footer_company="Nexora Auditor Technologies",
        port=5008,
        domain="auditor.nexora360.cloud",
        target="Startups SaaS, fintechs, agências e empresas com compliance",
        status="awaiting_activation",
    ),
}


# =============================================================================
# FACTORY MANAGER — Clona e adapta a LP da AXON para novos nichos
# =============================================================================

class FactoryManager:
    """
    Gera Landing Pages de venda a partir do template AXON,
    substituindo conteúdo, branding e paleta de cores.
    """

    def __init__(self, template_dir: Path = _TEMPLATE, output_dir: Path = _OUTPUT):
        self.template_dir = template_dir
        self.output_dir   = output_dir

    # ── Public API ────────────────────────────────────────────────────────────

    def clone(self, config: NicheConfig) -> Path:
        """
        Gera index.html + style.css para o nicho em startups/{slug}/.
        Retorna o path da pasta criada.
        """
        dest = self.output_dir / config.slug
        dest.mkdir(parents=True, exist_ok=True)

        html = self._render_html(config)
        css  = self._render_css(config)

        (dest / "index.html").write_text(html, encoding="utf-8")
        (dest / "style.css").write_text(css,  encoding="utf-8")

        # Copia arquivos não-gerados (audit_report permanece, mas não é linkado)
        self._save_metadata(config, dest)

        return dest

    def list_niches(self):
        print("\nNichos pre-configurados:")
        for slug, cfg in NICHES.items():
            print(f"  {slug:<16} -> {cfg.brand_name} ({cfg.tagline.splitlines()[0]})")
        print()

    # ── HTML Generator ────────────────────────────────────────────────────────

    def _render_html(self, c: NicheConfig) -> str:
        brand_logo  = c.brand_name.replace(c.brand_accent, "")
        brand_span  = c.brand_accent
        title_lines = c.tagline.splitlines()
        hero_h1     = "<br />\n        ".join(
            (f'<em>{l}</em>' if l == title_lines[-1] else l) for l in title_lines
        )
        problems_html = "\n".join(self._problem_card(p) for p in c.problems)
        features_html = "\n".join(self._feature_card(f) for f in c.features)
        metrics_html  = "\n".join(self._metric_card(m) for m in c.metrics)
        steps_html    = "\n".join(self._step_card(i, s) for i, s in enumerate(c.steps, 1))
        footer_brand  = c.brand_name.replace(c.brand_accent, "") + f"<span>{c.brand_accent}</span>"

        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="{c.brand_name} — {c.subtagline}" />
  <meta name="theme-color" content="#000000" />
  <meta property="og:title" content="{c.brand_name} — {c.subtagline}" />
  <meta property="og:type" content="website" />
  <title>{c.brand_name} — {c.subtagline}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="style.css" />
</head>
<body>

  <div class="ambient ambient-1" aria-hidden="true"></div>
  <div class="ambient ambient-2" aria-hidden="true"></div>
  <div class="ambient ambient-3" aria-hidden="true"></div>

  <nav class="navbar" role="navigation" aria-label="Navegacao principal">
    <a href="#" class="navbar-logo">{brand_logo}<span>{brand_span}</span></a>
    <a href="#waitlist" class="navbar-cta">Lista de Espera</a>
  </nav>

  <section class="hero" aria-labelledby="hero-title">
    <div class="container">
      <div class="hero-badge">
        <span class="hero-badge-dot" aria-hidden="true"></span>
        {c.hero_badge}
      </div>
      <h1 class="hero-title" id="hero-title">
        {hero_h1}
      </h1>
      <p class="hero-sub">{c.hero_sub}</p>
      <div class="hero-actions">
        <a href="#waitlist" class="btn btn-primary">
          {c.waitlist_cta}
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
            <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </a>
        <a href="#how" class="btn btn-ghost">Como funciona</a>
      </div>
    </div>
  </section>

  <section class="problem" aria-labelledby="problem-title">
    <div class="container">
      <div class="section-header">
        <span class="section-label">O Problema</span>
        <h2 class="section-title" id="problem-title">Por que o mercado ainda falha.</h2>
      </div>
      <div class="problem-grid">{problems_html}</div>
    </div>
  </section>

  <section class="metrics" aria-label="Metricas">
    <div class="container">
      <div class="metrics-row">{metrics_html}</div>
    </div>
  </section>

  <section class="features" aria-labelledby="features-title">
    <div class="container">
      <div class="section-header">
        <span class="section-label">Capacidades</span>
        <h2 class="section-title" id="features-title">Tecnologia que entrega resultado.</h2>
      </div>
      <div class="features-grid">{features_html}</div>
    </div>
  </section>

  <section class="how" id="how" aria-labelledby="how-title">
    <div class="container">
      <div class="section-header">
        <span class="section-label">Processo</span>
        <h2 class="section-title" id="how-title">Do cadastro ao resultado<br />em minutos.</h2>
      </div>
      <div class="steps">{steps_html}</div>
    </div>
  </section>

  <section class="waitlist" id="waitlist" aria-labelledby="waitlist-title">
    <div class="container">
      <div class="glass-card waitlist-box">
        <h2 id="waitlist-title">{c.waitlist_title}</h2>
        <p>{c.waitlist_desc}</p>
        <form class="waitlist-form" id="waitlistForm" action="{c.api_endpoint}" method="POST" novalidate>
          <div class="form-group">
            <label for="wl-name" class="sr-only">Nome completo</label>
            <input id="wl-name" name="name" type="text" class="form-input" placeholder="Nome completo" required />
          </div>
          <div class="form-group">
            <label for="wl-email" class="sr-only">E-mail profissional</label>
            <input id="wl-email" name="email" type="email" class="form-input" placeholder="E-mail profissional" required />
          </div>
          <div class="form-group">
            <label for="wl-company" class="sr-only">Empresa</label>
            <input id="wl-company" name="company" type="text" class="form-input" placeholder="Empresa (opcional)" />
          </div>
          <button type="submit" class="btn btn-primary btn-submit">{c.waitlist_cta}</button>
          <p class="form-note">Sem spam. Sem cartao de credito.</p>
        </form>
        <div class="form-success" id="formSuccess" style="display:none" aria-live="polite">
          <div class="success-icon">&#10003;</div>
          <p class="success-title">Voce esta na lista!</p>
          <p class="success-desc">Entraremos em contato assim que seu acesso estiver liberado.</p>
        </div>
      </div>
    </div>
  </section>

  <footer class="footer" role="contentinfo">
    <div class="container">
      <div class="footer-inner">
        <span class="footer-logo">{footer_brand}</span>
        <ul class="footer-links" aria-label="Links do rodape">
          <li><a href="#">Termos</a></li>
          <li><a href="#">Privacidade</a></li>
        </ul>
        <span class="footer-copy">&copy; {c.copyright_year} {c.footer_company}. Todos os direitos reservados.</span>
      </div>
    </div>
  </footer>

  <script>
    (function () {{
      'use strict';
      const form    = document.getElementById('waitlistForm');
      const success = document.getElementById('formSuccess');
      if (!form) return;
      form.addEventListener('submit', async function (e) {{
        e.preventDefault();
        const btn = form.querySelector('button[type="submit"]');
        btn.disabled = true;
        btn.textContent = 'Enviando...';
        const payload = {{
          name:    form['wl-name'].value.trim(),
          email:   form['wl-email'].value.trim(),
          company: form['wl-company'].value.trim(),
        }};
        try {{
          const res = await fetch('{c.api_endpoint}', {{
            method:  'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body:    JSON.stringify(payload),
          }});
          if (res.ok || res.status === 201) {{ showSuccess(); return; }}
          throw new Error('server');
        }} catch (err) {{
          if (err instanceof TypeError) {{ showSuccess(); return; }}
          btn.disabled = false;
          btn.textContent = '{c.waitlist_cta}';
        }}
      }});
      function showSuccess() {{
        form.style.display    = 'none';
        success.style.display = 'flex';
      }}
      document.querySelectorAll('a[href^="#"]').forEach(function (a) {{
        a.addEventListener('click', function (e) {{
          const t = document.querySelector(this.getAttribute('href'));
          if (t) {{ e.preventDefault(); t.scrollIntoView({{ behavior: 'smooth' }}); }}
        }});
      }});
    }})();
  </script>

</body>
</html>"""

    # ── CSS Generator — aplica paleta de cores do nicho ──────────────────────

    def _render_css(self, c: NicheConfig) -> str:
        template_css = (self.template_dir / "style.css")
        if not template_css.exists():
            return self._minimal_css(c)

        css = template_css.read_text(encoding="utf-8")

        # Substitui apenas os tokens de cor do :root
        css = re.sub(
            r'(--accent-primary:\s*)#[0-9a-fA-F]{3,8}',
            rf'\g<1>{c.accent_primary}',
            css
        )
        css = re.sub(
            r'(--accent-glow:\s*)rgba\([^)]+\)',
            rf'\g<1>{c.accent_glow}',
            css
        )
        css = re.sub(
            r'(--accent-subtle:\s*)rgba\([^)]+\)',
            rf'\g<1>{c.accent_subtle}',
            css
        )

        # Remove estilos específicos da AXON (drag&drop uploader) — não usados aqui
        css = re.sub(
            r'/\* ── UPLOAD / DRAG & DROP.*?(?=/\* ── UTILITY)',
            '',
            css, flags=re.DOTALL
        )
        return css

    @staticmethod
    def _minimal_css(c: NicheConfig) -> str:
        return (
            f":root {{\n"
            f"  --accent-primary: {c.accent_primary};\n"
            f"  --accent-glow: {c.accent_glow};\n"
            f"  --accent-subtle: {c.accent_subtle};\n"
            f"}}\n"
            "/* style.css — regenere com template AXON disponivel */\n"
        )

    # ── Card helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _problem_card(p: dict) -> str:
        return (
            f'\n        <div class="glass-card problem-card">'
            f'<div class="problem-icon">{p["icon"]}</div>'
            f'<h3>{p["title"]}</h3><p>{p["desc"]}</p></div>'
        )

    @staticmethod
    def _feature_card(f: dict) -> str:
        return (
            f'\n        <article class="glass-card feature-card">'
            f'<div class="feature-icon">{f["icon"]}</div>'
            f'<h3>{f["title"]}</h3><p>{f["desc"]}</p></article>'
        )

    @staticmethod
    def _metric_card(m: dict) -> str:
        return (
            f'\n        <div class="glass-card metric-card">'
            f'<div class="metric-value"><span>{m["value"]}</span>{m["unit"]}</div>'
            f'<div class="metric-label">{m["label"]}</div></div>'
        )

    @staticmethod
    def _step_card(i: int, s: dict) -> str:
        return (
            f'\n        <div class="glass-card step">'
            f'<div class="step-number">0{i}</div>'
            f'<div class="step-content"><h3>{s["title"]}</h3><p>{s["desc"]}</p></div></div>'
        )

    def _save_metadata(self, c: NicheConfig, dest: Path):
        meta = {
            "slug":           c.slug,
            "brand_name":     c.brand_name,
            "generated_by":   "Nexora Factory Manager v1.0",
            "accent_primary": c.accent_primary,
            "api_endpoint":   c.api_endpoint,
            "port":           c.port,
            "domain":         c.domain,
            "target":         c.target,
            "status":         c.status,
        }
        (dest / "factory_meta.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
        )


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Nexora Factory Manager — Gera Landing Pages por nicho"
    )
    parser.add_argument("--niche",   help="Nicho pre-configurado (ex: saude, imobiliario)")
    parser.add_argument("--list",    action="store_true", help="Lista nichos disponíveis")
    parser.add_argument("--all",     action="store_true", help="Gera todos os nichos")
    args = parser.parse_args()

    factory = FactoryManager()

    if args.list:
        factory.list_niches()
        return

    if args.all:
        for slug in NICHES:
            dest = factory.clone(NICHES[slug])
            print(f"[OK] {slug:<16} -> {dest}")
        return

    if args.niche:
        slug = args.niche.lower()
        if slug not in NICHES:
            print(f"[ERRO] Niche '{slug}' nao encontrado.")
            factory.list_niches()
            sys.exit(1)
        dest = factory.clone(NICHES[slug])
        print(f"\n[FACTORY] Landing Page gerada com sucesso!")
        print(f"  Niche  : {NICHES[slug].brand_name}")
        print(f"  Pasta  : {dest}")
        print(f"  Arquivos: index.html, style.css, factory_meta.json")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
