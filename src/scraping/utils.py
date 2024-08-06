import csv

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def save_to_csv(data, filename, fieldnames):
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"Datos guardados en {filename}")
    except Exception as e:
        print(f"Error al guardar en CSV: {e}")