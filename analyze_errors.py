import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from feature_extractor import extract_features

DATA_PATH = "data/phishing_dataset.csv"
MODEL_PATH = "model/phishing_model.pkl"
OUTPUT_PATH = "data/analisis_kesalahan_model.csv"


def main():
    df = pd.read_csv(DATA_PATH)

    df = df.rename(columns={
        "URL": "url",
        "label": "label"
    })

    df = df.dropna(subset=["url", "label"])

    df["label"] = (
        df["label"]
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({
            "benign": 0,
            "legitimate": 0,
            "good": 0,
            "phishing": 1,
            "malicious": 1,
            "bad": 1
        })
    )

    df = df[df["label"].isin([0, 1])]
    df["label"] = df["label"].astype(int)

    features = df["url"].apply(extract_features)
    X = pd.DataFrame(list(features))
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = joblib.load(MODEL_PATH)
    y_pred = model.predict(X_test)

    results = X_test.copy()
    results["actual_label"] = y_test.values
    results["predicted_label"] = y_pred
    results["url"] = df.loc[y_test.index, "url"].values

    false_positive = results[
        (results["actual_label"] == 0) &
        (results["predicted_label"] == 1)
    ]

    false_negative = results[
        (results["actual_label"] == 1) &
        (results["predicted_label"] == 0)
    ]

    print("Jumlah False Positive:", len(false_positive))
    print("Jumlah False Negative:", len(false_negative))

    print("\nContoh False Positive (Legitimate diprediksi Phishing):")
    print(false_positive[["url", "actual_label", "predicted_label"]].head(10))

    print("\nContoh False Negative (Phishing diprediksi Legitimate):")
    print(false_negative[["url", "actual_label", "predicted_label"]].head(10))

    analysis = pd.concat([
        false_positive.assign(error_type="False Positive"),
        false_negative.assign(error_type="False Negative")
    ])

    analysis.to_csv(OUTPUT_PATH, index=False)

    print("\nHasil analisis disimpan ke:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()