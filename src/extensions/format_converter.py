import os
import json
import pandas as pd
import numpy as np
from typing import Any, Optional, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FormatConverter")

class FormatConverter:
    """Format converter for data and file format conversion"""
    
    def __init__(self):
        """Initialize format converter"""
        pass
    
    def convert_data(
        self,
        input_path: str,
        output_path: str,
        input_format: Optional[str] = None,
        output_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert data between different formats
        
        Args:
            input_path: Path to input file
            output_path: Path to output file
            input_format: Input format (inferred from extension if None)
            output_format: Output format (inferred from extension if None)
            
        Returns:
            Conversion result
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Infer formats from file extensions if not provided
        if input_format is None:
            input_format = self._get_format_from_extension(input_path)
        
        if output_format is None:
            output_format = self._get_format_from_extension(output_path)
        
        logger.info(f"Converting {input_format} to {output_format}: {input_path} -> {output_path}")
        
        # Load data
        data = self._load_data(input_path, input_format)
        
        # Save data in output format
        self._save_data(data, output_path, output_format)
        
        result = {
            "success": True,
            "input_path": input_path,
            "output_path": output_path,
            "input_format": input_format,
            "output_format": output_format,
            "message": f"Successfully converted {input_format} to {output_format}"
        }
        
        logger.info(f"Conversion successful: {result['message']}")
        return result
    
    def _get_format_from_extension(self, file_path: str) -> str:
        """
        Infer format from file extension
        
        Args:
            file_path: File path
            
        Returns:
            Format name
        """
        ext = os.path.splitext(file_path)[1].lower()
        format_map = {
            ".csv": "csv",
            ".xlsx": "excel",
            ".xls": "excel",
            ".json": "json",
            ".npy": "numpy",
            ".npz": "numpy",
            ".h5": "hdf5",
            ".txt": "text",
            ".md": "markdown"
        }
        return format_map.get(ext, "unknown")
    
    def _load_data(self, file_path: str, format: str) -> Any:
        """
        Load data from file
        
        Args:
            file_path: File path
            format: File format
            
        Returns:
            Loaded data
        """
        if format == "csv":
            return pd.read_csv(file_path)
        elif format in ["excel", "xlsx", "xls"]:
            return pd.read_excel(file_path)
        elif format == "json":
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        elif format in ["numpy", "npy", "npz"]:
            return np.load(file_path)
        elif format == "hdf5":
            import h5py
            data = {}
            with h5py.File(file_path, "r") as f:
                for key in f.keys():
                    data[key] = f[key][:]
            return data
        elif format == "text":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif format == "markdown":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _save_data(self, data: Any, file_path: str, format: str):
        """
        Save data to file
        
        Args:
            data: Data to save
            file_path: File path
            format: File format
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if format == "csv":
            if isinstance(data, pd.DataFrame):
                data.to_csv(file_path, index=False)
            else:
                raise TypeError("Data must be a pandas DataFrame for CSV output")
        elif format in ["excel", "xlsx"]:
            if isinstance(data, pd.DataFrame):
                data.to_excel(file_path, index=False)
            else:
                raise TypeError("Data must be a pandas DataFrame for Excel output")
        elif format == "json":
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        elif format == "numpy":
            np.save(file_path, data)
        elif format == "hdf5":
            import h5py
            with h5py.File(file_path, "w") as f:
                if isinstance(data, dict):
                    for key, value in data.items():
                        f.create_dataset(key, data=value)
                else:
                    f.create_dataset("data", data=data)
        elif format in ["text", "markdown"]:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(str(data))
        else:
            raise ValueError(f"Unsupported format: {format}")
