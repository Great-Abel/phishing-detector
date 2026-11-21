import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
from feature_extractor import extract_features

DATA_PATH = "data/phishing_dataset.csv"
MODEL_PATH = "model/phishing_model.pkl"


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

    print("Total data:", len(df))
    print("\nDistribusi label:")
    print(df["label"].value_counts())

    print("\nMengekstrak fitur URL...")

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

    print("\nJumlah data training:", len(X_train))
    print("Jumlah data testing :", len(X_test))

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        random_state=42,
        n_jobs=-1
    )

    print("\nMelatih model...")
    model.fit(X_train, y_train)

    print("Menguji model...")
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    print("\n==============================")
    print("        HASIL EVALUASI        ")
    print("==============================")
    print(f"Accuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1-Score  : {f1:.4f}")

    print("\nConfusion Matrix:")
    print(cm)

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    joblib.dump(model, MODEL_PATH)

    print("\nModel berhasil disimpan ke:")
    print(MODEL_PATH)


if __name__ == "__main__":
    main()