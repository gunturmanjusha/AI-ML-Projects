"""Merge focused ANN tuning evidence into the authoritative results file.

No test predictions are produced here.  The historical selected ANN and its
existing final-test record are retained because the validation-only search did
not exceed its recorded recall.
"""
import json
from pathlib import Path

import pandas as pd

OUT = Path("outputs")


def read_json(path):
    with open(path) as handle:
        return json.load(handle)


def main():
    results = read_json(OUT / "results.json")
    xgboost = read_json(OUT / "xgboost_tuning.json")
    run_paths = sorted((OUT / "ann_tuning_runs").glob("*.json"))
    if len(run_paths) != 5:
        raise RuntimeError(f"Expected five ANN run files; found {len(run_paths)}")
    new_runs = [read_json(path)["attempted_configurations"][0] for path in run_paths]

    historical_ann = next(item for item in results["tuned_validation"]
                          if item["model"] == "Artificial Neural Network (tuned)")
    historical_ann = {**historical_ann,
                      "evidence_type": "previously recorded selected configuration",
                      "selection_candidate": True}
    new_best = max(new_runs, key=lambda row: (row["recall"], row["f1"], row["precision"]))

    # The declared validation criterion applies to the established selected ANN,
    # five actual new configurations, and tuned XGBoost.  This contains no test
    # metrics other than the pre-existing final model evaluation.
    candidates = [
        {"model": "ANN — historical selected regularized configuration", **{
            key: historical_ann[key] for key in ["accuracy", "precision", "recall", "f1", "tn", "fp", "fn", "tp"]}},
        *[{"model": f"ANN — {row['id']}", **{
            key: row[key] for key in ["accuracy", "precision", "recall", "f1", "tn", "fp", "fn", "tp"]}}
          for row in new_runs],
        {"model": "XGBoost (tuned)", **{
            key: xgboost["validation"][key] for key in ["accuracy", "precision", "recall", "f1", "tn", "fp", "fn", "tp"]}},
    ]
    selected = max(candidates, key=lambda row: (row["recall"], row["f1"], row["precision"]))
    if not selected["model"].startswith("ANN — historical selected"):
        raise RuntimeError("A new candidate won validation selection; final model/test update is required.")

    results["tuned_validation"] = [xgboost["validation"], historical_ann]
    results["tuning"] = {
        "xgboost": xgboost["search"],
        "ann": {
            "method": "Five pre-specified fixed-seed ANN configurations evaluated on the fixed timestamp-grouped chronological validation partition.",
            "selection_rule": "Highest validation recall; F1 then precision only if recall ties. The test partition was excluded.",
            "preprocessing": "Median imputation and StandardScaler fit only on training data; class weighting from training labels; validation-loss early stopping.",
            "historical_selected_configuration": historical_ann,
            "attempted_configurations": new_runs,
            "best_new_configuration": new_best,
            "selection_result": "The previously recorded regularized ANN remains the validation winner: 92.4928% recall versus 92.3965% for the best newly trained configuration (higher_dropout_l2).",
        },
    }
    results["validation_selection_comparison"] = candidates
    results["selection_rule"] = "Select highest validation recall; use F1 then precision only for a recall tie. Test metrics do not participate in selection."
    results["final_model"] = "Artificial Neural Network (tuned)"
    results["final_model_selection_note"] = (
        "Retained after the focused ANN validation search: recorded validation recall 92.4928% exceeds the best newly trained ANN configuration's 92.3965% and tuned XGBoost's 69.1049%."
    )
    results["test_evaluation_note"] = (
        "The final test metrics are unchanged because the validation-selected final ANN did not change. "
        "The historical test period had already been inspected during prior development; it was not used in the focused ANN configuration selection."
    )

    with open(OUT / "results.json", "w") as handle:
        json.dump(results, handle, indent=2, allow_nan=False)
    pd.DataFrame(results["baseline_validation"]).to_csv(OUT / "baseline_validation_metrics.csv", index=False)
    pd.DataFrame(results["tuned_validation"]).to_csv(OUT / "tuned_validation_metrics.csv", index=False)
    pd.DataFrame(candidates).to_csv(OUT / "validation_selection_comparison.csv", index=False)
    with open(OUT / "ann_tuning.json", "w") as handle:
        json.dump(results["tuning"]["ann"], handle, indent=2, allow_nan=False)
    print(pd.DataFrame(candidates)[["model", "accuracy", "precision", "recall", "f1"]].to_string(index=False))


if __name__ == "__main__":
    main()
