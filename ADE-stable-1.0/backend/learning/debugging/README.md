# Debugging Training System

A comprehensive system for training and improving debugging skills through interactive examples, visualizations, and evaluations.

## Features

- **Multiple Error Types**: Covers various types of programming errors including:
  - Syntax errors
  - Runtime errors
  - Logical errors
  - Concurrency issues
  - Security vulnerabilities

- **Interactive Training Interface**: Built with Streamlit, providing:
  - Code editor for solution submission
  - Real-time error messages
  - Step-by-step debugging guides
  - Visual feedback on progress

- **Visualization Tools**:
  - Code comparison visualization
  - Debugging steps flow diagram
  - Error resolution process visualization
  - Solution quality metrics radar chart

- **Comprehensive Evaluation**:
  - Error identification accuracy
  - Debugging steps quality
  - Fix correctness
  - Code style compliance
  - Performance considerations
  - Security best practices
  - Code maintainability

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the training interface:
```bash
streamlit run training_interface.py
```

## Usage

1. Select the error type you want to practice with from the sidebar
2. Choose the number of examples to generate
3. Click "Generate Examples" to start
4. For each example:
   - Review the buggy code
   - Read the error message and explanation
   - Submit your solution
   - View visualizations and evaluation results
   - Track your progress through the metrics

## Project Structure

```
backend/learning/debugging/
├── dataset_generator.py    # Generates training examples
├── bug_introducer.py      # Introduces bugs into working code
├── evaluator.py           # Evaluates debugging solutions
├── training_interface.py  # Streamlit-based training interface
├── requirements.txt       # Project dependencies
└── README.md             # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 