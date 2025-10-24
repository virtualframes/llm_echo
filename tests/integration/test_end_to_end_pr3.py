import pytest
import os
import subprocess

def test_end_to_end_pr3():
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

    # Check if the command includes the --mock-deepseek flag
    if "--mock-deepseek" in command:
        # Start the mock server if the flag is present
        mock_server = subprocess.Popen(["python", "search/mock_deepseek.py"])
    else:
        mock_server = None

    # Run the pipeline
    result = subprocess.run(command, capture_output=True, text=True)

    # Stop the mock server if it was started
    if mock_server:
        mock_server.terminate()

    # Check the results
    assert result.returncode == 0

    # Check that the provenance bundle was created
    provenance_bundle_path = ".github/PROVENANCE"
    assert os.path.exists(provenance_bundle_path)

    # Check that the output directory was created
    output_dir_path = "out/pr3_test"
    assert os.path.exists(output_dir_path)
