from relbench.datasets import get_dataset
from relbench.tasks import get_task
import lightgbm as lgbm
import pandas as pd

# Download dataset (if not present)
dataset = get_dataset("rel-f1", download=True)

# Get the task object
task = get_task("rel-f1", "driver-top3", download=True)

def drop_temporal(table, has_label=True):
    df = table.df
    temporal_cols = [col for col in df.columns if "time" in col or "date" in col or "timestamp" in col]
    if has_label:
        non_label_cols = [c for c in df.columns if c != "qualifying" and c not in temporal_cols]
        return df[non_label_cols], df["qualifying"]
    else:
        # For test, just drop temporal columns, no target
        non_label_cols = [c for c in df.columns if c not in temporal_cols]
        return df[non_label_cols]

# Obtain splits via get_table
train_table = task.get_table("train")
val_table = task.get_table("val")
test_table = task.get_table("test")

print("Train table columns:", train_table.df.columns)
print("Validation table columns:", val_table.df.columns)
print("Test table columns:", test_table.df.columns)
print(lgbm.__version__)

# Prepare features and targets
X_train, y_train = drop_temporal(train_table, has_label=True)
X_valid, y_valid = drop_temporal(val_table, has_label=True)
X_test = drop_temporal(test_table, has_label=False)

# Train LightGBM classifier
model = lgbm.LGBMClassifier()
model.fit(
    X_train,
    y_train,
    eval_set=[(X_valid, y_valid)],
    callbacks=[lgbm.early_stopping(stopping_rounds=10)]
)

test_preds = model.predict_proba(X_test)[:, 1]
score = task.evaluate(test_preds)
print("Static AUROC (non-temporal):", score)
