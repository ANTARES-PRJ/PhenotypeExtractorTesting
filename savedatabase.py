import pandas as pd
df1 = pd.read_parquet("hf://datasets/biololab/synthetic_clinical_cases/data/train-00000-of-00001.parquet")
df2 = pd.read_csv("hf://datasets/joseluhf11/clinical_case_symptoms_diseases_dataset/train.csv")

df1.to_csv(r"C:\Users\Amorl\Desktop\progetto\save1.csv")
df2.to_csv(r"C:\Users\Amorl\Desktop\progetto\save2.csv")
