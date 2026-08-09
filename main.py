# main.py

from prompt_generator import PromptGenerator

def get_user_categories():
    """Ask the user to input categories"""
    available_categories = ["fruits", "snacks", "drinks", "food"]
    print(f"Available categories: {', '.join(available_categories)}")
    
    user_input = input("Enter categories (comma-separated): ").strip().lower()
    selected_categories = [c.strip() for c in user_input.split(",") if c.strip() in available_categories]
    
    if not selected_categories:
        print("No valid categories selected. Exiting.")
        exit()
    
    return selected_categories

def get_prompt_choice():
    """Ask the user to choose a prompt format"""
    print("\nChoose a prompt style:")
    print("1: Simple description")
    print("2: Artistic theme")
    print("3: Detailed sketch style")
    
    while True:
        try:
            choice = int(input("Enter the number (1-3): ").strip())
            if choice in [1, 2, 3]:
                return choice
            else:
                print("Invalid choice, please enter 1, 2, or 3.")
        except ValueError:
            print("Please enter a valid number.")

def main():
    user_categories = get_user_categories()
    prompt_choice = get_prompt_choice()
    
    generator = PromptGenerator(user_categories, prompt_choice)
    prompts = generator.generate_prompt()

    print("\nGenerated Prompts:")
    for i, prompt in enumerate(prompts, 1):
        print(f"\nPage {i}:\n{prompt}")

if __name__ == "__main__":
    main()
