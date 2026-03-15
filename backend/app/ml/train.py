#!/usr/bin/env python3
"""
Script d'entrenament - LoL Esports 2024 AI

Entrena dos models basant-se en els notebooks:
  1. SGDClassifier  (IA_LoL.ipynb)           → models/sgd_model_vN.pkl
  2. PyTorch Neural Network (IA_LoL_NeuralNetwork.ipynb) → models/neural_net_vN.pth

Versioning automàtic, avaluació completa i quality gate via deployment_criteria.yaml.
Metadades guardades a metadata/metadata_vN.json i metadata/nn_metadata_vN.json.
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, confusion_matrix, f1_score,
    precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data as data


# ---------------------------------------------------------------------------
# Constants  (loaded from .env via Settings)
# ---------------------------------------------------------------------------

from app.core.config import get_settings as _get_settings
_s = _get_settings()

CSV_PATH             = _s.CSV_PATH
DEFAULT_MODEL_DIR    = _s.MODEL_DIR
DEFAULT_METADATA_DIR = _s.METADATA_DIR
DEFAULT_CRITERIA     = _s.DEPLOYMENT_CRITERIA

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
    Envuelve el modelo PyTorch + scaler + encoders en un objeto sklearn-like:
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
# Versioning helpers
# ---------------------------------------------------------------------------

def get_next_version_nn(model_dir: str = DEFAULT_MODEL_DIR) -> str:
    """Retorna la propera versió disponible per a la Neural Network (neural_net_vN.pth)."""
    models = Path(model_dir)
    models.mkdir(parents=True, exist_ok=True)
    existing = []
    for f in models.glob("neural_net_v*.pth"):
        try:
            existing.append(int(f.stem.split("_v")[1]))
        except (ValueError, IndexError):
            continue
    return f"v{max(existing, default=0) + 1}"


def get_next_version_pregame(model_dir: str = DEFAULT_MODEL_DIR) -> str:
    """Retorna la propera versió disponible per al Pre-Game RandomForest (pregame_rf_vN.pkl)."""
    models = Path(model_dir)
    models.mkdir(parents=True, exist_ok=True)
    existing = []
    for f in models.glob("pregame_rf_v*.pkl"):
        try:
            existing.append(int(f.stem.split("_v")[1]))
        except (ValueError, IndexError):
            continue
    return f"v{max(existing, default=0) + 1}"


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_classification(y_true, y_pred, y_prob) -> dict:
    """
    Avaluació completa d'un classificador binari.

    Returns:
        dict amb accuracy, precision, recall, f1_score, roc_auc i confusion_matrix.
    """
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    total_neg = tn + fp
    total_pos = fn + tp
    return {
        'accuracy':  float(accuracy_score(y_true, y_pred)),
        'precision': float(precision_score(y_true, y_pred, zero_division=0)),
        'recall':    float(recall_score(y_true, y_pred, zero_division=0)),
        'f1_score':  float(f1_score(y_true, y_pred, zero_division=0)),
        'roc_auc':   float(roc_auc_score(y_true, y_prob)),
        'false_positive_rate': float(fp / total_neg) if total_neg > 0 else 0.0,
        'false_negative_rate': float(fn / total_pos) if total_pos > 0 else 0.0,
        'confusion_matrix': {
            'true_negative':  int(tn), 'false_positive': int(fp),
            'false_negative': int(fn), 'true_positive':  int(tp),
        },
    }


def _log_metrics(metrics: dict) -> None:
    logger = logging.getLogger(__name__)
    logger.info(f"  Accuracy:  {metrics['accuracy']:.4f}")
    logger.info(f"  Precision: {metrics['precision']:.4f}")
    logger.info(f"  Recall:    {metrics['recall']:.4f}")
    logger.info(f"  F1 Score:  {metrics['f1_score']:.4f}")
    logger.info(f"  ROC-AUC:   {metrics['roc_auc']:.4f}")
    cm = metrics['confusion_matrix']
    logger.info(f"  Confusion: TN={cm['true_negative']} FP={cm['false_positive']} "
                f"FN={cm['false_negative']} TP={cm['true_positive']}")


# ---------------------------------------------------------------------------
# Quality gate
# ---------------------------------------------------------------------------

def load_criteria(criteria_file: str = DEFAULT_CRITERIA) -> dict:
    with open(criteria_file) as f:
        return yaml.safe_load(f).get('deployment_criteria', {})


def check_deployment_criteria(metrics: dict, criteria: dict) -> tuple[bool, list]:
    """
    Comprova si el model compleix els criteris de deployment_criteria.yaml.

    Returns:
        (deployment_ready, failed_checks)
    """
    logger = logging.getLogger(__name__)
    failed = []

    for name, threshold in criteria.items():
        if name.startswith('min_'):
            key = name[4:]
            if key in metrics and metrics[key] < threshold:
                failed.append(f"{key} {metrics[key]:.4f} < mínim {threshold}")
        elif name.startswith('max_'):
            key = name[4:]
            if key in metrics and metrics[key] > threshold:
                failed.append(f"{key} {metrics[key]:.4f} > màxim {threshold}")

    if not failed:
        logger.info("  ✓ Model compleix tots els criteris de desplegament")
    else:
        logger.warning("  ✗ Model NO compleix els criteris de desplegament:")
        for reason in failed:
            logger.warning(f"    - {reason}")

    return len(failed) == 0, failed


# ---------------------------------------------------------------------------
# Metadata persistence
# ---------------------------------------------------------------------------

def save_metadata(version: str, model_type: str, metrics: dict,
                  is_ready: bool, failed_checks: list,
                  metadata_dir: str = DEFAULT_METADATA_DIR,
                  filename_prefix: str = 'metadata') -> Path:
    """
    Guarda un fitxer JSON amb mètriques i el flag deployment_ready.

    Produces: metadata/{filename_prefix}_{version}.json
    """
    logger = logging.getLogger(__name__)
    out = Path(metadata_dir)
    out.mkdir(parents=True, exist_ok=True)

    payload = {
        'version':          version,
        'timestamp':        datetime.now().isoformat(),
        'model_type':       model_type,
        'metrics':          metrics,
        'deployment_ready': is_ready,
        'failed_checks':    failed_checks,
    }

    meta_file = out / f"{filename_prefix}_{version}.json"
    with open(meta_file, 'w') as f:
        json.dump(payload, f, indent=2)
    logger.info(f"  Metadades: {meta_file}")
    return meta_file


# ---------------------------------------------------------------------------
# Deployment promotion & README update
# ---------------------------------------------------------------------------

def promote_model(model_file: Path, meta_file: Path, model_key: str) -> None:
    """
    Copia el model i metadades versionats als paths de producció definits al config.
    S'executa quan deployment_ready=True.
    """
    logger = logging.getLogger(__name__)
    s = _get_settings()

    if model_key == 'nn':
        prod_model = s.resolve_path(s.NN_MODEL_PATH)
        prod_meta  = s.resolve_path(s.NN_METADATA_PATH)
    else:
        prod_model = s.resolve_path(s.PREGAME_MODEL_PATH)
        prod_meta  = s.resolve_path(s.PREGAME_METADATA_PATH)

    shutil.copy2(model_file, prod_model)
    shutil.copy2(meta_file, prod_meta)
    logger.info(f"  [PROMOTED] {model_file.name} → {prod_model.name}")
    print(f"  ✓ Promoted to production: {prod_model.name}")


def update_readme_metrics() -> None:
    """
    Llegeix els metadata de producció i actualitza la taula de mètriques del README.md.
    Requereix els markers <!-- METRICS_START --> i <!-- METRICS_END --> al fitxer.
    """
    logger = logging.getLogger(__name__)
    s = _get_settings()
    readme = s.resolve_path("README.md")
    if not readme.exists():
        logger.warning("README.md no trobat, saltant actualització de mètriques")
        return

    nn_path     = s.resolve_path(s.NN_METADATA_PATH)
    pregame_path = s.resolve_path(s.PREGAME_METADATA_PATH)

    nn_meta = json.loads(nn_path.read_text(encoding='utf-8')) if nn_path.exists() else {}
    pg_meta = json.loads(pregame_path.read_text(encoding='utf-8')) if pregame_path.exists() else {}

    def fmt_pct(val):
        return f"{val:.2%}" if isinstance(val, float) else "N/A"

    def fmt_num(val):
        return f"{val:.4f}" if isinstance(val, float) else "N/A"

    nn_v  = nn_meta.get('version', 'N/A')
    pg_v  = pg_meta.get('version', 'N/A')
    nn_m  = nn_meta.get('metrics', {})
    pg_m  = pg_meta.get('metrics', {})
    nn_ok = "✅" if nn_meta.get('deployment_ready') else "❌"
    pg_ok = "✅" if pg_meta.get('deployment_ready') else "❌"

    table = (
        f"| Metric | Neural Network ({nn_v}) | Pre-Game RF ({pg_v}) |\n"
        f"|:---|:---:|:---:|\n"
        f"| Accuracy | {fmt_pct(nn_m.get('accuracy', 'N/A'))} | {fmt_pct(pg_m.get('accuracy', 'N/A'))} |\n"
        f"| F1 Score | {fmt_num(nn_m.get('f1_score', 'N/A'))} | {fmt_num(pg_m.get('f1_score', 'N/A'))} |\n"
        f"| ROC-AUC | {fmt_num(nn_m.get('roc_auc', 'N/A'))} | {fmt_num(pg_m.get('roc_auc', 'N/A'))} |\n"
        f"| Precision | {fmt_num(nn_m.get('precision', 'N/A'))} | {fmt_num(pg_m.get('precision', 'N/A'))} |\n"
        f"| Recall | {fmt_num(nn_m.get('recall', 'N/A'))} | {fmt_num(pg_m.get('recall', 'N/A'))} |\n"
        f"| Deployment Ready | {nn_ok} | {pg_ok} |\n"
        f"\n*Last updated: {datetime.now().strftime('%Y-%m-%d')}*"
    )

    content = readme.read_text(encoding='utf-8')
    start_marker = "<!-- METRICS_START -->"
    end_marker   = "<!-- METRICS_END -->"
    start_idx = content.find(start_marker)
    end_idx   = content.find(end_marker)

    if start_idx == -1 or end_idx == -1:
        logger.warning("Markers METRICS_START/END no trobats al README.md")
        return

    new_content = (
        content[:start_idx + len(start_marker)]
        + "\n"
        + table
        + "\n"
        + content[end_idx:]
    )
    readme.write_text(new_content, encoding='utf-8')
    logger.info("  README.md mètriques actualitzades")
    print("  ✓ README.md metrics updated")


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
# 1. Train PyTorch Neural Network  (IA_LoL_NeuralNetwork.ipynb)
# ---------------------------------------------------------------------------

def train_neural_network(model_dir: str = DEFAULT_MODEL_DIR,
                         metadata_dir: str = DEFAULT_METADATA_DIR,
                         criteria_file: str = DEFAULT_CRITERIA) -> str:
    """
    Entrena la Neural Network PyTorch, l'avalua i guarda model + metadades versionades.

    Returns:
        Versió entrenada (p. ex. 'v1').
    """
    logger = logging.getLogger(__name__)
    version = get_next_version_nn(model_dir)

    print("\n" + "=" * 60)
    print(f"MODEL 2: PyTorch Neural Network  (IA_LoL_NeuralNetwork.ipynb)  →  {version}")
    print("=" * 60)

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
    y_preds_raw, y_probs_raw, y_trues_raw = [], [], []
    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            prob  = model(batch_x).cpu().numpy().flatten()
            pred  = (prob > 0.5).astype(int)
            y_probs_raw.extend(prob.tolist())
            y_preds_raw.extend(pred.tolist())
            y_trues_raw.extend(batch_y.cpu().numpy().flatten().astype(int).tolist())

    y_trues_np = np.array(y_trues_raw)
    y_preds_np = np.array(y_preds_raw)
    y_probs_np = np.array(y_probs_raw)

    metrics = evaluate_classification(y_trues_np, y_preds_np, y_probs_np)
    _log_metrics(metrics)
    print(f"\nTest accuracy: {metrics['accuracy']:.2%}  |  F1: {metrics['f1_score']:.4f}  "
          f"|  ROC-AUC: {metrics['roc_auc']:.4f}")

    # Quality gate
    logger.info("\n[Quality gate]")
    criteria = load_criteria(criteria_file)
    is_ready, failed = check_deployment_criteria(metrics, criteria)

    # --- Save model ---
    model_file = Path(model_dir) / f"neural_net_{version}.pth"
    model_file.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        'model_state_dict': model.state_dict(),
        'input_size': len(NN_FEATURES),
        'feature_names': NN_FEATURES,
        'scaler': scaler,
        'encoders': {
            'team': le_team, 'player': le_player, 'champion': le_champion,
            'side': le_side, 'position': le_position
        }
    }, model_file)
    logger.info(f"  Model: {model_file}")

    # Save metadata
    meta_file = save_metadata(version, 'pytorch_neural_network', metrics, is_ready, failed,
                  metadata_dir=metadata_dir, filename_prefix='nn_metadata')

    if is_ready:
        promote_model(model_file, meta_file, 'nn')

    print(f"deployment_ready={is_ready}")
    return version


# ---------------------------------------------------------------------------
# 3. Train Pre-Game RandomForest  (IA_LoL_Prediccion_Pre_Game.ipynb)
# ---------------------------------------------------------------------------

def train_pregame_rf(model_dir: str = DEFAULT_MODEL_DIR,
                     metadata_dir: str = DEFAULT_METADATA_DIR,
                     criteria_file: str = DEFAULT_CRITERIA) -> str:
    """
    Entrena el Pre-Game RandomForest, l'avalua i guarda model + metadades versionades.

    Returns:
        Versió entrenada (p. ex. 'v1').
    """
    logger = logging.getLogger(__name__)
    version = get_next_version_pregame(model_dir)

    print("\n" + "=" * 60)
    print(f"MODEL 3: RandomForest Pre-Game  (IA_LoL_Prediccion_Pre_Game.ipynb)  →  {version}")
    print("=" * 60)

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

    # --- Evaluate ---
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    metrics = evaluate_classification(y_test, y_pred, y_prob)
    _log_metrics(metrics)

    # Quality gate
    logger.info("\n[Quality gate]")
    criteria = load_criteria(criteria_file)
    is_ready, failed = check_deployment_criteria(metrics, criteria)

    # --- Save model + encoders + lookup tables ---
    model_file = Path(model_dir) / f"pregame_rf_{version}.pkl"
    model_file.parent.mkdir(parents=True, exist_ok=True)
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
    }, model_file)
    logger.info(f"  Model: {model_file}")

    # Save metadata
    meta_file = save_metadata(version, 'random_forest_pregame', metrics, is_ready, failed,
                  metadata_dir=metadata_dir, filename_prefix='pregame_metadata')

    if is_ready:
        promote_model(model_file, meta_file, 'pregame')

    print(f"Train accuracy: {accuracy_score(y_train, model.predict(X_train)):.2%}")
    print(f"Test  accuracy: {metrics['accuracy']:.2%}  |  F1: {metrics['f1_score']:.4f}  "
          f"|  ROC-AUC: {metrics['roc_auc']:.4f}  |  deployment_ready={is_ready}")
    return version


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    nn_ver      = train_neural_network()
    pregame_ver = train_pregame_rf()

    update_readme_metrics()

    print("\n" + "=" * 60)
    print("ENTRENAMENT COMPLETAT")
    print(f"  NN      → models/neural_net_{nn_ver}.pth      metadata/nn_metadata_{nn_ver}.json")
    print(f"  Pregame → models/pregame_rf_{pregame_ver}.pkl metadata/pregame_metadata_{pregame_ver}.json")
    print("=" * 60)

