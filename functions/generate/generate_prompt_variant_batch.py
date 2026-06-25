#!/usr/bin/env python3
"""Generate and stitch-test system-prompt variants.

The product flow has one reusable system prompt plus short user requests. This
runner keeps that shape intact: each variant changes only the system prompt,
then runs the same natural prompts through generation and stitch acceptance.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BACKEND = ROOT / "website" / "embroidery-stitch-backend"
sys.path.insert(0, str(HERE))

from generate import handler  # noqa: E402
from stitch_prompt import STITCHABLE_SOURCE_SYSTEM_PROMPT  # noqa: E402


PROMPT_VARIANTS = {
    "baseline": STITCHABLE_SOURCE_SYSTEM_PROMPT,
    "large_fields": STITCHABLE_SOURCE_SYSTEM_PROMPT
    + """

Additional conversion guidance:
- Prefer one large filled color region for each major body part.
- Avoid splitting one body part into many small patches.
- Avoid decorative internal contour lines. Use filled color shapes instead.
- If the subject needs markings, use one or two large closed color patches, not many small marks.
- Eyes, beaks, feet, noses, and cheeks should be simple bold filled shapes.
- Leave small highlights out unless they are essential to recognizing the subject.
""",
    "patch_icon": STITCHABLE_SOURCE_SYSTEM_PROMPT
    + """

Additional conversion guidance:
- Make the result look like a clean sticker cutout before embroidery conversion.
- Use bold silhouettes and broad, connected color fields.
- Use black outlines only as structural borders between regions.
- Do not add sketch lines, feather lines, fur lines, wrinkles, shine marks, tiny claws, tiny toes, or nested eye details.
- Simplify anatomy aggressively when needed so every visible color area is large enough to trace.
- For animals, use a round body, simple wings/ears/legs, dot eyes, and one clear accent color for beak/feet/nose if needed.
""",
    "patch_large_fields": STITCHABLE_SOURCE_SYSTEM_PROMPT
    + """

Additional conversion guidance:
- Make the result look like a clean sticker cutout before embroidery conversion.
- Use bold silhouettes and broad, connected color fields.
- Prefer one large filled color region for each major body part.
- Use flat color only inside each region. No soft shading, gradients, or airbrush transitions.
- Avoid splitting one body part into many small patches.
- Use black outlines only as structural borders between regions.
- Avoid decorative internal contour lines, sketch lines, feather lines, fur lines, wrinkles, shine marks, tiny claws, tiny toes, nested eye details, and repeated tiny marks.
- If the subject needs markings, use one or two large closed color patches, not many small marks.
- Eyes, beaks, feet, noses, and cheeks should be simple bold filled shapes.
- Simplify anatomy aggressively when needed so every visible color area is large enough to trace.
- Leave small highlights out unless they are essential to recognizing the subject.
""",
}


DEFAULT_CASES = {
    "cute_sparrow": "a cute sparrow",
    "pink_elephant": "a pink elephant",
    "green_leaf": "a green leaf",
    "simple_sunflower": "a simple sunflower",
    "blue_whale": "a blue whale",
    "yellow_duck": "a yellow duck",
    "brown_bear": "a brown bear",
    "green_frog": "a green frog",
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


def _parse_variant(values: list[str] | None) -> dict[str, str]:
    if not values:
        return PROMPT_VARIANTS
    variants = {}
    for name in values:
        if name not in PROMPT_VARIANTS:
            raise SystemExit(f"Unknown variant {name!r}; choose one of {sorted(PROMPT_VARIANTS)}")
        variants[name] = PROMPT_VARIANTS[name]
    return variants


def _generate_one(slug: str, user_prompt: str, system_prompt: str, fixture_dir: Path, sample_count: int) -> dict:
    response = handler(
        {
            "httpMethod": "POST",
            "body": json.dumps(
                {
                    "userPrompt": user_prompt,
                    "useSystemPrompt": True,
                    "systemPrompt": system_prompt,
                    "sampleCount": sample_count,
                }
            ),
        },
        None,
    )
    status = int(response.get("statusCode", 500))
    body = json.loads(response.get("body") or "{}")
    body_for_file = {
        **body,
        "imageBase64": "<base64 omitted>" if body.get("imageBase64") else body.get("imageBase64"),
        "candidates": [
            {**candidate, "data": "<base64 omitted>"}
            for candidate in body.get("candidates", [])
        ],
    }
    (fixture_dir / f"{slug}.response.json").write_text(json.dumps(body_for_file, indent=2, sort_keys=True))
    (fixture_dir / f"{slug}.user.txt").write_text(user_prompt + "\n")
    if status == 200 and body.get("imageBase64"):
        (fixture_dir / f"{slug}.png").write_bytes(base64.b64decode(body["imageBase64"]))
        (fixture_dir / f"{slug}.prompt.txt").write_text(body.get("generationPrompt", "") + "\n")
    return {
        "slug": slug,
        "userPrompt": user_prompt,
        "status": status,
        "error": body.get("error"),
        "selectedCandidateIndex": body.get("selectedCandidateIndex"),
        "sourceQuality": body.get("sourceQuality"),
    }


def _timeout_result(case_name: str, seconds: int) -> dict:
    return {
        "name": case_name,
        "status": 124,
        "error": f"acceptance timed out after {seconds}s",
        "qualityStatus": "timeout",
        "qualityScore": 0,
        "colors": [],
        "stitchCount": None,
        "jumpCount": None,
        "trimCount": None,
        "segmentationComponentCount": None,
        "segmentationTinyComponents": None,
        "droppedColors": [],
    }


def _run_acceptance(fixture_dir: Path, out_dir: Path, timeout_seconds: int = 300) -> tuple[int, str]:
    outputs = []
    combined_results = []
    return_code = 0
    fixture_paths = sorted(fixture_dir.glob("*.png"))
    if not fixture_paths:
        (out_dir / "summary.json").write_text("[]\n")
        (out_dir / "acceptance-output.txt").write_text("No generated PNG fixtures found.\n")
        return 1, "No generated PNG fixtures found.\n"

    for fixture_path in fixture_paths:
        case_name = fixture_path.stem
        case_out_dir = out_dir / case_name
        case_out_dir.mkdir(parents=True, exist_ok=True)
        summary_path = case_out_dir / "summary.json"
        cmd = [
            sys.executable,
            str(BACKEND / "scripts" / "generated_acceptance.py"),
            "--fixture-dir",
            str(fixture_dir.resolve()),
            "--out",
            str(case_out_dir.resolve()),
            "--case",
            case_name,
            "--strict",
        ]
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(BACKEND),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
                timeout=timeout_seconds,
            )
            outputs.append(f"## {case_name}\n\n{proc.stdout}")
            if proc.returncode != 0:
                return_code = proc.returncode
            if summary_path.exists():
                case_results = json.loads(summary_path.read_text())
                combined_results.extend(case_results)
            else:
                combined_results.append(
                    {
                        **_timeout_result(case_name, timeout_seconds),
                        "status": proc.returncode,
                        "error": "acceptance completed without summary.json",
                    }
                )
        except subprocess.TimeoutExpired as exc:
            return_code = 124
            output = exc.stdout or ""
            outputs.append(f"## {case_name}\n\nTimed out after {timeout_seconds}s.\n{output}")
            combined_results.append(_timeout_result(case_name, timeout_seconds))

    (out_dir / "summary.json").write_text(json.dumps(combined_results, indent=2, sort_keys=True))
    (out_dir / "acceptance-output.txt").write_text("\n\n".join(outputs))
    return return_code, "\n\n".join(outputs)


def _run_acceptance_all_at_once(fixture_dir: Path, out_dir: Path) -> tuple[int, str]:
    cmd = [
        sys.executable,
        str(BACKEND / "scripts" / "generated_acceptance.py"),
        "--fixture-dir",
        str(fixture_dir.resolve()),
        "--out",
        str(out_dir.resolve()),
        "--strict",
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(BACKEND),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    (out_dir / "acceptance-output.txt").write_text(proc.stdout)
    return proc.returncode, proc.stdout


def _summarize_variant(acceptance_dir: Path) -> dict:
    summary_path = acceptance_dir / "summary.json"
    if not summary_path.exists():
        return {"cases": []}
    results = json.loads(summary_path.read_text())
    return {
        "cases": [
            {
                "name": result["name"],
                "status": result["status"],
                "qualityStatus": result.get("qualityStatus"),
                "qualityScore": result.get("qualityScore"),
                "colors": result.get("colors") or [],
                "stitches": result.get("stitchCount"),
                "jumps": result.get("jumpCount"),
                "trims": result.get("trimCount"),
                "components": result.get("segmentationComponentCount"),
                "tinyComponents": result.get("segmentationTinyComponents"),
                "droppedColors": [
                    {
                        "hex": color.get("hex"),
                        "reason": color.get("dropReason"),
                        "fraction": color.get("pixelFraction"),
                    }
                    for color in result.get("droppedColors", [])
                ],
            }
            for result in results
        ]
    }


def _write_review(run_dir: Path, results: list[dict]) -> None:
    lines = [
        "# Prompt Variant Review",
        "",
        "Each variant uses the same short user prompts. Only the system prompt changes.",
        "",
        "| Variant | Case | Quality | Colors | Components | Tiny | Jumps | Trims | Dropped colors |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for variant in results:
        for case in variant.get("acceptance", {}).get("cases", []):
            dropped = ", ".join(
                f"{item['hex']}:{item['reason']}({item['fraction']})"
                for item in case.get("droppedColors", [])
            )
            quality = case.get("qualityStatus") or "-"
            if case.get("qualityScore") is not None:
                quality = f"{quality} {case['qualityScore']}"
            lines.append(
                "| {variant} | {case} | {quality} | {colors} | {components} | {tiny} | {jumps} | {trims} | {dropped} |".format(
                    variant=variant["variant"],
                    case=case["name"],
                    quality=quality,
                    colors=len(case.get("colors") or []),
                    components=case.get("components"),
                    tiny=case.get("tinyComponents"),
                    jumps=case.get("jumps"),
                    trims=case.get("trims"),
                    dropped=dropped or "-",
                )
            )
    lines.extend(["", "## Artifact Directories", ""])
    for variant in results:
        lines.append(f"- `{variant['variant']}`: `{variant['artifactDir']}`")
    (run_dir / "review.md").write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(ROOT / "tmp" / "prompt_variant_generation"))
    parser.add_argument("--case", action="append", help="Repeatable: slug=user prompt")
    parser.add_argument("--variant", action="append", choices=sorted(PROMPT_VARIANTS))
    parser.add_argument("--sample-count", type=int, default=4)
    parser.add_argument("--skip-acceptance", action="store_true")
    args = parser.parse_args()

    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit("GEMINI_API_KEY is not set in this shell.")

    run_dir = Path(args.out)
    run_dir.mkdir(parents=True, exist_ok=True)
    cases = _parse_case(args.case)
    variants = _parse_variant(args.variant)

    run_results = []
    for variant_name, system_prompt in variants.items():
        variant_dir = run_dir / variant_name
        fixture_dir = variant_dir / "fixtures"
        acceptance_dir = variant_dir / "acceptance"
        fixture_dir.mkdir(parents=True, exist_ok=True)
        acceptance_dir.mkdir(parents=True, exist_ok=True)
        (fixture_dir / "system_prompt.txt").write_text(system_prompt + "\n")

        generated = [
            _generate_one(slug, user_prompt, system_prompt, fixture_dir, max(1, min(4, args.sample_count)))
            for slug, user_prompt in cases.items()
        ]
        acceptance_code = None
        if not args.skip_acceptance and all(item["status"] == 200 for item in generated):
            acceptance_code, _ = _run_acceptance(fixture_dir, acceptance_dir)
        variant_result = {
            "variant": variant_name,
            "artifactDir": str(variant_dir),
            "generated": generated,
            "acceptanceCode": acceptance_code,
            "acceptance": _summarize_variant(acceptance_dir),
        }
        run_results.append(variant_result)

    (run_dir / "summary.json").write_text(json.dumps(run_results, indent=2, sort_keys=True))
    _write_review(run_dir, run_results)
    print(json.dumps(run_results, indent=2, sort_keys=True))

    failures = [
        result for result in run_results
        if any(item["status"] != 200 for item in result["generated"])
        or (result["acceptanceCode"] not in (None, 0))
    ]
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
