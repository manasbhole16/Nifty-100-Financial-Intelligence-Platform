import pytest
import os
import pandas as pd

def test_cluster_labels_exist():
    """Ensures KMeans output was successfully generated."""
    assert os.path.exists("output/cluster_labels.csv")

def test_cluster_columns():
    """Validates the schema of the cluster output."""
    df = pd.read_csv("output/cluster_labels.csv")
    required = ['company_id', 'cluster_id', 'cluster_name']
    for col in required:
        assert col in df.columns