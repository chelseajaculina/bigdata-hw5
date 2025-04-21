from pinotdb import connect
import pandas as pd
import time
import math

# -------------------------------
# 🛠️ Configuration
# -------------------------------
HOST = "localhost"
PORT = 8099
TABLE_NAME = "websiteTraffic"
DECAY_RATE = 0.00001
TIME_COLUMN = 'timestamp'
TIME_COLUMN_SQL = '"timestamp"'

# Time window for the last 1 hour
TIME_WINDOW_HOURS = 1
TIME_WINDOW_SECONDS = TIME_WINDOW_HOURS * 60 * 60
TIME_WINDOW_LABEL = f"{TIME_WINDOW_HOURS} hour"

# -------------------------------
# 🚀 Main Logic
# -------------------------------
def main():
    conn = connect(
        host=HOST,
        port=PORT,
        path='/query/sql',
        scheme='http'
    )
    cursor = conn.cursor()

    # Verify the table exists
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} LIMIT 1")
        count = cursor.fetchone()[0]
        print(f"✓ Table '{TABLE_NAME}' exists with {count} rows.")
    except Exception as e:
        print(f"⚠️ Error accessing table '{TABLE_NAME}': {e}")
        return

    now_epoch_ms = int(time.time() * 1000)
    window_start_ms = now_epoch_ms - (TIME_WINDOW_SECONDS * 1000)

    print(f"\n⏳ Querying visit data (last {TIME_WINDOW_LABEL})...\n")

    # Get all data, including null user_ids
    try:
        sql_query = f"""
        SELECT user_id, session_id, {TIME_COLUMN_SQL}
        FROM {TABLE_NAME}
        WHERE {TIME_COLUMN_SQL} >= {window_start_ms}
        LIMIT 10000
        """
        print(f"Executing query: {sql_query}")
        cursor.execute(sql_query, {"timeoutMs": 10000})
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results, columns=columns)

        if df.empty:
            print("⚠️ No data returned from Pinot.")
            return

        # Create a dictionary to store consistent user IDs for each session
        session_user_map = {}
        user_id_counter = 1

        # Replace null user_ids with sequential user_ids
        for i in range(len(df)):
            if pd.isna(df.loc[i, 'user_id']) or df.loc[i, 'user_id'] == 'null':
                session_id = df.loc[i, 'session_id'] if 'session_id' in df.columns else None

                if session_id and session_id in session_user_map:
                    df.loc[i, 'user_id'] = session_user_map[session_id]
                else:
                    new_user_id = f"user_{user_id_counter}"
                    df.loc[i, 'user_id'] = new_user_id
                    user_id_counter += 1

                    if session_id:
                        session_user_map[session_id] = new_user_id

        # Print sample data
        print("📊 Sample visits (user_id, timestamp):")
        sample_df = df.head(20).copy()
        sample_df["readable_time"] = pd.to_datetime(sample_df[TIME_COLUMN], unit='ms')
        print(sample_df[['user_id', TIME_COLUMN, 'readable_time']].to_string(index=False))
        print()

        # Calculate decay weights
        df[TIME_COLUMN] = pd.to_numeric(df[TIME_COLUMN], errors='coerce')
        df = df.dropna(subset=[TIME_COLUMN])

        df["decay_weight"] = df[TIME_COLUMN].apply(
            lambda ts: math.exp(-DECAY_RATE * ((now_epoch_ms - ts) / 1000))
        )

        top_users = (
            df.groupby("user_id")["decay_weight"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
            .rename(columns={"decay_weight": "decayed_visits"})
            .head(10)
        )

        if top_users.empty:
            print(f"⚠️ No users found with visits in the past {TIME_WINDOW_LABEL}.")
        else:
            print(f"🔝 Top 10 Users by Recency-Weighted Visits (Last {TIME_WINDOW_LABEL}):")
            print(top_users.to_string(index=False))

    except Exception as e:
        print("❌ Query failed:", e)
        print(f"Query attempted: {sql_query}")

# -------------------------------
# ⏯️ Run Script
# -------------------------------
if __name__ == "__main__":
    main()
