import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Database, Mail, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { api } from '../lib/api';

export default function ForgotPasswordPage() {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await api.post('/auth/forgot-password', { email });
            setSuccess(true);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to send reset email');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-background relative overflow-hidden">
            {/* Subtle background effect */}
            <div className="absolute inset-0 opacity-5">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-accent rounded-full blur-3xl" />
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent rounded-full blur-3xl" />
            </div>

            {/* Card */}
            <div className="relative w-full max-w-md px-6">
                {/* Logo */}
                <div className="flex items-center justify-center gap-2 mb-12">
                    <div className="w-10 h-10 rounded-xl bg-accent/10 flex items-center justify-center">
                        <Database className="w-6 h-6 text-accent" />
                    </div>
                    <span className="text-xl font-semibold text-foreground">AI Data Analyst</span>
                </div>

                <div className="bg-card border border-border rounded-2xl p-8 shadow-depth">
                    {!success ? (
                        <>
                            <div className="mb-8 text-center">
                                <h1 className="text-2xl font-semibold mb-2 text-foreground">Forgot password?</h1>
                                <p className="text-sm text-muted-foreground">
                                    Enter your email and we'll send you a reset link
                                </p>
                            </div>

                            {error && (
                                <div className="mb-4 p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-sm text-destructive">
                                    {error}
                                </div>
                            )}

                            <form onSubmit={handleSubmit} className="space-y-4">
                                <div>
                                    <label className="text-sm font-medium text-foreground mb-1.5 block">
                                        Email
                                    </label>
                                    <div className="relative">
                                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                                        <Input
                                            type="email"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            placeholder="you@company.com"
                                            required
                                            className="pl-10 h-11 bg-muted border-border focus:border-accent"
                                        />
                                    </div>
                                </div>

                                <Button
                                    type="submit"
                                    className="w-full h-11 bg-accent hover:bg-accent/90 text-white font-medium"
                                    disabled={loading}
                                >
                                    {loading ? 'Sending...' : 'Send reset link'}
                                </Button>
                            </form>

                            <div className="mt-6 text-center">
                                <Link
                                    to="/login"
                                    className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-accent transition-colors"
                                >
                                    <ArrowLeft className="w-4 h-4" />
                                    Back to login
                                </Link>
                            </div>
                        </>
                    ) : (
                        <div className="text-center py-8">
                            <div className="w-16 h-16 rounded-full bg-accent/10 flex items-center justify-center mx-auto mb-4">
                                <CheckCircle2 className="w-8 h-8 text-accent" />
                            </div>
                            <h2 className="text-xl font-semibold mb-2 text-foreground">Check your email</h2>
                            <p className="text-sm text-muted-foreground mb-8">
                                If an account exists for <strong>{email}</strong>, you will receive a password reset link shortly.
                            </p>
                            <p className="text-xs text-muted-foreground mb-6">
                                Didn't receive the email? Check your spam folder or try again.
                            </p>
                            <Link to="/login">
                                <Button variant="outline" className="w-full">
                                    Return to login
                                </Button>
                            </Link>
                        </div>
                    )}
                </div>

                {/* Privacy Note */}
                <p className="text-center text-xs text-muted-foreground mt-6">
                    Your data stays private. No training on your data.
                </p>
            </div>
        </div>
    );
}
