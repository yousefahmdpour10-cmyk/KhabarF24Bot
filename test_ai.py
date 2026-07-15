from ai_processor import process_news



title = """
Thinking Machines launches Inkling, its first public AI model
"""


summary = """
Thinking Machines announced its first open AI model after months of developing artificial intelligence infrastructure.
The company says the model will compete with other AI systems.
"""



result = process_news(
    title,
    summary
)



print("\n========== TITLE ==========\n")

print(
    result["title"]
)


print("\n========== SUMMARY ==========\n")

print(
    result["summary"]
)
