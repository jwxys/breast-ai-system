#!/usr/bin/env python3
"""
Dataset Validator

Validates downloaded datasets for completeness and integrity.
"""

import os
import json
from pathlib import Path


def validate_busi_dataset(base_path: str = "data/datasets/public/BUSI"):
    """Validate BUSI dataset structure."""
    path = Path(base_path)
    
    if not path.exists():
        return False, f"Dataset directory not found: {path}"
    
    required_dirs = ["normal", "benign", "malignant"]
    for dir_name in required_dirs:
        dir_path = path / dir_name
        if not dir_path.exists():
            return False, f"Missing directory: {dir_name}"
        
        png_files = list(dir_path.glob("*.png"))
        if len(png_files) == 0:
            return False, f"No PNG files in {dir_name}"
    
    return True, f"BUSI dataset validated ({path})"


def validate_uci_dataset(base_path: str = "data/datasets/public/UCI-Breast-Cancer"):
    """Validate UCI dataset."""
    path = Path(base_path)
    
    if not path.exists():
        return False, f"Dataset directory not found: {path}"
    
    required_files = ["dataset_info.json"]
    for file_name in required_files:
        file_path = path / file_name
        if not file_path.exists():
            return False, f"Missing file: {file_name}"
    
    return True, f"UCI dataset validated ({path})"


def main():
    print("Dataset Validator")
    print("=" * 60)
    
    # Validate BUSI
    valid, msg = validate_busi_dataset()
    print(f"{'✅' if valid else '❌'} BUSI: {msg}")
    
    # Validate UCI
    valid, msg = validate_uci_dataset()
    print(f"{'✅' if valid else '❌'} UCI: {msg}")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
