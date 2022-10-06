import pandas as pd 
import os, shutil, re




def save_to_file(foldername, filename, brand=False):
    
    pattern = "\d{1,}\,\d{3,}\.\d{2}|\d{3}\.\d{2}"
    
    dataframe = pd.concat([pd.read_csv(file) for file in os.listdir() if file.endswith('.csv')])
    if brand:
        dataframe['brand'] = dataframe['brand'].apply(lambda x: x.replace(x, foldername.title()))

    dataframe.dropna(inplace=True)
    dataframe['brand_price'] = dataframe['brand_price'].apply(lambda x: float("".join((re.findall(string=x, pattern=pattern)[-1]).split(','))))
    try:
        os.makedirs(f"selenium/cleaner_output/{foldername}")
    except FileExistsError:
        "File Already Exists"
        
    dataframe.sort_values(by="brand_price").to_csv(f"selenium/cleaner_output/{foldername}/{filename}.csv", index=False)

def send_to_trash(destination):
    files = [file for file in os.listdir() if file.endswith('.csv') or file.endswith('.txt')]
    try:
        os.makedirs(f"selenium/trash/{destination}")
    
    except FileExistsError:
        "File Already Exist"
    for file in files: 
        shutil.move(file, f"selenium/trash/{destination}")

