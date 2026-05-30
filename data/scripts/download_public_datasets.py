#!/usr/bin/env python3
"""
Breast Ultrasound Images (BUSI) Dataset Downloader

Downloads the BUSI dataset from public sources and organizes it for the project.

Dataset Info:
- URL: https://www.kaggle.com/datasets/aryashah2k/breast-ultrasound-images-dataset
- Size: ~200MB
- Images: 780 ultrasound images
- Categories: normal, benign, malignant
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Dataset metadata
DATASET_INFO = {
    "name": "BUSI - Breast Ultrasound Images Dataset",
    "version": "1.0",
    "source": "Kaggle",
    "url": "https://www.kaggle.com/datasets/aryashah2k/breast-ultrasound-images-dataset",
    "size_samples": 780,
    "categories": {
        "normal": 133,
        "benign": 437,
        "malignant": 210
    },
    "annotation_types": ["classification", "segmentation"],
    "modality": "ultrasound",
    "organ": "breast",
    "license": "Public Domain",
    "citation": """
@dataset{al-dhabyani2020busi,
  title={Dataset of breast ultrasound images},
  author={Al-Dhabyani, Walid and Gomaa, Mohammed and Khaled, Hussien and Fahmy, Aly},
  year={2020},
  publisher={Elsevier}
}
    """.strip()
}


def download_busi(output_dir: str = "data/datasets/public/BUSI"):
    """
    Download BUSI dataset.
    
    Note: Direct download requires Kaggle API credentials.
    Manual download instructions are provided.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("BUSI Dataset Download Instructions")
    print("=" * 60)
    print()
    print(f"Dataset: {DATASET_INFO['name']}")
    print(f"Source: {DATASET_INFO['url']}")
    print(f"Output Directory: {output_path.absolute()}\n")
    
    print("Method 1: Manual Download (Recommended)")
    print("-" * 40)
    print("1. Visit: https://www.kaggle.com/datasets/aryashah2k/breast-ultrasound-images-dataset")
    print("2. Click 'Download' button")
    print("3. Extract the downloaded ZIP file")
    print("4. Move contents to:", output_path)
    print()
    
    print("Method 2: Kaggle API (Requires API Credentials)")
    print("-" * 40)
    print("1. Install Kaggle CLI:")
    print("   pip install kaggle")
    print()
    print("2. Set up API credentials:")
    print("   - Get API token from: https://www.kaggle.com/account")
    print("   - Save as ~/.kaggle/kaggle.json")
    print("   chmod 600 ~/.kaggle/kaggle.json")
    print()
    print("3. Download dataset:")
    print(f"   kaggle datasets download -d aryashah2k/breast-ultrasound-images-dataset")
    print(f"   unzip breast-ultrasound-images-dataset.zip -d {output_path}")
    print()
    
    print("Dataset Structure (after extraction):")
    print("-" * 40)
    print("BUSI/")
    print("├── normal/          # 133 normal images")
    print("│   ├── (1).png")
    print("│   └── ...")
    print("├── benign/          # 437 benign tumor images")
    print("│   ├── (1).png")
    print("│   ├── (1)_mask.png  # Corresponding segmentation mask")
    print("│   └── ...")
    print("├── malignant/       # 210 malignant tumor images")
    print("│   ├── (1).png")
    print("│   ├── (1)_mask.png  # Corresponding segmentation mask")
    print("│   └── ...")
    print("└── README.txt")
    print()
    
    # Save dataset metadata
    metadata_file = output_path / "dataset_info.json"
    metadata = {
        **DATASET_INFO,
        "downloaded_at": datetime.now().isoformat(),
        "download_path": str(output_path.absolute())
    }
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Dataset metadata saved to: {metadata_file}")
    print()
    print("=" * 60)


def download_uci(output_dir: str = "data/datasets/public/UCI-Breast-Cancer"):
    """
    Download UCI Wisconsin Breast Cancer Dataset.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("UCI Breast Cancer Dataset Download")
    print("=" * 60)
    print()
    
    # Direct download URLs
    urls = {
        "data": "https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/wdbc.data",
        "features": "https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/wdbc.names"
    }
    
    print("Dataset: UCI Wisconsin Breast Cancer Diagnostic")
    print(f"Output Directory: {output_path.absolute()}\n")
    
    print("Download URLs:")
    for name, url in urls.items():
        print(f"  {name}: {url}")
    print()
    
    print("Download commands:")
    print("-" * 40)
    print("wget -P", output_path, urls["data"])
    print("wget -P", output_path, urls["features"])
    print()
    
    # Save metadata
    metadata = {
        "name": "UCI Wisconsin Breast Cancer Diagnostic",
        "version": "1.0",
        "source": "UCI Machine Learning Repository",
        "urls": urls,
        "size_samples": 569,
        "features": 30,
        "classes": 2,  # benign, malignant
        "year": 1995,
        "license": "Public Domain"
    }
    
    metadata_file = output_path / "dataset_info.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    print("Breast Cancer Dataset Downloader")
    print("=" * 60)
    print()
    
    # Parse arguments
    dataset = "busi"
    if len(sys.argv) > 1:
        dataset = sys.argv[1].lower()
    
    if dataset == "busi":
        download_busi()
    elif dataset == "uci":
        download_uci()
    elif dataset == "all":
        download_busi()
        print()
        download_uci()
    else:
        print("Available datasets: busi, uci, all")
        print("Usage: python download_public_datasets.py [dataset_name]")
