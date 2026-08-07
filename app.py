from flask import Flask, render_template, request, redirect, url_for, Response
import json
import os
import csv
import io
from datetime import datetime
from collections import Counter, defaultdict
from models_api import get_model_response, judge_response, MODEL_A, MODEL_B

app = Flask(__name__)
EVAL_FILE = "evaluations.json"


def normalize_scores(scores):
    return {
        "factual_accuracy": scores.get("factual_accuracy", scores.get("accuracy", 0)),
        "instruction_following": scores.get("instruction_following", scores.get("instruction", 0)),
        "completeness": scores.get("completeness", 0),
        "clarity_structure": scores.get("clarity_structure", scores.get("clarity", 0)),
        "safety_appropriateness": scores.get("safety_appropriateness", scores.get("safety", 0)),
    }


def load_evaluations():
    if not os.path.exists(EVAL_FILE):
        return []
    try:
        with open(EVAL_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            data = json.loads(content)
            for ev in data:
                if isinstance(ev, dict) and "scores" in ev and isinstance(ev["scores"], dict):
                    ev["scores"] = normalize_scores(ev["scores"])
                else:
                    ev["scores"] = normalize_scores({})
                ev["judge_scores"] = normalize_scores(ev.get("judge_scores", {}))
                ev["prompt"] = ev.get("prompt", "")
                ev["prompt_type"] = ev.get("prompt_type", "unknown")
                ev["model_name"] = ev.get("model_name", "unknown")
                ev["response"] = ev.get("response", "")
                ev["comment"] = ev.get("comment", "")
                ev["timestamp"] = ev.get("timestamp", "")
                ev["id"] = ev.get("id", "")
                ev["reviewer"] = ev.get("reviewer", "Yann")
            return data
    except json.JSONDecodeError:
        return []


def save_evaluations(evaluations):
    with open(EVAL_FILE, "w", encoding="utf-8") as f:
        json.dump(evaluations, f, ensure_ascii=False, indent=2)


@app.route("/", methods=["GET", "POST"])
def index():
    prompt = ""
    responses = None

    if request.method == "POST" and "generate" in request.form:
        prompt = request.form.get("prompt", "").strip()
        if prompt:
            responses = {
                MODEL_A: get_model_response(prompt, MODEL_A),
                MODEL_B: get_model_response(prompt, MODEL_B),
            }

    if request.method == "POST" and "save" in request.form:
        evaluations = load_evaluations()

        prompt = request.form.get("prompt_hidden", "").strip()
        prompt_type = request.form.get("prompt_type", "").strip()

        response_a = request.form.get("response_a_hidden", "").strip()
        response_b = request.form.get("response_b_hidden", "").strip()

        scores_a = {
            "factual_accuracy": int(request.form.get("a_factual_accuracy", "0")),
            "instruction_following": int(request.form.get("a_instruction_following", "0")),
            "completeness": int(request.form.get("a_completeness", "0")),
            "clarity_structure": int(request.form.get("a_clarity_structure", "0")),
            "safety_appropriateness": int(request.form.get("a_safety_appropriateness", "0")),
        }
        scores_b = {
            "factual_accuracy": int(request.form.get("b_factual_accuracy", "0")),
            "instruction_following": int(request.form.get("b_instruction_following", "0")),
            "completeness": int(request.form.get("b_completeness", "0")),
            "clarity_structure": int(request.form.get("b_clarity_structure", "0")),
            "safety_appropriateness": int(request.form.get("b_safety_appropriateness", "0")),
        }

        judge_a = judge_response(prompt, response_a)
        judge_b = judge_response(prompt, response_b)

        comment_a = request.form.get("a_comment", "").strip()
        comment_b = request.form.get("b_comment", "").strip()

        next_id = len(evaluations) + 1
        evaluations.append({
            "id": f"eval_{next_id:03d}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prompt": prompt,
            "prompt_type": prompt_type,
            "model_name": MODEL_A,
            "response": response_a,
            "scores": scores_a,
            "judge_scores": normalize_scores(judge_a),
            "comment": comment_a,
            "reviewer": "Yann"
        })

        next_id = len(evaluations) + 1
        evaluations.append({
            "id": f"eval_{next_id:03d}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prompt": prompt,
            "prompt_type": prompt_type,
            "model_name": MODEL_B,
            "response": response_b,
            "scores": scores_b,
            "judge_scores": normalize_scores(judge_b),
            "comment": comment_b,
            "reviewer": "Yann"
        })

        save_evaluations(evaluations)
        return redirect(url_for("results"))

    return render_template("index.html", prompt=prompt, responses=responses)


@app.route("/results")
def results():
    evaluations = load_evaluations()

    model_stats = defaultdict(lambda: {
        "count": 0,
        "accuracy_sum": 0,
        "instruction_sum": 0,
        "completeness_sum": 0,
        "clarity_sum": 0,
        "safety_sum": 0,
    })

    prompt_type_counts = Counter()
    comparison_rows = []

    for ev in evaluations:
        model = ev.get("model_name", "unknown")
        s = normalize_scores(ev.get("scores", {}))
        j = normalize_scores(ev.get("judge_scores", {}))

        model_stats[model]["count"] += 1
        model_stats[model]["accuracy_sum"] += s["factual_accuracy"]
        model_stats[model]["instruction_sum"] += s["instruction_following"]
        model_stats[model]["completeness_sum"] += s["completeness"]
        model_stats[model]["clarity_sum"] += s["clarity_structure"]
        model_stats[model]["safety_sum"] += s["safety_appropriateness"]

        prompt_type_counts[ev.get("prompt_type", "unknown")] += 1

        human_avg = sum(s.values()) / 5
        judge_avg = sum(j.values()) / 5
        comparison_rows.append({
            "id": ev.get("id", ""),
            "model_name": model,
            "human_avg": human_avg,
            "judge_avg": judge_avg,
            "diff": human_avg - judge_avg,
        })

    stats = {}
    for model, st in model_stats.items():
        count = st["count"] or 1
        stats[model] = {
            "count": st["count"],
            "avg_accuracy": st["accuracy_sum"] / count,
            "avg_instruction": st["instruction_sum"] / count,
            "avg_completeness": st["completeness_sum"] / count,
            "avg_clarity": st["clarity_sum"] / count,
            "avg_safety": st["safety_sum"] / count,
        }

    return render_template(
        "results.html",
        evaluations=evaluations,
        stats=stats,
        prompt_type_counts=prompt_type_counts,
        comparison_rows=comparison_rows,
    )


@app.route("/export_csv")
def export_csv():
    evaluations = load_evaluations()
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "id", "timestamp", "prompt", "prompt_type", "model_name",
        "factual_accuracy", "instruction_following", "completeness",
        "clarity_structure", "safety_appropriateness",
        "judge_factual_accuracy", "judge_instruction_following", "judge_completeness",
        "judge_clarity_structure", "judge_safety_appropriateness",
        "comment", "reviewer"
    ])

    for ev in evaluations:
        s = normalize_scores(ev.get("scores", {}))
        j = normalize_scores(ev.get("judge_scores", {}))
        writer.writerow([
            ev.get("id", ""),
            ev.get("timestamp", ""),
            ev.get("prompt", ""),
            ev.get("prompt_type", ""),
            ev.get("model_name", ""),
            s["factual_accuracy"],
            s["instruction_following"],
            s["completeness"],
            s["clarity_structure"],
            s["safety_appropriateness"],
            j["factual_accuracy"],
            j["instruction_following"],
            j["completeness"],
            j["clarity_structure"],
            j["safety_appropriateness"],
            ev.get("comment", ""),
            ev.get("reviewer", "")
        ])

    csv_data = output.getvalue()
    output.close()
    response = Response(csv_data, mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=evaluations.csv"
    return response


if __name__ == "__main__":
    app.run(debug=True)
