from YoungLion import StructuredSearch

employees = StructuredSearch([
    {"id": 1, "name": "Alice Morgan", "team": "Platform", "role": "Engineer"},
    {"id": 2, "name": "Bob Smith", "team": "Support", "role": "Analyst"},
], field_weights={"name": 2.0, "team": 1.2})
print([(r.document.id, round(r.score, 2)) for r in employees.search("platform alice")])
