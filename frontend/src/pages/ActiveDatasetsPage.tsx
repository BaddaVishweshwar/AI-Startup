import { useEffect, useState } from 'react';
import { datasetsAPI } from '../lib/api';
import { Database, ArrowLeft, Table2, Calendar, Trash2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { useNavigate } from 'react-router-dom';

export default function ActiveDatasetsPage() {
    const [datasets, setDatasets] = useState<any[]>([]);
    const [activeDatasetIds, setActiveDatasetIds] = useState<number[]>([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        loadActiveDatasets();
    }, []);

    const loadActiveDatasets = async () => {
        try {
            setLoading(true);
            // Get active dataset IDs from localStorage
            const saved = localStorage.getItem('activeDatasets');
            const activeIds: number[] = saved ? JSON.parse(saved) : [];
            setActiveDatasetIds(activeIds);

            // Fetch all datasets
            const response = await datasetsAPI.list();
            // Filter to show only active ones
            const activeDatasets = response.data.filter((d: any) => activeIds.includes(d.id));
            setDatasets(activeDatasets);
        } catch (error) {
            console.error('Error loading datasets:', error);
        } finally {
            setLoading(false);
        }
    };

    const removeFromActive = (datasetId: number) => {
        const updated = activeDatasetIds.filter(id => id !== datasetId);
        setActiveDatasetIds(updated);
        localStorage.setItem('activeDatasets', JSON.stringify(updated));
        setDatasets(prev => prev.filter(d => d.id !== datasetId));

        // Reload parent component
        window.dispatchEvent(new Event('storage'));
    };

    if (loading) {
        return (
            <div className="h-full flex items-center justify-center bg-background">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
            </div>
        );
    }

    return (
        <div className="h-full overflow-y-auto bg-background">
            <div className="max-w-7xl mx-auto px-6 py-12">
                {/* Header */}
                <div className="flex items-center gap-4 mb-8">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => navigate(-1)}
                        className="gap-2"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Back
                    </Button>
                    <div>
                        <h1 className="text-3xl font-semibold text-foreground">
                            Active Datasets
                        </h1>
                        <p className="text-muted-foreground text-sm mt-1">
                            Datasets currently selected for analysis
                        </p>
                    </div>
                </div>

                {/* Datasets List */}
                {datasets.length === 0 ? (
                    <div className="text-center py-20">
                        <Database className="w-16 h-16 text-muted-foreground/30 mx-auto mb-4" />
                        <p className="text-muted-foreground mb-6">
                            No datasets selected for analysis
                        </p>
                        <Button
                            className="bg-accent hover:bg-accent/90"
                            onClick={() => navigate('/datasets')}
                        >
                            Browse Datasets
                        </Button>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {datasets.map((dataset) => (
                            <div
                                key={dataset.id}
                                className="group flex items-center justify-between border border-border rounded-xl p-6 hover:bg-muted/30 transition-all bg-card"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center shrink-0">
                                        <Database className="w-6 h-6 text-accent" />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-semibold text-foreground mb-1">
                                            {dataset.name}
                                        </h3>
                                        <div className="flex items-center gap-3 text-xs text-muted-foreground">
                                            <span className="flex items-center gap-1">
                                                <Table2 className="w-3 h-3" />
                                                {dataset.row_count?.toLocaleString() || 0} rows
                                            </span>
                                            <span>•</span>
                                            <span className="flex items-center gap-1">
                                                <Calendar className="w-3 h-3" />
                                                {new Date(dataset.created_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-2">
                                    <Button
                                        variant="default"
                                        size="sm"
                                        className="bg-accent hover:bg-accent/90"
                                        onClick={() => navigate(`/data-view?dataset=${dataset.id}`)}
                                    >
                                        View Data
                                    </Button>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => navigate(`/analytics?dataset=${dataset.id}`)}
                                    >
                                        Analyze
                                    </Button>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        className="text-destructive hover:bg-destructive hover:text-white"
                                        onClick={() => removeFromActive(dataset.id)}
                                        title="Remove from active session"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </Button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
