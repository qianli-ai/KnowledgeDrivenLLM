# AI Chat Application

A modern AI chat application built with Vue 3 + Vite, featuring real-time chat interface and knowledge base upload functionality.

## Features

- 💬 **Real-time Chat**: Interactive chat interface with AI responses
- 📝 **Markdown Support**: AI responses support full Markdown formatting (headers, code blocks, tables, etc.)
- 📁 **Knowledge Upload**: Upload documents to knowledge base (PDF, Word, Excel, TXT, Markdown)
- 🎨 **Modern UI**: Clean and responsive design with Ant Design Vue
- ⚡ **Fast Development**: Built with Vite for lightning-fast development experience
- 🔄 **Message Actions**: Copy, regenerate, and manage chat messages

## Tech Stack

- **Frontend**: Vue 3 (Composition API)
- **Build Tool**: Vite 7.0.4
- **UI Library**: Ant Design Vue 4.2.6
- **HTTP Client**: Axios 1.11.0
- **Icons**: @ant-design/icons-vue 7.0.1
- **Markdown**: marked (for rendering AI responses)

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

## API Configuration

The application is configured to work with backend APIs:
- **Chat API**: `/chat/` - Send messages and receive AI responses (supports Markdown formatting)
- **Upload API**: `/uploadfile/` - Upload knowledge documents

Backend server is proxied through Vite configuration to handle CORS and development needs.

## Markdown Support

AI responses now support full Markdown formatting including:
- **Headers** (H1-H6)
- **Text formatting** (bold, italic, code)
- **Code blocks** with syntax highlighting
- **Lists** (ordered and unordered)
- **Tables** with proper styling
- **Blockquotes** and links
- **Line breaks** and paragraphs
