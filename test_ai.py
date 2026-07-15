from ai_processor import process_news


title = """
Apple announces new artificial intelligence features for iPhone
"""


summary = """
Apple announced new AI features for iPhone users. The company says the new system will improve Siri performance.
"""


result = process_news(
    title,
    summary
)


print("================ TITLE ================")
print(result["title"])


print("\n================ SUMMARY ================")
print(result["summary"])
