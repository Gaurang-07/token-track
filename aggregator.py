"""
aggregator.py - Aggregates token logs from all providers into dashboard stats.
"""

from collections import defaultdict


def aggregate(logs):
    """Aggregate raw log entries into dashboard-ready stats."""
    if not logs:
        return empty_stats()

    total_input   = sum(r.get("input_tokens", 0)  for r in logs)
    total_output  = sum(r.get("output_tokens", 0) for r in logs)
    total_tokens  = sum(r.get("total_tokens", 0)  for r in logs)

    # --- Per Provider ---
    providers = defaultdict(lambda: {"provider": "", "total_tokens": 0,
                                      "input_tokens": 0, "output_tokens": 0,
                                      "message_count": 0})
    for r in logs:
        p = r.get("provider", "unknown")
        providers[p]["provider"]      = p
        providers[p]["total_tokens"]  += r.get("total_tokens", 0)
        providers[p]["input_tokens"]  += r.get("input_tokens", 0)
        providers[p]["output_tokens"] += r.get("output_tokens", 0)
        providers[p]["message_count"] += 1
    providers_list = sorted(providers.values(), key=lambda x: x["total_tokens"], reverse=True)

    # --- Per Model ---
    models = defaultdict(lambda: {"model": "", "provider": "", "total_tokens": 0, "message_count": 0})
    for r in logs:
        m = r.get("model", "unknown")
        models[m]["model"]         = m
        models[m]["provider"]      = r.get("provider", "")
        models[m]["total_tokens"]  += r.get("total_tokens", 0)
        models[m]["message_count"] += 1
    models_list = sorted(models.values(), key=lambda x: x["total_tokens"], reverse=True)

    # --- Per Day ---
    daily = defaultdict(lambda: {"date": "", "total_tokens": 0,
                                  "input_tokens": 0, "output_tokens": 0, "message_count": 0})
    for r in logs:
        d = r.get("date", "")[:10]
        daily[d]["date"]          = d
        daily[d]["total_tokens"]  += r.get("total_tokens", 0)
        daily[d]["input_tokens"]  += r.get("input_tokens", 0)
        daily[d]["output_tokens"] += r.get("output_tokens", 0)
        daily[d]["message_count"] += 1
    daily_list = sorted(daily.values(), key=lambda x: x["date"])

    # --- Top Prompts ---
    top_prompts = sorted(
        [{"text": r.get("prompt", "")[:150], "tokens": r.get("total_tokens", 0),
          "provider": r.get("provider", ""), "model": r.get("model", ""),
          "timestamp": r.get("timestamp", "")}
         for r in logs if r.get("prompt")],
        key=lambda x: x["tokens"], reverse=True
    )[:15]

    # --- Cost estimates (per 1M tokens, rough free-tier pricing) ---
    # Groq Llama: ~free / Gemini Flash: ~free for our volumes
    cost_by_provider = {}
    for p, data in providers.items():
        if "groq" in p.lower():
            cost = 0.0  # free tier
        elif "gemini" in p.lower():
            cost = round(data["total_tokens"] * 0.075 / 1_000_000, 4)
        else:
            cost = 0.0
        cost_by_provider[p] = cost
    total_cost = round(sum(cost_by_provider.values()), 4)

    return {
        "summary": {
            "total_tokens":   total_tokens,
            "total_input":    total_input,
            "total_output":   total_output,
            "total_messages": len(logs),
            "total_providers": len(providers),
            "total_models":   len(models),
            "estimated_cost": total_cost,
        },
        "providers":   providers_list,
        "models":      models_list,
        "daily":       daily_list,
        "top_prompts": top_prompts,
        "cost_by_provider": cost_by_provider,
    }


def empty_stats():
    return {
        "summary": {
            "total_tokens": 0, "total_input": 0, "total_output": 0,
            "total_messages": 0, "total_providers": 0,
            "total_models": 0, "estimated_cost": 0,
        },
        "providers": [], "models": [], "daily": [],
        "top_prompts": [], "cost_by_provider": {},
    }
