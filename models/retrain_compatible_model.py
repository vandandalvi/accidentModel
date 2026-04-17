import pickle
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "Database" / "6accident_data.csv"
MODEL_PATH = ROOT / "models" / "random_forest_model.pkl"

INPUT_FEATURES = [
    "age_band_of_driver",
    "vehicle_type",
    "age_of_vehicle",
    "weather_conditions",
    "day_of_week",
    "road_surface_conditions",
    "light_conditions",
    "sex_of_driver",
    "season",
    "speed_limit",
]

weather_map = {
    "Fine no high winds": 1,
    "Raining no high winds": 5,
    "Snowing no high winds": 7,
    "Fine + high winds": 0,
    "Raining + high winds": 4,
    "Snowing + high winds": 6,
    "Fog or mist": 2,
    "Unknown": 3,
    "Other": 3,
}

light_map = {
    "Daylight": 3,
    "Darkness - lights lit": 0,
    "Darkness - lights unlit": 1,
    "Darkness - no lighting": 2,
}

season_map = {"Winter": 3, "Summer": 2, "Rainy": 1, "Autumn": 0}

vehicle_map = {
    "Car": 1,
    "Goods Vehicle": 2,
    "Motorcycle": 3,
    "Other Vehicle": 4,
    "Bus": 0,
}

age_map = {
    "Under 16": 4,
    "16-25": 0,
    "26-45": 1,
    "46-65": 2,
    "Over 65": 3,
}

road_surface_condition_map = {
    "Dry": 1,
    "Wet or damp": 5,
    "Snow": 4,
    "Frost or ice": 3,
    "Flood over 3cm. deep": 2,
    "Mud": 0,
}

week_map = {
    "Sunday": 3,
    "Monday": 1,
    "Tuesday": 5,
    "Wednesday": 6,
    "Thursday": 4,
    "Friday": 0,
    "Saturday": 2,
}


def normalize_age_band(value: str) -> str:
    if pd.isna(value):
        return "26-45"
    text = str(value).strip().lower()
    if "under" in text:
        return "Under 16"
    if any(x in text for x in ["16", "17", "18", "19", "20", "21", "22", "23", "24", "25"]):
        if "26" not in text:
            return "16-25"
    if any(x in text for x in ["26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45"]):
        return "26-45"
    if any(x in text for x in ["46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65"]):
        return "46-65"
    if "over" in text or "66" in text or "70" in text:
        return "Over 65"
    return "26-45"


def normalize_vehicle(value: str) -> str:
    if pd.isna(value):
        return "Other Vehicle"
    text = str(value).lower()
    if "bus" in text:
        return "Bus"
    if "goods" in text or "van" in text or "lorry" in text:
        return "Goods Vehicle"
    if "motorcycle" in text or "scooter" in text or "bike" in text or "m/cycle" in text:
        return "Motorcycle"
    if "car" in text or "taxi" in text:
        return "Car"
    return "Other Vehicle"


def normalize_road_surface(value: str) -> str:
    if pd.isna(value):
        return "Mud"
    text = str(value).strip()
    if text in road_surface_condition_map:
        return text
    return "Mud"


def normalize_weather(value: str) -> str:
    if pd.isna(value):
        return "Unknown"
    text = str(value).strip()
    if text in weather_map:
        return text
    return "Other"


def normalize_light(value: str) -> str:
    if pd.isna(value):
        return "Daylight"
    text = str(value).strip()
    if text in light_map:
        return text
    return "Daylight"


def normalize_weekday(value: str) -> str:
    if pd.isna(value):
        return "Monday"
    text = str(value).strip()
    if text in week_map:
        return text
    return "Monday"


def month_to_season(month: int) -> str:
    if month in [12, 1, 2]:
        return "Winter"
    if month in [3, 4, 5]:
        return "Summer"
    if month in [6, 7, 8, 9]:
        return "Rainy"
    return "Autumn"


def load_and_prepare() -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(DATA_PATH)

    work = pd.DataFrame()
    work["age_band_of_driver"] = df["Age_Band_of_Driver"].apply(normalize_age_band)
    work["vehicle_type"] = df["Vehicle_Type"].apply(normalize_vehicle)
    work["age_of_vehicle"] = pd.to_numeric(df["Age_of_Vehicle"], errors="coerce").fillna(0).clip(lower=0)
    work["weather_conditions"] = df["Weather_Conditions"].apply(normalize_weather)
    work["day_of_week"] = df["Day_of_Week"].apply(normalize_weekday)
    work["road_surface_conditions"] = df["Road_Surface_Conditions"].apply(normalize_road_surface)
    work["light_conditions"] = df["Light_Conditions"].apply(normalize_light)
    work["sex_of_driver"] = df["Sex_of_Driver"].fillna("Male").astype(str)
    work["speed_limit"] = pd.to_numeric(df["Speed_limit"], errors="coerce").fillna(40).clip(lower=10)

    parsed_date = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
    work["season"] = parsed_date.dt.month.fillna(1).astype(int).apply(month_to_season)

    # Same encoding used by the Streamlit app
    work["weather_conditions"] = work["weather_conditions"].map(weather_map)
    work["light_conditions"] = work["light_conditions"].map(light_map)
    work["season"] = work["season"].map(season_map)
    work["vehicle_type"] = work["vehicle_type"].map(vehicle_map)
    work["sex_of_driver"] = work["sex_of_driver"].apply(lambda x: 1 if str(x).strip().lower() == "male" else 0)
    work["road_surface_conditions"] = work["road_surface_conditions"].map(road_surface_condition_map)
    work["age_band_of_driver"] = work["age_band_of_driver"].map(age_map)
    work["day_of_week"] = work["day_of_week"].map(week_map)

    work = work.reindex(columns=INPUT_FEATURES, fill_value=0).fillna(0)

    target_map = {"Fatal": 0, "Serious": 2, "Slight": 1}
    y = df["Accident_Severity"].map(target_map)

    valid = y.notna()
    X = work.loc[valid]
    y = y.loc[valid].astype(int)

    return X, y


def main() -> None:
    X, y = load_and_prepare()

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced_subsample",
    )
    model.fit(X, y)

    with MODEL_PATH.open("wb") as f:
        pickle.dump(model, f)

    print(f"Saved compatible model to: {MODEL_PATH}")
    print(f"Training rows: {len(X)}")


if __name__ == "__main__":
    main()
