import { useState } from 'react';
import { Menu, X } from 'lucide-react';

/**
 * Header component for CleanPeak (CPL) website
 * Features responsive navigation with mobile hamburger menu
 * Logo uses text-only branding (no sparkle icon)
 */
const Header = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    const navLinks = [
        { name: 'Home', href: '#home' },
        { name: 'Services', href: '#services' },
        { name: 'Why Us', href: '#why-us' },
        { name: 'Contact', href: '#contact' },
    ];

    return (
        <header className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm shadow-sm">
            <div className="container-custom">
                <div className="flex items-center justify-between h-16 md:h-20 px-4">
                    {/* Logo - Text Only */}
                    <a href="#home" className="flex items-center gap-2 group">
                        <div className="flex flex-col">
                            <div className="flex items-baseline gap-1">
                                <span className="text-sm font-semibold text-gray-500">CPL</span>
                                <span className="text-xl font-bold text-primary-700 group-hover:text-primary-600 transition-colors">CleanPeak</span>
                            </div>
                        </div>
                    </a>

                    {/* Desktop Navigation */}
                    <nav className="hidden md:flex items-center gap-8">
                        {navLinks.map((link) => (
                            <a
                                key={link.name}
                                href={link.href}
                                className="text-gray-600 hover:text-primary-600 font-medium transition-colors duration-200 relative after:absolute after:bottom-0 after:left-0 after:w-0 after:h-0.5 after:bg-primary-600 after:transition-all after:duration-300 hover:after:w-full"
                            >
                                {link.name}
                            </a>
                        ))}
                        <a
                            href="#contact"
                            className="btn-primary text-sm"
                        >
                            Book Now
                        </a>
                    </nav>

                    {/* Mobile Menu Button */}
                    <button
                        className="md:hidden p-2 text-gray-600 hover:text-primary-600 transition-colors"
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                        aria-label="Toggle menu"
                    >
                        {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                    </button>
                </div>

                {/* Mobile Navigation */}
                <div
                    className={`md:hidden overflow-hidden transition-all duration-300 ease-in-out ${isMenuOpen ? 'max-h-80 opacity-100' : 'max-h-0 opacity-0'
                        }`}
                >
                    <nav className="flex flex-col pb-4 px-4">
                        {navLinks.map((link) => (
                            <a
                                key={link.name}
                                href={link.href}
                                onClick={() => setIsMenuOpen(false)}
                                className="py-3 text-gray-600 hover:text-primary-600 font-medium transition-colors border-b border-gray-100"
                            >
                                {link.name}
                            </a>
                        ))}
                        <a
                            href="#contact"
                            onClick={() => setIsMenuOpen(false)}
                            className="btn-primary text-center mt-4"
                        >
                            Book Now
                        </a>
                    </nav>
                </div>
            </div>
        </header>
    );
};

export default Header;
