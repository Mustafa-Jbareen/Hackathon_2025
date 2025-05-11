# ------------------- Imports ---------------------

import json
import logging
from openai import OpenAI
from my_secrets import OPENROUTER_API_KEY, OPENROUTER_API_BASE,EXA_API_KEY  # Your API settings
from exa_py import Exa


# ------------------- Logging Setup -------------------

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ------------------- ConflictExtractor Class -------------------

class ConflictExtractor:
    def __init__(self, json_path: str, model_name: str):
        self.json_path = json_path
        self.model_name = model_name
        self.article_text = self._load_article_text()
        self.exa = Exa(api_key=EXA_API_KEY)

        try:
            self.client = OpenAI(
                base_url=OPENROUTER_API_BASE,
                api_key=OPENROUTER_API_KEY
            )
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise

    def _load_article_text(self) -> str:
        try:
            with open(self.json_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            return data.get("text", "")
        except Exception as e:
            logger.error(f"Failed to load article text: {str(e)}")
            raise

    def _build_prompt(self) -> str:
        return f"""
Given the following text, extract:
1. The main idea in conflict.
2. The two sides involved in the conflict, labeling them as 'Side A' and 'Side B'.

Output the result in this format:
Side A: 
Side B: 
Idea of the conflict:

Text:
\"\"\"{self.article_text}\"\"\"
"""

    def extract_conflict(self) -> dict:
        prompt = self._build_prompt()

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )

            result_text = response.choices[0].message.content.strip()
            if not result_text:
                raise ValueError("No valid content returned from the model.")

            logger.info(f"Raw model output:\n{result_text}")
            # Manually parse the structured text
            parsed = {}
            for line in result_text.splitlines():
                if ':' in line:
                    key, value = line.split(':', 1)
                    parsed[key.strip()] = value.strip()

            return parsed

        except Exception as e:
            logger.error(f"An error occurred during extraction: {str(e)}")
            return {"error": str(e)}
        
    from exa_py import Exa

    def search_conflict_urls(self, idea_of_conflict: str, exa_api_key: str , max_results: int = 5) -> list:
        # Initialize Exa client with API key

        try:
            # Use Exa's search_and_contents method to search the query and fetch results
            result = self.exa.search_and_contents(idea_of_conflict, text=True)
            logger.info(f"Raw Exa search results:\n{result}")
            #json.loads(result)

            # Extract URLs from the 'results' field in the response
            #urls = []
            results_list=[]
            if hasattr(result, 'results'):
                for item in result.results[:max_results]:
                    url = getattr(item, 'url', None)
                    text = getattr(item, 'text', None)
                    #if url:
                    #    urls.append({"url": url})
                    if url and text:
                        results_list.append({"url": url, "text": text})
                    elif url:
                        results_list.append({"url": url, "text": ""})
            return results_list

        except Exception as e:
            logger.error(f"Exa API call failed: {str(e)}")
            return [{"error": str(e)}]


    def classify_bias_and_aggregate(self,
        urls_text_json_path: str,
        sides_json_path: str,
        model_client,  # This should be your OpenAI client (extractor.client)
        model_name: str,
        output_path: str = "classified_bias_output.json"
    ):
    # Load the URLs/texts
        with open(urls_text_json_path, "r", encoding="utf-8") as f:
            url_entries = json.load(f)

    # Load the sides and claim
        with open(sides_json_path, "r", encoding="utf-8") as f:
            sides_data = json.load(f)

    # Extract claim and sides
        claim = (
            sides_data.get("Idea of the conflict") or
            sides_data.get("Idea of Conflict") or
            sides_data.get("claim") or
        ""
        )
        side_a = sides_data.get("Side A", "Side A")
        side_b = sides_data.get("Side B", "Side B")

    # Prepare groups for output
        groups = {
            "Group A": {"name": side_a, "sources": []},
            "Group B": {"name": side_b, "sources": []}
        }

    # For each URL/text, classify bias using the model
        for entry in url_entries:
            url = entry.get("url", "")
            text = entry.get("text", "")

            if not text.strip():
                continue  # skip empty texts

        # Build the prompt
            prompt = f"""
    Given the following claim and the two groups, classify whether the provided article text is biased toward Group A or Group B. Only respond with "Group A" or "Group B".

    Claim: {claim}

    Group A: {side_a}
    Group B: {side_b}

    Article text:
    \"\"\"{text}\"\"\"
    """

            try:
                response = model_client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    max_tokens=10
                )
                answer = response.choices[0].message.content.strip()
            # Normalize answer
                if "A" in answer:
                    groups["Group A"]["sources"].append(url)
                elif "B" in answer:
                    groups["Group B"]["sources"].append(url)
                else:
                    logging.warning(f"Unrecognized model response for {url}: {answer}")

            except Exception as e:
                logging.error(f"Error classifying bias for {url}: {e}")

    # Prepare final output
        output = {
            "claim": claim,
            "groups": groups
        }

    # Save to JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"Classification results saved to {output_path}")

        return output

    def run_pipeline(
        self,
        conflict_output_path="conflict_output.json",
        exa_output_path="exa_output.json",
        classified_output_path="classified_bias_output.json",
        exa_max_results=10
    ):
    # Step 1: Extract conflict info from the article
        result = self.extract_conflict()
        self.pretty_print(result)
        self.save_to_json(result, conflict_output_path)

    # Step 2: Get the main idea of conflict
        idea = result.get("Idea of the conflict") or result.get("Idea of Conflict") or ""
        if not idea:
            logger.warning("No idea of conflict found to search URLs.")
            return

    # Step 3: Search for related URLs and save them
        urls = self.search_conflict_urls(idea, EXA_API_KEY, exa_max_results)
        self.save_urls_to_json(urls, exa_output_path)

    # Step 4: Classify bias and aggregate results
        classified = self.classify_bias_and_aggregate(
            urls_text_json_path=exa_output_path,
            sides_json_path=conflict_output_path,
            model_client=self.client,
            model_name=self.model_name,
            output_path=classified_output_path
        )
        logger.info(f"Pipeline complete. Final classified output saved to {classified_output_path}")
        return classified

        
    
        
    def save_urls_to_json(self, urls: list, output_path: str):
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(urls, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved search results to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save URLs JSON: {str(e)}")



    def pretty_print(self, data: dict):
        print(json.dumps(data, indent=2, ensure_ascii=False))

    def save_to_json(self, data: dict, output_path: str):
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved extracted data to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save JSON: {str(e)}")


# Example usage:
# merge_side_fields('source.json', 'destination.json')


# ------------------- Example Usage -------------------

if __name__ == "__main__":
    model_name = "openai/gpt-4.1-nano"  # Or any OpenRouter-supported model
    json_path = "tayaraToMahmoud.json"

    extractor = ConflictExtractor(json_path, model_name)
    extractor.run_pipeline()






