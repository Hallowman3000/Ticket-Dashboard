import { Building2, Home, Briefcase, Truck, ArrowRight } from 'lucide-react';

/**
 * Services section for CleanPeak (CPL) website
 * Displays Residential, Commercial, Office, and Moving In/Out cleaning services
 */
const Services = () => {
    const services = [
        {
            icon: Home,
            title: 'Residential Cleaning',
            description: 'Complete home cleaning services—from regular maintenance to deep cleaning. Come home to a spotless sanctuary every day.',
            features: ['Kitchen & bathroom deep cleaning', 'Bedroom & living areas', 'Window & floor cleaning'],
            color: 'secondary',
        },
        {
            icon: Building2,
            title: 'Commercial Cleaning',
            description: 'Professional cleaning solutions for retail stores, restaurants, and commercial establishments. Keep your business spotless.',
            features: ['Retail space cleaning', 'Restaurant sanitation', 'Common area maintenance'],
            color: 'primary',
        },
        {
            icon: Briefcase,
            title: 'Office Cleaning',
            description: 'Daily, weekly, or monthly office cleaning tailored to your business needs. Keep your workspace pristine and productive.',
            features: ['Desk & workstation cleaning', 'Restroom maintenance', 'Break room sanitization'],
            color: 'primary',
        },
        {
            icon: Truck,
            title: 'Move In/Out Cleaning',
            description: 'Comprehensive cleaning for tenants moving in or out. We make sure the space is spotless for the next chapter.',
            features: ['Deep cleaning all rooms', 'Appliance cleaning', 'Final inspection ready'],
            color: 'secondary',
        },
    ];

    const getColorClasses = (color) => {
        const colors = {
            primary: {
                bg: 'bg-primary-100 text-primary-600 group-hover:bg-primary-600',
                dot: 'bg-primary-500',
                link: 'text-primary-600 hover:text-primary-700',
            },
            secondary: {
                bg: 'bg-secondary-100 text-secondary-600 group-hover:bg-secondary-600',
                dot: 'bg-secondary-500',
                link: 'text-secondary-600 hover:text-secondary-700',
            },
        };
        return colors[color] || colors.primary;
    };

    return (
        <section id="services" className="section-padding bg-white">
            <div className="container-custom">
                {/* Section Header */}
                <div className="text-center max-w-3xl mx-auto mb-16">
                    <span className="inline-block px-4 py-1 bg-secondary-100 text-secondary-600 rounded-full text-sm font-semibold mb-4">
                        Our Services
                    </span>
                    <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                        Professional Cleaning <span className="text-secondary-600">Solutions</span>
                    </h2>
                    <p className="text-gray-600 text-lg">
                        From corporate offices to cozy homes, CleanPeak (CPL) provides comprehensive
                        cleaning services tailored to your specific needs.
                    </p>
                </div>

                {/* Services Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {services.map((service) => {
                        const colorClasses = getColorClasses(service.color);
                        return (
                            <div
                                key={service.title}
                                className="group bg-white rounded-2xl p-8 shadow-sm border border-gray-100 card-hover"
                            >
                                <div className={`w-14 h-14 rounded-xl flex items-center justify-center mb-6 transition-all duration-300 ${colorClasses.bg} group-hover:text-white group-hover:scale-110`}>
                                    <service.icon className="w-7 h-7" />
                                </div>
                                <h3 className="text-xl font-semibold text-gray-900 mb-3 group-hover:text-primary-600 transition-colors">
                                    {service.title}
                                </h3>
                                <p className="text-gray-600 mb-4 leading-relaxed">
                                    {service.description}
                                </p>
                                <ul className="space-y-2 mb-6">
                                    {service.features.map((feature, index) => (
                                        <li key={index} className="flex items-center gap-2 text-sm text-gray-500">
                                            <span className={`w-1.5 h-1.5 rounded-full ${colorClasses.dot}`} />
                                            {feature}
                                        </li>
                                    ))}
                                </ul>
                                <a
                                    href="#contact"
                                    className={`inline-flex items-center gap-2 font-medium transition-colors ${colorClasses.link}`}
                                >
                                    Get a Quote
                                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                </a>
                            </div>
                        );
                    })}
                </div>

                {/* CTA Banner */}
                <div className="mt-16 bg-gradient-to-r from-primary-600 to-primary-800 rounded-2xl p-8 md:p-12 text-center">
                    <h3 className="text-2xl md:text-3xl font-bold text-white mb-4">
                        Need a Custom Cleaning Solution?
                    </h3>
                    <p className="text-primary-100 mb-6 max-w-2xl mx-auto">
                        Every space is unique. Contact us for a personalized cleaning plan
                        that fits your exact requirements and budget.
                    </p>
                    <a href="#contact" className="inline-flex items-center gap-2 bg-white text-primary-700 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                        Request Custom Quote
                        <ArrowRight className="w-5 h-5" />
                    </a>
                </div>
            </div>
        </section>
    );
};

export default Services;
