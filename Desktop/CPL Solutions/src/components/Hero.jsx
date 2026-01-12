import { ArrowRight } from 'lucide-react';

/**
 * Hero section component for CleanPeak (CPL) website
 * Features background image with overlay and call-to-action
 */
const Hero = () => {
    return (
        <section id="home" className="relative min-h-screen flex items-center overflow-hidden">
            {/* Background Image */}
            <div
                className="absolute inset-0 bg-cover bg-center bg-no-repeat"
                style={{
                    backgroundImage: 'url(/hero-bg.png)',
                }}
            />

            {/* Dark Overlay */}
            <div className="absolute inset-0 bg-black/50" />

            <div className="container-custom relative z-10 px-4 py-32 md:py-40">
                <div className="max-w-3xl mx-auto text-center">
                    {/* Main Headline */}
                    <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6 animate-fade-in-up">
                        Experience the Clean
                    </h1>

                    {/* Subheadline */}
                    <p className="text-lg md:text-xl text-white/90 mb-10 max-w-2xl mx-auto leading-relaxed animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
                        CleanPeak (CPL) offers premium cleaning services tailored to your home and office needs.
                    </p>

                    {/* CTA Button */}
                    <div className="animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                        <a
                            href="#contact"
                            className="inline-flex items-center gap-2 bg-secondary-600 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-300 hover:bg-secondary-700 hover:shadow-lg hover:shadow-secondary-500/25 active:scale-95"
                        >
                            Get a Free Recommendation
                            <ArrowRight className="w-5 h-5" />
                        </a>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default Hero;
