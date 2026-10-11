# AI & Machine Learning Projects

A collection of applied machine-learning projects developed for coursework and portfolio practice. Each project keeps its data, analysis notebooks, reproducible scripts, and deliverables in its own directory.

## Projects

### Wind Turbine Failure Detection

A low-code classification project for identifying recorded drivetrain fault states from 10-minute SCADA observations from 15 wind turbines.

**Highlights**

- 131,760 SCADA observations spanning 15 turbines.
- Timestamp-grouped chronological 70/15/15 train, validation, and test partitions.
- Five baseline classifiers: Decision Tree, Random Forest, Gradient Boosting, XGBoost, and Artificial Neural Network.
- Validation-led hyperparameter tuning for ANN and XGBoost.
- Recall-first model selection because missed fault observations are operationally costly.
- Feature interpretation using validation-set permutation importance.

**Final recorded model**

The selected model is a tuned Artificial Neural Network. On the recorded test partition it achieved 92.58% accuracy, 49.48% precision, 86.40% recall, and 62.93% F1-score. Its confusion matrix was TN 17,058, FP 1,271, FN 196, and TP 1,245.

> The classifier identifies fault state recorded at a SCADA timestamp. It does not establish future-failure lead time or quantify financial savings.

**Project contents**

- `WindTurbineFailureDetection/AIML_Project_1_Low_Code_Notebook.ipynb` — course notebook and analysis narrative.
- `WindTurbineFailureDetection/authoritative_analysis.py` — reproducible chronological modeling workflow.
- `WindTurbineFailureDetection/focused_ann_tuning.py` — focused validation-only ANN configuration search.
- `WindTurbineFailureDetection/outputs/results.json` — authoritative metrics, confusion matrices, selection evidence, and feature importance.
- `WindTurbineFailureDetection/outputs/charts/` — generated analysis charts.
- `WindTurbineFailureDetection/outputs/` — presentation deliverables and supporting tables.

## Reproducibility

Run project commands from the relevant project directory using its Python environment. Model selection must use validation data only; the test partition must not be used for tuning or threshold selection.

## Repository conventions

- Keep project-specific work within its project directory.
- Save generated deliverables in each project's `outputs/` directory.
- Keep previous presentation versions in `outputs/archive/`.
- Do not include credentials, private data, or environment-specific secrets.
