# Frontend Quick Start Guide

Welcome to the Multi-Agent Orchestration System React Frontend! 🚀

## Prerequisites

- Node.js 18+ installed
- Backend server running on port 8000

## Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install
```

## Running the Application

### Development Mode

```bash
npm run dev
```

The application will start on `http://localhost:5173`

### Building for Production

```bash
npm run build
```

This creates an optimized build in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── Navigation.jsx
│   │   ├── TaskExecutor.jsx
│   │   ├── TaskHistory.jsx
│   │   └── SystemHealth.jsx
│   ├── services/
│   │   └── api.js       # API client
│   ├── App.jsx          # Main app component
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles
├── index.html
├── vite.config.js       # Vite configuration
└── package.json
```

## Features

### 🚀 Task Executor
- Submit tasks to the multi-agent system
- Add optional JSON context
- View real-time results
- Error handling

### 📜 Task History
- View all executed tasks
- Task details and results
- Delete tasks
- Persistent storage

### 💚 System Health
- Monitor backend status
- API endpoint checks
- Auto-refresh every 30 seconds
- System statistics

## API Configuration

The frontend communicates with the backend through Vite's proxy configuration:

- **Development**: Proxies `/tasks/*` and `/system/*` to `http://localhost:8000`
- **Production**: Configure your reverse proxy or API base URL

## Environment Variables

Create a `.env.local` file if you need custom configuration:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Troubleshooting

### Port Already in Use

If port 5173 is occupied:

```bash
npm run dev -- --port 3000
```

### CORS Errors

Ensure the backend has CORS configured for `http://localhost:5173`

### API Connection Issues

1. Verify backend is running on port 8000
2. Check browser console for error messages
3. Verify Vite proxy configuration in `vite.config.js`

## Tech Stack

- **React 18.2** - UI library
- **Vite 5.0** - Build tool
- **React Router 6** - Client-side routing
- **Axios** - HTTP client
- **Custom CSS** - Premium dark theme

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Need Help?

Check the main [README.md](../README.md) for complete documentation.
