# prompt_generator.py

import json
from pathlib import Path
import random
from prompt_templates import prompt_templates

HISTORY_FILE = Path("history.json")

# Built-in fallback presets for popular book categories
THEME_PRESETS = {
    "jungle": [
        "baby lion", "cute elephant", "baby monkey", "smiling giraffe", "cute tiger cub",
        "hippopotamus", "baby zebra", "cartoon parrot", "lazy sloth", "toucan bird",
        "friendly crocodile", "panda bear", "cute koala", "chameleon", "baby rhino",
        "leopard cub", "tree frog", "meerkat", "cute gorilla", "boar piglet",
        "peacock", "flamingo", "otter", "lemur", "baby panther",
        "chimpanzee", "armadillo", "anteater", "cute snake", "fruit bat",
        "jaguar cub", "tapir", "okapi", "gibbon", "capybara"
    ],
    "ocean": [
        "happy dolphin", "cute baby whale", "sea turtle", "friendly octopus", "clownfish",
        "starfish", "seahorse", "jellyfish", "cute shark", "baby seal",
        "crab", "lobster", "stingray", "pufferfish", "walrus",
        "penguin", "squid", "orca", "sea otter", "narwhal"
    ],
    "vehicles": [
        "fire truck", "police car", "school bus", "airplane", "tractor",
        "train engine", "helicopter", "dump truck", "cement mixer", "race car",
        "submarine", "space rocket", "tow truck", "motorcycle", "hot air balloon"
    ],
    "fruits": [
        "apple", "banana", "strawberry", "orange", "watermelon",
        "grapes", "pineapple", "mango", "peach", "cherry",
        "pear", "blueberry", "kiwi", "lemon", "papaya"
    ],
    "snacks": [
        "cupcake", "donut", "cookie", "ice cream cone", "lollipop",
        "popcorn box", "pancake", "waffle", "muffin", "pretzel"
    ]
}

# Action modifiers to dynamically yield infinite distinct subjects when base lists run low
SCENE_VARIATIONS = [
    "playing happily", "wearing a small bowtie", "sitting cute", 
    "waving friendly", "eating a treat", "curious look", 
    "holding a small flower", "resting peacefully"
]


class PromptGenerator:
    def __init__(self, topic: str = "jungle animals for kids", prompt_id: int = 1):
        self.topic = topic.strip()
        self.template_id = prompt_id if prompt_id in prompt_templates else 1
        self.template = prompt_templates.get(self.template_id, "")
        self.history = self._load_history()

    def _load_history(self) -> set:
        """Load previously generated items from persistent history.json."""
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return set(data.get("generated_items", []))
            except Exception:
                return set()
        return set()

    def _save_item(self, item: str):
        """Append item to history.json to ensure it is never repeated."""
        self.history.add(item)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"generated_items": sorted(list(self.history))}, f, indent=2)

    def _resolve_candidates(self) -> list:
        """Match input topic against presets or categories."""
        topic_lower = self.topic.lower()
        candidates = []
        
        # Check dictionary keys
        for key, preset_list in THEME_PRESETS.items():
            if key in topic_lower:
                candidates.extend(preset_list)

        return candidates

    def get_unique_item(self) -> str:
        """Retrieve a fresh item guaranteed not to exist in history.json."""
        candidates = self._resolve_candidates()
        random.shuffle(candidates)

        # 1. Try unused base items
        for item in candidates:
            if item not in self.history:
                self._save_item(item)
                return item

        # 2. If all base items have been used, generate variation pairs
        if candidates:
            for item in candidates:
                for action in SCENE_VARIATIONS:
                    combined = f"{item} {action}"
                    if combined not in self.history:
                        self._save_item(combined)
                        return combined

        # 3. Procedural fallback for custom topics
        counter = 1
        while True:
            candidate = f"{self.topic} character {counter}"
            if candidate not in self.history:
                self._save_item(candidate)
                return candidate
            counter += 1

    def generate_prompts(self, num_pages: int = 30) -> list:
        """
        Generate (item_name, prompt) tuples for the specified page count.
        Matches the interface expected by unified main.py.
        """
        prompts = []
        for _ in range(num_pages):
            item = self.get_unique_item()

            if self.template:
                prompt = self.template.format(item=item, items=item)
            else:
                # Standalone fallback if prompt_templates is empty
                prompt = (
                    f"cute simple cartoon {item}, toddler color by number page, "
                    f"thick continuous black outlines, bold clean lines, large open empty shapes, "
                    f"wide closed sections, minimalist vector line art, pure white blank background, "
                    f"no shading, no gray, centered composition, high contrast, "
                    f"placed in upper half of page, wide empty white bottom margin"
                )
            prompts.append((item, prompt))
        return prompts