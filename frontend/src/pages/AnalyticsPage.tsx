import { useEffect, useState, useRef } from 'react';
import { Send, Sparkles, ChevronDown, ChevronRight } from 'lucide-react';
import { conversationsAPI } from '../lib/conversationsAPI';
import { Button } from '../components/ui/button';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import ChartRenderer from '../components/ChartRenderer';

interface Message {
    role: 'user' | 'assistant';
    content: any;
}

export default function AnalyticsPage() {
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);
    const [currentConversation, setCurrentConversation] = useState<any>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim() || loading) return;

        const userMessage: Message = { role: 'user', content: query };
        setMessages(prev => [...prev, userMessage]);
        const userQuery = query;
        setQuery('');
        setLoading(true);

        try {
            // Simulated AI response - replace with actual API
            setTimeout(() => {
                const assistantMessage: Message = {
                    role: 'assistant',
                    content: {
                        directAnswer: "Based on the data, revenue increased by 23% in Q4 compared to Q3.",
                        sql: "SELECT quarter, SUM(revenue) as total_revenue FROM sales GROUP BY quarter ORDER BY quarter",
                        resultData: [
                            { quarter: "Q1", total_revenue: 150000 },
                            { quarter: "Q2", total_revenue: 175000 },
                            { quarter: "Q3", total_revenue: 200000 },
                            { quarter: "Q4", total_revenue: 246000 }
                        ],
                        columns: ["quarter", "total_revenue"],
                        explanation: "The revenue growth is primarily driven by increased customer acquisition in the enterprise segment during Q4. Holiday season promotions and year-end deals contributed significantly to this growth."
                    }
                };
                setMessages(prev => [...prev, assistantMessage]);
                setLoading(false);
            }, 2000);
        } catch (error) {
            console.error('Error:', error);
            setLoading(false);
        }
    };

    return (
        <div className="h-full flex flex-col bg-background">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto">
                <div className="max-w-4xl mx-auto px-6 py-8">
                    <AnimatePresence mode="popLayout">
                        {messages.length === 0 ? (
                            <EmptyState onSelectPrompt={setQuery} />
                        ) : (
                            messages.map((message, idx) => (
                                <MessageBubble key={idx} message={message} />
                            ))
                        )}
                    </AnimatePresence>

                    {loading && <TypingIndicator />}
                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input Bar - Fixed at Bottom */}
            <div className="border-t border-border bg-card/50 backdrop-blur-sm">
                <div className="max-w-4xl mx-auto px-6 py-4">
                    <form onSubmit={handleSubmit} className="relative">
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Ask about trends, comparisons, anomalies..."
                            disabled={loading}
                            className="w-full px-5 py-3.5 pr-14 bg-muted border border-border rounded-xl text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent/20 transition-all"
                        />
                        <Button
                            type="submit"
                            size="sm"
                            disabled={loading || !query.trim()}
                            className="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg bg-accent hover:bg-accent/90"
                        >
                            <Send className="w-4 h-4" />
                        </Button>
                    </form>
                    <p className="text-xs text-center text-muted-foreground mt-2">
                        Your data stays private. No training on your data.
                    </p>
                </div>
            </div>
        </div>
    );
}

// Empty State Component
function EmptyState({ onSelectPrompt }: { onSelectPrompt: (prompt: string) => void }) {
    const prompts = [
        "Show me top 10 customers by revenue",
        "What are the main trends this quarter?",
        "Find any unusual patterns in sales data",
        "Compare performance across regions"
    ];

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4"
        >
            <div className="mb-8">
                <h1 className="text-3xl font-semibold mb-3 text-foreground">
                    Ask your data anything
                </h1>
                <p className="text-muted-foreground text-sm max-w-md">
                    Powered by your dataset, not assumptions
                </p>
            </div>

            <div className="grid grid-cols-2 gap-3 w-full max-w-2xl">
                {prompts.map((prompt, i) => (
                    <button
                        key={i}
                        onClick={() => onSelectPrompt(prompt)}
                        className="px-4 py-3 text-left text-sm border border-border rounded-lg hover:bg-muted/50 hover:border-accent/30 transition-all text-foreground"
                    >
                        {prompt}
                    </button>
                ))}
            </div>
        </motion.div>
    );
}

// Message Bubble Component
function MessageBubble({ message }: { message: Message }) {
    const [sqlExpanded, setSqlExpanded] = useState(false);

    if (message.role === 'user') {
        return (
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-end mb-6"
            >
                <div className="max-w-[70%] px-4 py-3 rounded-xl bg-accent/10 text-accent border border-accent/20">
                    <p className="text-sm">{message.content}</p>
                </div>
            </motion.div>
        );
    }

    const content = message.content;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
        >
            <div className="flex gap-3">
                <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center shrink-0">
                    <Sparkles className="w-4 h-4 text-accent" />
                </div>

                <div className="flex-1 space-y-4">
                    {/* a. Direct Answer */}
                    {content.directAnswer && (
                        <div className="prose prose-invert max-w-none">
                            <p className="text-foreground font-semibold text-base leading-relaxed">
                                {content.directAnswer}
                            </p>
                        </div>
                    )}

                    {/* b. Generated SQL (Collapsible) */}
                    {content.sql && (
                        <div className="border border-border rounded-lg overflow-hidden bg-card">
                            <button
                                onClick={() => setSqlExpanded(!sqlExpanded)}
                                className="w-full px-4 py-2.5 flex items-center justify-between text-sm text-muted-foreground hover:bg-muted/50 transition-colors"
                            >
                                <span className="font-medium">Generated SQL</span>
                                {sqlExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                            </button>
                            {sqlExpanded && (
                                <div className="px-4 py-3 border-t border-border">
                                    <pre className="text-xs text-foreground overflow-x-auto">
                                        <code>{content.sql}</code>
                                    </pre>
                                </div>
                            )}
                        </div>
                    )}

                    {/* c. Result Table */}
                    {content.resultData && content.resultData.length > 0 && (
                        <div className="border border-border rounded-lg overflow-hidden">
                            <div className="px-4 py-2 bg-muted/30 border-b border-border">
                                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                                    Results
                                </span>
                            </div>
                            <div className="overflow-x-auto max-h-96">
                                <table className="w-full text-sm">
                                    <thead>
                                        <tr>
                                            {content.columns?.map((col: string) => (
                                                <th key={col} className="text-left">
                                                    {col}
                                                </th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {content.resultData.map((row: any, i: number) => (
                                            <tr key={i}>
                                                {content.columns?.map((col: string) => (
                                                    <td key={col}>{row[col]}</td>
                                                ))}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {/* d. Visualization (if available) */}
                    {content.visualization && (
                        <div className="border border-border rounded-lg p-4 bg-card">
                            <ChartRenderer config={content.visualization} />
                        </div>
                    )}

                    {/* e. Explanation */}
                    {content.explanation && (
                        <div className="prose prose-invert max-w-none">
                            <p className="text-sm text-muted-foreground leading-relaxed">
                                {content.explanation}
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </motion.div>
    );
}

// Typing Indicator
function TypingIndicator() {
    return (
        <div className="flex gap-3 mb-8">
            <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center shrink-0">
                <Sparkles className="w-4 h-4 text-accent" />
            </div>
            <div className="flex items-center gap-1 px-4 py-3">
                {[0, 1, 2].map((i) => (
                    <div
                        key={i}
                        className="w-2 h-2 rounded-full bg-muted-foreground"
                        style={{
                            animation: 'typing-bounce 1.4s ease-in-out infinite',
                            animationDelay: `${i * 0.2}s`
                        }}
                    />
                ))}
            </div>
        </div>
    );
}
