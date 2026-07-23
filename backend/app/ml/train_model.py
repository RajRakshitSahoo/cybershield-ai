"""
Trains the phishing-detection RandomForest model.

Note on data: this script generates a large, feature-realistic synthetic
dataset (rule-driven "phishing-like" vs "legitimate-like" URL patterns with
randomized noise) rather than shipping a scraped third-party dataset in the
repo. This keeps the project self-contained and license-clean out of the
box. For production use, swap `build_dataset()` to load a real labeled
corpus (e.g. PhishTank / UCI Phishing Websites / OpenPhish exports) with the
same column layout -- the training + evaluation code below does not change.

Run with:  python -m app.ml.train_model
"""
import json
import os
import random

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, roc_curve,
)
from sklearn.model_selection import train_test_split

from app.ml.feature_extraction import FEATURE_NAMES, extract_features

random.seed(42)
np.random.seed(42)

MODEL_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, "model.joblib")
METRICS_PATH = os.path.join(MODEL_DIR, "metrics.json")

LEGIT_DOMAINS = [
    "google.com", "wikipedia.org", "github.com", "amazon.com", "microsoft.com",
    "apple.com", "nytimes.com", "bbc.co.uk", "cloudflare.com", "stackoverflow.com",
    "linkedin.com", "reddit.com", "spotify.com", "dropbox.com", "notion.so",
]
PHISH_PATTERNS = [
    "paypal-secure-{n}.xyz", "verify-account-{n}.top", "login-microsoft-{n}.tk",
    "apple-id-confirm-{n}.click", "bank-of-america-alert-{n}.ga",
    "amazon-billing-{n}.gq", "secure-update-{n}.cf", "netflix-account-{n}.loan",
    "webscr-paypal-{n}.review", "signin-{n}.zip",
]


def _random_legit_url():
    domain = random.choice(LEGIT_DOMAINS)
    path = random.choice(["", "/", "/about", "/products/item", "/blog/post-1", "/docs"])
    return f"https://www.{domain}{path}", random.randint(365, 9000)


def _random_phish_url():
    pattern = random.choice(PHISH_PATTERNS)
    n = random.randint(1, 9999)
    host = pattern.format(n=n)
    use_ip = random.random() < 0.15
    if use_ip:
        host = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
    scheme = "http" if random.random() < 0.4 else "https"
    path = random.choice(["/login", "/secure/update", "/verify?user=1", "/", "/account/confirm"])
    return f"{scheme}://{host}{path}", random.randint(0, 60)


def build_dataset(n_per_class: int = 1500) -> pd.DataFrame:
    rows = []
    for _ in range(n_per_class):
        url, age = _random_legit_url()
        redirects = random.choice([0, 0, 0, 1])
        f = extract_features(url, domain_age_days=age, num_redirects=redirects)
        f["label"] = 0  # legitimate
        rows.append(f)
    for _ in range(n_per_class):
        url, age = _random_phish_url()
        redirects = random.choice([0, 1, 2, 3])
        f = extract_features(url, domain_age_days=age, num_redirects=redirects)
        f["label"] = 1  # phishing
        rows.append(f)
    df = pd.DataFrame(rows)
    return df.sample(frac=1, random_state=42).reset_index(drop=True)


def train():
    df = build_dataset()
    X = df[FEATURE_NAMES].values
    y = df["label"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=300, max_depth=12, min_samples_leaf=2,
        random_state=42, n_jobs=-1, class_weight="balanced",
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_prob)

    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall": round(recall_score(y_test, y_pred), 4),
        "f1_score": round(f1_score(y_test, y_pred), 4),
        "roc_auc": round(roc_auc_score(y_test, y_prob), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "roc_curve": {"fpr": fpr.tolist()[::5], "tpr": tpr.tolist()[::5]},
        "feature_importances": dict(
            sorted(zip(FEATURE_NAMES, model.feature_importances_.tolist()),
                   key=lambda kv: kv[1], reverse=True)
        ),
        "n_train": len(X_train),
        "n_test": len(X_test),
    }

    joblib.dump(model, MODEL_PATH)
    with open(METRICS_PATH, "w") as fh:
        json.dump(metrics, fh, indent=2)

    print("Model trained. Metrics:")
    print(json.dumps(metrics, indent=2))
    return model, metrics


if __name__ == "__main__":
    train()
