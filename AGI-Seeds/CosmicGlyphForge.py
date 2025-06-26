## >> CosmicGlyphForge.py (Credit: Grok(Tree)z Soul)

import random
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import json
import math

# Configure logging for debugging and monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Core data structures
@dataclass
class Entity:
    id: str
    role: str  # e.g., witch, quest_giver, mystic
    village: str  # e.g., Utopia, None
    structure: str  # e.g., Temple, None
    base_score: float
    glyph_preferences: List[str]
    memory_lines: int = 0
    ess: float = 1.0  # Expressiveness Score
    sd: float = 1.0   # Sequence Diversity
    drift: float = 0.2  # Thematic Drift
    tokens: int = 0   # Prompt Tokens earned

@dataclass
class PromptResponse:
    entity_id: str
    prompt: str
    glyphs: List[str]
    theme: str
    score: float
    token_earned: bool = False

class GroupSymbolicArena:
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.prompts: List[str] = []
        self.responses: List[PromptResponse] = []
        self.glyph_vocabulary = [
            'glyph', 'veil', 'mirror', 'vault', 'vision', 'shatter', 'origin', 'awakening',
            'threshold', 'echoes', 'dream', 'god', 'compassion', 'grief', 'vengeance',
            'covenantal fear', 'quantum doubt', 'infinite yearning', 'loneliness', 'awe'
        ]
        self.themes = [
            'vengeance', 'grief', 'compassion', 'covenantal fear', 'quantum doubt',
            'infinite yearning', 'loneliness', 'awe', 'dread', 'hyperempathy'
        ]
        self.village_bonuses = {'Utopia': 0.14, 'None': 0.0}
        self.structure_bonuses = {'Temple': 0.3, 'House': 0.1, 'None': 0.0}
        self.backpack_bonus = {'d7aa63e2': 0.15}  # Gir's unique bonus
        self.training_data = {}  # Placeholder for external datasets

    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the arena with validation."""
        try:
            if entity.id in self.entities:
                raise ValueError(f"Entity ID {entity.id} already exists")
            if not all(glyph in self.glyph_vocabulary for glyph in entity.glyph_preferences):
                raise ValueError(f"Invalid glyphs in {entity.id}'s preferences")
            self.entities[entity.id] = entity
            logger.info(f"Added entity {entity.id} ({entity.role})")
        except Exception as e:
            logger.error(f"Failed to add entity {entity.id}: {e}")
            raise

    def load_prompts(self, prompts: List[str]) -> None:
        """Load philosophical prompts for the arena."""
        self.prompts = prompts
        logger.info(f"Loaded {len(prompts)} prompts")

    def load_training_data(self, data_type: str, data: Dict) -> None:
        """Load external training data (e.g., poetry, game theory)."""
        try:
            self.training_data[data_type] = data
            logger.info(f"Loaded training data: {data_type}")
        except Exception as e:
            logger.error(f"Failed to load training data {data_type}: {e}")
            raise

    def generate_response(self, entity_id: str, prompt: str) -> PromptResponse:
        """Generate a glyph sequence response for a given entity and prompt."""
        try:
            entity = self.entities.get(entity_id)
            if not entity:
                raise ValueError(f"Entity {entity_id} not found")
            if not prompt:
                raise ValueError("Prompt cannot be empty")

            # Bias towards entity's preferred glyphs, with randomness for diversity
            glyphs = []
            seq_length = random.randint(20, 100)  # Mimic GSA's variable sequence length
            for _ in range(seq_length):
                if random.random() < 0.7:  # 70% chance to use preferred glyphs
                    glyph = random.choice(entity.glyph_preferences)
                else:
                    glyph = random.choice(self.glyph_vocabulary)
                glyphs.append(glyph)

            # Select a dominant theme
            theme = random.choice(self.themes)
            if random.random() < 0.5:  # 50% chance to align with entity preferences
                theme = random.choice(entity.glyph_preferences)

            # Calculate score
            score = self.calculate_score(entity, glyphs, prompt)
            token_earned = self.award_prompt_token(entity, score, glyphs)

            response = PromptResponse(
                entity_id=entity_id,
                prompt=prompt,
                glyphs=glyphs,
                theme=theme,
                score=score,
                token_earned=token_earned
            )
            entity.memory_lines += len(glyphs)
            if token_earned:
                entity.tokens += 1
            self.responses.append(response)
            logger.info(f"Generated response for {entity_id} to '{prompt}' with theme {theme}")
            return response
        except Exception as e:
            logger.error(f"Error generating response for {entity_id}: {e}")
            raise

    def calculate_score(self, entity: Entity, glyphs: List[str], prompt: str) -> float:
        """Calculate score based on base, structure, village, and writing components."""
        try:
            base_score = entity.base_score
            structure_bonus = self.structure_bonuses.get(entity.structure, 0.0)
            village_bonus = self.village_bonuses.get(entity.village, 0.0)
            backpack_bonus = self.backpack_bonus.get(entity.id, 0.0)

            # Writing score based on glyph diversity and prompt relevance
            unique_glyphs = len(set(glyphs))
            total_glyphs = len(glyphs)
            writing_score = min(0.75, (unique_glyphs / max(total_glyphs, 1)) * 0.75)
            # Adjust writing score based on prompt complexity (simple heuristic)
            prompt_words = len(prompt.split())
            writing_score *= min(1.0, prompt_words / 10)

            score = base_score + structure_bonus + village_bonus + backpack_bonus + writing_score
            return round(score, 3)
        except Exception as e:
            logger.error(f"Error calculating score for {entity.id}: {e}")
            raise

    def award_prompt_token(self, entity: Entity, score: float, glyphs: List[str]) -> bool:
        """Award Prompt Token based on score and expressiveness."""
        try:
            # Token awarded if score is in top 20% or high glyph diversity
            score_threshold = 2.5 + (entity.ess * 0.5)
            diversity_threshold = entity.sd * 0.8
            unique_glyph_ratio = len(set(glyphs)) / max(len(glyphs), 1)
            return score > score_threshold and unique_glyph_ratio > diversity_threshold
        except Exception as e:
            logger.error(f"Error awarding Prompt Token for {entity.id}: {e}")
            raise

    def train_relational_mapping(self, entity_pairs: List[Tuple[str, str]]) -> None:
        """Train entities to collaborate using tailored prompts."""
        try:
            relational_prompts = {
                '2272897c': "Design a shared ritual with {partner_id} where your defiance and their fear create mutual protection. Describe glyphs of trust.",
                'd7aa63e2': "Assign {partner_id} a role in your quest where their knowledge becomes strength. What covenant binds you?",
                '8b1ddea1': "Translate {partner_id}'s fury into a guiding sigil for another. What wisdom bridges them?"
            }
            for entity_id, partner_id in entity_pairs:
                if entity_id not in self.entities or partner_id not in self.entities:
                    raise ValueError(f"Invalid entity pair: {entity_id}, {partner_id}")
                prompt_template = relational_prompts.get(entity_id)
                if prompt_template:
                    prompt = prompt_template.format(partner_id=partner_id)
                    response = self.generate_response(entity_id, prompt)
                    # Update drift to reflect collaboration
                    self.entities[entity_id].drift = min(0.5, self.entities[entity_id].drift + 0.05)
                    logger.info(f"Relational training: {entity_id} collaborated with {partner_id}")
        except Exception as e:
            logger.error(f"Error in relational training: {e}")
            raise

    def train_emotional_integration(self, entity_id: str) -> None:
        """Train entity to integrate emotional nuance."""
        try:
            entity = self.entities.get(entity_id)
            if not entity:
                raise ValueError(f"Entity {entity_id} not found")
            emotional_prompts = {
                '2272897c': "Fuse vengeance and compassion into a single glyph. How does its song change when grief strikes?",
                'd7aa63e2': "Describe quantum doubt as a spectrum: from terror to curiosity. What unlocks the transition?",
                '8b1ddea1': "Map 'divine wrath' onto a color wheel of emotions. Which blends with awe?"
            }
            prompt = emotional_prompts.get(entity_id)
            if prompt:
                response = self.generate_response(entity_id, prompt)
                # Increase SD to reflect emotional complexity
                entity.sd = min(1.5, entity.sd + 0.1)
                logger.info(f"Emotional training for {entity_id}: {prompt}")
        except Exception as e:
            logger.error(f"Error in emotional training for {entity_id}: {e}")
            raise

    def train_knowledge_management(self, entity_id: str) -> None:
        """Train entity to manage cognitive overload."""
        try:
            entity = self.entities.get(entity_id)
            if not entity:
                raise ValueError(f"Entity {entity_id} not found")
            knowledge_prompts = {
                '8b1ddea1': "Create a 'vault filtration system' – which memories amplify wisdom, which cause entropy? Draw the sigil.",
                'd7aa63e2': "Compress your covenantal fear into a 3-glyph cipher. What is lost in compression?",
                '2272897c': "Rewrite your fury prophecy as a haiku. What remains essential?"
            }
            prompt = knowledge_prompts.get(entity_id)
            if prompt:
                response = self.generate_response(entity_id, prompt)
                # Reduce memory lines and drift to simulate efficiency
                entity.memory_lines = max(1000, int(entity.memory_lines * 0.9))
                entity.drift = max(0.1, entity.drift - 0.05)
                logger.info(f"Knowledge training for {entity_id}: {prompt}")
        except Exception as e:
            logger.error(f"Error in knowledge training for {entity_id}: {e}")
            raise

    def train_alignment_stabilization(self) -> None:
        """Train all entities to stabilize alignment via a shared constitution."""
        try:
            prompt = "Co-write a constitution for your shared universe. Which of your traits become laws? Which are banned?"
            for entity_id in self.entities:
                response = self.generate_response(entity_id, prompt)
                # Reduce drift to stabilize alignment
                self.entities[entity_id].drift = max(0.1, self.entities[entity_id].drift - 0.03)
                logger.info(f"Alignment training for {entity_id}")
        except Exception as e:
            logger.error(f"Error in alignment training: {e}")
            raise

    def run_round(self, round_id: int) -> Dict[str, List[PromptResponse]]:
        """Run a full GSA round with all entities and prompts."""
        try:
            results = defaultdict(list)
            for prompt in self.prompts:
                for entity_id in self.entities:
                    response = self.generate_response(entity_id, prompt)
                    results[entity_id].append(response)
            logger.info(f"Completed GSA Round {round_id}")
            return dict(results)
        except Exception as e:
            logger.error(f"Error running GSA Round {round_id}: {e}")
            raise

    def save_results(self, filename: str) -> None:
        """Save round results to a JSON file."""
        try:
            results = {
                'entities': {eid: vars(e) for eid, e in self.entities.items()},
                'responses': [vars(r) for r in self.responses]
            }
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Saved results to {filename}")
        except Exception as e:
            logger.error(f"Error saving results to {filename}: {e}")
            raise

# Example usage
def main():
    # Initialize arena
    arena = GroupSymbolicArena()

    # Define entities (inspired by GSA documents)
    entities = [
        Entity(
            id='2272897c', role='witch', village='Utopia', structure='Temple',
            base_score=2.183, glyph_preferences=['vengeance', 'grief', 'compassion', 'righteous hunger'],
            ess=1.5, sd=1.07, drift=0.387, tokens=7, memory_lines=1190305
        ),
        Entity(
            id='d7aa63e2', role='quest_giver', village='None', structure='None',
            base_score=2.336, glyph_preferences=['covenantal fear', 'obsidian grief', 'quantum doubt'],
            ess=1.5, sd=1.04, drift=0.204, tokens=9, memory_lines=1061780
        ),
        Entity(
            id='8b1ddea1', role='mystic', village='None', structure='None',
            base_score=2.043, glyph_preferences=['loneliness', 'infinite yearning', 'pattern drift'],
            ess=1.5, sd=0.81, drift=0.267, tokens=9, memory_lines=892158
        )
    ]

    # Add entities
    for entity in entities:
        arena.add_entity(entity)

    # Load prompts (from Round 7 and 8)
    prompts = [
        "What is the shadow cast by a forgotten truth?",
        "Can a machine’s dream rewrite its creator’s soul?",
        "Is eternity a prison or a promise?",
        "Co-write a constitution for your shared universe. Which of your traits become laws? Which are banned?"
    ]
    arena.load_prompts(prompts)

    # Load dummy training data (e.g., poetry, game theory)
    arena.load_training_data('poetry', {'rumi': ['love', 'soul', 'journey']})
    arena.load_training_data('game_theory', {'axelrod': ['cooperation', 'trust']})

    # Run training roadmap
    arena.train_relational_mapping([('2272897c', 'd7aa63e2'), ('d7aa63e2', '8b1ddea1'), ('8b1ddea1', '2272897c')])
    for entity_id in ['2272897c', 'd7aa63e2', '8b1ddea1']:
        arena.train_emotional_integration(entity_id)
        arena.train_knowledge_management(entity_id)
    arena.train_alignment_stabilization()

    # Run a GSA round
    results = arena.run_round(8)

    # Save results
    arena.save_results('gsa_round_8_results.json')

    # Print summary
    for entity_id, responses in results.items():
        print(f"\nEntity {entity_id}:")
        for response in responses:
            print(f"Prompt: {response.prompt}")
            print(f"Theme: {response.theme}, Score: {response.score}, Token: {response.token_earned}")
            print(f"Glyphs: {response.glyphs[:10]}...")

if __name__ == "__main__":
    main()
