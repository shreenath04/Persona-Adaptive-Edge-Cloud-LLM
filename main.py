# main.py

from auth import login_loop, create_user
from router import decide_route_and_build_prompt, ROUTE_LOCAL, ROUTE_CLOUD
from models import call_local_model, call_cloud_model


def chat_session(session: dict) -> None:
    """
    Run a single chat session for a logged-in user.
    """
    username = session["username"]
    traits = session["traits"] or {}

    print(f"\nWelcome, {username}!")
    print("Your persona:", traits.get("persona_description", "N/A"))
    print("Type 'exit' or 'quit' to end the session.")

    while True:
        user_request = input("\nYou: ").strip()
        if user_request.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        # Ask router (Gemma) what to use and build final prompt
        routing = decide_route_and_build_prompt(traits, user_request)
        route = routing["route"]
        final_prompt = routing["final_prompt"]

        print(f"\n[Router chose: {route}]")

        # Call appropriate model
        if route == ROUTE_LOCAL:
            answer = call_local_model(final_prompt)
        else:
            answer = call_cloud_model(final_prompt)

        print("\nAssistant:", answer)


def main():
    print("=== Edge-Cloud AI Demo ===")

    while True:
        print("\n=== Main Menu ===")
        print("1) Log in")
        print("2) Create a new account")
        print("3) Exit")

        choice = input("Select an option (1/2/3): ").strip()

        if choice == "1":
            # Log in and start chat
            session = login_loop()
            chat_session(session)

        elif choice == "2":
            # Create user, then go to login
            create_user()
            print("\nAccount created. Please log in.\n")
            session = login_loop()
            chat_session(session)

        elif choice == "3":
            print("Exiting. Bye!")
            break

        else:
            print("Invalid option. Please choose 1, 2, or 3.")


if __name__ == "__main__":
    main()