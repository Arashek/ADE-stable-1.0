# ADE Command Hub Dashboard

The Command Hub Dashboard is a comprehensive interface for interacting with the Autonomous Development Environment (ADE) platform. It provides engineers and architects with powerful tools for managing development tasks, monitoring system status, and collaborating with AI agents.

## Features

- **Central Command Panel**: Monitor active agents and execute commands
- **Project Timeline**: Track milestones and decision points
- **Code Evolution**: View code changes with split-screen diff visualization
- **Agent Communication**: Direct messaging with AI agents
- **Runtime Preview**: Embedded application browser with debugging tools
- **Contextual Chat**: Task-specific conversation threads
- **Dark Mode**: Engineer-friendly dark theme with syntax highlighting
- **Keyboard Shortcuts**: Vim/Emacs-inspired navigation

## Prerequisites

- Node.js 18.x or later
- npm 9.x or later
- Git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/ade-platform.git
cd ade-platform/interfaces/command-hub
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the project root:
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Development

Start the development server:
```bash
npm run dev
```

The dashboard will be available at `http://localhost:3000`.

## Building for Production

Build the application:
```bash
npm run build
```

The built files will be in the `dist` directory.

## Keyboard Shortcuts

- `Ctrl + K`: Focus command input
- `Ctrl + J`: Toggle chat panel
- `Ctrl + /`: Toggle code preview
- `Ctrl + Shift + P`: Open command palette
- `Esc`: Close active panel
- `Tab`: Navigate between panels
- `Shift + Tab`: Navigate backwards

## Project Structure

```
command-hub/
├── src/
│   ├── components/     # React components
│   ├── hooks/         # Custom React hooks
│   ├── store/         # State management
│   ├── types/         # TypeScript types
│   ├── utils/         # Utility functions
│   ├── App.tsx        # Main application component
│   ├── main.tsx       # Application entry point
│   └── index.css      # Global styles
├── public/            # Static assets
├── index.html         # HTML template
├── package.json       # Dependencies and scripts
├── tsconfig.json      # TypeScript configuration
└── vite.config.ts     # Vite configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the development team. 