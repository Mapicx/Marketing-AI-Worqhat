# TechNeeti Marketing AI Platform

A modern, responsive dashboard web application built with React, TypeScript, Tailwind CSS, and shadcn/ui components. This AI-powered marketing platform provides comprehensive tools for predictive analytics, content generation, and campaign optimization.

## 🚀 Features

### 📊 **Predictive Analytics** (`/forecast`)
- Upload customer data (`customers.csv`) and campaign history (`campaign_history.csv`)
- Generate AI-powered campaign forecasts and recommendations
- View success probability, target segments, and privacy compliance
- Download detailed reports (HTML/PDF)

### 🎨 **AI Image Generator** (`/image-generator`)
- Generate marketing visuals using AI image generation
- Auto-fill prompts from forecast results
- Professional campaign imagery creation
- Download generated images

### ✨ **Slogan Generator** (`/slogan-generator`)
- Create compelling campaign slogans with AI
- Context-aware generation using forecast data
- Multiple slogan variants
- Copy-to-clipboard functionality

### 🎥 **YouTube QA System** (`/youtube-qa`)
- Process YouTube videos for content analysis
- Ask questions about video content using RAG technology
- AI-powered responses based on video transcripts
- Support for educational and informational content

## 🛠️ Technology Stack

- **Frontend**: React 18 + TypeScript
- **Styling**: Tailwind CSS with custom design system
- **UI Components**: shadcn/ui
- **Routing**: React Router DOM
- **State Management**: React Context API
- **API Client**: Axios
- **Theme**: Light/Dark mode with next-themes
- **Build Tool**: Vite

## 🎨 Design System

The platform features a professional design system with:
- **Primary Colors**: Blue (#3B82F6) and Purple (#8B5CF6) gradients
- **Semantic Tokens**: HSL-based color system for consistency
- **Responsive Design**: Mobile-first approach
- **Modern Animations**: Smooth transitions and hover effects
- **Professional Typography**: Optimized for readability

## 📱 UI/UX Features

- **Sidebar Navigation**: Collapsible sidebar with icon states
- **Loading States**: Elegant loading indicators for all API calls
- **Error Handling**: Toast notifications for user feedback
- **File Upload**: Drag-and-drop CSV file uploads
- **Progress Indicators**: Visual progress bars for analytics
- **Responsive Cards**: Modern card-based layout
- **Theme Toggle**: Light/dark mode switching

## 🔌 Backend Integration

The frontend integrates with a FastAPI backend through these endpoints:

- `POST /forecast` - Predictive analytics processing
- `POST /img` - AI image generation
- `POST /slogan` - Campaign slogan generation
- `POST /rag/process` - YouTube video processing
- `POST /rag/query` - Video content querying

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd techneeti-marketing-ai
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure backend URL**
   Update the `API_BASE_URL` in `src/services/api.ts` to match your FastAPI backend.

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Build for production**
   ```bash
   npm run build
   ```

## 📁 Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── layout/         # Layout components (Sidebar, Header)
│   ├── providers/      # Context providers
│   └── ui/             # shadcn/ui components
├── contexts/           # React Context for state management
├── pages/              # Route components
├── services/           # API service functions
├── assets/             # Static assets and images
└── lib/                # Utility functions
```

## 🎯 Key Features Implementation

### State Management
- Global state for sharing forecast results across features
- Context API for clean state distribution
- Loading states for improved UX

### File Handling
- CSV file uploads with validation
- Drag-and-drop interface
- File size and type restrictions

### API Integration
- Axios-based HTTP client
- Error handling and retry logic
- Response data validation
- Loading state management

### Responsive Design
- Mobile-first CSS approach
- Flexible grid layouts
- Collapsible sidebar navigation
- Touch-friendly interactions

## 🔧 Configuration

### API Configuration
Configure your FastAPI backend URL in `src/services/api.ts`:

```typescript
const API_BASE_URL = 'http://localhost:8000'; // Update this URL
```

### Theme Configuration
Customize the design system in `src/index.css` and `tailwind.config.ts`.

## 📈 Performance Optimizations

- Tree-shaking with Vite
- Lazy loading for images
- Optimized re-renders with React Context
- Efficient state updates
- Component code splitting ready

## 🤝 Contributing

This platform is designed to be extensible and maintainable. Follow the established patterns for adding new features:

1. Create reusable components in `src/components/`
2. Use the design system tokens for consistent styling
3. Implement proper error handling and loading states
4. Add TypeScript interfaces for data structures
5. Follow the established file and folder conventions

---

Built with ❤️ using React, TypeScript, and modern web technologies.
