import json

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from farmerSchema import FarmerProfile


class ProfileAgent:

    def __init__(self):

        # This is the AI model used by the Profile Agent
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0
        )


    def process(self, message, profile):

        # ==========================================
        # STEP 1: Understand what the farmer said
        # ==========================================

        extracted = self.extract_information(
            message,
            profile
        )


        # ==========================================
        # STEP 2: Update the farmer profile
        # ==========================================

        updated_profile = self.update_profile(
            profile,
            extracted
        )


        # ==========================================
        # STEP 3: Check what information is missing
        # ==========================================

        missing_information = self.find_missing_information(
            updated_profile
        )


        # ==========================================
        # STEP 4: Decide what to ask next
        # ==========================================

        next_question = self.get_next_question(
            missing_information
        )


        # ==========================================
        # Return everything
        # ==========================================

        return {
            "profile": updated_profile,
            "extracted": extracted,
            "missing_information": missing_information,
            "next_question": next_question
        }


    # ==================================================
    # 1. EXTRACT INFORMATION
    # ==================================================

    def extract_information(self, message, profile):

        current_profile = profile.model_dump()

        prompt = ChatPromptTemplate.from_messages([

            (
                "system",
                """
You are the Profile Agent of a farmer
government-benefit assistant.

Your job is to understand what the farmer says
and extract useful information about the farmer.

IMPORTANT RULES:

1. Extract EVERY useful fact mentioned by the farmer.

2. Never invent information.

3. Never assume information.

4. If the farmer does not mention something,
   do not create a value for it.

5. If the farmer corrects previous information,
   use the new information.

6. One sentence can contain multiple facts.

7. Understand Hindi, Hinglish and English.

8. Convert common Hindi farming information
   into simple English values where appropriate.

Examples:

"mere paas 3 acre zameen hai"
→ total_land_acres = 3

"main gehun ugata hoon"
→ crops = ["wheat"]

"meri age 45 saal hai"
→ age = 45

"zameen mere naam par hai"
→ ownership_type = "owned"

9. Do NOT decide whether the farmer is eligible
   for any government scheme.

10. Do NOT recommend schemes.

11. Return ONLY JSON.

Current profile:

{profile}

Return ONLY the information newly learned
from the farmer's message.

Example:

Farmer:
"Mera naam Ramesh hai aur mere paas 3 acre zameen hai."

Return:

{{
    "personal": {{
        "name": "Ramesh"
    }},
    "land": {{
        "total_land_acres": 3
    }}
}}

If the farmer gives no useful profile information:

{{}}
"""
            ),

            (
                "human",
                """
Farmer message:

{message}
"""
            )
        ])


        chain = prompt | self.llm


        response = chain.invoke({

            "profile": json.dumps(
                current_profile,
                ensure_ascii=False
            ),

            "message": message
        })


        content = response.content


        # Sometimes the model returns a list
        if isinstance(content, list):

            content = "".join(
                part.get("text", "")
                for part in content
                if isinstance(part, dict)
            )


        content = content.strip()


        # Remove markdown JSON block if model adds it
        if content.startswith("```"):

            content = content.replace(
                "```json",
                ""
            )

            content = content.replace(
                "```",
                ""
            )

            content = content.strip()


        return json.loads(content)


    # ==================================================
    # 2. UPDATE PROFILE
    # ==================================================

    def update_profile(self, profile, extracted):

        # Convert Pydantic profile into dictionary
        data = profile.model_dump()


        # Go through every section
        for section, values in extracted.items():

            # Ignore unknown sections
            if section not in data:
                continue


            # Make sure section contains a dictionary
            if not isinstance(values, dict):
                continue


            # Go through every field
            for field, value in values.items():

                # Don't update with empty/null values
                if value is None:
                    continue


                # Don't overwrite a list with an empty list
                if isinstance(value, list) and len(value) == 0:
                    continue


                # Update the profile
                if field in data[section]:

                    data[section][field] = value


        # Convert dictionary back to FarmerProfile
        return FarmerProfile.model_validate(data)


    # ==================================================
    # 3. FIND MISSING INFORMATION
    # ==================================================

    def find_missing_information(self, profile):

        data = profile.model_dump()


        # Information we currently want
        required_fields = [

            ("personal", "name"),

            ("personal", "age"),

            ("location", "state"),

            ("location", "district"),

            ("land", "ownership_type"),

            ("land", "total_land_acres"),

            ("farming", "crops")
        ]


        missing = []


        for section, field in required_fields:

            value = data[section][field]


            if value is None:

                missing.append(
                    f"{section}.{field}"
                )


            elif value == []:

                missing.append(
                    f"{section}.{field}"
                )


        return missing


    # ==================================================
    # 4. DECIDE NEXT QUESTION
    # ==================================================

    def get_next_question(self, missing_information):

        if not missing_information:

            return None


        # Questions for missing information
        questions = {

            "personal.name":
                "Aapka naam kya hai?",

            "personal.age":
                "Aapki umar kitni hai?",

            "location.state":
                "Aap kis rajya mein kheti karte hain?",

            "location.district":
                "Aap kis district mein kheti karte hain?",

            "land.ownership_type":
                "Kya zameen aapke naam par hai?",

            "land.total_land_acres":
                "Aapke paas kul kitni zameen hai?",

            "farming.crops":
                "Aap kaunsi fasal ugate hain?"
        }


        # Take the first missing field
        next_field = missing_information[0]


        return questions.get(
            next_field,
            "Kripya iske baare mein thodi aur jankari dein."
        )