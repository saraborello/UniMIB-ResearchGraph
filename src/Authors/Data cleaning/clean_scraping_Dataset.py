import pandas as pd

def clean_dataset(file_path, output_path):
    """Clean the dataset and restructure it."""
    
    df = pd.read_csv(file_path)
    df.rename(columns={
        'Full Name': 'Full_Name',
        'SSD': 'SSD',
        'Role': 'Role'
    }, inplace=True)

    name_split = df['Full_Name'].str.split(' ', n=1, expand=True)
    df['Family_Name'] = name_split[0]
    df['Given_Name'] = name_split[1]

    df['Department_Code'] = df['SSD'].str.extract(r'\(([^)]+)\)')
    df['Specific_Field'] = df['SSD'].str.split('(', n=1, expand=True)[0].str.replace('SSD: ', '').str.strip()

    role_translation = {
        'Full Professor': 'Full Professor',
        'Professore/ssa ordinario/a': 'Full Professor',
        'Professore/ssa associato/a': 'Associate Professor',
        'Ricercatore/rice': 'Researcher',
        'Ricercatore/rice a tempo determinato': 'Fixed-Term Researcher',
        'Professore/ssa emerito/a': 'Professor Emeritus',
        'Assegnista di ricerca': 'Research Fellow',
        'Dottorando/a': 'PhD Student'
    }
    df['Role'] = df['Role'].map(role_translation)

    field_translation = {
        'Informatica': 'Computer Science',
        'Sistemi di elaborazione delle informazioni': 'Information Processing Systems',
        'Ricerca operativa': 'Operations Research',
        'SSD not available': 'SSD not available'
    }
    df['Specific_Field'] = df['Specific_Field'].map(field_translation)

    df.drop(columns=['Full_Name', 'SSD'], inplace=True)

    df = df[df['Role'] != 'PhD Student']

    df.to_csv(output_path, index=False)

if __name__ == "__main__":
    input_file = "data/raw/staff_data.csv"  
    output_file = "data/raw/authors_inernal_short.csv"  
    clean_dataset(input_file, output_file)

