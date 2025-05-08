

import json
import os
import logging
from typing import List, Dict
from openai import OpenAI
from my_secrets import OPENROUTER_API_KEY, OPENROUTER_API_BASE

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Define the LanguageModel wrapper
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

    def ask_stream(self, prompt: str):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def __call__(self, prompt: str) -> str:
        return self.ask(prompt)


# Main class for simulating a debate
class DebateSimulator:
    def __init__(self, data: dict, model_name: str = "google/gemma-7b-it:free"):
        self.claim = data["claim"]
        self.groups = {
            "group1": {
                "name": data["group1"]["name"],
                "sources": data["group1"]["sources"]
            },
            "group2": {
                "name": data["group2"]["name"],
                "sources": data["group2"]["sources"]
            }
        }
        self.model = LanguageModel(model_name)

    def format_sources(self, sources: List[str]) -> str:
        return "\n".join(f"- {source}" for source in sources)

    def simulate_chat_debate(self):
        print("=== Starting Debate ===\n")
        group_infos = [self.groups["group1"], self.groups["group2"]]
        history = []

        for round_num in range(2):  # Change number of rounds as needed
            for group_info in group_infos:
                name = group_info["name"]
                sources = self.format_sources(group_info["sources"])

                # Build prompt
                prompt = (
                    f"You are representing '{name}' in a formal debate.\n"
                    f"Claim: {self.claim}\n\n"
                    f"Debate History:\n" +
                    "\n".join(f"{entry['speaker']}: {entry['content']}" for entry in history) +
                    f"\n\nYour sources:\n{sources}\n\n"
                    f"Respond concisely in this format:\n"
                    f"Point: <your argument>\nSource: <cite your source(s)>"
                )

                print(f"\n{name} says:")
                streamed = ""
                try:
                    for token in self.model.ask_stream(prompt):
                        print(token, end="", flush=True)
                        streamed += token
                    print("\n" + "-" * 40)
                except Exception as e:
                    print(f"\n[ERROR streaming response]: {e}")

                history.append({"speaker": name, "content": streamed.strip()})


# Example input data
sample_json_data = {
    "claim": "Climate change is primarily driven by human activity.",
    "group1": {
        "name": "Climate Scientists",
        "sources": [
            "https://www.ipcc.ch/report/ar6/",
            "https://www.nature.com/articles/s41586-019-1711-1"
        ]
    },
    "group2": {
        "name": "Climate Skeptics",
        "sources": [
            "https://www.heritage.org/environment/report/the-dubious-science-climate-alarmism",
            "https://wattsupwiththat.com/"
        ]
    }
}


# Run it
if __name__ == "__main__":
    model_name = "google/gemma-3-4b-it:free"  # or "openai/gpt-4-vision-preview" if supported
    simulator = DebateSimulator(sample_json_data, model_name)
    simulator.simulate_chat_debate()

