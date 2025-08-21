from relbench.datasets import get_dataset
from relbench.tasks import get_task
import lightgbm as lgbm

# Download rel-trial dataset
dataset = get_dataset("rel-trial", download=True)

# Load a specific task from rel-trial
task_name = "study-outcome"
task = get_task("rel-trial", task_name, download=True)

# Use the robust preprocessing function
def preprocess_relbench_table(table, has_label=True):
    df = table.df.copy()
    # Convert timestamp if needed or drop
    df = df.drop(columns=["timestamp"])
    if has_label:
        X = df.drop(columns=["outcome"])
        y = df["outcome"]
        return X, y
    else:
        return df


# Getting train, validation, test tables
train_table = task.get_table("train")
val_table = task.get_table("val")
test_table = task.get_table("test")

X_train, y_train = preprocess_relbench_table(train_table, has_label=True)
X_val, y_val = preprocess_relbench_table(val_table, has_label=True)
X_test = preprocess_relbench_table(test_table, has_label=False)

# Initialize and train LightGBM model
model = lgbm.LGBMClassifier()
model.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    callbacks=[lgbm.early_stopping(stopping_rounds=10)]
)

# Predict and evaluate
test_preds = model.predict_proba(X_test)[:, 1]
score = task.evaluate(test_preds)
print(f"Evaluation score: {score}")
