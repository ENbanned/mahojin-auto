import random
from typing import List, Optional, Dict
import string
import json
from pathlib import Path


class RandomPromptEngine:
    
    def __init__(self, custom_data_path: Optional[Path] = None):
        self._word_data = self._initialize_data(custom_data_path)
        self._pattern_functions = [
            self._pattern_simple,
            self._pattern_complex,
            self._pattern_descriptive,
            self._pattern_stylized,
            self._pattern_scene,
            self._pattern_artistic,
            self._pattern_technical,
            self._pattern_narrative,
            self._pattern_emotion_driven,
            self._pattern_conceptual
        ]
        self._connectors = [", ", " with ", " in ", " featuring ", " displaying ",
                           " showing ", "; ", " containing ", " including ", 
                           " portraying ", " exhibiting ", " presenting "]
        self._prefixes = ["a", "the", "an elegant", "a stunning", "an ethereal", 
                        "a mesmerizing", "a captivating", "a striking", "an abstract",
                        "a dynamic", "a minimalist", "a hyperrealistic", "a gorgeous",
                        "a magnificent", "an exceptional", "a dramatic", "an extraordinary"]
        self._suffixes = ["", "scene", "composition", "artwork", "image", "illustration",
                         "picture", "portrait", "concept", "design", "masterpiece", 
                         "creation", "render", "visualization"]
        self._formats = ["medium shot", "close-up", "panorama", "wide angle", "macro",
                        "portrait", "landscape", "aerial view", "fisheye", "tilt-shift"]
        self._advanced_descriptors = {
            "quality": ["8k", "photorealistic", "hyperdetailed", "ultra-high definition", 
                       "studio quality", "professional", "cinematic", "detailed"],
            "lighting": ["volumetric lighting", "ray tracing", "golden hour", "blue hour", 
                         "soft lighting", "dramatic shadows", "ambient occlusion", 
                         "rim lighting", "global illumination"],
            "rendering": ["unreal engine", "octane render", "ray tracing", "V-ray", 
                         "physically based rendering", "cycles render", "path tracing"]
        }
        
        
    def _initialize_data(self, custom_path: Optional[Path]) -> Dict:
        if custom_path and custom_path.exists():
            try:
                with open(custom_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        elements = {
            "subjects": [
                "cat", "dog", "wolf", "fox", "dragon", "knight", "astronaut", "mermaid", 
                "robot", "unicorn", "fairy", "wizard", "cyberpunk character", "elf", 
                "vampire", "werewolf", "monster", "angel", "demon", "goddess", "god", 
                "warrior", "samurai", "ninja", "pirate", "cowboy", "detective", "alien",
                "zombie", "ghost", "witch", "sorcerer", "princess", "prince", "king", 
                "queen", "emperor", "villain", "hero", "cyborg", "android", "mutant"
            ],
            "environments": [
                "city", "forest", "mountains", "ocean", "desert", "jungle", "tundra", 
                "savanna", "riverbank", "lakeside", "beach", "canyon", "volcano", 
                "island", "waterfall", "cave", "ruins", "temple", "castle", "spaceship", 
                "starship", "space station", "underwater city", "floating island", 
                "ancient civilization", "futuristic metropolis", "dystopian city", 
                "utopian society", "abandoned building", "haunted house", "mansion"
            ],
            "styles": [
                "photorealistic", "watercolor", "oil painting", "digital art", 
                "pixel art", "cartoon", "anime", "surrealism", "impressionism", 
                "minimalism", "cyberpunk", "steampunk", "retro", "futuristic", 
                "gothic", "baroque", "renaissance", "art nouveau", "art deco", 
                "pop art", "cubism", "abstract expressionism", "fantasy", 
                "sci-fi", "horror", "vaporwave", "ukiyo-e", "synthwave"
            ],
            "moods": [
                "dark", "bright", "mysterious", "joyful", "melancholic", 
                "energetic", "calm", "tense", "romantic", "fantastic", 
                "apocalyptic", "mystical", "whimsical", "dreamy", "nightmarish", 
                "serene", "chaotic", "peaceful", "ominous", "ethereal"
            ],
            "time_periods": [
                "medieval", "renaissance", "victorian era", "1920s", "1950s", 
                "1980s", "future", "prehistoric", "ancient Egypt", "ancient Greece", 
                "ancient Rome", "feudal Japan", "wild west", "bronze age", 
                "iron age", "stone age", "byzantine", "colonial", "industrial revolution", 
                "world war I", "world war II", "cold war", "space age", "information age"
            ],
            "lighting": [
                "sunlight", "moonlight", "sunset", "dawn", "backlight", "soft-box", 
                "neon lighting", "candles", "lanterns", "studio lighting", 
                "natural lighting", "dramatic lighting", "cinematic lighting", 
                "firelight", "torchlight", "bioluminescence", "glow-in-the-dark"
            ],
            "compositions": [
                "close-up", "panorama", "bird's eye view", "symmetrical composition", 
                "first-person view", "minimalist", "detailed", "dynamic", 
                "rule of thirds", "golden ratio", "centered composition", 
                "asymmetrical balance", "leading lines", "frame within a frame"
            ],
            "art_movements": [
                "baroque", "renaissance", "impressionism", "expressionism", 
                "cubism", "surrealism", "art nouveau", "art deco", "abstract expressionism", 
                "pop art", "minimalism", "romanticism", "neoclassicism", "dada", 
                "futurism", "modernism", "postmodernism", "constructivism", "symbolism", 
                "contemporary art", "lowbrow art", "digital art", "post-digital"
            ],
            "artists": [
                "da Vinci", "Michelangelo", "Van Gogh", "Monet", "Picasso", 
                "Dali", "Warhol", "Klimt", "Rembrandt", "Monet", "O'Keeffe", 
                "Kahlo", "Giger", "Beeple", "Beksiński", "Mucha", "Escher", 
                "Studio Ghibli", "Tim Burton", "Wes Anderson"
            ],
            "techniques": [
                "tilt-shift", "long exposure", "low-key", "high-key", "silhouette", 
                "bokeh", "hdr", "forced perspective", "macro photography", 
                "chiaroscuro", "sfumato", "cross-hatching", "pointillism", 
                "scanography", "photomontage", "collage", "stippling", "etching"
            ],
            "textures": [
                "smooth", "rough", "glossy", "matte", "metallic", "rustic", 
                "silky", "velvety", "grainy", "weathered", "distressed", 
                "polished", "brushed", "textured", "patterned", "crystalline", 
                "liquid", "glass-like", "organic", "geometric"
            ],
            "adjectives": [
                "beautiful", "stunning", "incredible", "amazing", "breathtaking", 
                "magnificent", "gorgeous", "striking", "captivating", "mesmerizing", 
                "enchanting", "alluring", "fascinating", "spellbinding", "hypnotic", 
                "intriguing", "extraordinary", "spectacular", "phenomenal", "majestic"
            ],
            "locations": [
                "Tokyo", "New York", "Paris", "London", "Venice", "Kyoto", 
                "Santorini", "Iceland", "Machu Picchu", "Grand Canyon", 
                "Amazon Rainforest", "Swiss Alps", "Great Barrier Reef", 
                "Sahara Desert", "Antarctica", "Mars", "Jupiter", "deep space", 
                "underwater", "inside a computer", "inside the human body"
            ]
        }
        
        return elements
    
    
    def _get_random_elements(self, category: str, count: int = 1) -> List[str]:
        if category not in self._word_data or not self._word_data[category]:
            return [""]
        
        available = self._word_data[category]
        if count >= len(available):
            return available.copy()
        
        return random.sample(available, count)
    
    
    def _pattern_simple(self) -> str:
        subject = random.choice(self._get_random_elements("subjects"))
        style = random.choice(self._get_random_elements("styles"))
        connector = random.choice(self._connectors)
        return f"{subject}{connector}{style}"
    
    
    def _pattern_complex(self) -> str:
        subject = random.choice(self._get_random_elements("subjects"))
        environment = random.choice(self._get_random_elements("environments"))
        style = random.choice(self._get_random_elements("styles"))
        lighting = random.choice(self._get_random_elements("lighting"))
        
        parts = [subject, environment, style, lighting]
        random.shuffle(parts)
        
        return ", ".join(parts)
    
    
    def _pattern_descriptive(self) -> str:
        prefix = random.choice(self._prefixes)
        subject = random.choice(self._get_random_elements("subjects"))
        adjective = random.choice(self._get_random_elements("adjectives"))
        environment = random.choice(self._get_random_elements("environments"))
        suffix = random.choice(self._suffixes)
        
        template = random.choice([
            f"{prefix} {adjective} {subject} in {environment} {suffix}",
            f"{adjective} {subject} in {environment}, {suffix}",
            f"{prefix} {subject} in {adjective} {environment} {suffix}"
        ])
        
        return template.strip()
    
    
    def _pattern_stylized(self) -> str:
        subject = random.choice(self._get_random_elements("subjects"))
        artist = random.choice(self._get_random_elements("artists"))
        art_movement = random.choice(self._get_random_elements("art_movements"))
        
        template = random.choice([
            f"{subject} in the style of {artist}",
            f"{subject}, {art_movement} style",
            f"{subject} inspired by {artist}",
            f"{art_movement} {subject}"
        ])
        
        return template
    
    
    def _pattern_scene(self) -> str:
        environment = random.choice(self._get_random_elements("environments"))
        time_period = random.choice(self._get_random_elements("time_periods"))
        mood = random.choice(self._get_random_elements("moods"))
        lighting = random.choice(self._get_random_elements("lighting"))
        
        templates = [
            f"{environment} during {time_period}, {mood} atmosphere, {lighting}",
            f"{mood} {environment} in {time_period} with {lighting}",
            f"{time_period} {environment}, {lighting}, {mood} mood"
        ]
        
        return random.choice(templates)
    
    
    def _pattern_artistic(self) -> str:
        technique = random.choice(self._get_random_elements("techniques"))
        subject = random.choice(self._get_random_elements("subjects"))
        texture = random.choice(self._get_random_elements("textures"))
        art_movement = random.choice(self._get_random_elements("art_movements"))
        
        templates = [
            f"{subject} using {technique} technique, {texture} texture, {art_movement}",
            f"{technique} of {subject} with {texture} textures, {art_movement} inspired",
            f"{art_movement} {subject}, {technique}, {texture} finish"
        ]
        
        return random.choice(templates)
    
    
    def _pattern_technical(self) -> str:
        subject = random.choice(self._get_random_elements("subjects"))
        quality = random.choice(self._advanced_descriptors["quality"])
        lighting = random.choice(self._advanced_descriptors["lighting"])
        rendering = random.choice(self._advanced_descriptors["rendering"])
        camera_format = random.choice(self._formats)
        
        templates = [
            f"{subject}, {quality}, {lighting}, {rendering}, {camera_format}",
            f"{quality} {subject}, {camera_format}, {lighting}, {rendering}",
            f"{camera_format} of {subject}, {quality}, {lighting}, {rendering}"
        ]
        
        return random.choice(templates)
    
    
    def _pattern_narrative(self) -> str:
        subject = random.choice(self._get_random_elements("subjects"))
        environment = random.choice(self._get_random_elements("environments"))
        time_period = random.choice(self._get_random_elements("time_periods"))
        
        templates = [
            f"{subject} exploring {environment} during {time_period}",
            f"{subject} discovering ancient secrets in {environment}, {time_period}",
            f"{subject} fighting for survival in {environment}, {time_period}",
            f"{subject} building a new life in {environment}, {time_period}"
        ]
        
        return random.choice(templates)
    
    
    def _pattern_emotion_driven(self) -> str:
        mood = random.choice(self._get_random_elements("moods"))
        subject = random.choice(self._get_random_elements("subjects"))
        environment = random.choice(self._get_random_elements("environments"))
        
        templates = [
            f"{mood} atmosphere, {subject} in {environment}",
            f"{subject} expressing {mood} emotions in {environment}",
            f"{mood} scene with {subject} in {environment}"
        ]
        
        return random.choice(templates)
    
    
    def _pattern_conceptual(self) -> str:
        subjects = self._get_random_elements("subjects", 2)
        environment = random.choice(self._get_random_elements("environments"))
        
        templates = [
            f"contrast between {subjects[0]} and {subjects[1]} in {environment}",
            f"evolution of {subjects[0]} into {subjects[1]} in {environment}",
            f"hybrid of {subjects[0]} and {subjects[1]} in {environment}",
            f"transformation from {subjects[0]} to {subjects[1]} in {environment}"
        ]
        
        return random.choice(templates)
    
    
    def _add_random_prefix_suffix(self, prompt: str) -> str:
        if random.random() < 0.4: 
            if random.random() < 0.5:
                quality = random.choice(self._advanced_descriptors["quality"])
                prompt = f"{quality}, {prompt}"
            else: 
                rendering = random.choice(self._advanced_descriptors["rendering"])
                prompt = f"{prompt}, {rendering}"
        return prompt
    
    
    def _randomize_capitalization(self, prompt: str) -> str:
        if random.random() < 0.7:
            return prompt
        
        if random.random() < 0.5: 
            return prompt.lower()
        else:  
            return " ".join(word.capitalize() for word in prompt.split())
    
    
    def _randomize_punctuation(self, prompt: str) -> str:
        if random.random() < 0.8:
            return prompt
        
        if random.random() < 0.5:
            if prompt and prompt[-1] in string.punctuation:
                prompt = prompt[:-1]
            new_punct = random.choice(['.', '!', '...', ' -', ''])
            return prompt + new_punct
        else:
            if ',' in prompt:
                return prompt.replace(',', ';')
            elif ';' in prompt:
                return prompt.replace(';', ',')
        return prompt
    
    
    def _create_prompt(self) -> str:
        pattern_func = random.choice(self._pattern_functions)
        
        prompt = pattern_func()
        
        prompt = self._add_random_prefix_suffix(prompt)
        prompt = self._randomize_capitalization(prompt)
        prompt = self._randomize_punctuation(prompt)
        
        return prompt


    def generate_prompts(self, count: int) -> List[str]:
        return [self._create_prompt() for _ in range(count)]


def get_diverse_prompts(count: int = 1, custom_data_path: Optional[Path] = None) -> List[str]:
    engine = RandomPromptEngine(custom_data_path)
    return engine.generate_prompts(count)
