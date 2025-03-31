# ADE Dataset Generation System

A comprehensive system for generating synthetic datasets for AI model training, with a focus on code-related tasks.

## Features

- **Multiple Generation Strategies**:
  - Code pair generation
  - Bug introduction and fixing examples
  - Comment-to-code and code-to-comment generation
  - Project structure examples

- **GitHub Integration**:
  - API-based access to public repositories
  - Filtering by language, stars, and activity
  - Automatic forking and local cloning
  - Selective extraction of relevant code patterns

- **Dataset Management**:
  - Versioning support
  - Quality scoring
  - Deduplication
  - Format conversion for different training frameworks

- **Interactive Interface**:
  - Chat-based system for defining parameters
  - Preview generated examples
  - Controls for approving/rejecting/editing samples
  - Scale dataset size

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ade-platform.git
cd ade-platform
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r src/core/models/proprietary/dataset_generation/requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your GitHub token and other settings
```

## Usage

1. Start the interactive interface:
```bash
python src/core/models/proprietary/dataset_generation/serve.py
```

2. Open your web browser and navigate to `http://localhost:8501`

3. Configure your dataset generation:
   - Select generation strategy
   - Set programming language
   - Configure GitHub parameters
   - Set quality thresholds
   - Enable/disable deduplication

4. Generate and review examples:
   - Preview generated examples
   - Approve/reject/edit samples
   - Export in various formats

## Project Structure

```
dataset_generation/
├── generator.py           # Core generation logic
├── github_integration.py  # GitHub API integration
├── dataset_manager.py     # Dataset management
├── interactive_interface.py # Web interface
├── serve.py              # Server script
├── requirements.txt      # Dependencies
└── README.md            # Documentation
```

## Generation Strategies

### Code Pair Generation
Generates pairs of related code snippets, such as:
- Function implementations and their tests
- Class definitions and their usage examples
- API endpoints and their client code

### Bug Fix Examples
Creates examples of bug introduction and fixing:
- Introduces common bugs in code
- Provides correct implementations
- Includes bug descriptions and fixes

### Comment-Code Generation
Generates pairs of:
- Code comments and their implementations
- Code snippets and their documentation
- Natural language descriptions and code

### Project Structure Examples
Creates examples of:
- Project layouts
- File organization
- Module dependencies

## Quality Metrics

The system uses several metrics to ensure dataset quality:

1. **Length Score**:
   - Evaluates input/output length
   - Prefers examples of reasonable size

2. **Complexity Score**:
   - Measures code complexity
   - Uses cyclomatic complexity
   - Considers nesting levels

3. **Similarity Score**:
   - Checks input/output similarity
   - Uses TF-IDF and cosine similarity
   - Prefers diverse examples

## Export Formats

The system supports multiple export formats:

1. **CSV**:
   - Simple tabular format
   - Easy to import into spreadsheets

2. **JSONL**:
   - Line-delimited JSON
   - Efficient for large datasets

3. **HuggingFace**:
   - Compatible with HuggingFace datasets
   - Includes dataset info and splits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- GitHub API for repository access
- Streamlit for the web interface
- scikit-learn for similarity calculations
- All contributors and maintainers 