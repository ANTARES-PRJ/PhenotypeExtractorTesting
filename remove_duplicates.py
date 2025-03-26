import pandas as pd
import numpy as np

# Load the CSV file
df = pd.read_csv("output/HPO-t2.csv",dtype=str)

# Set all values in df are strings
df = df.astype(str)

# Sort the values in each row while keeping the DataFrame structure
df_sorted = pd.DataFrame(np.sort(df.values, axis=1), columns=df.columns)

# Drop duplicate rows
df_unique = df_sorted.drop_duplicates()

# Save the cleaned file
df_unique.to_csv("output/HPO-t2-cleaned.csv", index=False)

print("Duplicates removed successfully!")