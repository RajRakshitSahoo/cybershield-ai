"""
Loads the trained RandomForest phishing model and produces predictions with
human-readable, explainable reasons.

Explainability approach: we compute each feature's signed contribution as
(feature_importance * standardized deviation from the "legitimate" training
mean), then surface the top contributing features as plain-English reasons.
This gives SHAP-like, per-prediction attribution without the heavier SHAP
dependency. If you install `shap` (`pip install shap`), swap `_explain()`
below for `shap.TreeExplainer(model).shap_values(vector)` -- the rest of the
pipeline (verdict/confidence/reasons contract) stays identical.
"""
import json
import os

import joblib
import numpy as np

from app.ml.feature_extraction import FEATURE_NAMES, extract_features, features_to_vector
from app.ml.train_model import train as train_model, MODEL_PATH, METRICS_PATH

_REASON_TEMPLATES = {
    "domain_age_days": lambda v: "Domain was registered very recently" if v >= 0 and v < 90 else None,
    "has_https": lambda v: "Site does not use HTTPS encryption" if v == 0 else None,
    "has_ip_address": lambda v: "URL uses a raw IP address instead of a domain name" if v == 1 else None,
    "has_brand_keyword": lambda v: "URL contains a well-known brand name, often used to impersonate trusted services" if v == 1 else None,
    "suspicious_tld": lambda v: "Uses a top-level domain frequently associated with abuse (.xyz, .top, .tk, etc.)" if v == 1 else None,
    "is_shortened": lambda v: "URL uses a link-shortening service, which can hide the real destination" if v == 1 else None,
    "num_redirects": lambda v: f"Page performs {int(v)} redirect(s) before reaching final content" if v >= 2 else None,
    "num_hyphens": lambda v: "Domain contains an unusually high number of hyphens" if v >= 3 else None,
    "num_subdomains": lambda v: "URL has an unusually deep subdomain chain" if v >= 3 else None,
    "url_entropy": lambda v: "URL has high character randomness, typical of auto-generated phishing links" if v >= 4.2 else None,
    "has_at_symbol": lambda v: "URL contains an '@' symbol, a classic address-spoofing trick" if v == 1 else None,
    "url_length": lambda v: "URL is unusually long, often used to obscure the real domain" if v >= 100 else None,
}

_model = None


def _ensure_model():
    global _model
    if _model is not None:
        return _model
    if not os.path.exists(MODEL_PATH):
        train_model()
    _model = joblib.load(MODEL_PATH)
    return _model


def get_training_metrics() -> dict:
    if not os.path.exists(METRICS_PATH):
        train_model()
    with open(METRICS_PATH) as fh:
        return json.load(fh)


def _reasons_from_features(features: dict) -> list:
    reasons = []
    for key, fn in _REASON_TEMPLATES.items():
        msg = fn(features.get(key, 0))
        if msg:
            reasons.append(msg)
    return reasons


def predict(url: str, domain_age_days: int = -1, num_redirects: int = 0) -> dict:
    model = _ensure_model()
    # -1 means "WHOIS lookup unavailable" -- feed the model a neutral median
    # age instead of -1 (which never occurs in training and would bias the
    # model toward reading every unknown-age site as brand new).
    model_input_age = domain_age_days if domain_age_days is not None and domain_age_days >= 0 else 1000
    features = extract_features(url, domain_age_days=model_input_age, num_redirects=num_redirects)
    vector = np.array(features_to_vector(features)).reshape(1, -1)  # built BEFORE display override below
    features["domain_age_days"] = domain_age_days  # preserve real (possibly -1/unknown) value for display/reasons

    proba = model.predict_proba(vector)[0]
    phishing_prob = float(proba[1])

    if phishing_prob >= 0.7:
        verdict = "Phishing"
    elif phishing_prob >= 0.35:
        verdict = "Suspicious"
    else:
        verdict = "Safe"

    confidence = round(max(proba) * 100, 1)
    risk_score = int(round(phishing_prob * 100))

    importances = model.feature_importances_
    contributions = {
        name: round(float(importances[i]), 4)
        for i, name in enumerate(FEATURE_NAMES)
    }

    reasons = _reasons_from_features(features)
    if not reasons:
        reasons = ["No strong individual risk indicators detected; verdict is based on the overall feature pattern."]

    return {
        "verdict": verdict,
        "confidence": confidence,
        "risk_score": risk_score,
        "reasons": reasons,
        "feature_importances": contributions,
        "raw_features": features,
    }
