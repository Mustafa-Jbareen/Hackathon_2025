import json
import os
from typing import List, Dict
from openai import OpenAI
from my_secrets import OPENROUTER_API_KEY, OPENROUTER_API_BASE
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class LanguageModel:
    def __init__(self,
                 model_name: str,
                 temperature: float = 0.7,
                 openrouter_api_key: str = OPENROUTER_API_KEY,
                 openrouter_api_base: str = OPENROUTER_API_BASE):
        self.client = OpenAI(base_url=openrouter_api_base, api_key=openrouter_api_key)
        self.model_name = model_name
        self.temperature = temperature

    def ask(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature
        )
        return response.choices[0].message.content

    def __call__(self, prompt: str) -> str:
        return self.ask(prompt)


class DebateSimulator:
    def __init__(self, data: dict, model_name: str = "openai/gpt-4.1-nano", history_file: str = "debate_history.json"):
        self.claim = data["claim"]
        self.groups = {
            "group1": {
                "name": data["groups"]["Group A"]["name"],
                "sources": data["groups"]["Group A"]["sources"]
            },
            "group2": {
                "name": data["groups"]["Group B"]["name"],
                "sources": data["groups"]["Group B"]["sources"]
            }
        }

        self.model = LanguageModel(model_name)
        self.history_file = history_file

        # Reset the history file at initialization
        with open(self.history_file, 'w') as f:
            json.dump({}, f, indent=4)

    def format_sources(self, sources: List[str]) -> str:
        return "\n".join(f"- {source}" for source in sources)

    def read_history(self) -> Dict[str, str]:
        """Reads the history from the JSON file."""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        else:
            return {}

    def write_history(self, history: Dict[str, str]):
        """Writes the updated history back to the JSON file."""
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=4)

    def simulate_debate(self) -> Dict[str, str]:
        """
        Simulates a 2-sentence back-and-forth debate (3 turns per group), appends it to the history,
        and writes back to the JSON file.
        :return: A dictionary with keys "i" (as strings) and values "Group Name: <argument>"
        """
        # Read current history
        history = self.read_history()
        full_session = {}

        for _ in range(2):
            turn = len(history)  # current turn number
            turn_key = str(turn)

            # Determine current group
            current_group_key = "group1" if turn % 2 == 0 else "group2"
            current_group = self.groups[current_group_key]
            group_name = current_group["name"]
            sources = self.format_sources(current_group["sources"])

            # Build debate history string
            debate_history = "\n".join(
                f"{i}: {self.groups['group1' if int(i) % 2 == 0 else 'group2']['name']}: {v}"
                for i, v in history.items()
            )

            # Build the prompt
            # Build the prompt
            prompt = (
                f"You’re part of a friendly, structured chat about the claim:\n"
                f"'{self.claim}'\n\n"
                f"Your role: {group_name}\n"
                f"Here’s what’s been said so far:\n{debate_history}\n\n"
                f"You have these sources to help you make your point:\n{sources}\n\n"
                f"Now add ONE short, natural-sounding sentence that responds directly to the last thing said.\n"
                f"Keep it friendly and conversational—like you're talking to someone you respect but disagree with.\n"
                f"Use one of the sources to support your point, but don't sound too formal.\n"
                f"You can question, agree a little, clarify something, or suggest a middle ground—whatever keeps things respectful and moving forward.\n"
                f"Format it like this:\n"
                f"<your sentence> (Source: <source> only the link)"
                )
            try:
                response = self.model.ask(prompt)
                print(response)
            except Exception as e:
                print(f"[ERROR] Error generating response: {e}")
                response = "[ERROR generating response]"

            # Add to history
            history[turn_key] = response.strip()
            self.write_history(history)

            # Append to result dict
            full_session[turn_key] = f"{group_name}: {response.strip()}"

        return full_session

    def summarize_debate(self) -> Dict[str, str]:
        """
        Summarizes the full debate from a non-biased perspective and optionally gives a verdict.
        :return: A dictionary with key "summary" and a summary + verdict as value
        """
        # Read full debate history
        history = self.read_history()

        # Reconstruct debate history in human-readable format
        debate_text = "\n".join(
            f"{self.groups['group1' if int(i) % 2 == 0 else 'group2']['name']}: {v}"
            for i, v in history.items()
        )

        # Build the summarization prompt
        prompt = (
            f"You are a neutral observer tasked with summarizing the following debate:\n"
            f"Claim: {self.claim}\n\n"
            f"Debate Transcript:\n{debate_text}\n\n"
            f"Please provide only a very very short, non-biased summary of the debate.\n"
            f"Then, offer very very short a non-biased final verdict on the debate, based only on the arguments provided."
        )

        try:
            print("\n[Summary Requesting from model...]")
            summary_response = self.model.ask(prompt)
            print(summary_response)
        except Exception as e:
            print(f"[ERROR] Error generating summary: {e}")
            summary_response = "[ERROR generating summary]"

        return {"summary": summary_response.strip()}
