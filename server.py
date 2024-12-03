from fastapi import FastAPI
import strawberry
from strawberry.fastapi import GraphQLRouter
from typing import List
from openai import OpenAI

# Get the OpenAI API key from the environment
import os
from dotenv import load_dotenv
load_dotenv()

# Set your OpenAI API key here
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@strawberry.type
class TranslationResponse:
    language: str
    translation: str


@strawberry.type
class Query:
    @strawberry.field
    async def get_translation(self, content: str, target_languages: List[str]) -> List[TranslationResponse]:
        translations = []
        for lang in target_languages:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": f"Translate the following text into {lang}:\n\n{content}"}
                    ]
                )
                print(response.choices)
                translated_text = response.choices[0].message.content.strip()
                translations.append(TranslationResponse(
                    language=lang, translation=translated_text))
            except Exception as e:
                translations.append(TranslationResponse(
                    language=lang, translation=f"Error: {str(e)}"))
        return translations


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

# Run with: uvicorn filename:app --reload
