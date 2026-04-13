def python_bot():
    print("--- Welcome to Python Bot (Rule Based) 🐍 ---")
    print("Type 'bye' to exit.")

    # Rule-based dictionary (The brain of the bot)
    responses = {
        "hi": "Hello there! How can I help you today?",
        "hello": "Hi! Nice to meet you.",
        "how are you": "I'm a bot, so I don't have feelings, but I'm running perfectly! ⚙️",
        "who are you": "I am a simple rule-based Python chatbot created for Worko.",
        "help": "I can answer simple greetings and tell you about myself. Try 'hi' or 'who are you'.",
        "bye": "Goodbye! Have a great day! 👋"
    }

    while True:
        # Get user input
        user_input = input("You: ").lower().strip()

        # Check if user wants to exit
        if user_input == "bye":
            print(f"Bot: {responses['bye']}")
            break

        # Check for matching rules
        found_match = False
        for key in responses:
            if key in user_input:
                print(f"Bot: {responses[key]}")
                found_match = True
                break
        
        # Fallback if no rule matches
        if not found_match:
            print("Bot: I'm sorry, I don't know that rule yet. Try asking 'help'.")

if __name__ == "__main__":
    python_bot()
