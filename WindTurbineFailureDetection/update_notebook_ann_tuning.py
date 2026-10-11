"""Insert focused ANN tuning evidence into the original 220-cell notebook."""
from pathlib import Path

import nbformat

path = Path("AIML_Project_1_Low_Code_Notebook.ipynb")
notebook = nbformat.read(path, as_version=4)

notebook.cells[165].source = """# The six-configuration XGBoost search uses timestamp-grouped expanding folds.\n# It has already been run; this merges its validated holdout metrics into results.\nexec(compile(Path('update_authoritative_results.py').read_text(), 'update_authoritative_results.py', 'exec'))\nresults = json.load(open('outputs/results.json'))\ndisplay(pd.DataFrame([results['tuning']['xgboost']['best_parameters']]))\nprint('Best XGBoost CV recall:', results['tuning']['xgboost']['best_cv_recall'])\nprint('Holdout validation recall:', results['tuned_validation'][0]['recall'])"""
notebook.cells[171].source = """# Focused ANN tuning: five pre-specified architectures are evaluated only on the\n# timestamp-grouped chronological validation split.  Training-only imputation and\n# scaling, training-label class weights, fixed seeds, and validation-loss early\n# stopping are defined in focused_ann_tuning.py. The test split is not loaded.\nimport subprocess, sys\nsubprocess.run([sys.executable, 'focused_ann_tuning.py'], check=True)\nexec(compile(Path('finalize_ann_tuning.py').read_text(), 'finalize_ann_tuning.py', 'exec'))\nresults = json.load(open('outputs/results.json'))"""
notebook.cells[172].source = """ann_tuning = results['tuning']['ann']\nann_runs = pd.DataFrame(ann_tuning['attempted_configurations'])\ndisplay(ann_runs[['id', 'accuracy', 'precision', 'recall', 'f1', 'epochs_completed']].sort_values('recall', ascending=False))\nprint(ann_tuning['selection_result'])"""
notebook.cells[173].source = """# Candidate selection comparison includes the historical selected ANN, all new\n# ANN runs, and expanded-search XGBoost. Selection is recall-first; F1 and\n# precision break only an exact recall tie.\ncomparison = pd.DataFrame(results['validation_selection_comparison'])\ndisplay(comparison[['model', 'accuracy', 'precision', 'recall', 'f1']].sort_values('recall', ascending=False))"""
notebook.cells[203].source = """### Tuning interpretation\nANN and XGBoost were selected from baseline validation recall. XGBoost was searched across six configurations with two timestamp-grouped expanding folds. Five focused ANN configurations (including the previous regularised setup) were evaluated on the fixed chronological validation partition. The previously recorded regularised ANN remained the recall-first winner (92.49% validation recall), narrowly above the best new ANN run (92.40%). Test metrics did not determine this choice."""
notebook.cells[206].source = """# The retained ANN wins by validation recall. The final test evaluation is the\n# existing evaluation of that same selected model; no new model was tested.\nprint(results['final_model_selection_note'])\nprint(results['test_evaluation_note'])"""
notebook.cells[216].source = """## Business Insights\nThe tuned ANN is retained because it has the highest recorded validation recall under the declared selection rule. On the historical test period it misses 196 of 1,441 recorded fault-state observations; these are the principal operational risk. It also produces 1,271 false-positive SCADA observations, which are not equivalent to technician visits or unique incidents. The classifier labels recorded current condition and does not establish a future-failure lead time."""

nbformat.write(notebook, path)
print(f"Updated {path} with {len(notebook.cells)} cells")
