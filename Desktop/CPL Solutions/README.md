# CleanPeak (CPL) - Professional Cleaning Services Website

A modern, production-ready website for CleanPeak (CPL), a professional cleaning company based in Nairobi, Kenya. Built with React, Vite, and Tailwind CSS with a focus on security and performance.

## 🏢 About CleanPeak (CPL)

CleanPeak (abbreviated as CPL) provides professional commercial and residential cleaning services across Nairobi, Kenya. This website showcases their services, company values, and provides a contact form for quote requests.

## 🚀 Tech Stack

- **Framework**: React 19
- **Build Tool**: Vite 7
- **Styling**: Tailwind CSS 4
- **Icons**: Lucide React
- **Security**: react-helmet-async, DOMPurify

## 📋 Features

- **Responsive Design**: Fully responsive across mobile, tablet, and desktop
- **Modern UI**: Professional blue/white/green color palette with smooth animations
- **SEO Optimized**: Proper meta tags and semantic HTML
- **Secure Contact Form**: XSS prevention with DOMPurify input sanitization
- **Accessible**: WCAG-compliant with proper focus management

## 🛠️ Installation

### Prerequisites

- Node.js 18.x or higher
- npm 9.x or higher

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd "CPL Solutions"
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create environment file:
   ```bash
   cp .env.example .env
   ```

4. Update `.env` with your configuration (optional for development)

## 🏃 Running the Project

### Development Server

Start the development server with hot-reload:

```bash
npm run dev
```

The site will be available at `http://localhost:5173`

### Production Build

Create an optimized production build:

```bash
npm run build
```

The output will be in the `dist/` directory.

### Preview Production Build

Preview the production build locally:

```bash
npm run preview
```

## 📁 Project Structure

```
CPL Solutions/
├── public/              # Static assets
├── src/
│   ├── components/      # React components
│   │   ├── Header.jsx   # Navigation header
│   │   ├── Hero.jsx     # Hero section
│   │   ├── Services.jsx # Services section
│   │   ├── WhyChooseUs.jsx
│   │   ├── Contact.jsx  # Contact form
│   │   └── Footer.jsx   # Footer
│   ├── App.jsx          # Main app component
│   ├── App.css          # App-specific styles
│   ├── index.css        # Tailwind + custom CSS
│   └── main.jsx         # Entry point
├── .env                 # Environment variables (git-ignored)
├── .env.example         # Environment template
├── .gitignore           # Git ignore rules
├── index.html           # HTML template
├── package.json         # Dependencies
├── tailwind.config.js   # Tailwind configuration
└── vite.config.js       # Vite configuration
```

## 🔒 Security Features

| Feature | Implementation |
|---------|----------------|
| XSS Prevention | DOMPurify sanitizes all form inputs |
| Secure Headers | react-helmet-async manages CSP and security meta tags |
| Input Validation | Client-side validation for email and phone formats |
| Environment Variables | Sensitive config in `.env` (git-ignored) |

## 🎨 Design System

### Colors

- **Primary**: Blues (#3b82f6, #2563eb, #1d4ed8)
- **Secondary**: Greens (#22c55e, #16a34a, #15803d)
- **Accent**: Cyan (#06b6d4, #22d3ee)
- **Neutrals**: Grays for text and backgrounds

### Typography

- **Font Family**: Inter (Google Fonts)
- **Weights**: 300-800

## 📱 Sections

1. **Header**: Responsive navigation with mobile hamburger menu
2. **Hero**: Main headline with CTAs and trust indicators
3. **Services**: Commercial and Residential cleaning services
4. **Why Choose Us**: Key differentiators and statistics
5. **Contact**: Quote request form with validation
6. **Footer**: Company info, links, and contact details

## 🧪 Testing

Run ESLint for code quality:

```bash
npm run lint
```

## 📝 Environment Variables

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API base URL |
| `VITE_CONTACT_API_ENDPOINT` | Contact form submission endpoint |
| `VITE_GA_TRACKING_ID` | Google Analytics tracking ID |
| `VITE_GOOGLE_MAPS_API_KEY` | Google Maps embed API key |

## 🚢 Deployment

The `dist/` folder after `npm run build` can be deployed to:

- Vercel
- Netlify
- AWS S3 + CloudFront
- Firebase Hosting
- Any static hosting provider

## 📄 License

© 2026 CleanPeak (CPL). All rights reserved.

---

**Note**: CPL must always be capitalized as it is the official abbreviation for CleanPeak.
