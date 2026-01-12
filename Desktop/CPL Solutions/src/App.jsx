import { HelmetProvider, Helmet } from 'react-helmet-async';
import Header from './components/Header';
import Hero from './components/Hero';
import Services from './components/Services';
import WhyChooseUs from './components/WhyChooseUs';
import Contact from './components/Contact';
import Footer from './components/Footer';
import './App.css';

/**
 * Main App component for CleanPeak (CPL) website
 * Wrapped with HelmetProvider for secure head management
 */
function App() {
  return (
    <HelmetProvider>
      <Helmet>
        {/* Primary Meta Tags */}
        <title>CleanPeak (CPL) | Professional Cleaning Services in Nairobi, Kenya</title>
        <meta
          name="description"
          content="CleanPeak (CPL) offers professional commercial and residential cleaning services in Nairobi, Kenya. Office cleaning, home cleaning, post-construction cleanup, and more."
        />
        <meta name="keywords" content="cleaning services Nairobi, office cleaning Kenya, residential cleaning, commercial cleaning, CleanPeak, CPL" />
        <meta name="author" content="CleanPeak (CPL)" />

        {/* Open Graph / Social Media */}
        <meta property="og:type" content="website" />
        <meta property="og:title" content="CleanPeak (CPL) | Professional Cleaning Services in Nairobi" />
        <meta
          property="og:description"
          content="Expert commercial and residential cleaning services in Nairobi. Get a free quote today!"
        />
        <meta property="og:locale" content="en_KE" />

        {/* Twitter Card */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="CleanPeak (CPL) | Cleaning Services Nairobi" />
        <meta
          name="twitter:description"
          content="Professional cleaning for offices and homes in Nairobi, Kenya."
        />

        {/* Viewport and Language */}
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <html lang="en" />

        {/* Security Headers (CSP hints for the browser) */}
        <meta httpEquiv="X-Content-Type-Options" content="nosniff" />
        <meta httpEquiv="X-Frame-Options" content="DENY" />
        <meta httpEquiv="X-XSS-Protection" content="1; mode=block" />
        <meta name="referrer" content="strict-origin-when-cross-origin" />

        {/* Favicon */}
        <link rel="icon" type="image/svg+xml" href="/vite.svg" />

        {/* Google Fonts - Inter */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </Helmet>

      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-grow">
          <Hero />
          <Services />
          <WhyChooseUs />
          <Contact />
        </main>
        <Footer />
      </div>
    </HelmetProvider>
  );
}

export default App;
