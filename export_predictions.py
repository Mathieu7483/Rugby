"""Exporte les probabilités de victoire du modèle pour toutes les paires
des 24 équipes de la Coupe du Monde 2027 (poules + phases finales) vers
web/predictions.js (lu par web/index.html et web/knockout.html).

Usage : python export_predictions.py
Prérequis : model_rugby.pkl (généré par train_and_save.py) et data/rugby.db
"""
import json
import os
import joblib
import pandas as pd

from predict import load_team_stats

POOLS = {
    "A": ["New Zealand", "Australia", "Chile", "Hong Kong China"],
    "B": ["South Africa", "Italy", "Georgia", "Romania"],
    "C": ["Argentina", "Fiji", "Spain", "Canada"],
    "D": ["Ireland", "Scotland", "Uruguay", "Portugal"],
    "E": ["France", "Japan", "USA", "Samoa"],
    "F": ["England", "Wales", "Tonga", "Zimbabwe"],
}

# Noms alternatifs possibles dans ta base SQLite (adapte si besoin)
ALIASES = {
    "Hong Kong China": ["Hong Kong China", "Hong Kong", "Hong Kong, China"],
    "USA": ["USA", "United States", "United States of America"],
}

HOST = "Australia"  # seule équipe réellement "à domicile"


def resolve(name, available):
    for candidate in ALIASES.get(name, [name]):
        if candidate in available:
            return candidate
    return None


def p_home_wins(model, stats, home, away, neutral):
    h, a = stats.loc[home], stats.loc[away]
    X = pd.DataFrame([{
        "diff_ranking": a["ranking"] - h["ranking"],
        "diff_points": h["points"] - a["points"],
        "diff_wc_titles": h["wc_titles"] - a["wc_titles"],
        "home_points": h["points"],
        "away_points": a["points"],
        "neutral_int": 1 if neutral else 0,
    }])
    proba = model.predict_proba(X)[0]
    return float(proba[list(model.classes_).index(1)])


def p_team_a_wins(model, stats, a, b):
    """Probabilité que a batte b. Australie = domicile, sinon terrain neutre
    (moyenne des deux ordres pour supprimer le biais domicile/extérieur)."""
    if a == HOST:
        return p_home_wins(model, stats, a, b, neutral=False)
    if b == HOST:
        return 1 - p_home_wins(model, stats, b, a, neutral=False)
    p1 = p_home_wins(model, stats, a, b, neutral=True)
    p2 = 1 - p_home_wins(model, stats, b, a, neutral=True)
    return (p1 + p2) / 2


def main():
    model = joblib.load("model_rugby.pkl")
    stats = load_team_stats("data/rugby.db").set_index("team")
    available = set(stats.index)

    # Toutes les paires possibles (poules + phases finales)
    teams_all = [t for teams in POOLS.values() for t in teams]
    out, missing = {}, []
    for i in range(len(teams_all)):
        for j in range(i + 1, len(teams_all)):
            a, b = teams_all[i], teams_all[j]
            da, db = resolve(a, available), resolve(b, available)
            if not da or not db:
                missing += [t for t, d in ((a, da), (b, db)) if not d]
                continue
            out[f"{a}|{b}"] = round(p_team_a_wins(model, stats, da, db), 4)

    os.makedirs("web", exist_ok=True)
    with open("web/predictions.js", "w", encoding="utf-8") as f:
        f.write("window.PREDICTIONS = " + json.dumps(out, indent=1) + ";\n")

    print(f"{len(out)} paires exportées vers web/predictions.js")
    if missing:
        print("Équipes absentes de la base (estimation de secours utilisée) :",
              ", ".join(sorted(set(missing))))


if __name__ == "__main__":
    main()