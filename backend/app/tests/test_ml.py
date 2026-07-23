"""Unit tests for critical backend logic: feature extraction + ML prediction."""
from app.ml.feature_extraction import extract_features
from app.ml import ml_service


def test_extract_features_basic_shape():
    f = extract_features("https://www.example.com/")
    assert f["has_https"] == 1
    assert f["num_dots"] == 2


def test_extract_features_detects_ip_and_at_symbol():
    f = extract_features("http://192.168.0.1/@evil.com/login")
    assert f["has_ip_address"] == 1
    assert f["has_at_symbol"] == 1


def test_extract_features_detects_suspicious_tld():
    f = extract_features("http://free-gift-card.xyz/claim")
    assert f["suspicious_tld"] == 1


def test_predict_flags_classic_phishing_pattern():
    result = ml_service.predict(
        "http://paypal-secure-login-verify.xyz/account/confirm",
        domain_age_days=3,
        num_redirects=4,
    )
    assert result["verdict"] in ("Phishing", "Suspicious")
    assert result["risk_score"] > 50
    assert len(result["reasons"]) > 0


def test_predict_treats_established_domain_as_safe():
    result = ml_service.predict("https://www.wikipedia.org/", domain_age_days=8000)
    assert result["verdict"] == "Safe"
    assert result["risk_score"] < 50


def test_predict_unknown_age_does_not_bias_toward_phishing():
    """A -1 (WHOIS unavailable) sentinel must not be fed raw into the model."""
    result = ml_service.predict("https://www.wikipedia.org/")
    assert result["verdict"] == "Safe"
