import re
from typing import List

US_STATES = {
    "ALABAMA", "ALASKA", "ARIZONA", "ARKANSAS", "CALIFORNIA", "COLORADO",
    "CONNECTICUT", "DELAWARE", "FLORIDA", "GEORGIA", "HAWAII", "IDAHO",
    "ILLINOIS", "INDIANA", "IOWA", "KANSAS", "KENTUCKY", "LOUISIANA",
    "MAINE", "MARYLAND", "MASSACHUSETTS", "MICHIGAN", "MINNESOTA",
    "MISSISSIPPI", "MISSOURI", "MONTANA", "NEBRASKA", "NEVADA",
    "NEW HAMPSHIRE", "NEW JERSEY", "NEW MEXICO", "NEW YORK",
    "NORTH CAROLINA", "NORTH DAKOTA", "OHIO", "OKLAHOMA", "OREGON",
    "PENNSYLVANIA", "RHODE ISLAND", "SOUTH CAROLINA", "SOUTH DAKOTA",
    "TENNESSEE", "TEXAS", "UTAH", "VERMONT", "VIRGINIA", "WASHINGTON",
    "WEST VIRGINIA", "WISCONSIN", "WYOMING", "DISTRICT OF COLUMBIA"
}

US_PLATE_SLOGANS = {
    "THE GOLDEN STATE", "GOLDEN STATE",
    "EMPIRE STATE", "EXCELSIOR",
    "SUNSHINE STATE", "IN GOD WE TRUST",
    "LONE STAR STATE", "THE LONE STAR STATE",
    "GARDEN STATE", "LAND OF LINCOLN",
    "FIRST STATE", "OCEAN STATE",
    "CONSTITUTION STATE", "GREEN MOUNTAIN STATE",
    "KEYSTONE STATE", "TAR HEEL STATE",
    "PEACH STATE", "ALOHA STATE",
    "GREAT LAKE STATE", "PURE MICHIGAN",
    "EXPLORE MINNESOTA", "SHOW ME STATE",
    "SPORTSMANS PARADISE", "VACATIONLAND",
    "BEAUTIFUL BRITISH COLUMBIA", "WILD ROSE COUNTRY",
    "DMV", "CA.GOV", "NY.GOV", "MYFLORIDA.COM", "TEXAS.GOV"
}

CHINESE_PROVINCES = set("京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领")


def clean_markdown_and_wrappers(raw_text: str) -> str:
    text = raw_text.strip()
    
    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if code_block_match:
        text = code_block_match.group(1).strip()

    if text.startswith("{") and text.endswith("}"):
        try:
            import json
            data = json.loads(text)
            if isinstance(data, dict):
                if "text" in data:
                    text = str(data["text"]).strip()
                elif "transcription" in data:
                    text = str(data["transcription"]).strip()
        except Exception:
            match = re.search(r'"(?:text|transcription)"\s*:\s*"([^"]+)"', text, re.IGNORECASE)
            if match:
                text = match.group(1).strip()
        
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        text = text[1:-1].strip()
    if text.startswith('“') and text.endswith('”'):
        text = text[1:-1].strip()

    intro_pattern = (
        r"^(?:here\s+(?:is|are)\s+(?:the\s+)?(?:transcription|text|characters|license\s*plate|sign)?(?:\s+of\s+the\s+[a-z\s]+)?\s*:\s*|"
        r"(?:the\s+)?(?:text|image|sign|plate)(?:\s+in\s+the\s+image)?\s+(?:is|reads|says|shows)?\s*:\s*|"
        r"(?:transcription|output|result|license\s*plate|sign(?:\s*text)?)\s*:\s*|"
        r"^i\s+(?:can\s+)?see\s*:\s*)"
    )
    text = re.sub(intro_pattern, "", text, flags=re.IGNORECASE).strip()
        
    return text


def is_chinese_plate(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if stripped[0] in CHINESE_PROVINCES:
        return True
    if len(stripped) > 1 and stripped[1] in CHINESE_PROVINCES:
        return True
    return False


def is_banner_or_url(line: str) -> bool:
    upper = line.upper().strip()
    if upper in US_STATES or upper in US_PLATE_SLOGANS:
        return True
    if re.search(r"\b(?:[a-z0-9_\-\.]+\.(?:gov|com|org|us|edu|net))\b", line, re.IGNORECASE):
        return True
    if re.search(r"\b(?:dmv|ca\.gov|ny\.gov)\b", line, re.IGNORECASE):
        return True
    return False


def clean_us_license_plate(text: str) -> str:
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return text.strip()

    filtered_lines = [line for line in lines if not is_banner_or_url(line)]
    candidate = " ".join(filtered_lines).strip() if filtered_lines else text.strip()

    for state in sorted(US_STATES, key=len, reverse=True):
        candidate = re.sub(rf"\b{re.escape(state)}\b", "", candidate, flags=re.IGNORECASE).strip()

    for slogan in sorted(US_PLATE_SLOGANS, key=len, reverse=True):
        candidate = re.sub(rf"\b{re.escape(slogan)}\b", "", candidate, flags=re.IGNORECASE).strip()

    state_words = {
        "CALIFORNIA", "NEW", "YORK", "TEXAS", "FLORIDA", "ILLINOIS", "PENNSYLVANIA", "OHIO", "MICHIGAN",
        "GEORGIA", "NORTH", "SOUTH", "CAROLINA", "VIRGINIA", "WASHINGTON", "ARIZONA", "MASSACHUSETTS",
        "TENNESSEE", "INDIANA", "MISSOURI", "MARYLAND", "WISCONSIN", "COLORADO", "MINNESOTA",
        "EMPIRE", "STATE", "GOLDEN", "SUNSHINE", "EXCELSIOR", "DMV"
    }
    # Only remove isolated state words if substantial registration characters remain
    test_candidate = candidate
    for word in state_words:
        test_candidate = re.sub(rf"\b{re.escape(word)}\b", "", test_candidate, flags=re.IGNORECASE).strip()
    if len(re.sub(r"\s+", "", test_candidate)) >= 3:
        candidate = test_candidate

    candidate = re.sub(r"\b(?:[a-z0-9_\-\.]+\.(?:gov|com|org|us|net))\b", "", candidate, flags=re.IGNORECASE).strip()
    candidate = re.sub(r"\s+", " ", candidate).strip()

    # If format is "1234 ABC" (digits before letters on standard US plates), reorder if typical "ABC 1234"
    parts = candidate.split()
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isalpha():
        candidate = f"{parts[1]} {parts[0]}"
    return candidate


def postprocess_transcription(raw_text: str) -> str:
    if not raw_text:
        return ""

    cleaned = clean_markdown_and_wrappers(raw_text)

    if is_chinese_plate(cleaned):
        lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
        chinese_text = "".join(lines) if len(lines) > 1 else lines[0]
        return re.sub(r"\s+", " ", chinese_text).strip()

    cleaned_plate = clean_us_license_plate(cleaned)
    lines = [line.strip() for line in cleaned_plate.split("\n") if line.strip()]
    return re.sub(r"[ \t]+", " ", " ".join(lines)).strip()


def evaluator_normalize(text: str) -> str:
    t = text.upper()
    t = re.sub(r"\s+", "", t)
    t = re.sub(r"[\-\.·_]", "", t)
    return t
