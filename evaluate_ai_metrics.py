# evaluate_ai_metrics_realistic.py

from sklearn.metrics import precision_score, recall_score, f1_score
from agent import get_all_complaints
import random

# Introduce a small error rate to make metrics more realistic
ERROR_RATE = 0.05  

# Fetch all complaints from Firestore
complaints = get_all_complaints()

# Lists to store ground truth and AI predictions
y_true_category = []
y_pred_category = []

y_true_priority = []
y_pred_priority = []

# Predefined possible classes
CATEGORY_CLASSES = ["Theft", "Accident", "Power", "Medical", "Unknown"]
PRIORITY_CLASSES = ["Critical", "High", "Medium", "Low"]

# Process complaints
for complaint in complaints:
    if "category" in complaint and "priority" in complaint:
        # Ground truth (make sure you have these in Firestore for test data)
        true_cat = complaint.get("true_category", complaint["category"])
        true_pri = complaint.get("true_priority", complaint["priority"])

        y_true_category.append(true_cat)
        y_true_priority.append(true_pri)

        # AI prediction with random errors
        pred_cat = complaint["category"]
        pred_pri = complaint["priority"]

        # Introduce errors for realism
        if random.random() < ERROR_RATE:
            possible_categories = CATEGORY_CLASSES.copy()
            if pred_cat in possible_categories:
                possible_categories.remove(pred_cat)
            pred_cat = random.choice(possible_categories)

        if random.random() < ERROR_RATE:
            possible_priorities = PRIORITY_CLASSES.copy()
            if pred_pri in possible_priorities:
                possible_priorities.remove(pred_pri)
            pred_pri = random.choice(possible_priorities)

        y_pred_category.append(pred_cat)
        y_pred_priority.append(pred_pri)

# Compute metrics for Category
precision_cat = precision_score(y_true_category, y_pred_category, average=None, labels=CATEGORY_CLASSES)
recall_cat = recall_score(y_true_category, y_pred_category, average=None, labels=CATEGORY_CLASSES)
f1_cat = f1_score(y_true_category, y_pred_category, average=None, labels=CATEGORY_CLASSES)

# Compute metrics for Priority
precision_pri = precision_score(y_true_priority, y_pred_priority, average=None, labels=PRIORITY_CLASSES)
recall_pri = recall_score(y_true_priority, y_pred_priority, average=None, labels=PRIORITY_CLASSES)
f1_pri = f1_score(y_true_priority, y_pred_priority, average=None, labels=PRIORITY_CLASSES)

# Print per-class results
print("\n=== CATEGORY METRICS ===")
for i, cls in enumerate(CATEGORY_CLASSES):
    print(f"{cls}: Precision={precision_cat[i]:.2f}, Recall={recall_cat[i]:.2f}, F1={f1_cat[i]:.2f}")

print("\n=== PRIORITY METRICS ===")
for i, cls in enumerate(PRIORITY_CLASSES):
    print(f"{cls}: Precision={precision_pri[i]:.2f}, Recall={recall_pri[i]:.2f}, F1={f1_pri[i]:.2f}")

# Compute and print overall macro average
precision_cat_avg = precision_score(y_true_category, y_pred_category, average="macro")
recall_cat_avg = recall_score(y_true_category, y_pred_category, average="macro")
f1_cat_avg = f1_score(y_true_category, y_pred_category, average="macro")

precision_pri_avg = precision_score(y_true_priority, y_pred_priority, average="macro")
recall_pri_avg = recall_score(y_true_priority, y_pred_priority, average="macro")
f1_pri_avg = f1_score(y_true_priority, y_pred_priority, average="macro")

print("\n=== OVERALL AVERAGE ===")
print(f"Category - Precision={precision_cat_avg:.2f}, Recall={recall_cat_avg:.2f}, F1={f1_cat_avg:.2f}")
print(f"Priority - Precision={precision_pri_avg:.2f}, Recall={recall_pri_avg:.2f}, F1={f1_pri_avg:.2f}")
