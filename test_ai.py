from ai_processor import process_news


title = "Manchester United defeated Chelsea in Premier League match"

summary = """
Manchester United defeated Chelsea after a great performance.
Bruno Fernandes scored the winning goal.
"""


result = process_news(
    title,
    summary
)


print("TITLE:")
print(result["title"])

print("\nSUMMARY:")
print(result["summary"])
