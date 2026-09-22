from ai import generate_sql


question = "What was our total sales?"

sql = generate_sql(question)

print("\nGenerated SQL:")
print(sql)