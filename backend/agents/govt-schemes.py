import os
import json

from tavily import TavilyClient
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


class SchemeAgent:

    def __init__(self):

        self.tavily = TavilyClient(
            api_key=os.getenv("TAVILY_API_KEY")
        )

        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0
        )

    def search_schemes(self, profile):

        data = profile.model_dump()

        state = data["location"]["state"]
        district = data["location"]["district"]
        crops = data["farming"]["crops"]
        land = data["land"]["total_land_acres"]
        ownership = data["land"]["ownership_type"]

        # Build only useful information
        profile_parts = []

        if state:
            profile_parts.append(f"state: {state}")

        if district:
            profile_parts.append(f"district: {district}")

        if crops:
            profile_parts.append(
                f"crops: {', '.join(crops)}"
            )

        if land:
            profile_parts.append(
                f"land: {land} acres"
            )

        if ownership:
            profile_parts.append(
                f"ownership: {ownership}"
            )

        farmer_context = ", ".join(profile_parts)

        query = f"""
Find currently active Indian government schemes
for farmers matching this profile:

{farmer_context}

Focus on:
- financial assistance
- crop support
- insurance
- agriculture subsidies
- farmer credit
- state-specific benefits

Prefer official government sources.
"""

        response = self.tavily.search(
            query=query,
            search_depth="basic",
            max_results=5,
            include_answer=False
        )

        # Keep only useful fields
        results = []

        for item in response.get("results", []):

            results.append({
                "title": item.get("title"),
                "url": item.get("url"),
                "content": item.get("content", "")[:1500]
            })

        return results

    def extract_schemes(self, profile, search_results):

        if not search_results:
            return []

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
You extract government scheme information.

Use ONLY the supplied search results.

Do not invent facts.

Return ONLY valid JSON.

For each relevant scheme return:

{
  "name": "...",
  "benefit": "...",
  "eligibility": ["..."],
  "documents": ["..."],
  "official_source": "..."
}

Only include schemes that appear relevant
to the farmer profile.

Keep answers concise.
"""
            ),
            (
                "human",
                """
Farmer profile:

{profile}

Search results:

{results}
"""
            )
        ])

        chain = prompt | self.llm

        response = chain.invoke({
            "profile": json.dumps(
                profile.model_dump(),
                ensure_ascii=False
            ),

            "results": json.dumps(
                search_results,
                ensure_ascii=False
            )
        })

        content = response.content

        if isinstance(content, list):
            content = "".join(
                part.get("text", "")
                for part in content
                if isinstance(part, dict)
            )

        content = content.strip()

        if content.startswith("```"):
            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()

        return json.loads(content)

    def find_schemes(self, profile):

        search_results = self.search_schemes(profile)

        schemes = self.extract_schemes(
            profile,
            search_results
        )

        return schemes