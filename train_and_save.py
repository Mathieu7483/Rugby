import sqlite3
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

def load_data_from_sqlite(db_path="data/rugby.db"):
    conn = sqlite3.connect(db_path)
    df_rankings = pd.read_sql_query("SELECT name AS team, position AS ranking, points FROM team_world_rankings;", conn)
    df_worldcups = pd.read_sql_query("SELECT t.name AS team, w.wins AS wc_titles FROM worldcupwinners w JOIN teams t ON t.id = w.national_team_id;", conn)
    conn.close()
    return df_rankings, df_worldcups

def load_real_matches(csv_path="data/results.csv"):
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"] >= "2000-01-01"].copy()
    
    df["target"] = 0
    df.loc[df["home_score"] > df["away_score"], "target"] = 1
    df.loc[df["home_score"] < df["away_score"], "target"] = -1
    
    df = df[df["target"] != 0].copy()
    df["neutral_int"] = df["neutral"].astype(int)
    return df

def engineer_features(df_matches, df_rankings, df_worldcups):
    df = df_matches.merge(df_rankings, left_on="home_team", right_on="team", how="inner").rename(columns={"ranking": "home_ranking", "points": "home_points"}).drop(columns=["team"])
    df = df.merge(df_rankings, left_on="away_team", right_on="team", how="inner").rename(columns={"ranking": "away_ranking", "points": "away_points"}).drop(columns=["team"])
    df = df.merge(df_worldcups, left_on="home_team", right_on="team", how="left").rename(columns={"wc_titles": "home_wc_titles"}).drop(columns=["team"])
    df = df.merge(df_worldcups, left_on="away_team", right_on="team", how="left").rename(columns={"wc_titles": "away_wc_titles"}).drop(columns=["team"])
    
    df["home_wc_titles"] = df["home_wc_titles"].fillna(0)
    df["away_wc_titles"] = df["away_wc_titles"].fillna(0)
    
    df["diff_ranking"] = df["away_ranking"] - df["home_ranking"]
    df["diff_points"] = df["home_points"] - df["away_points"]
    df["diff_wc_titles"] = df["home_wc_titles"] - df["away_wc_titles"]
    return df

def main():
    df_rankings, df_worldcups = load_data_from_sqlite("data/rugby.db")
    df_matches = load_real_matches("data/results.csv")
    df_full = engineer_features(df_matches, df_rankings, df_worldcups)
    
    features = ["diff_ranking", "diff_points", "diff_wc_titles", "home_points", "away_points", "neutral_int"]
    X = df_full[features]
    y = df_full["target"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Modele final
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy du modele final : {acc * 100:.2f}%")
    
    # Sauvegarde
    joblib.dump(model, "model_rugby.pkl")
    print("Modèle sauvegardé sous 'model_rugby.pkl'.")

if __name__ == "__main__":
    main()