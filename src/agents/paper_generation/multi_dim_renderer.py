import os
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MultiDimRenderer")

class MultiDimRenderer:
    """Renderer for 4D (3D + time) data visualizations"""
    
    def __init__(self, output_path: str = "./storage/visualizations"):
        self.output_path = output_path
        os.makedirs(output_path, exist_ok=True)
        
        # Configure matplotlib for non-interactive use
        plt.switch_backend('Agg')
    
    def render_3d_scatter(
        self,
        data: np.ndarray,
        paper_id: str,
        version_number: int,
        timestamp: datetime,
        title: str = "3D Data Visualization",
        labels: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Render 3D scatter plot
        
        Args:
            data: 3D numpy array
            paper_id: Paper ID
            version_number: Version number
            timestamp: Timestamp
            title: Plot title
            labels: Axis labels (x, y, z)
            
        Returns:
            Path to generated image
        """
        if labels is None:
            labels = {"x": "X", "y": "Y", "z": "Z"}
        
        # Create figure and 3D axis
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Extract x, y, z data (assuming Nx3 array)
        if data.shape[1] != 3:
            raise ValueError(f"Expected 3D data (Nx3 array), got {data.shape}")
        
        x = data[:, 0]
        y = data[:, 1]
        z = data[:, 2]
        
        # Create scatter plot
        scatter = ax.scatter(x, y, z, c=z, cmap='viridis', s=50, alpha=0.7)
        
        # Set labels and title
        ax.set_xlabel(labels["x"])
        ax.set_ylabel(labels["y"])
        ax.set_zlabel(labels["z"])
        ax.set_title(f"{title}\\nPaper: {paper_id} v{version_number}\\n{timestamp.strftime('%Y-%m-%d')}")
        
        # Add color bar
        fig.colorbar(scatter, ax=ax, label='Z Value')
        
        # Save plot
        ts_str = timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"{paper_id}_v{version_number}_3d_{ts_str}.png"
        filepath = os.path.join(self.output_path, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"3D visualization generated: {filepath}")
        return filepath
    
    def render_time_series(
        self,
        time_data: np.ndarray,
        value_data: np.ndarray,
        paper_id: str,
        version_number: int,
        title: str = "Time Series Data",
        labels: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Render time series plot (4D: 3D + time)
        
        Args:
            time_data: Time values
            value_data: 3D value data
            paper_id: Paper ID
            version_number: Version number
            title: Plot title
            labels: Axis labels
            
        Returns:
            Path to generated image
        """
        if labels is None:
            labels = {"x": "Time", "y": "Value", "legend": "Dimension"}
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot each dimension
        dimensions = ["X", "Y", "Z"]
        colors = ['r', 'g', 'b']
        
        for i in range(3):
            if i < value_data.shape[1]:
                ax.plot(time_data, value_data[:, i], color=colors[i], label=f"{dimensions[i]} Dimension")
        
        # Set labels and title
        ax.set_xlabel(labels["x"])
        ax.set_ylabel(labels["y"])
        ax.set_title(f"{title}\\nPaper: {paper_id} v{version_number}")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Save plot
        ts_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{paper_id}_v{version_number}_timeseries_{ts_str}.png"
        filepath = os.path.join(self.output_path, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Time series visualization generated: {filepath}")
        return filepath
    
    def render_spatial_heatmap(
        self,
        lat_data: np.ndarray,
        lon_data: np.ndarray,
        value_data: np.ndarray,
        paper_id: str,
        version_number: int,
        title: str = "Spatial Heatmap",
        labels: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Render spatial heatmap (latitude/longitude + value)
        
        Args:
            lat_data: Latitude data
            lon_data: Longitude data
            value_data: Value data
            paper_id: Paper ID
            version_number: Version number
            title: Plot title
            labels: Axis labels
            
        Returns:
            Path to generated image
        """
        if labels is None:
            labels = {"x": "Longitude", "y": "Latitude", "color": "Value"}
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create scatter plot with color mapping
        scatter = ax.scatter(lon_data, lat_data, c=value_data, cmap='plasma', 
                            s=100, alpha=0.7, edgecolors='black', linewidth=0.5)
        
        # Set labels and title
        ax.set_xlabel(labels["x"])
        ax.set_ylabel(labels["y"])
        ax.set_title(f"{title}\\nPaper: {paper_id} v{version_number}")
        
        # Add color bar
        cbar = fig.colorbar(scatter, ax=ax)
        cbar.set_label(labels["color"])
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Save plot
        ts_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{paper_id}_v{version_number}_heatmap_{ts_str}.png"
        filepath = os.path.join(self.output_path, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Spatial heatmap generated: {filepath}")
        return filepath