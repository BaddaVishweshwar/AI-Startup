import { motion, useScroll, useTransform } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
    ArrowRight, Sparkles, Zap, Shield, TrendingUp,
    BarChart3, Database, MessageSquare, ChevronDown
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { useEffect, useRef, useState } from 'react';

export default function LandingPage() {
    const navigate = useNavigate();
    const heroRef = useRef<HTMLDivElement>(null);
    const [scrollY, setScrollY] = useState(0);

    useEffect(() => {
        const handleScroll = () => setScrollY(window.scrollY);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const features = [
        {
            icon: MessageSquare,
            title: 'Natural Language Queries',
            description: 'Ask questions in plain English and get instant insights from your data',
            color: 'from-accent to-emerald-500'
        },
        {
            icon: Sparkles,
            title: 'AI-Powered Analysis',
            description: 'Advanced AI agents understand context and deliver accurate results',
            color: 'from-emerald-500 to-teal-500'
        },
        {
            icon: BarChart3,
            title: 'Interactive Visualizations',
            description: 'Beautiful charts and graphs auto-generated from your queries',
            color: 'from-teal-500 to-cyan-500'
        },
        {
            icon: Database,
            title: 'Multi-Source Support',
            description: 'Connect to databases, CSV files, and cloud storage seamlessly',
            color: 'from-cyan-500 to-accent'
        },
        {
            icon: TrendingUp,
            title: 'Predictive Insights',
            description: 'Forecast trends and get recommendations based on your data',
            color: 'from-accent to-emerald-600'
        },
        {
            icon: Shield,
            title: 'Enterprise Security',
            description: 'Your data stays secure with encryption and access controls',
            color: 'from-emerald-600 to-teal-600'
        }
    ];

    return (
        <div className="min-h-screen bg-black text-white overflow-x-hidden">
            {/* Navigation */}
            <motion.nav
                initial={{ y: -100 }}
                animate={{ y: 0 }}
                className="fixed top-0 w-full z-50 bg-black/80 backdrop-blur-xl border-b border-white/10"
            >
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent to-emerald-500 flex items-center justify-center">
                            <Sparkles className="w-5 h-5 text-black" />
                        </div>
                        <span className="text-xl font-bold bg-gradient-to-r from-accent to-emerald-400 bg-clip-text text-transparent">
                            AI Analyst
                        </span>
                    </div>
                    <div className="flex items-center gap-4">
                        <Button
                            variant="ghost"
                            onClick={() => navigate('/login')}
                            className="text-white hover:text-accent"
                        >
                            Sign In
                        </Button>
                        <Button
                            onClick={() => navigate('/register')}
                            className="bg-gradient-to-r from-accent to-emerald-500 hover:from-accent/90 hover:to-emerald-500/90 text-black font-semibold"
                        >
                            Get Started
                        </Button>
                    </div>
                </div>
            </motion.nav>

            {/* Hero Section */}
            <section ref={heroRef} className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
                {/* Animated Background Grid */}
                <div className="absolute inset-0 opacity-20">
                    <div className="absolute inset-0" style={{
                        backgroundImage: `linear-gradient(to right, #00bfa5 1px, transparent 1px),
                                        linear-gradient(to bottom, #00bfa5 1px, transparent 1px)`,
                        backgroundSize: '80px 80px',
                        transform: `translateY(${scrollY * 0.5}px)`
                    }} />
                </div>

                {/* Glowing Orbs */}
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-accent/20 rounded-full blur-[120px] animate-pulse" />
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-emerald-500/20 rounded-full blur-[120px] animate-pulse delay-700" />

                <div className="relative z-10 max-w-6xl mx-auto px-6 text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                    >
                        <motion.div
                            initial={{ scale: 0.8, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            transition={{ delay: 0.2, duration: 0.5 }}
                            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent/10 border border-accent/20 mb-8"
                        >
                            <Zap className="w-4 h-4 text-accent" />
                            <span className="text-sm text-accent">Powered by Advanced AI</span>
                        </motion.div>

                        <h1 className="text-6xl md:text-8xl font-bold mb-6 leading-tight">
                            <span className="block bg-gradient-to-r from-white via-accent to-emerald-400 bg-clip-text text-transparent">
                                Data Analysis
                            </span>
                            <span className="block bg-gradient-to-r from-emerald-400 via-accent to-white bg-clip-text text-transparent">
                                Made Simple
                            </span>
                        </h1>

                        <p className="text-xl md:text-2xl text-gray-400 mb-12 max-w-3xl mx-auto">
                            Ask questions in plain English. Get powerful insights instantly.
                            <span className="text-accent"> No SQL required.</span>
                        </p>

                        <div className="flex items-center justify-center gap-4">
                            <Button
                                onClick={() => navigate('/register')}
                                size="lg"
                                className="bg-gradient-to-r from-accent to-emerald-500 hover:from-accent/90 hover:to-emerald-500/90 text-black font-semibold text-lg px-8 py-6 shadow-[0_0_30px_rgba(0,191,165,0.3)] hover:shadow-[0_0_50px_rgba(0,191,165,0.5)] transition-all"
                            >
                                Start Analyzing Free
                                <ArrowRight className="w-5 h-5 ml-2" />
                            </Button>
                            <Button
                                onClick={() => navigate('/login')}
                                size="lg"
                                variant="outline"
                                className="border-accent/30 text-accent hover:bg-accent/10 text-lg px-8 py-6"
                            >
                                Watch Demo
                            </Button>
                        </div>
                    </motion.div>

                    {/* Scroll Indicator */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 1.5 }}
                        className="absolute bottom-10 left-1/2 -translate-x-1/2"
                    >
                        <motion.div
                            animate={{ y: [0, 10, 0] }}
                            transition={{ repeat: Infinity, duration: 2 }}
                        >
                            <ChevronDown className="w-8 h-8 text-accent" />
                        </motion.div>
                    </motion.div>
                </div>
            </section>

            {/* Features Grid */}
            <section className="py-32 relative">
                <div className="max-w-7xl mx-auto px-6">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                        className="text-center mb-20"
                    >
                        <h2 className="text-5xl font-bold mb-6">
                            <span className="bg-gradient-to-r from-accent to-emerald-400 bg-clip-text text-transparent">
                                Powerful Features
                            </span>
                        </h2>
                        <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                            Everything you need to turn your data into actionable insights
                        </p>
                    </motion.div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {features.map((feature, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 30 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: index * 0.1, duration: 0.5 }}
                                whileHover={{ y: -5, scale: 1.02 }}
                                className="group relative p-8 rounded-2xl bg-gradient-to-br from-white/5 to-white/0 border border-white/10 hover:border-accent/30 transition-all duration-300 overflow-hidden"
                            >
                                {/* Hover Gradient */}
                                <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />

                                <div className="relative">
                                    <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                                        <feature.icon className="w-7 h-7 text-black" />
                                    </div>

                                    <h3 className="text-2xl font-semibold mb-3 text-white group-hover:text-accent transition-colors">
                                        {feature.title}
                                    </h3>

                                    <p className="text-gray-400">
                                        {feature.description}
                                    </p>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-32 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-b from-accent/10 to-transparent" />
                <div className="absolute inset-0">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-accent/20 rounded-full blur-[200px]" />
                </div>

                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="relative z-10 max-w-4xl mx-auto px-6 text-center"
                >
                    <h2 className="text-5xl md:text-6xl font-bold mb-6">
                        <span className="bg-gradient-to-r from-white via-accent to-emerald-400 bg-clip-text text-transparent">
                            Ready to Transform Your Data?
                        </span>
                    </h2>

                    <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto">
                        Join thousands of businesses using AI Analyst to make data-driven decisions faster
                    </p>

                    <Button
                        onClick={() => navigate('/register')}
                        size="lg"
                        className="bg-gradient-to-r from-accent to-emerald-500 hover:from-accent/90 hover:to-emerald-500/90 text-black font-semibold text-lg px-12 py-7 shadow-[0_0_40px_rgba(0,191,165,0.4)] hover:shadow-[0_0_60px_rgba(0,191,165,0.6)] transition-all"
                    >
                        Get Started for Free
                        <ArrowRight className="w-5 h-5 ml-2" />
                    </Button>

                    <p className="text-sm text-gray-500 mt-6">
                        No credit card required • Free forever plan available
                    </p>
                </motion.div>
            </section>

            {/* Footer */}
            <footer className="border-t border-white/10 py-12">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-accent to-emerald-500" />
                            <span className="font-semibold text-gray-400">AI Analyst</span>
                        </div>
                        <p className="text-gray-500 text-sm">
                            © 2024 AI Analyst. All rights reserved.
                        </p>
                    </div>
                </div>
            </footer>
        </div>
    );
}
