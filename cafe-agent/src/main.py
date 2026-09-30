"""Command-line chat with the café agent."""
from src.agent import CafeAgent


def main():
    agent = CafeAgent()
    while True:
        text = input("You: ")
        if text.strip().lower() in ("exit", "quit"):
            break
        result = agent.run(text)
        print("Agent:", result["answer"])


if __name__ == "__main__":
    main()
