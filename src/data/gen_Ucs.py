# Sometimes the data is not in the correct format '8h00 - 10h00' should be '08h00-10h00'

import pandas as pd

data_frame = pd.read_excel("grade_2024_01.xlsx")

# Define the days and their corresponding columns in the Excel file
days = {'Segunda': ['C', 'K'],
        'Terca': ['L', 'T'],
        'Quarta': ['U', 'AD'],
        'Quinta': ['AE', 'AL'],
        'Sexta': ['AM', 'AP'],
        'Sabado': ['AQ', 'AS']}

# Function to convert Excel column letter to index
def convert_to_index(column: str):
    index = 0
    for i, letter in enumerate(reversed(column)):
        index += (26 ** i) * (ord(letter) - ord('A') + 1)
    return index - 1

# Function to get the day based on the Excel column index
def get_day(column: int):
    for day, columns in days.items():
        if convert_to_index(columns[0]) <= column <= convert_to_index(columns[1]):
            return day


class UC:
    def __init__(self, name, class_info, hour, day) -> None:
        self.NAME = str(name)
        self.CLASS_INFO = str(class_info).split("-")[0] if "-" in str(class_info) else str(class_info)
        self.PROFESSORS = str(class_info).split("-")[1] if "-" in str(class_info) else "Nenhum"
        self.HOUR = str(hour)
        self.DAY = str(day)

    def __str__(self) -> str:
        return f"Nome: {self.NOME} Turma: {self.TURMA} Horário: {self.HORARIO} Dia: {self.DIA}"

# List to store the UCs
ucs = []

# Iterate over the rows in the data frame
for i, row in data_frame.iterrows(): 
    if (str(row.iloc[1]) != "Docente" or str(row.iloc[1]) == "") and i > 1:
        # Iterate over the cells in the row
        for j, cell in enumerate(row):
            if str(cell) != "nan" and len(str(cell)) > 1 and j > 1 and str(row.iloc[1]) != "":
                ucs.append(UC(str(cell), str(data_frame.iloc[i + 1 , j]), str(row.iloc[1]), get_day(j)))

# Convert the list of UCs to a data frame
df_ucs = pd.DataFrame([vars(uc) for uc in ucs])

# Group the UCs by name, professors, and class info
unique_ucs = df_ucs.groupby(['NAME', 'PROFESSORS', 'CLASS_INFO'], as_index=False).agg({'HOUR': lambda x: list(x), 'DAY': lambda y: list(y)})

# Convert the data frame to JSON
result = unique_ucs.to_json(orient='records')

# Write the JSON to a file
with open('materias_2024_01.json', 'w+') as out:
    out.write(result)

print("Done!, check the file materias_2024_01.json")
