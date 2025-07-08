# Daylight Post-Processing Project Reorganization Plan

## Overview
Transform the current collection of scripts and utility functions into a well-structured Python package for daylight simulation post-processing.

## Current State Analysis

The codebase contains:
- **Data Models**: `models.py` and `modelsRefactor.py` (appears to be an evolution)
- **Data Loading**: `load_ill.py`, `load_sunup.py`, `load_npy.py`, `parse_hbjson.py`
- **Utilities**: `util_output.py`, `util_plotting.py`, `util_statistics.py`
- **Transformers**: `transformers.py` for data transformations
- **Main Script**: `Folder analysis FOR LOOP Refactor.py` (the primary analysis workflow)

## Proposed Directory Structure

```
daylight-post-process/
├── README.md                           # Project documentation
├── setup.py                           # Package installation
├── requirements.txt                   # Dependencies
├── pyproject.toml                     # Modern Python packaging
├── .gitignore                         # Git ignore patterns
├── daylight_post_process/             # Main package directory
│   ├── __init__.py                   # Package initialization
│   ├── core/                         # Core data models and classes
│   │   ├── __init__.py
│   │   ├── models.py                 # Data models (consolidated)
│   │   └── exceptions.py             # Custom exceptions
│   ├── io/                           # Input/Output operations
│   │   ├── __init__.py
│   │   ├── illuminance.py            # load_ill.py functionality
│   │   ├── sunup.py                  # load_sunup.py functionality
│   │   ├── npy_loader.py             # load_npy.py functionality
│   │   └── hbjson_parser.py          # parse_hbjson.py functionality
│   ├── transformers/                 # Data transformation classes
│   │   ├── __init__.py
│   │   ├── base.py                   # Base transformer class
│   │   ├── illuminance.py            # Illuminance-specific transforms
│   │   └── daylight_autonomy.py      # Daylight autonomy calculations
│   ├── utils/                        # Utility functions
│   │   ├── __init__.py
│   │   ├── output.py                 # util_output.py functionality
│   │   ├── plotting.py               # util_plotting.py functionality
│   │   └── statistics.py             # util_statistics.py functionality
│   ├── analysis/                     # Analysis workflows
│   │   ├── __init__.py
│   │   ├── batch_processor.py        # Main analysis workflow
│   │   └── single_run.py             # Single simulation analysis
│   └── config/                       # Configuration management
│       ├── __init__.py
│       └── settings.py               # Default settings and paths
├── scripts/                          # Command-line scripts
│   ├── analyze_simulation.py         # Main CLI entry point
│   └── batch_process.py              # Batch processing script
├── examples/                         # Example usage and tutorials
│   ├── basic_usage.py
│   └── advanced_analysis.py
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_io.py
│   ├── test_transformers.py
│   └── test_utils.py
├── docs/                             # Documentation
│   ├── api.md
│   ├── user_guide.md
│   └── developer_guide.md
└── data/                             # Sample data (if any)
    └── examples/
```

## Implementation Plan

### Phase 1: Core Package Structure
1. **Create package directory structure**
2. **Consolidate data models** - Merge `models.py` and `modelsRefactor.py` into a single, clean models module
3. **Organize IO modules** - Move loading functions to `io/` subpackage
4. **Create base transformer class** - Establish common interface for transformations
5. **Extract main workflow** - Convert `Folder analysis FOR LOOP Refactor.py` into modular functions

### Phase 2: Refactor and Clean
1. **Update imports** - Fix all import statements to use new structure
2. **Remove redundant code** - Clean up any duplicate functionality
3. **Standardize interfaces** - Ensure consistent method signatures
4. **Add type hints** - Improve code documentation and IDE support
5. **Rename main script** - Convert `Folder analysis FOR LOOP Refactor.py` to a proper CLI script

### Phase 3: CLI and Scripts
1. **Create command-line interface** - Main entry point for analysis
2. **Convert scripts to functions** - Make analysis workflows callable
3. **Add configuration management** - Handle paths, settings, and defaults

### Phase 4: Testing and Documentation
1. **Write unit tests** - Test each module independently
2. **Create user documentation** - How to use the package
3. **Add API documentation** - Document all public interfaces
4. **Create examples** - Show common usage patterns

## Key Benefits

1. **Modularity**: Clear separation of concerns
2. **Reusability**: Functions can be imported and used independently
3. **Testability**: Each module can be tested in isolation
4. **Maintainability**: Easier to find and fix issues
5. **Installability**: Can be installed as a Python package
6. **Documentation**: Clear structure for documentation
7. **CLI Interface**: Easy to use from command line

## Migration Strategy

1. **Preserve existing functionality** - The main analysis workflow should continue to work
2. **Gradual migration** - Move one module at a time, starting with the most independent ones
3. **Backward compatibility** - Maintain existing interfaces where possible
4. **Testing at each step** - Ensure nothing breaks during migration
5. **Focus on the main script** - The `Folder analysis FOR LOOP Refactor.py` is the primary workflow to preserve

## Dependencies

The project will need these dependencies:
- numpy
- pandas
- matplotlib
- pathlib (built-in)
- logging (built-in)
- coloredlogs
- json (built-in)
- struct (built-in)

## Next Steps

1. **Create the directory structure** - Set up the new package layout
2. **Start with core models consolidation** - Merge `models.py` and `modelsRefactor.py`
3. **Move IO functions to appropriate modules** - Organize data loading functions
4. **Create the main package `__init__.py`** - Set up package imports
5. **Extract the main workflow** - Convert `Folder analysis FOR LOOP Refactor.py` into modular functions
6. **Add setup.py and requirements.txt** - Make the package installable
7. **Create CLI entry points** - Convert the main script to a proper command-line tool
8. **Add tests and documentation** - Ensure reliability and usability