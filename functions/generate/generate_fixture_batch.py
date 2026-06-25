#!/usr/bin/env python3
"""Generate source-art fixtures using the product prompt contract."""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from generate import handler  # noqa: E402
from stitch_prompt import STITCHABLE_SOURCE_SYSTEM_PROMPT  # noqa: E402


DEFAULT_CASES = {
    "leaf_single_smooth": "a green leaf",
    "leaf_two_tone": "a green leaf with a darker green lower edge",
    "flower_daisy_simple": "a simple daisy",
    "flower_sunflower_simple": "a simple sunflower",
    "cartoon_elephant": "a pink elephant",
    "bee_simple": "a simple bumblebee",
    "badge_circle_star": "a blue circle badge with a white star cutout",
}


def _parse_case(values: list[str] | None) -> dict[str, str]:
    if not values:
        return DEFAULT_CASES
    cases = {}
    for value in values:
        if "=" not in value:
            raise SystemExit("--case must be in the form slug=user prompt")
        slug, prompt = value.split("=", 1)
        slug = slug.strip().replace("-", "_")
        prompt = prompt.strip()
        if not slug or not prompt:
            raise SystemExit("--case must include both slug and user prompt")
        cases[slug] = prompt
    return cases


def _generate(slug: str, user_prompt: str, out_dir: Path) -> dict:
    response = handler(
        {
            "httpMethod": "POST",
            "body": json.dumps(
                {
                    "userPrompt": user_prompt,
                    "useSystemPrompt": True,
                    "systemPrompt": STITCHABLE_SOURCE_SYSTEM_PROMPT,
                }
            ),
        },
        None,
    )
    status = int(response.get("statusCode", 500))
    body = json.loads(response.get("body") or "{}")

    case_dir = out_dir / slug
    case_dir.mkdir(parents=True, exist_ok=True)
    (case_dir / "response.json").write_text(json.dumps(body, indent=2, sort_keys=True))
    (case_dir / "system_prompt.txt").write_text(STITCHABLE_SOURCE_SYSTEM_PROMPT + "\n")
    (case_dir / "user_prompt.txt").write_text(user_prompt + "\n")

    if status == 200 and body.get("imageBase64"):
        (case_dir / "source.png").write_bytes(base64.b64decode(body["imageBase64"]))

    return {
        "slug": slug,
        "userPrompt": user_prompt,
        "status": status,
        "error": body.get("error"),
        "artifactDir": str(case_dir),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="tmp/product_prompt_generation")
    parser.add_argument("--case", action="append", help="Repeatable: slug=user prompt")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "system_prompt.txt").write_text(STITCHABLE_SOURCE_SYSTEM_PROMPT + "\n")

    results = [_generate(slug, prompt, out_dir) for slug, prompt in _parse_case(args.case).items()]
    (out_dir / "summary.json").write_text(json.dumps(results, indent=2, sort_keys=True))
    print(json.dumps(results, indent=2, sort_keys=True))

    failures = [result for result in results if result["status"] != 200]
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
