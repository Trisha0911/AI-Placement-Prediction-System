import pandas as pd
import random

data = []

for i in range(1000):

    cgpa = round(random.uniform(5.0, 10.0), 1)
    aptitude = random.randint(40, 100)
    communication = random.randint(40, 100)
    projects = random.randint(0, 5)
    internships = random.randint(0, 3)
    certifications = random.randint(0, 5)
    dsa = random.randint(40, 100)

    score = (
        cgpa * 10 +
        aptitude +
        communication +
        projects * 10 +
        internships * 15 +
        certifications * 5 +
        dsa
    )

    placement = 1 if score > 280 else 0

    data.append([
        cgpa,
        aptitude,
        communication,
        projects,
        internships,
        certifications,
        dsa,
        placement
    ])

df = pd.DataFrame(
    data,
    columns=[
        "CGPA",
        "Aptitude",
        "Communication",
        "Projects",
        "Internships",
        "Certifications",
        "DSA",
        "Placement"
    ]
)

df.to_csv("placement.csv", index=False)

print("1000 records generated successfully!")