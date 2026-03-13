PLANS = {
    "free": {
        "name": "Free",
        "scans_per_month": 3,
        "max_size_mb": 10,
        "features": ["scan_basic", "preview"],
        "price_brl": 0,
    },
    "pro": {
        "name": "Pro",
        "scans_per_month": 50,
        "max_size_mb": 500,
        "features": ["scan_basic", "preview", "full_report", "autofix", "pdf", "email"],
        "price_brl": 29900,
    },
    "enterprise": {
        "name": "Enterprise",
        "scans_per_month": -1,
        "max_size_mb": 2000,
        "features": ["scan_basic", "preview", "full_report", "autofix", "pdf", "email", "github_pr", "api_access"],
        "price_brl": 99000,
    },
}


def can_scan(user) -> tuple[bool, str]:
    plan = PLANS.get(user.plan, PLANS["free"])
    limit = plan["scans_per_month"]
    if limit == -1:
        return True, "ok"
    if user.scans_this_month >= limit:
        return False, f"Limite de {limit} scans/mês atingido. Faça upgrade."
    return True, "ok"


def has_feature(user, feature: str) -> bool:
    plan = PLANS.get(user.plan, PLANS["free"])
    return feature in plan["features"]
