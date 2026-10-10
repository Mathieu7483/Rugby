import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score

def load_data_from_sqlite(db_path="data/rugby.db"):
    """Extraction des tables métier depuis la base SQLite."""
    conn = sqlite3.connect(db_path)
    
    df_rankings = pd.read_sql_query(
        "SELECT name AS team, position AS ranking, points FROM team_world_rankings;", 
        conn
    )
    
    df_worldcups = pd.read_sql_query(
        """
        SELECT t.name AS team, w.wins AS wc_titles 
        FROM worldcupwinners w 
        JOIN teams t ON t.id = w.national_team_id;
        """, 
        conn
    )
    
    conn.close()
    return df_rankings, df_worldcups

def compute_rolling_form(df, window=5):
    """Calcul de la forme récente (taux de victoire sur les N derniers matchs)."""
    records = []
    for idx, row in df.iterrows():
        home_win = 1 if row["home_score"] > row["away_score"] else 0
        records.append({"date": row["date"], "team": row["home_team"], "win": home_win, "match_id": idx})
        
        away_win = 1 if row["away_score"] > row["home_score"] else 0
        records.append({"date": row["date"], "team": row["away_team"], "win": away_win, "match_id": idx})
    
    df_teams = pd.DataFrame(records).sort_values("date").reset_index(drop=True)
    
    # Decalage temporal (shift(1)) pour eviter la fuite de donnees
    df_teams["win_rate_5"] = df_teams.groupby("team")["win"].transform(
        lambda x: x.shift(1).rolling(window, min_periods=1).mean()
    )
    
    home_form_dict = df_teams.set_index(["match_id", "team"])["win_rate_5"].to_dict()
    
    home_form_list = []
    away_form_list = []
    
    for idx, row in df.iterrows():
        h_f = home_form_dict.get((idx, row["home_team"]), 0.5)
        a_f = home_form_dict.get((idx, row["away_team"]), 0.5)
        home_form_list.append(0.5 if pd.isna(h_f) else h_f)
        away_form_list.append(0.5 if pd.isna(a_f) else a_f)
        
    df["home_form_5"] = home_form_list
    df["away_form_5"] = away_form_list
    df["diff_form"] = df["home_form_5"] - df["away_form_5"]
    
    return df

def load_real_matches(csv_path="data/results.csv"):
    """Chargement et preparation des matchs depuis results.csv."""
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    
    df = compute_rolling_form(df, window=5)
    
    df = df[df["date"] >= "2000-01-01"].copy()
    
    df["target"] = 0
    df.loc[df["home_score"] > df["away_score"], "target"] = 1
    df.loc[df["home_score"] < df["away_score"], "target"] = -1
    
    df = df[df["target"] != 0].copy()
    df["neutral_int"] = df["neutral"].astype(int)
    
    return df

def engineer_features(df_matches, df_rankings, df_worldcups):
    """Croisement des matchs avec SQLite."""
    df = df_matches.merge(
        df_rankings, left_on="home_team", right_on="team", how="inner"
    ).rename(columns={"ranking": "home_ranking", "points": "home_points"}).drop(columns=["team"])
    
    df = df.merge(
        df_rankings, left_on="away_team", right_on="team", how="inner"
    ).rename(columns={"ranking": "away_ranking", "points": "away_points"}).drop(columns=["team"])
    
    df = df.merge(
        df_worldcups, left_on="home_team", right_on="team", how="left"
    ).rename(columns={"wc_titles": "home_wc_titles"}).drop(columns=["team"])
    
    df = df.merge(
        df_worldcups, left_on="away_team", right_on="team", how="left"
    ).rename(columns={"wc_titles": "away_wc_titles"}).drop(columns=["team"])
    
    df["home_wc_titles"] = df["home_wc_titles"].fillna(0)
    df["away_wc_titles"] = df["away_wc_titles"].fillna(0)
    
    df["diff_ranking"] = df["away_ranking"] - df["home_ranking"]
    df["diff_points"] = df["home_points"] - df["away_points"]
    df["diff_wc_titles"] = df["home_wc_titles"] - df["away_wc_titles"]
    
    return df

def main():
    print("1. Lecture de data/rugby.db...")
    df_rankings, df_worldcups = load_data_from_sqlite("data/rugby.db")
    
    print("2. Chargement de data/results.csv et calcul de la forme dynamique...")
    df_matches = load_real_matches("data/results.csv")
    
    print("3. Feature Engineering...")
    df_full = engineer_features(df_matches, df_rankings, df_worldcups)
    print(f"   Matchs retenus : {len(df_full)}")
    
    features = [
        "diff_ranking", 
        "diff_points", 
        "diff_wc_titles", 
        "home_points", 
        "away_points", 
        "neutral_int",
        "home_form_5",
        "away_form_5",
        "diff_form"
    ]
    
    X = df_full[features]
    y = df_full["target"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Modeles avec normalisation et hyperparametres ajustes
    models = {
        "RandomForest": RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.05, max_depth=3, random_state=42),
        "LogisticRegression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, random_state=42))
    }
    
    print("\n4. Comparaison des modèles optimisés :")
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"   - {name} : {acc * 100:.2f}% d'accuracy")

if __name__ == "__main__":
    main()