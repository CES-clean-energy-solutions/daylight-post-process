from dataclasses import dataclass
import pandas as pd
from pathlib import Path

@dataclass
class Grid:
    name: str
    points: list
    mesh_faces: list
    mesh_vertices: list
    mesh_directions: list
    npy_path: Path # The original path to the npy file
    daylight_df: pd.DataFrame # Indexed on datetime 8760 hours, with sensors as columns

@dataclass
class Level:
    name: str
    level: str
    base_path: Path
    output_path: Path
    grids: list
    sunup_hours: pd.Series