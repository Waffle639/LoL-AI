#!/usr/bin/env python3
"""
Script d'entrenament - LoL Esports 2024 AI

Entrena dos models basant-se en els notebooks:
  1. SGDClassifier  (IA_LoL.ipynb)           → models/sgd_model.pkl
  2. PyTorch Neural Network (IA_LoL_NeuralNetwork.ipynb) → models/neural_net.pth
"""

import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.data as data
import torch.optim as optim


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CSV_PATH = 'data/2024_LoL_esports_match_data_from_OraclesElixir1.csv'

# Features used by the SGDClassifier (IA_LoL.ipynb)
SGD_FEATURES = [
    'kills', 'deaths', 'assists',
    'teamkills', 'teamdeaths',
    'dragons', 'opp_dragons',
    'elders', 'opp_elders',
    'barons', 'opp_barons',
    'towers', 'opp_towers',
    'totalgold',
]

# All features used by the Neural Network (IA_LoL_NeuralNetwork.ipynb)
NN_FEATURES = [
    'team_encoded', 'player_encoded', 'champion_encoded', 'side_encoded', 'position_encoded',
    'team_winrate', 'player_winrate', 'player_kda', 'champion_winrate', 'player_champ_winrate',
    'kills', 'deaths', 'assists', 'teamkills', 'teamdeaths',
    'dragons', 'opp_dragons', 'elders', 'opp_elders',
    'barons', 'opp_barons', 'towers', 'opp_towers', 'totalgold',
]

NN_NUMERIC_FEATURES = [
    'team_winrate', 'player_winrate', 'player_kda', 'champion_winrate', 'player_champ_winrate',
    'kills', 'deaths', 'assists', 'teamkills', 'teamdeaths',
    'dragons', 'opp_dragons', 'elders', 'opp_elders',
    'barons', 'opp_barons', 'towers', 'opp_towers', 'totalgold',
]

# Features used by the Pre-Game RandomForest (IA_LoL_Prediccion_Pre_Game.ipynb)
PRE_GAME_FEATURES = [
    'team_encoded', 'player_encoded', 'champion_encoded', 'side_encoded', 'position_encoded',
    'team_winrate', 'player_winrate', 'player_kda', 'champion_winrate', 'player_champ_winrate',
]

# Neural network hyperparameters (from IA_LoL_NeuralNetwork.ipynb)
BATCH_SIZE_TRAIN = 16
BATCH_SIZE_TEST  = 1000
LEARNING_RATE    = 0.001
EPOCHS           = 50
DROPOUT_RATE     = 0.2


# ---------------------------------------------------------------------------
# Neural Network architecture (exactly as in IA_LoL_NeuralNetwork.ipynb)
# ---------------------------------------------------------------------------

class AI_LoL_NeuralNetwork(nn.Module):
    def __init__(self, input_size):
        super().__init__()
        self.fc1      = nn.Linear(input_size, 64)
        self.dropout1 = nn.Dropout(DROPOUT_RATE)
        self.fc2      = nn.Linear(64, 32)
        self.dropout2 = nn.Dropout(DROPOUT_RATE)
        self.fc3      = nn.Linear(32, 1)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout1(x)
        x = F.relu(self.fc2(x))
        x = self.dropout2(x)
        x = torch.sigmoid(self.fc3(x))
        return x


# ---------------------------------------------------------------------------
# Wrapper sklearn-like para la Neural Network
# ---------------------------------------------------------------------------

class LoLNeuralNetWrapper:
    """
    Envuelve el modelo PyTorch + scaler + encoders en un objeto
    que se usa exactamente igual que el SGDClassifier:
        model.predict(X)       → array [0, 1, 1, 0]
        model.predict_proba(X) → array [0.82, 0.61, ...]
    """

    def __init__(self, checkpoint_path: str):
        ck = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
        self._net           = AI_LoL_NeuralNetwork(input_size=ck['input_size'])
        self._net.load_state_dict(ck['model_state_dict'])
        self._net.eval()
        self.scaler         = ck['scaler']
        self.encoders       = ck['encoders']
        self.feature_names  = ck['feature_names']

    def _to_tensor(self, X: pd.DataFrame) -> torch.FloatTensor:
        X = X[self.feature_names].copy()
        X[NN_NUMERIC_FEATURES] = self.scaler.transform(X[NN_NUMERIC_FEATURES])
        return torch.FloatTensor(X.values)

    def predict(self, X: pd.DataFrame):
        with torch.no_grad():
            proba = self._net(self._to_tensor(X)).numpy().flatten()
        return (proba > 0.5).astype(int)

    def predict_proba(self, X: pd.DataFrame):
        with torch.no_grad():
            return self._net(self._to_tensor(X)).numpy().flatten()


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_csv() -> pd.DataFrame:
    if not Path(CSV_PATH).exists():
        raise FileNotFoundError(f"No s'ha trobat el dataset: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH, sep=';')
    print(f"Dataset carregat: {df.shape[0]} files, {df.shape[1]} columnes")
    return df


# ---------------------------------------------------------------------------
# 1. Train SGDClassifier  (IA_LoL.ipynb)
# ---------------------------------------------------------------------------

def train_sgd(output_path: str = 'models/sgd_model.pkl'):
    print("\n" + "="*60)
    print("MODEL 1: SGDClassifier  (IA_LoL.ipynb)")
    print("="*60)

    # Load & clean
    df = load_csv()
    df_clean = df[SGD_FEATURES + ['result']].fillna(0)
    print(f"Features: {len(SGD_FEATURES)}  |  Samples: {len(df_clean)}")

    X = df_clean[SGD_FEATURES]
    y = df_clean['result']

    # Split 70/30 (igual que al notebook)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    # Train (mateixos paràmetres que al notebook)
    model = SGDClassifier(
        loss='log_loss', penalty='l2', alpha=0.0001,
        max_iter=1000, tol=0.001,
        learning_rate='constant', eta0=0.001,
        shuffle=True
    )
    model.fit(X_train_scaled, y_train)

    train_acc = model.score(X_train_scaled, y_train)
    test_acc  = model.score(X_test_scaled, y_test)
    print(f"Train accuracy: {train_acc:.2%}")
    print(f"Test  accuracy: {test_acc:.2%}")

    # Save
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({'model': model, 'scaler': scaler, 'feature_names': SGD_FEATURES}, output_path)
    print(f"Model guardat a: {output_path}")


# ---------------------------------------------------------------------------
# 2. Train PyTorch Neural Network  (IA_LoL_NeuralNetwork.ipynb)
# ---------------------------------------------------------------------------

def train_neural_network(output_path: str = 'models/neural_net.pth'):
    print("\n" + "="*60)
    print("MODEL 2: PyTorch Neural Network  (IA_LoL_NeuralNetwork.ipynb)")
    print("="*60)

    # --- Load & select columns ---
    df = load_csv()
    training_columns = [
        'gameid', 'teamname', 'playername', 'position', 'champion', 'side',
        'kills', 'deaths', 'assists', 'teamkills', 'teamdeaths',
        'dragons', 'opp_dragons', 'elders', 'opp_elders',
        'barons', 'opp_barons', 'towers', 'opp_towers', 'totalgold',
        'result'
    ]
    df_clean = df[training_columns].copy().fillna(0)
    df_clean['playername'] = df_clean['playername'].astype(str)
    df_clean['champion']   = df_clean['champion'].astype(str)

    # --- Historical stats ---
    team_stats = df_clean.groupby('teamname')['result'].mean().reset_index()
    team_stats.columns = ['teamname', 'team_winrate']

    player_stats = df_clean.groupby('playername').agg(
        player_winrate=('result', 'mean'),
        player_avg_kills=('kills', 'mean'),
        player_avg_deaths=('deaths', 'mean'),
        player_avg_assists=('assists', 'mean')
    ).reset_index()
    player_stats['player_kda'] = (
        (player_stats['player_avg_kills'] + player_stats['player_avg_assists'])
        / (player_stats['player_avg_deaths'] + 1)
    )

    champion_stats = df_clean.groupby('champion')['result'].mean().reset_index()
    champion_stats.columns = ['champion', 'champion_winrate']

    player_champ_stats = df_clean.groupby(['playername', 'champion'])['result'].mean().reset_index()
    player_champ_stats.columns = ['playername', 'champion', 'player_champ_winrate']

    # --- Merge ---
    df_features = (
        df_clean
        .merge(team_stats, on='teamname', how='left')
        .merge(player_stats[['playername', 'player_winrate', 'player_kda']], on='playername', how='left')
        .merge(champion_stats, on='champion', how='left')
        .merge(player_champ_stats, on=['playername', 'champion'], how='left')
        .fillna(0)
    )

    # --- Encode categoricals ---
    le_team     = LabelEncoder()
    le_player   = LabelEncoder()
    le_champion = LabelEncoder()
    le_side     = LabelEncoder()
    le_position = LabelEncoder()

    df_features['team_encoded']     = le_team.fit_transform(df_clean['teamname'])
    df_features['player_encoded']   = le_player.fit_transform(df_clean['playername'])
    df_features['champion_encoded'] = le_champion.fit_transform(df_clean['champion'])
    df_features['side_encoded']     = le_side.fit_transform(df_clean['side'])
    df_features['position_encoded'] = le_position.fit_transform(df_clean['position'])

    print(f"Features: {len(NN_FEATURES)}  |  Samples: {len(df_features)}")

    X = df_features[NN_FEATURES]
    y = df_features['result'].values

    # --- Split 80/20 ---
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # --- Scale only numeric features ---
    scaler = StandardScaler()
    x_train_scaled = x_train.copy()
    x_test_scaled  = x_test.copy()
    x_train_scaled[NN_NUMERIC_FEATURES] = scaler.fit_transform(x_train[NN_NUMERIC_FEATURES])
    x_test_scaled[NN_NUMERIC_FEATURES]  = scaler.transform(x_test[NN_NUMERIC_FEATURES])

    # --- PyTorch tensors & dataloaders ---
    x_train_tensor = torch.FloatTensor(x_train_scaled.values)
    y_train_tensor = torch.FloatTensor(y_train).unsqueeze(1)
    x_test_tensor  = torch.FloatTensor(x_test_scaled.values)
    y_test_tensor  = torch.FloatTensor(y_test).unsqueeze(1)

    train_loader = data.DataLoader(
        data.TensorDataset(x_train_tensor, y_train_tensor),
        batch_size=BATCH_SIZE_TRAIN, shuffle=True
    )
    test_loader = data.DataLoader(
        data.TensorDataset(x_test_tensor, y_test_tensor),
        batch_size=BATCH_SIZE_TEST, shuffle=False
    )

    # --- Model, loss, optimizer ---
    model     = AI_LoL_NeuralNetwork(input_size=len(NN_FEATURES))
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    print(f"Arquitectura: {len(NN_FEATURES)} → 64 → 32 → 1")
    print(f"Epochs: {EPOCHS}  |  Batch: {BATCH_SIZE_TRAIN}  |  LR: {LEARNING_RATE}\n")

    # --- Training loop ---
    for epoch in range(EPOCHS):
        model.train()
        epoch_loss = 0.0
        correct = total = 0

        for batch_x, batch_y in train_loader:
            output = model(batch_x)
            loss   = criterion(output, batch_y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            correct    += ((output > 0.5).float() == batch_y).sum().item()
            total      += batch_y.size(0)

        avg_loss = epoch_loss / len(train_loader)
        acc      = 100 * correct / total
        if (epoch + 1) % 10 == 0 or epoch == 0:
            print(f"Epoch [{epoch+1:2d}/{EPOCHS}]  Loss: {avg_loss:.4f}  Train Acc: {acc:.2f}%")

    # --- Evaluate ---
    model.eval()
    y_preds, y_trues = [], []
    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            preds = (model(batch_x) > 0.5).float()
            y_preds.extend(preds.cpu().numpy())
            y_trues.extend(batch_y.cpu().numpy())

    test_acc = accuracy_score(np.array(y_trues), np.array(y_preds))
    print(f"\nTest accuracy: {test_acc:.2%}")

    # --- Save ---
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        'model_state_dict': model.state_dict(),
        'input_size': len(NN_FEATURES),
        'feature_names': NN_FEATURES,
        'scaler': scaler,
        'encoders': {
            'team': le_team, 'player': le_player, 'champion': le_champion,
            'side': le_side, 'position': le_position
        }
    }, output_path)
    print(f"Model guardat a: {output_path}")


# ---------------------------------------------------------------------------
# 3. Train Pre-Game RandomForest  (IA_LoL_Prediccion_Pre_Game.ipynb)
# ---------------------------------------------------------------------------

def train_pregame_rf(output_path: str = 'models/pregame_rf.pkl'):
    print("\n" + "="*60)
    print("MODEL 3: RandomForest Pre-Game  (IA_LoL_Prediccion_Pre_Game.ipynb)")
    print("="*60)

    # --- Load & select columns ---
    df = load_csv()
    training_columns = [
        'gameid', 'teamname', 'playername', 'position', 'champion', 'side', 'result'
    ]
    df_clean = df[training_columns].copy().fillna(0)
    df_clean['playername'] = df_clean['playername'].astype(str)
    df_clean['champion']   = df_clean['champion'].astype(str)

    # --- Historical stats (lookup tables saved with model for inference) ---
    team_stats = df_clean.groupby('teamname')['result'].mean().reset_index()
    team_stats.columns = ['teamname', 'team_winrate']

    kda_base = df[['playername', 'kills', 'deaths', 'assists', 'result']].copy().fillna(0)
    player_kda_stats = kda_base.groupby('playername').agg(
        player_winrate=('result', 'mean'),
        player_avg_kills=('kills', 'mean'),
        player_avg_deaths=('deaths', 'mean'),
        player_avg_assists=('assists', 'mean'),
    ).reset_index()
    player_kda_stats['player_kda'] = (
        (player_kda_stats['player_avg_kills'] + player_kda_stats['player_avg_assists'])
        / (player_kda_stats['player_avg_deaths'] + 1)
    )

    champion_stats = df_clean.groupby('champion')['result'].mean().reset_index()
    champion_stats.columns = ['champion', 'champion_winrate']

    player_champ_stats = df_clean.groupby(['playername', 'champion'])['result'].mean().reset_index()
    player_champ_stats.columns = ['playername', 'champion', 'player_champ_winrate']

    # --- Merge historical features ---
    df_features = (
        df_clean
        .merge(team_stats, on='teamname', how='left')
        .merge(player_kda_stats[['playername', 'player_winrate', 'player_kda']], on='playername', how='left')
        .merge(champion_stats, on='champion', how='left')
        .merge(player_champ_stats, on=['playername', 'champion'], how='left')
        .fillna(0.5)
    )

    # --- Encode categoricals ---
    le_team     = LabelEncoder()
    le_player   = LabelEncoder()
    le_champion = LabelEncoder()
    le_side     = LabelEncoder()
    le_position = LabelEncoder()

    df_features['team_encoded']     = le_team.fit_transform(df_clean['teamname'])
    df_features['player_encoded']   = le_player.fit_transform(df_clean['playername'])
    df_features['champion_encoded'] = le_champion.fit_transform(df_clean['champion'])
    df_features['side_encoded']     = le_side.fit_transform(df_clean['side'])
    df_features['position_encoded'] = le_position.fit_transform(df_clean['position'])

    print(f"Features: {len(PRE_GAME_FEATURES)}  |  Samples: {len(df_features)}")

    X = df_features[PRE_GAME_FEATURES]
    y = df_features['result'].values

    # --- Split 80/20 ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # --- Train RandomForest (same hyperparams as notebook) ---
    model = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    train_acc = accuracy_score(y_train, model.predict(X_train))
    test_acc  = accuracy_score(y_test,  model.predict(X_test))
    print(f"Train accuracy: {train_acc:.2%}")
    print(f"Test  accuracy: {test_acc:.2%}")

    # --- Save model + encoders + lookup tables ---
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        'model': model,
        'feature_names': PRE_GAME_FEATURES,
        'encoders': {
            'team': le_team, 'player': le_player, 'champion': le_champion,
            'side': le_side, 'position': le_position,
        },
        'team_stats':         team_stats,
        'player_stats':       player_kda_stats[['playername', 'player_winrate', 'player_kda']],
        'champion_stats':     champion_stats,
        'player_champ_stats': player_champ_stats,
    }, output_path)
    print(f"Model guardat a: {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    train_sgd()
    train_neural_network()
    train_pregame_rf()
    print("\n" + "="*60)
    print("ENTRENAMENT COMPLETAT")
    print("="*60)

