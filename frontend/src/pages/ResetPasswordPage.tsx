import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Database, Lock, CheckCircle2, AlertCircle } from 'lucide-react';
import { api } from '../lib/api';

export default function ResetPasswordPage() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const token = searchParams.get('token');

    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [validating, setValidating] = useState(true);
    const [tokenValid, setTokenValid] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!token) {
            setError('Invalid reset link');
            setValidating(false);
            return;
        }

        // Verify token
        api.get(`/auth/verify-reset-token/${token}`)
            .then(response => {
                setTokenValid(response.data.valid);
                if (!response.data.valid) {
                    setError('This reset link is invalid or has expired');
                }
            })
            .catch(() => {
                setError('Failed to verify reset link');
            })
            .finally(() => {
                setValidating(false);
            });
    }, [token]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (newPassword !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (newPassword.length < 6) {
            setError('Password must be at least 6 characters');
            return;
        }

        setLoading(true);

        try {
            await api.post('/auth/reset-password', {
                token,
                new_password: newPassword
            });
            setSuccess(true);

            // Redirect to login after 2 seconds
            setTimeout(() => {
                navigate('/login');
            }, 2000);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to reset password');
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
                    {validating ? (
                        <div className="text-center py-12">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent mx-auto mb-4"></div>
                            <p className="text-sm text-muted-foreground">Verifying reset link...</p>
                        </div>
                    ) : !tokenValid ? (
                        <div className="text-center py-8">
                            <div className="w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center mx-auto mb-4">
                                <AlertCircle className="w-8 h-8 text-destructive" />
                            </div>
                            <h2 className="text-xl font-semibold mb-2 text-foreground">Invalid Reset Link</h2>
                            <p className="text-sm text-muted-foreground mb-8">
                                {error || 'This password reset link is invalid or has expired.'}
                            </p>
                            <Link to="/forgot-password">
                                <Button className="w-full bg-accent hover:bg-accent/90">
                                    Request new link
                                </Button>
                            </Link>
                        </div>
                    ) : success ? (
                        <div className="text-center py-8">
                            <div className="w-16 h-16 rounded-full bg-accent/10 flex items-center justify-center mx-auto mb-4">
                                <CheckCircle2 className="w-8 h-8 text-accent" />
                            </div>
                            <h2 className="text-xl font-semibold mb-2 text-foreground">Password Reset Successful</h2>
                            <p className="text-sm text-muted-foreground mb-4">
                                Your password has been updated successfully.
                            </p>
                            <p className="text-xs text-muted-foreground">
                                Redirecting to login...
                            </p>
                        </div>
                    ) : (
                        <>
                            <div className="mb-8 text-center">
                                <h1 className="text-2xl font-semibold mb-2 text-foreground">Reset your password</h1>
                                <p className="text-sm text-muted-foreground">
                                    Enter your new password below
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
                                        New Password
                                    </label>
                                    <div className="relative">
                                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                                        <Input
                                            type="password"
                                            value={newPassword}
                                            onChange={(e) => setNewPassword(e.target.value)}
                                            placeholder="••••••••"
                                            required
                                            minLength={6}
                                            className="pl-10 h-11 bg-muted border-border focus:border-accent"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="text-sm font-medium text-foreground mb-1.5 block">
                                        Confirm Password
                                    </label>
                                    <div className="relative">
                                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                                        <Input
                                            type="password"
                                            value={confirmPassword}
                                            onChange={(e) => setConfirmPassword(e.target.value)}
                                            placeholder="••••••••"
                                            required
                                            minLength={6}
                                            className="pl-10 h-11 bg-muted border-border focus:border-accent"
                                        />
                                    </div>
                                </div>

                                <Button
                                    type="submit"
                                    className="w-full h-11 bg-accent hover:bg-accent/90 text-white font-medium"
                                    disabled={loading}
                                >
                                    {loading ? 'Resetting...' : 'Reset password'}
                                </Button>
                            </form>
                        </>
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
