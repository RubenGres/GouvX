from src.agents.gouvx import GouvX

gouvx_agent = GouvX()

history = []
while True:
    user_prompt = input("user: ")
    print("GouvX: ", end="")
    gouvx_reply = gouvx_agent.query(user_prompt, history=history)

    reply_str = ""
    for token in gouvx_reply:
        reply_str += token
        print(token, end="")

    print()

    history.append({
        "role": "user",
        "content": user_prompt
    })

    history.append({
        "role": "assistant",
        "content": reply_str
    })