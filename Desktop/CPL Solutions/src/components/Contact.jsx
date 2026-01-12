import { useState } from 'react';
import DOMPurify from 'dompurify';
import { Send, MapPin, Phone, Mail, Clock, CheckCircle, AlertCircle } from 'lucide-react';

/**
 * Contact section for CleanPeak (CPL) website
 * Features a quote request form with XSS prevention via DOMPurify
 */
const Contact = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        phone: '',
        service: '',
        message: '',
    });

    const [status, setStatus] = useState({
        type: '', // 'success' | 'error'
        message: '',
    });

    const [isSubmitting, setIsSubmitting] = useState(false);

    /**
     * Sanitizes input to prevent XSS attacks
     * Uses DOMPurify to strip malicious content
     */
    const sanitizeInput = (input) => {
        return DOMPurify.sanitize(input, {
            ALLOWED_TAGS: [], // Strip all HTML tags
            ALLOWED_ATTR: [], // Strip all attributes
        });
    };

    /**
     * Validates email format
     */
    const isValidEmail = (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };

    /**
     * Validates phone number (Kenyan format)
     */
    const isValidPhone = (phone) => {
        // Allow Kenyan phone formats: +254..., 07..., 01...
        const phoneRegex = /^(\+254|0)[17]\d{8}$/;
        return !phone || phoneRegex.test(phone.replace(/\s/g, ''));
    };

    /**
     * Handles input changes with sanitization
     */
    const handleChange = (e) => {
        const { name, value } = e.target;
        // Sanitize input immediately on change
        const sanitizedValue = sanitizeInput(value);
        setFormData((prev) => ({
            ...prev,
            [name]: sanitizedValue,
        }));
        // Clear any previous status messages
        if (status.message) {
            setStatus({ type: '', message: '' });
        }
    };

    /**
     * Handles form submission
     */
    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);

        // Validate required fields
        if (!formData.name || !formData.email || !formData.message) {
            setStatus({
                type: 'error',
                message: 'Please fill in all required fields.',
            });
            setIsSubmitting(false);
            return;
        }

        // Validate email format
        if (!isValidEmail(formData.email)) {
            setStatus({
                type: 'error',
                message: 'Please enter a valid email address.',
            });
            setIsSubmitting(false);
            return;
        }

        // Validate phone format (optional field)
        if (formData.phone && !isValidPhone(formData.phone)) {
            setStatus({
                type: 'error',
                message: 'Please enter a valid Kenyan phone number.',
            });
            setIsSubmitting(false);
            return;
        }

        // Simulate form submission (replace with actual API call)
        try {
            // In production, send sanitized data to backend
            // const response = await fetch('/api/contact', {
            //   method: 'POST',
            //   headers: { 'Content-Type': 'application/json' },
            //   body: JSON.stringify(formData),
            // });

            // Simulate API delay
            await new Promise((resolve) => setTimeout(resolve, 1000));

            setStatus({
                type: 'success',
                message: 'Thank you! We will contact you shortly.',
            });

            // Reset form
            setFormData({
                name: '',
                email: '',
                phone: '',
                service: '',
                message: '',
            });
        } catch {
            setStatus({
                type: 'error',
                message: 'Something went wrong. Please try again.',
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const serviceOptions = [
        { value: '', label: 'Select a service' },
        { value: 'office', label: 'Office Cleaning' },
        { value: 'post-construction', label: 'Post-Construction Cleanup' },
        { value: 'industrial', label: 'Industrial Cleaning' },
        { value: 'home', label: 'Home Cleaning' },
        { value: 'upholstery', label: 'Upholstery Cleaning' },
        { value: 'carpet', label: 'Carpet & Rug Cleaning' },
        { value: 'other', label: 'Other / Custom' },
    ];

    const contactInfo = [
        {
            icon: MapPin,
            title: 'Our Location',
            content: 'Westlands, Nairobi, Kenya',
        },
        {
            icon: Phone,
            title: 'Phone',
            content: '+254 700 000 000',
            href: 'tel:+254700000000',
        },
        {
            icon: Mail,
            title: 'Email',
            content: 'info@cleanpeak.co.ke',
            href: 'mailto:info@cleanpeak.co.ke',
        },
        {
            icon: Clock,
            title: 'Working Hours',
            content: 'Mon - Sat: 7AM - 7PM',
        },
    ];

    return (
        <section id="contact" className="section-padding bg-gray-50">
            <div className="container-custom">
                {/* Section Header */}
                <div className="text-center max-w-3xl mx-auto mb-16">
                    <span className="inline-block px-4 py-1 bg-primary-100 text-primary-600 rounded-full text-sm font-semibold mb-4">
                        Contact Us
                    </span>
                    <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                        Get a <span className="text-primary-600">Free Quote</span>
                    </h2>
                    <p className="text-gray-600 text-lg">
                        Ready for a spotless space? Contact CleanPeak (CPL) today
                        for a free, no-obligation quote tailored to your needs.
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 lg:gap-12">
                    {/* Contact Information */}
                    <div className="lg:col-span-2">
                        <div className="bg-gradient-to-br from-primary-600 to-primary-800 rounded-2xl p-8 text-white h-full">
                            <h3 className="text-2xl font-bold mb-6">Get in Touch</h3>
                            <p className="text-primary-100 mb-8">
                                Have questions? We would love to hear from you.
                                Reach out through any of these channels.
                            </p>

                            <div className="space-y-6">
                                {contactInfo.map((info) => (
                                    <div key={info.title} className="flex items-start gap-4">
                                        <div className="w-12 h-12 bg-white/10 rounded-lg flex items-center justify-center flex-shrink-0">
                                            <info.icon className="w-6 h-6 text-secondary-300" />
                                        </div>
                                        <div>
                                            <p className="text-primary-200 text-sm mb-1">{info.title}</p>
                                            {info.href ? (
                                                <a
                                                    href={info.href}
                                                    className="text-white font-medium hover:text-secondary-300 transition-colors"
                                                >
                                                    {info.content}
                                                </a>
                                            ) : (
                                                <p className="text-white font-medium">{info.content}</p>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Decorative Element */}
                            <div className="mt-12 pt-8 border-t border-white/20">
                                <p className="text-primary-200 text-sm">
                                    Serving all of Nairobi and surrounding areas
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Contact Form */}
                    <div className="lg:col-span-3">
                        <form onSubmit={handleSubmit} className="bg-white rounded-2xl p-8 shadow-sm">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* Name */}
                                <div>
                                    <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                                        Full Name <span className="text-red-500">*</span>
                                    </label>
                                    <input
                                        type="text"
                                        id="name"
                                        name="name"
                                        value={formData.name}
                                        onChange={handleChange}
                                        placeholder="John Doe"
                                        className="input-field"
                                        required
                                        maxLength={100}
                                    />
                                </div>

                                {/* Email */}
                                <div>
                                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                                        Email Address <span className="text-red-500">*</span>
                                    </label>
                                    <input
                                        type="email"
                                        id="email"
                                        name="email"
                                        value={formData.email}
                                        onChange={handleChange}
                                        placeholder="john@example.com"
                                        className="input-field"
                                        required
                                        maxLength={100}
                                    />
                                </div>

                                {/* Phone */}
                                <div>
                                    <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                                        Phone Number
                                    </label>
                                    <input
                                        type="tel"
                                        id="phone"
                                        name="phone"
                                        value={formData.phone}
                                        onChange={handleChange}
                                        placeholder="+254 700 000 000"
                                        className="input-field"
                                        maxLength={20}
                                    />
                                </div>

                                {/* Service */}
                                <div>
                                    <label htmlFor="service" className="block text-sm font-medium text-gray-700 mb-2">
                                        Service Needed
                                    </label>
                                    <select
                                        id="service"
                                        name="service"
                                        value={formData.service}
                                        onChange={handleChange}
                                        className="input-field bg-white"
                                    >
                                        {serviceOptions.map((option) => (
                                            <option key={option.value} value={option.value}>
                                                {option.label}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                {/* Message */}
                                <div className="md:col-span-2">
                                    <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                                        Your Message <span className="text-red-500">*</span>
                                    </label>
                                    <textarea
                                        id="message"
                                        name="message"
                                        value={formData.message}
                                        onChange={handleChange}
                                        placeholder="Tell us about your cleaning needs..."
                                        rows={5}
                                        className="input-field resize-none"
                                        required
                                        maxLength={1000}
                                    />
                                </div>
                            </div>

                            {/* Status Message */}
                            {status.message && (
                                <div
                                    className={`mt-6 p-4 rounded-lg flex items-center gap-3 ${status.type === 'success'
                                            ? 'bg-secondary-50 text-secondary-700'
                                            : 'bg-red-50 text-red-700'
                                        }`}
                                >
                                    {status.type === 'success' ? (
                                        <CheckCircle className="w-5 h-5 flex-shrink-0" />
                                    ) : (
                                        <AlertCircle className="w-5 h-5 flex-shrink-0" />
                                    )}
                                    <p>{status.message}</p>
                                </div>
                            )}

                            {/* Submit Button */}
                            <button
                                type="submit"
                                disabled={isSubmitting}
                                className="mt-6 w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isSubmitting ? (
                                    <>
                                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        Sending...
                                    </>
                                ) : (
                                    <>
                                        <Send className="w-5 h-5" />
                                        Send Message
                                    </>
                                )}
                            </button>

                            <p className="mt-4 text-center text-sm text-gray-500">
                                We typically respond within 2 hours during business hours.
                            </p>
                        </form>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default Contact;
