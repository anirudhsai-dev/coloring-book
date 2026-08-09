# prompt_generator.py

import random
from categories import categories
from prompt_templates import prompt_templates  # ✅ Updated import

class PromptGenerator:
    def __init__(self, selected_categories, prompt_id):
        self.selected_categories = selected_categories
        self.prompt_template = prompt_templates.get(prompt_id, prompt_templates[1])  # Default to template 1
        self.all_items = self.get_all_items()
        self.used_items = set()


    def get_all_items(self):
        """Fetch all possible items from the selected categories."""
        all_items = []
        for category in self.selected_categories:
            all_items.extend(categories.get(category, []))
        random.shuffle(all_items)
        return all_items

    def get_unique_items(self):
        """Get six unique items for a page, ensuring no repeats across pages."""
        available_items = [item for item in self.all_items if item not in self.used_items]
        
        if len(available_items) < 6:
            self.used_items.clear()
            available_items = self.all_items.copy()
            random.shuffle(available_items)

        selected_items = available_items[:6]
        self.used_items.update(selected_items)
        return selected_items

    def generate_prompt(self, num_pages=30):
        """Generate unique prompts for a given number of pages."""
        prompts = []
        for _ in range(num_pages):
            items = self.get_unique_items()
            formatted_items = ', '.join(items)
            prompt = self.prompt_template.format(items=formatted_items, theme="food and snacks")  # Dynamically inserts items
            prompts.append(prompt)
        return prompts
