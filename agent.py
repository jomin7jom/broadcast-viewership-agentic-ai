
import os
import json
from datetime import date
from decimal import Decimal

from dotenv import load_dotenv
from openai import OpenAI

from tools import get_network_ratings, get_etl_audit

load_dotenv()
client = OpenAI()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")

# Define the tools available to the AI model
TOOLS = [
    {
        "type": "function",
        "name": "get_network_ratings",
        "description": (
            "Retrieve TV program ratings for a network "
            "on a specified date and the preceding day."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "network": {
                    "type": "string",
                    "description": "TV network, e.g. ABC or CBS"
                },
                "business_date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format"
                }
            },
            "required": ["network", "business_date"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "get_etl_audit",
        "description": (
            "Retrieve ETL pipeline execution status, "
            "source rows, target rows and errors "
            "for a network and business date."
        ),
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "network": {
                    "type": "string",
                    "description": "TV network, e.g. ABC or CBS"
                },
                "business_date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format"
                }
            },
            "required": ["network", "business_date"],
            "additionalProperties": False
        }
    }
]

FUNCTIONS = {
    "get_network_ratings": get_network_ratings,
    "get_etl_audit": get_etl_audit
}

INSTRUCTIONS = """
You are an enterprise TV ratings data analyst.

Use the available database tools to investigate
business questions.

When investigating a viewership decline:
1. Retrieve network ratings.
2. Compare the relevant dates and programs.
3. Check ETL audit records.
4. Explain findings using actual tool results.

Never invent database records.
Never claim an ETL failure caused a decline
unless the available evidence establishes causation.
Clearly distinguish correlation from root cause.

The tools are read-only.
Do not request data modifications.
"""

def investigate(question):
    messages = [
        {"role": "user", "content": question}
    ]

    for round_number in range(5):
        response = client.responses.create(
            model=MODEL,
            instructions=INSTRUCTIONS,
            input=messages,
            tools=TOOLS,
            store=False
        )

        messages.extend(response.output)

        calls = [
            item for item in response.output
            if item.type == "function_call"
        ]

        if not calls:
            return response.output_text

        for call in calls:
            print(f"\nAI selected tool: {call.name}")

            try:
                if call.name not in FUNCTIONS:
                    raise ValueError("Unknown tool")

                args = json.loads(call.arguments)

                if set(args) != {
                    "network", "business_date"
                }:
                    raise ValueError("Invalid arguments")

                date.fromisoformat(args["business_date"])

                result = FUNCTIONS[call.name](**args)

                print(f"Rows returned: {len(result)}")

                output = json.dumps(
                    result,
                    default=lambda value: (
                        float(value)
                        if isinstance(value, Decimal)
                        else str(value)
                    )
                )

            except (ValueError, TypeError, KeyError) as exc:
                output = json.dumps({
                    "error": "Invalid tool arguments"
                })

            except Exception:
                output = json.dumps({
                    "error": "Database tool execution failed"
                })

            messages.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": output
            })

    return "Investigation stopped: tool-call limit reached."


if __name__ == "__main__":
    question = (
        "Why did ABC viewership drop on "
        "2026-10-30? Check the ETL audit."
    )

    print("\nUSER QUESTION:")
    print(question)

    print("\nAGENT INVESTIGATION:")
    answer = investigate(question)

    print("\nFINAL AI ANSWER:")
    print(answer)
