import pandas as pd
import random

data = []

for i in range(1000):
    hours = random.randint(1, 10)
    attendance = random.randint(40, 100)
    previous = random.randint(30, 100)
    assignments = random.randint(1, 5)
    extra = random.randint(0, 1)
    sleep = random.randint(4, 9)

    score = (hours * 3 + attendance * 0.4 + previous * 0.5 + assignments * 6 + sleep * 2 + extra * 5)

    if score > 140:
        performance = 1
    else:
        performance = 0

    data.append([hours, attendance, previous, assignments, extra, sleep, performance])

df = pd.DataFrame(data, columns=[
    "hours_studied",
    "attendance",
    "previous_score",
    "assignments",
    "extracurricular",
    "sleep_hours",
    "performance"
])

df.to_csv("dataset.csv", index=False)

print("Balanced dataset created!")