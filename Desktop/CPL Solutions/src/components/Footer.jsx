import { MapPin, Phone, Mail, Clock, Facebook, Twitter, Instagram, Linkedin } from 'lucide-react';

/**
 * Footer component for CleanPeak (CPL) website
 * Contains company info, contact details, and social links
 */
const Footer = () => {
    const currentYear = new Date().getFullYear();

    const quickLinks = [
        { name: 'Home', href: '#home' },
        { name: 'Services', href: '#services' },
        { name: 'Why Choose Us', href: '#why-us' },
        { name: 'Contact', href: '#contact' },
    ];

    const services = [
        'Residential Cleaning',
        'Commercial Cleaning',
        'Office Cleaning',
        'Move In/Out Cleaning',
    ];

    const socialLinks = [
        { icon: Facebook, href: '#', label: 'Facebook' },
        { icon: Twitter, href: '#', label: 'Twitter' },
        { icon: Instagram, href: '#', label: 'Instagram' },
        { icon: Linkedin, href: '#', label: 'LinkedIn' },
    ];

    return (
        <footer className="bg-gray-900 text-gray-300">
            {/* Main Footer Content */}
            <div className="container-custom section-padding">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">
                    {/* Company Info */}
                    <div className="lg:col-span-1">
                        <div className="flex items-center gap-2 mb-4">
                            <div className="flex flex-col">
                                <div className="flex items-baseline gap-1">
                                    <span className="text-sm font-semibold text-gray-400">CPL</span>
                                    <span className="text-xl font-bold text-white">CleanPeak</span>
                                </div>
                            </div>
                        </div>
                        <p className="text-gray-400 mb-4 leading-relaxed">
                            Professional commercial and residential cleaning services in Nairobi, Kenya.
                            Delivering spotless results since day one.
                        </p>
                        <div className="flex gap-3">
                            {socialLinks.map((social) => (
                                <a
                                    key={social.label}
                                    href={social.href}
                                    aria-label={social.label}
                                    className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center text-gray-400 hover:bg-primary-600 hover:text-white transition-all duration-300"
                                >
                                    <social.icon className="w-5 h-5" />
                                </a>
                            ))}
                        </div>
                    </div>

                    {/* Quick Links */}
                    <div>
                        <h3 className="text-white font-semibold text-lg mb-4">Quick Links</h3>
                        <ul className="space-y-3">
                            {quickLinks.map((link) => (
                                <li key={link.name}>
                                    <a
                                        href={link.href}
                                        className="text-gray-400 hover:text-primary-400 transition-colors duration-200"
                                    >
                                        {link.name}
                                    </a>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Services */}
                    <div>
                        <h3 className="text-white font-semibold text-lg mb-4">Our Services</h3>
                        <ul className="space-y-3">
                            {services.map((service) => (
                                <li key={service}>
                                    <span className="text-gray-400">{service}</span>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Contact Info */}
                    <div>
                        <h3 className="text-white font-semibold text-lg mb-4">Contact Us</h3>
                        <ul className="space-y-4">
                            <li className="flex items-start gap-3">
                                <MapPin className="w-5 h-5 text-primary-500 mt-0.5 flex-shrink-0" />
                                <span className="text-gray-400">Westlands, Nairobi, Kenya</span>
                            </li>
                            <li className="flex items-center gap-3">
                                <Phone className="w-5 h-5 text-primary-500 flex-shrink-0" />
                                <a href="tel:+254700000000" className="text-gray-400 hover:text-primary-400 transition-colors">
                                    +254 700 000 000
                                </a>
                            </li>
                            <li className="flex items-center gap-3">
                                <Mail className="w-5 h-5 text-primary-500 flex-shrink-0" />
                                <a href="mailto:info@cleanpeak.co.ke" className="text-gray-400 hover:text-primary-400 transition-colors">
                                    info@cleanpeak.co.ke
                                </a>
                            </li>
                            <li className="flex items-start gap-3">
                                <Clock className="w-5 h-5 text-primary-500 mt-0.5 flex-shrink-0" />
                                <span className="text-gray-400">
                                    Mon - Sat: 7:00 AM - 7:00 PM<br />
                                    Sunday: By Appointment
                                </span>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>

            {/* Bottom Bar */}
            <div className="border-t border-gray-800">
                <div className="container-custom py-6 px-4">
                    <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                        <p className="text-gray-500 text-sm text-center md:text-left">
                            © {currentYear} CleanPeak (CPL). All rights reserved.
                        </p>
                        <div className="flex gap-6 text-sm">
                            <a href="#" className="text-gray-500 hover:text-primary-400 transition-colors">
                                Privacy Policy
                            </a>
                            <a href="#" className="text-gray-500 hover:text-primary-400 transition-colors">
                                Terms of Service
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
