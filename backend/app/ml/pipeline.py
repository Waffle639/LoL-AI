"""
Pipeline ETL bàsic (Sessió 4)

Carrega CSV, fa validacions bàsiques, i guarda en format Parquet.
"""

import pandas as pd
from pathlib import Path
import logging
import sys
import numpy as np
from sklearn.model_selection import train_test_split

from app.core.config import setup_logging

logger = logging.getLogger(__name__)

RANDOM_SEED = 42
TRAIN_RATIO = 0.60
VAL_RATIO = 0.20
PROD_RATIO = 0.20

DEFAULT_INPUT = "data/2024_LoL_esports_match_data_from_OraclesElixir1.csv"


def load_csv(file_path: str) -> pd.DataFrame:
    """Carrega un fitxer CSV i mostra informació bàsica."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Fitxer no trobat: {file_path}")

    logger.info(f"Carregant dades de: {file_path}")
    df = pd.read_csv(file_path, sep=';')
    logger.info(f"Dimensions: {df.shape[0]} files x {df.shape[1]} columnes")
    logger.info(f"Columnes: {list(df.columns)}")

    return df


def validate_basic(df: pd.DataFrame) -> bool:
    """Validació bàsica: valors faltants i DataFrame buit."""
    is_valid = True

    # Check missing values
    missing = df.isnull().sum()
    missing_cols = missing[missing > 0]

    if len(missing_cols) > 0:
        logger.warning("Valors faltants detectats:")
        for col, count in missing_cols.items():
            pct = (count / len(df)) * 100
            logger.warning(f"  {col}: {count} ({pct:.1f}%)")
    else:
        logger.info("Cap valor faltant detectat")

    if df.empty:
        logger.error("El DataFrame està buit!")
        is_valid = False

    return is_valid


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalitza els noms de columnes i converteix el target.

    - Renombra: thalch -> thalach, num -> target
    - Elimina: id, dataset
    - Converteix target de multi-classe (0-4) a binari (0 vs 1+)
    """
    df = df.copy()

    # Renombrar columnes amb noms alternatius
    df = df.rename(columns={'thalch': 'thalach', 'num': 'target'})

    # Eliminar columnes de metadades
    cols_to_drop = [c for c in ['id', 'dataset'] if c in df.columns]
    if cols_to_drop:
        logger.info(f"Eliminant columnes de metadades: {cols_to_drop}")
        df = df.drop(columns=cols_to_drop)

    # Convertir target multi-classe a binari (0 = no malaltia, 1 = malaltia)
    if 'target' in df.columns:
        original_values = sorted(df['target'].unique())
        if max(original_values) > 1:
            df['target'] = (df['target'] > 0).astype(int)
            logger.info(f"Target convertit de {original_values} a binari [0, 1]")

    logger.info(f"Columnes normalitzades: {list(df.columns)}")
    return df


def create_splits(df: pd.DataFrame) -> tuple:
    """
    Crea splits estratificats 60/20/20.

    Estratègia en dos passos:
    1. Separar training (60%) de la resta (40%)
    2. Dividir la resta en validation (50% de 40% = 20%) i production (50% de 40% = 20%)

    Returns:
        tuple: (train_df, val_df, prod_df)
    """
    stratify_col = 'target' if 'target' in df.columns else None
    stratify = df[stratify_col] if stratify_col else None

    # Pas 1: Separar training (60%)
    train_df, rest_df = train_test_split(
        df,
        test_size=1 - TRAIN_RATIO,
        random_state=RANDOM_SEED,
        stratify=stratify
    )

    # Pas 2: Dividir la resta en validation (50%) i production (50%)
    # 50% de 40% = 20% del total
    stratify_rest = rest_df[stratify_col] if stratify_col else None

    val_df, prod_df = train_test_split(
        rest_df,
        test_size=0.5,
        random_state=RANDOM_SEED,
        stratify=stratify_rest
    )

    total = len(df)
    logger.info(f"Splits creats:")
    logger.info(f"  Training:   {len(train_df):4d} files ({len(train_df)/total:.1%})")
    logger.info(f"  Validation: {len(val_df):4d} files ({len(val_df)/total:.1%})")
    logger.info(f"  Production: {len(prod_df):4d} files ({len(prod_df)/total:.1%})")

    return train_df, val_df, prod_df


def save_splits(train_df: pd.DataFrame, val_df: pd.DataFrame, prod_df: pd.DataFrame,
                output_dir: str = "data") -> None:
    """Guarda els tres splits com a fitxers Parquet."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for name, df in [('training_set', train_df), ('validation_set', val_df), ('production_set', prod_df)]:
        path = out / f'{name}.parquet'
        df.to_parquet(path, index=False)
        size_kb = path.stat().st_size / 1024
        logger.info(f"  Guardat: {path} ({size_kb:.1f} KB, {len(df)} files)")
    
def run_pipeline(
    input_file: str = DEFAULT_INPUT,
) -> None:
    """Executa el pipeline ETL bàsic."""
    logger.info("=" * 50)
    logger.info("INICIANT PIPELINE ETL")
    logger.info("=" * 50)

    # Pas 1: Carregar
    logger.info("\n[Pas 1/4] Carregant dades...")
    df = load_csv(input_file)

    # Pas 2: Normalitzar columnes
    logger.info("\n[Pas 2/4] Normalitzant columnes...")
    df = normalize_columns(df)

    # Pas 3: Validar
    logger.info("\n[Pas 3/4] Validant...")
    is_valid = validate_basic(df)
    if not is_valid:
        logger.error("Validació fallida. Aturant pipeline.")
        sys.exit(1)

    # Pas 4: Crear splits i guardar
    logger.info("\n[Pas 4/4] Creant splits 60/20/20...")
    train_df, val_df, prod_df = create_splits(df)
    save_splits(train_df, val_df, prod_df)

    logger.info("=" * 50)
    logger.info("PIPELINE COMPLETAT")
    logger.info("=" * 50)


if __name__ == "__main__":
    setup_logging(log_file="logs/pipeline.log")
    run_pipeline()