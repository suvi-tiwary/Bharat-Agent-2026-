class EligibilityAgent:

    def check_scheme(self, profile, scheme):

        data = profile.model_dump()

        missing = []
        satisfied = []

        for rule in scheme.get("eligibility", []):

            rule_text = rule.lower()

            # We will expand these rules gradually.
            # For now, identify rules requiring information.

            if "state" in rule_text:
                state = data["location"]["state"]

                if state is None:
                    missing.append("location.state")
                else:
                    satisfied.append("location.state")

            elif "land" in rule_text or "acre" in rule_text:
                land = data["land"]["total_land_acres"]

                if land is None:
                    missing.append("land.total_land_acres")
                else:
                    satisfied.append("land.total_land_acres")

            elif "crop" in rule_text:
                crops = data["farming"]["crops"]

                if not crops:
                    missing.append("farming.crops")
                else:
                    satisfied.append("farming.crops")

        if missing:

            status = "more_information_needed"

        else:

            # At this stage, all required information
            # has been collected.
            status = "ready_for_verification"

        return {
            "scheme": scheme["name"],
            "status": status,
            "missing_information": missing,
            "satisfied_information": satisfied
        }

    def check_all(self, profile, schemes):

        results = []

        for scheme in schemes:

            result = self.check_scheme(
                profile,
                scheme
            )

            results.append(result)

        return results