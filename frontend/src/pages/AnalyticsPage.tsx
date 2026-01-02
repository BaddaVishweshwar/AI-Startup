import { useEffect, useState, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { Send, Sparkles, Plus, Database, Menu } from 'lucide-react';
import { datasetsAPI } from '../lib/api';
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
    const location = useLocation();
    const [datasets, setDatasets] = useState<any[]>([]);
    const [selectedDataset, setSelectedDataset] = useState<number | null>(location.state?.datasetId || null);
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);
    const [currentConversation, setCurrentConversation] = useState<any>(null);
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        loadDatasets();
    }, []);

    useEffect(() => {
        if (selectedDataset && !currentConversation) {
            createConversation();
        }
    }, [selectedDataset]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const loadDatasets = async () => {
        try {
            const response = await datasetsAPI.list();
            setDatasets(response.data);
            if (response.data.length > 0 && !selectedDataset) {
                setSelectedDataset(response.data[0].id);
            }
        } catch (error) {
            console.error('Error loading datasets:', error);
        }
    };

    const createConversation = async () => {
        if (!selectedDataset) return;
        try {
            const response = await conversationsAPI.create(selectedDataset);
            setCurrentConversation(response.data);
        } catch (error) {
            console.error('Error creating conversation:', error);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim() || !currentConversation || loading) return;

        const userMessage: Message = { role: 'user', content: query };
        setMessages(prev => [...prev, userMessage]);
        const userQuery = query;
        setQuery('');
        setLoading(true);

        try {
            const response = await conversationsAPI.sendMessage(currentConversation.id, userQuery);
            const messageData = response.data;

            const assistantMessage: Message = {
                role: 'assistant',
                content: {
                    text: messageData.content,
                    generated_sql: messageData.query_data?.generated_sql,
                    result_data: messageData.query_data?.result_data,
                    visualization: messageData.query_data?.visualization,
                    columns: messageData.query_data?.columns
                }
            };
            setMessages(prev => [...prev, assistantMessage]);
        } catch (error: any) {
            console.error('Error:', error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: { text: error.response?.data?.detail || 'Error processing query' }
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleNewChat = () => {
        setMessages([]);
        setQuery('');
        createConversation();
    };

    return (
        <div className="flex h-screen bg-background">
            {/* Minimal Sidebar - ChatGPT Style */}
            <div className={`${sidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 border-r border-border bg-card overflow-hidden`}>
                <div className="p-4 space-y-4">
                    <Button onClick={handleNewChat} className="w-full" variant="outline">
                        <Plus className="w-4 h-4 mr-2" />
                        New Chat
                    </Button>

                    <div className="space-y-2">
                        <label className="text-xs text-muted-foreground uppercase tracking-wider">Dataset</label>
                        <select
                            value={selectedDataset || ''}
                            onChange={(e) => setSelectedDataset(Number(e.target.value))}
                            className="w-full p-2 bg-background border border-border rounded-lg text-sm text-foreground"
                        >
                            {datasets.map((dataset) => (
                                <option key={dataset.id} value={dataset.id}>
                                    {dataset.name}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>

            {/* Main Chat Area - ChatGPT Style */}
            <div className="flex-1 flex flex-col">
                {/* Top Bar */}
                <div className="h-14 border-b border-border flex items-center px-4 gap-4">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSidebarOpen(!sidebarOpen)}
                    >
                        <Menu className="w-5 h-5" />
                    </Button>
                    <h1 className="text-sm font-medium text-foreground">AI Data Analyst</h1>
                </div>

                {/* Messages - Centered like ChatGPT */}
                <div className="flex-1 overflow-y-auto">
                    <div className="max-w-3xl mx-auto px-4 py-8">
                        <AnimatePresence>
                            {messages.length === 0 ? (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="flex flex-col items-center justify-center h-[60vh] text-center"
                                >
                                    <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center mb-4">
                                        <Database className="w-6 h-6 text-muted-foreground" />
                                    </div>
                                    <h2 className="text-2xl font-semibold mb-2 text-foreground">How can I help you analyze data today?</h2>
                                    <p className="text-muted-foreground mb-8">Ask me anything about your dataset</p>

                                    <div className="grid grid-cols-2 gap-3 w-full max-w-2xl">
                                        {[
                                            "Summarize this dataset",
                                            "Show me key trends",
                                            "Find any anomalies",
                                            "Create a visualization"
                                        ].map((suggestion, i) => (
                                            <button
                                                key={i}
                                                onClick={() => setQuery(suggestion)}
                                                className="p-3 text-left border border-border rounded-lg hover:bg-muted transition-colors text-sm text-foreground"
                                            >
                                                {suggestion}
                                            </button>
                                        ))}
                                    </div>
                                </motion.div>
                            ) : (
                                messages.map((message, idx) => (
                                    <motion.div
                                        key={idx}
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="mb-8"
                                    >
                                        {message.role === 'user' ? (
                                            <div className="flex gap-4">
                                                <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center shrink-0">
                                                    <span className="text-xs font-medium">You</span>
                                                </div>
                                                <div className="flex-1 pt-1">
                                                    <p className="text-foreground">{message.content}</p>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="flex gap-4">
                                                <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0">
                                                    <Sparkles className="w-4 h-4 text-white" />
                                                </div>
                                                <div className="flex-1 space-y-4">
                                                    {typeof message.content === 'object' ? (
                                                        <>
                                                            {message.content.text && (
                                                                <div className="prose prose-invert max-w-none text-foreground">
                                                                    <ReactMarkdown>{message.content.text}</ReactMarkdown>
                                                                </div>
                                                            )}

                                                            {message.content.visualization && message.content.result_data && (
                                                                <div className="border border-border rounded-lg p-4 bg-card">
                                                                    <ChartRenderer config={{
                                                                        type: message.content.visualization.type,
                                                                        xAxis: message.content.visualization.x_axis,
                                                                        yAxis: message.content.visualization.y_axis,
                                                                        data: message.content.result_data,
                                                                        columns: message.content.columns
                                                                    }} />
                                                                </div>
                                                            )}

                                                            {message.content.generated_sql && (
                                                                <details className="text-sm">
                                                                    <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
                                                                        View SQL
                                                                    </summary>
                                                                    <pre className="mt-2 p-3 bg-muted rounded-lg overflow-x-auto text-xs">
                                                                        <code>{message.content.generated_sql}</code>
                                                                    </pre>
                                                                </details>
                                                            )}
                                                        </>
                                                    ) : (
                                                        <p className="text-foreground">{message.content}</p>
                                                    )}
                                                </div>
                                            </div>
                                        )}
                                    </motion.div>
                                ))
                            )}
                        </AnimatePresence>
                        {loading && (
                            <div className="flex gap-4 mb-8">
                                <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0">
                                    <Sparkles className="w-4 h-4 text-white" />
                                </div>
                                <div className="flex-1 pt-1">
                                    <div className="flex gap-1">
                                        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                </div>

                {/* Input - Fixed at Bottom like ChatGPT */}
                <div className="border-t border-border bg-background">
                    <div className="max-w-3xl mx-auto p-4">
                        <form onSubmit={handleSubmit} className="relative">
                            <input
                                type="text"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="Message AI Data Analyst..."
                                disabled={loading || !selectedDataset}
                                className="w-full p-4 pr-12 bg-muted border border-border rounded-2xl text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20"
                            />
                            <Button
                                type="submit"
                                size="sm"
                                disabled={loading || !query.trim() || !selectedDataset}
                                className="absolute right-2 top-1/2 -translate-y-1/2 rounded-xl"
                            >
                                <Send className="w-4 h-4" />
                            </Button>
                        </form>
                        <p className="text-xs text-center text-muted-foreground mt-2">
                            AI can make mistakes. Check important info.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
