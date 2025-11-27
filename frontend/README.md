# Artificial-Me Frontend

A modern React application built with TypeScript, Vite, and Ant Design. This frontend application provides a user interface for the Artificial-Me project.

## 🚀 Features

- Built with React 19 and TypeScript
- Modern UI components using Ant Design
- Dark mode support
- Markdown rendering capabilities
- Tailwind CSS for styling
- Docker support for development and production

## 🛠️ Tech Stack

- **Framework**: React 19
- **Language**: TypeScript
- **Build Tool**: Vite
- **UI Library**: Ant Design
- **Styling**: Tailwind CSS
- **Markdown**: markdown-to-jsx
- **Development**: ESLint, TypeScript

## ⚙️ Configuration

The application can be configured through `src/config/config.ts`. All fields are optional and will fall back to default values if not specified.

```typescript
export const UI_CONFIG = {
  // The name displayed in the header
  // Default: "AI Assistant"
  name?: string;
  
  // Placeholder text for the input field
  // Default: "Ask me anything..."
  inputPlaceholder?: string;
  
  // Maximum length for user input messages
  // Default: 256
  maxInputLength?: number;
  
  // Default prompt suggestions shown to users
  // These appear as clickable buttons below the chat
  // Default: ["Tell me about yourself", "What can you do?"]
  defaultPrompts?: string[];
  
  // Welcome message shown in markdown format
  // Supports markdown syntax and @spin[emoji] for animated emojis
  // Default: A simple welcome message
  chatDescription?: string;
  
  // Feature flags to control UI elements
  features?: {
    // Enable/disable particle background effect
    // Creates an interactive particle network in the background
    // Default: true
    enableParticles?: boolean;
    
    // Enable/disable hexagon pattern background
    // Adds a subtle hexagonal pattern overlay
    // Default: true
    enableHexagons?: boolean;
  }
}
```

### Default Configuration

If you don't specify any configuration, the application will use these default values:

```typescript
const DEFAULT_CONFIG = {
  name: "AI Assistant",
  inputPlaceholder: "Ask me anything...",
  maxInputLength: 256,
  defaultPrompts: [
    "Tell me about yourself",
    "What can you do?"
  ],
  chatDescription: `
# Welcome! 👋

I'm your AI assistant. Feel free to ask me anything!

* Try the suggested prompts below
* Ask your own questions
* I'm here to help!
  `.trim(),
  features: {
    enableParticles: true,
    enableHexagons: true
  }
}
```

### Customizing the Chat

1. **Name and Branding**
   - `name`: Customize the header text (optional)
   - `inputPlaceholder`: Change the input field placeholder (optional)

2. **Default Prompts**
   - `defaultPrompts`: Array of suggested questions (optional)
   - Each prompt should be concise and engaging
   - These appear as clickable buttons below the chat

3. **Welcome Message**
   - `chatDescription`: Markdown-formatted welcome message (optional)
   - Supports all markdown features (headings, lists, links, etc.)
   - Use `@spin[emoji]` for animated emojis
   - Example:
     ```markdown
     # Welcome! @spin[👋]
     
     * Point 1
     * Point 2
     
     > Custom quote
     ```

4. **Visual Features**
   - `features.enableParticles`: Toggle particle background (optional)
   - `features.enableHexagons`: Toggle hexagon pattern (optional)
   - Both default to true if not specified

### Example Configuration

Here's a minimal configuration example:

```typescript
export const UI_CONFIG = {
  name: "My AI Assistant",
  defaultPrompts: [
    "What's your favorite color?",
    "Tell me a joke"
  ]
} as const;
```

All other fields will use their default values.

## 📦 Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

## 🚀 Development

To start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## 🏗️ Building for Production

To build the application for production:

```bash
npm run build
```

The built files will be in the `dist` directory.

## 🐳 Docker Support

### Development
```bash
docker build -f Dockerfile.dev -t artificial-me-frontend:dev .
docker run -p 5173:5173 artificial-me-frontend:dev
```

### Production
```bash
docker build -t artificial-me-frontend:prod .
docker run -p 80:80 artificial-me-frontend:prod
```

## 🔍 Code Quality

The project uses ESLint for code quality. To run linting:

```bash
npm run lint
```

## 📝 Environment Variables

Create a `.env` file based on `.env.example` with your configuration.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
