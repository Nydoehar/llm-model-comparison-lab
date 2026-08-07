# Final Testing Checklist

Use this checklist before you publish the project on GitHub or share it with recruiters.

## Core app flow

- [ ] App starts with `python app.py` without errors.
- [ ] Home page loads correctly.
- [ ] One prompt can be entered and submitted.
- [ ] Both Gemini models return responses for the same prompt.
- [ ] Both responses appear on the page.
- [ ] Both evaluation forms are visible and save correctly.
- [ ] Results page loads correctly after saving.

## Human scoring

- [ ] Human scores save for both models.
- [ ] Score fields accept values from 1 to 5.
- [ ] Missing score fields do not crash the app.
- [ ] Old saved records still display correctly.

## Judge comparison

- [ ] Judge scores are generated for both model responses.
- [ ] Judge scores are stored in `evaluations.json`.
- [ ] Results page shows human vs judge comparison.
- [ ] Judge score values display correctly.
- [ ] Difference column displays numeric values.

## Data storage

- [ ] `evaluations.json` is created if it does not exist.
- [ ] Empty JSON file does not break the app.
- [ ] Invalid old schema records do not break the app.
- [ ] New evaluations are appended correctly.
- [ ] Data remains valid JSON after saving.

## CSV export

- [ ] `/export_csv` downloads a CSV file.
- [ ] CSV includes human scores.
- [ ] CSV includes judge scores.
- [ ] CSV opens correctly in spreadsheet software.

## Results page

- [ ] Model averages show correctly.
- [ ] Prompt type counts show correctly.
- [ ] Human vs judge comparison table shows correctly.
- [ ] All evaluations table shows prompt, response, human scores, judge scores, and comments.
- [ ] No KeyError or template rendering errors appear.

## Prompt set

- [ ] At least 6 test prompts are saved in `TEST_PROMPTS.md`.
- [ ] Prompts cover summarization, coding, reasoning, safety, translation, and instruction following.
- [ ] The prompts create meaningful differences between model outputs.

## GitHub and README

- [ ] README explains the project clearly.
- [ ] README includes setup instructions.
- [ ] README includes the architecture diagram.
- [ ] README mentions the Gemini models used.
- [ ] README mentions CSV export and judge comparison.
- [ ] Screenshots or a short demo are added if possible.

## Portfolio quality

- [ ] Project title is clear and recruiter-friendly.
- [ ] Code is organized and readable.
- [ ] File names are consistent.
- [ ] No secret keys are committed.
- [ ] The project feels like a real evaluation tool, not a toy demo.
