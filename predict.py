import sys
import sqlite3
import pandas as pd
import joblib

def load_team_stats(db_path="data/rugby.db"):
    """Extrait les données actuelles des équipes depuis SQLite."""
    conn = sqlite3.connect(db_path)
    
    # Rankings et points
    df_rankings = pd.read_sql_query("SELECT name AS team, position AS ranking, points FROM team_world_rankings;", conn)
    
    # Titres en Coupe du Monde
    df_worldcups = pd.read_sql_query(
        """
        SELECT t.name AS team, w.wins AS wc_titles 
        FROM worldcupwinners w 
        JOIN teams t ON t.id = w.national_team_id;
        """, 
        conn
    )
    conn.close()
    
    # Fusion des données par équipe
    df_teams = df_rankings.merge(df_worldcups, on="team", how="left")
    df_teams["wc_titles"] = df_teams["wc_titles"].fillna(0)
    
    return df_teams

def predict_match(home_team_name, away_team_name, neutral=False, model_path="model_rugby.pkl", db_path="data/rugby.db"):
    # 1. Chargement du modèle
    try:
        model = joblib.load(model_path)
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{model_path}' est introuvable. Exécute train_and_save.py d'abord.")
        return

    # 2. Chargement des données d'équipes
    df_teams = load_team_stats(db_path)
    
    # Vérification des équipes dans la DB
    teams_available = df_teams["team"].tolist()
    
    if home_team_name not in teams_available:
        print(f"Équipe introuvable dans la base : '{home_team_name}'")
        print(f"Équipes disponibles : {', '.join(teams_available)}")
        return

    if away_team_name not in teams_available:
        print(f"Équipe introuvable dans la base : '{away_team_name}'")
        print(f"Équipes disponibles : {', '.join(teams_available)}")
        return

    # 3. Récupération des métriques des 2 équipes
    home_stats = df_teams[df_teams["team"] == home_team_name].iloc[0]
    away_stats = df_teams[df_teams["team"] == away_team_name].iloc[0]

    # 4. Calcul des variables différentielles
    diff_ranking = away_stats["ranking"] - home_stats["ranking"]
    diff_points = home_stats["points"] - away_stats["points"]
    diff_wc_titles = home_stats["wc_titles"] - away_stats["wc_titles"]
    neutral_int = 1 if neutral else 0

    # DataFrame pour la prédiction
    features_df = pd.DataFrame([{
        "diff_ranking": diff_ranking,
        "diff_points": diff_points,
        "diff_wc_titles": diff_wc_titles,
        "home_points": home_stats["points"],
        "away_points": away_stats["points"],
        "neutral_int": neutral_int
    }])

    # 5. Prédiction & Probabilités
    prediction = model.predict(features_df)[0]
    probabilities = model.predict_proba(features_df)[0]
    
    # Mapping des probabilités selon les classes du modèle
    classes = list(model.classes_)  # [-1, 1]
    prob_away = probabilities[classes.index(-1)] * 100
    prob_home = probabilities[classes.index(1)] * 100

    # 6. Affichage des résultats
    print("\n" + "="*50)
    print(f"    PRÉDICTION DE MATCH DE RUGBY")
    print("="*50)
    terrain_str = "Terrain Neutre" if neutral else f"Domicile : {home_team_name}"
    print(f" Contexte : {terrain_str}")
    print(f" Match    : {home_team_name} vs {away_team_name}")
    print("-" * 50)
    print(f" Stats {home_team_name} : Rang #{int(home_stats['ranking'])} | Points : {home_stats['points']} | Titres : {int(home_stats['wc_titles'])}")
    print(f" Stats {away_team_name} : Rang #{int(away_stats['ranking'])} | Points : {away_stats['points']} | Titres : {int(away_stats['wc_titles'])}")
    print("-" * 50)
    print(f" Probabilité de victoire {home_team_name} : {prob_home:.1f}%")
    print(f" Probabilité de victoire {away_team_name} : {prob_away:.1f}%")
    print("-" * 50)
    
    if prediction == 1:
        print(f" Vainqueur prédit : {home_team_name.upper()}")
    else:
        print(f" Vainqueur prédit : {away_team_name.upper()}")
    print("="*50 + "\n")

if __name__ == "__main__":
    # Permet de passer les équipes en argument CLI : python predict.py France "New Zealand" neutral
    if len(sys.argv) >= 3:
        home = sys.argv[1]
        away = sys.argv[2]
        is_neutral = True if len(sys.argv) > 3 and sys.argv[3].lower() in ["neutral", "neutre", "true", "1"] else False
        predict_match(home, away, neutral=is_neutral)
    else:
        # Mode interactif si aucun argument n'est fourni
        home = input("Équipe à domicile (ex: France) : ").strip()
        away = input("Équipe à l'extérieur (ex: New Zealand) : ").strip()
        neutral_input = input("Terrain neutre ? (o/n) : ").strip().lower()
        is_neutral = True if neutral_input in ["o", "oui", "y", "yes", "1"] else False
        
        predict_match(home, away, neutral=is_neutral)