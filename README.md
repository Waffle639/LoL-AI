<div align="center">
  <img width="400" alt="League of Legends Logo" src="https://github.com/user-attachments/assets/78d634ba-8997-4168-bf9e-4bb424d4b8f7" />
</div>

# League of Legends Esports 2024 - AI Match Prediction

A machine learning project that predicts League of Legends professional match outcomes based on in-game statistics using 2024 esports data.

## Project Overview

This project analyzes professional League of Legends matches from 2024 and builds a classification model to predict whether a player/team will win or lose based on in-game performance metrics.

## What Does It Do?

The AI model learns patterns from thousands of professional matches and can predict match outcomes using statistics like:
- Kills, Deaths, Assists (KDA)
- Team performance (team kills/deaths)
- Objective control (Dragons, Barons, Elders)
- Map control (Towers destroyed)
- Gold earned


## 🔧 Technologies Used

<div align="center">
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" width="50" alt="Python"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/pandas/pandas-original.svg" width="50" alt="Pandas"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/numpy/numpy-original.svg" width="50" alt="NumPy"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/matplotlib/matplotlib-original.svg" width="50" alt="Matplotlib"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/scikitlearn/scikitlearn-original.svg" width="50" alt="scikit-learn"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/jupyter/jupyter-original.svg" width="50" alt="Jupyter"/>
</div>

<br>

- **Python 3.13+** - Programming language
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computations
- **matplotlib & seaborn** - Data visualization
- **scikit-learn** - Machine learning (SGDClassifier model)
- **Jupyter Notebook** - Interactive development environment

## Dataset

- **Source**: [League of Legends 2024 Competitive Game Dataset (Kaggle)](https://www.kaggle.com/datasets/barthetur/league-of-legends-2024-competitive-game-dataset)
- **Content**: Player-level statistics from professional League of Legends matches
- **Key Features**: 14 important columns selected from 140+ available columns

## How to Run

1. **Install Dependencies**
   ```bash
   pip install pandas numpy matplotlib seaborn scikit-learn
   ```

2. **Open the Notebook**
   ```bash
   jupyter notebook IA_LoL.ipynb
   ```

3. **Run All Cells**
   - Execute cells sequentially from top to bottom
   - The notebook will load data, train the model, and make predictions

## Notebook Sections

### 1. **Data Loading**
- Imports the CSV file with 2024 esports match data
- Displays basic dataset information (dimensions, data types)

### 2. **Data Cleaning**
- Selects 14 most important features:
  - Individual stats: `kills`, `deaths`, `assists`
  - Team stats: `teamkills`, `teamdeaths`
  - Objectives: `dragons`, `opp_dragons`, `elders`, `opp_elders`, `barons`, `opp_barons`
  - Map control: `towers`, `opp_towers`
  - Economy: `totalgold`
  - Target: `result` (0 = defeat, 1 = victory)
- Replaces missing values (NaN) with 0

### 3. **Correlation Matrix**
- Visualizes relationships between all features
- Shows which features correlate positively/negatively with victory
- **Key insights**:
  - Own towers/objectives → Positive correlation with victory
  - Enemy towers/objectives → Negative correlation with victory

### 4. **Machine Learning Preparation**
- Splits data into training (70%) and test (30%) sets
- Uses stratification to maintain class balance (50/50 wins/losses)
- Displays distribution of victories and defeats in each set

### 5. **Model Training**
- **Algorithm**: SGDClassifier (Stochastic Gradient Descent)
- **Features**: 
  - Loss function: `log_loss` (logistic regression)
  - Regularization: L2 penalty (alpha=0.0001)
  - Learning rate: constant (eta0=0.001)
- **Data preprocessing**: StandardScaler to normalize features
- **Evaluation metrics**:
  - Accuracy (train and test)
  - R² (Coefficient of Determination)
  - MSE/RMSE (Mean Squared Error)
  - MAE (Mean Absolute Error)

### 6. **Confusion Matrix**
- Visual representation of model predictions
- Shows:
  - True Positives: Victories correctly predicted
  - True Negatives: Defeats correctly predicted
  - False Positives: Defeats predicted as victories
  - False Negatives: Victories predicted as defeats
- Displays Precision, Recall, and F1-Score

### 7. **New Predictions**
- Tests the model with 5 example scenarios:
  1. **Dominant team**: High towers, objectives, gold → Predicts Victory
  2. **Losing team**: Low towers, no objectives → Predicts Defeat
  3. **Balanced match**: Even stats → Uncertain prediction
  4. **Extreme advantage**: Overwhelming stats → Strong Victory prediction
  5. **Extreme disadvantage**: Poor stats → Strong Defeat prediction

## 📈 Model Performance

The model achieves:
- **High accuracy** on both training and test sets
- **Balanced performance** (similar precision/recall for both classes)
- **Reliable predictions** for matches with clear stat advantages

