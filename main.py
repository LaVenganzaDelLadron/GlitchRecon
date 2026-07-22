from app.dependencies import get_llm_provider

llm = get_llm_provider()
answer = llm.generate("Hello What is your model?")
print(answer)