from app.agents.devmind_agent import DevMindAgent

agent = DevMindAgent()

response1 = agent.chat(
    session_id = None,
    message = "My name is Jeel"
)

session_id = response1["session_id"]

response2 = agent.chat(
    session_id = session_id,
    message = "What is my name?"
)
print(response2)
