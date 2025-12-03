<div align="center">
  <img width="400" alt="image" src="https://github.com/user-attachments/assets/7ba83f6d-afd9-4650-9b2d-4c2c87e7f01e" />
</div>




# League of Legends Esports 2024 - AI Match Prediction

Machine learning project with two prediction models for League of Legends professional matches using 2024 esports data.

## Three Prediction Models

### Pre-Game Prediction - Random Forest (`IA_LoL_Prediccion_Pre_Game.ipynb`)
Predicts match winner **before** the game starts using historical data:
- Team winrates
- Player performance & KDA
- Champion winrates  
- Player-champion mastery
- Full 5v5 team composition analysis

**Algorithm**: RandomForestClassifier (200 trees, max_depth 15)

### Pre-Game Prediction - Neural Network (`IA_LoL_NeuralNetwork.ipynb`)
Same pre-game prediction using deep learning:
- PyTorch neural network (24 → 64 → 32 → 1)
- Selective feature scaling (numeric features only)
- Binary cross-entropy loss with Adam optimizer
- Dropout regularization (0.2) to prevent overfitting

**Algorithm**: PyTorch Neural Network

### In-Game Prediction (`IA_LoL.ipynb`)
Predicts match winner based on in-game statistics:
- Kills, Deaths, Assists
- Team performance
- Objective control (Dragons, Barons, Elders)
- Map control (Towers)
- Gold earned

**Algorithm**: SGDClassifier


## Technologies Used

<div align="center">
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" width="50" alt="Python"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/pandas/pandas-original.svg" width="50" alt="Pandas"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/numpy/numpy-original.svg" width="50" alt="NumPy"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/matplotlib/matplotlib-original.svg" width="50" alt="Matplotlib"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/scikitlearn/scikitlearn-original.svg" width="50" alt="scikit-learn"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/pytorch/pytorch-original.svg" width="50" alt="PyTorch"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/jupyter/jupyter-original.svg" width="50" alt="Jupyter"/>
</div>

<br>

- **Python 3.13+** - Programming language
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computations
- **matplotlib & seaborn** - Data visualization
- **scikit-learn** - Machine learning (RandomForestClassifier, SGDClassifier, LabelEncoder, StandardScaler)
- **PyTorch** - Deep learning framework for neural networks
## Datasetotebook** - Interactive development environment

## 📊 Dataset

- **Source**: [League of Legends 2024 Competitive Game Dataset (Kaggle)](https://www.kaggle.com/datasets/barthetur/league-of-legends-2024-competitive-game-dataset)
- **Size**: 12,276 player records
- **Teams**: 253 professional teams
- **Players**: 1,305 unique players
- **Champions**: 147 different champions

## How to Run

**Install Dependencies**
```bash
pip install pandas numpy matplotlib seaborn scikit-learn torch
```

**Open Notebooks**
```bash
# Pre-game prediction (Random Forest)
jupyter notebook IA_LoL_Prediccion_Pre_Game.ipynb

# Pre-game prediction (Neural Network)
jupyter notebook IA_LoL_NeuralNetwork.ipynb

# In-game prediction
jupyter notebook IA_LoL.ipynb
```

## Real Match Example

**G2 Esports vs MAD Lions KOI** (Game ID: LOLTMNT05_13119)

```
G2 ESPORTS (Blue side)          MAD LIONS KOI (Red side)
BrokenBlade - K'Sante (top)     Myrwn - Gwen (top)
Yike - Vi (jng)                 Elyoya - Viego (jng)
Caps - Azir (mid)               Fresskowy - Neeko (mid)
Hans Sama - Varus (bot)         Supa - Ashe (bot)
Mikyx - Zyra (sup)              Alvaro - Renata Glasc (sup)

Model Prediction: G2 77.8% | MAD 22.2%
Actual Winner: G2 Esports ✓
```

## In-Game Prediction Notebook Sections

1. Data Loading & Cleaning
2. Correlation Matrix (feature analysis)
3. Train/Test Split (70/30)
4. SGDClassifier Training
5. Confusion Matrix & Metrics
6. Example Predictions

## Pre-Game Prediction Notebook Sections

1. Load & Explore Data
2. Create Historical Features (team winrate, player KDA, champion winrate, player-champion mastery)
3. Correlation Matrix (team_winrate: +0.49 strongest)
4. Encode Variables & Prepare Features (10 total features)
5. Train RandomForest Model (80/20 split)
6. Confusion Matrix & Evaluation
7. Team vs Team Prediction Function
8. Real Match Recreation (G2 vs MAD Lions)

