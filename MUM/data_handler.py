import csv
from typing import List


def append_to_csv(file: str, data: List) -> None:
    with open(file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)


def append_to_txt(file: str, text: str):
    with open(file, "a") as file:
        file.write(text)
