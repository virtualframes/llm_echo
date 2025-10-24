import pytest
import os
import subprocess


def test_end_to_end_pr3():
    # Set the mock URL
    os.environ["DEEPSEEKMOCKURL"] = "http://localhost:8000/v1/chat/completions"

    # Run the pipeline with mock deepseek
    command = [
        "python",
        "workflows/pipeline.py",
        "--mock-deepseek",
        "--limit",
        "10",
        "--outdir",
        "out/pr3_test",
    ]

    # Run the pipeline
    result = subprocess.run(command, capture_output=True, text=True)

    # Check the results
    assert result.returncode == 0

    # Check that the provenance bundle was created
    provenance_bundle_path = ".github/PROVENANCE"
    assert os.path.exists(provenance_bundle_path)

    # Check that the output directory was created
    output_dir_path = "out/pr3_test"
    assert os.path.exists(output_dir_path)
