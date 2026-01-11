#!/usr/bin/env python3
# Library import
import argparse
import json
import sys
from src.data.classes import Text, PersonalizeProfile

# Main execution (for CLI)
def main() -> None:
    # Parameters configuration
    parser = argparse.ArgumentParser(
        prog="sparky",
        description=(
            "Sparky is a CLI tool that performs text personalization "
            "using structured data profiles."
        ),
        allow_abbrev=False
    )

    parser.add_argument(
        "--text",
        required=True,
        help="Text containing personalization tokens (e.g. {{USER.NAME}})"
    )

    parser.add_argument(
        "--profile",
        help="JSON string with the data profile"
    )

    parser.add_argument(
        "--profile-file",
        help="Path to a JSON file with the data profile"
    )
    
    args = parser.parse_args()

    # Validate arguments and get data
    if args.profile_file:
        with open(args.profile_file, "r", encoding="utf-8") as f:
            profile_data = json.load(f)
    elif args.profile:
        raw = args.profile.strip()

        # PowerShell may pass surrounding single quotes
        if raw.startswith("'") and raw.endswith("'"):
            raw = raw[1:-1]

        profile_data = json.loads(raw)
    else:
        parser.error("You must provide --profile or --profile-file")

    text = Text(args.text)
    profile = PersonalizeProfile(profile_data)

    result = profile.personalize_text(text)
    print(result, end="")

# Execute the main application CLI
if __name__ == "__main__":
    main()
