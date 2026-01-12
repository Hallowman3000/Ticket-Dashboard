import { Award, Users, Leaf, Clock, Shield, ThumbsUp } from 'lucide-react';

/**
 * Why Choose Us section for CleanPeak (CPL) website
 * Highlights key differentiators and company values
 */
const WhyChooseUs = () => {
    const features = [
        {
            icon: Users,
            title: 'Professional Team',
            description: 'Our cleaners are trained, vetted, and uniformed. We hire only the best to ensure top-quality service.',
            color: 'primary',
        },
        {
            icon: Leaf,
            title: 'Eco-Friendly Products',
            description: 'We use environmentally safe, non-toxic cleaning solutions that are gentle on your space and the planet.',
            color: 'secondary',
        },
        {
            icon: Clock,
            title: 'Flexible Scheduling',
            description: 'Book cleaning at your convenience—weekdays, weekends, or after hours. We work around your schedule.',
            color: 'accent',
        },
        {
            icon: Shield,
            title: 'Fully Insured',
            description: 'Complete peace of mind with full insurance coverage. Your property is protected while we work.',
            color: 'primary',
        },
        {
            icon: Award,
            title: 'Quality Guaranteed',
            description: 'Not satisfied? We will re-clean at no extra cost. Our 100% satisfaction guarantee means zero risk for you.',
            color: 'secondary',
        },
        {
            icon: ThumbsUp,
            title: 'Trusted by Nairobi',
            description: 'Join hundreds of satisfied clients across Nairobi who trust CleanPeak (CPL) for their cleaning needs.',
            color: 'accent',
        },
    ];

    const getColorClasses = (color) => {
        const colors = {
            primary: 'bg-primary-100 text-primary-600 group-hover:bg-primary-600',
            secondary: 'bg-secondary-100 text-secondary-600 group-hover:bg-secondary-600',
            accent: 'bg-accent-100 text-accent-600 group-hover:bg-accent-500',
        };
        return colors[color] || colors.primary;
    };

    return (
        <section id="why-us" className="section-padding bg-gray-50">
            <div className="container-custom">
                {/* Section Header */}
                <div className="text-center max-w-3xl mx-auto mb-16">
                    <span className="inline-block px-4 py-1 bg-primary-100 text-primary-600 rounded-full text-sm font-semibold mb-4">
                        Why Choose Us
                    </span>
                    <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                        The CleanPeak <span className="text-primary-600">Difference</span>
                    </h2>
                    <p className="text-gray-600 text-lg">
                        At CPL, we do not just clean—we create healthier, happier spaces.
                        Here is why Nairobi businesses and homeowners choose us.
                    </p>
                </div>

                {/* Features Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {features.map((feature, index) => (
                        <div
                            key={feature.title}
                            className="group bg-white rounded-2xl p-8 shadow-sm card-hover"
                            style={{ animationDelay: `${index * 0.1}s` }}
                        >
                            <div className={`w-14 h-14 rounded-xl flex items-center justify-center mb-6 transition-all duration-300 ${getColorClasses(feature.color)} group-hover:text-white group-hover:scale-110`}>
                                <feature.icon className="w-7 h-7" />
                            </div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-3 group-hover:text-primary-600 transition-colors">
                                {feature.title}
                            </h3>
                            <p className="text-gray-600 leading-relaxed">
                                {feature.description}
                            </p>
                        </div>
                    ))}
                </div>

                {/* Stats Section */}
                <div className="mt-16 bg-gradient-to-r from-primary-600 to-primary-800 rounded-2xl p-8 md:p-12">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                        <div className="text-center">
                            <div className="text-4xl md:text-5xl font-bold text-white mb-2">500+</div>
                            <div className="text-primary-200 text-sm md:text-base">Happy Clients</div>
                        </div>
                        <div className="text-center">
                            <div className="text-4xl md:text-5xl font-bold text-white mb-2">10K+</div>
                            <div className="text-primary-200 text-sm md:text-base">Cleanings Done</div>
                        </div>
                        <div className="text-center">
                            <div className="text-4xl md:text-5xl font-bold text-white mb-2">50+</div>
                            <div className="text-primary-200 text-sm md:text-base">Team Members</div>
                        </div>
                        <div className="text-center">
                            <div className="text-4xl md:text-5xl font-bold text-white mb-2">99%</div>
                            <div className="text-primary-200 text-sm md:text-base">Satisfaction Rate</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default WhyChooseUs;
