from openai import OpenAI
from dotenv import load_dotenv
import json, os
from ..types import SalesOrderEmail
from dateutil import parser
from typing import Optional, Tuple

load_dotenv()

class GPT:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.schema = self.load_schema()
        self.system_prompt = self.load_system_prompt()

    def load_schema(self):
        schema_path = os.path.join(os.path.dirname(__file__), "entity_recognition_schema.json")
        with open(schema_path, "r") as f:
            return json.load(f)

    def load_system_prompt(self):
        prompt_path = os.path.join(os.path.dirname(__file__), "systm_prompt.txt")
        with open(prompt_path, "r") as f:
            return f.read()
        
    def clean_response(self, model_response: SalesOrderEmail)->SalesOrderEmail:
        date_time = model_response.get("date_time", None)
        if not date_time:
            pass
        else:
            parsed_date = parser.parse(date_time)
            model_response["date_time"] = parsed_date.strftime('%Y-%m-%d') 
        
        return model_response

    def recognize(self, text: str) -> Tuple[Optional[SalesOrderEmail], bool]:
        response = self.client.responses.create(
        model="gpt-4.1",
        input=[
            {
            "role": "system",
            "content": [
                {
                "type": "input_text",
                "text": self.system_prompt
                }
            ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": text
                    }
                ]
            }

        ],
        text=self.schema,
        reasoning={},
        tools=[
        ],
        temperature=0.67,
        max_output_tokens=2048,
        top_p=1,
        store=True
        )

        try:
            model_response = json.loads(response.output_text)
            return self.clean_response(model_response), True

        except Exception as e:
            print(f"Error parsing response: {e}")
            return None, False


    