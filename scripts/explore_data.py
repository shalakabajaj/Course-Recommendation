import pandas as pd

# Load Udemy dataset
udemy_path = "C:\\Users\\admin\\Desktop\\IMCC_Material\\MCA_SEM_3\\Project\\Course_Recommendator\\data\\raw\\udemy_courses.csv"
udemy_df = pd.read_csv(udemy_path)

# Load Coursera dataset
coursera_path = "C:\\Users\\admin\\Desktop\\IMCC_Material\\MCA_SEM_3\\Project\\Course_Recommendator\\data\\raw\\coursera_courses.csv"
coursera_df = pd.read_csv(coursera_path)

# Basic info
print("📊 Udemy Dataset Info")
print(udemy_df.info())
print("\n🔍 Udemy Dataset Sample")
print(udemy_df.head())

print("\n\n📊 Coursera Dataset Info")
print(coursera_df.info())
print("\n🔍 Coursera Dataset Sample")
print(coursera_df.head())
