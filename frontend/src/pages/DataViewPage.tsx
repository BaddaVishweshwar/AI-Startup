import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '../lib/api';
import { Button } from '../components/ui/button';
import { Download, RefreshCw, Search } from 'lucide-react';
import { Input } from '../components/ui/input';

export default function DataViewPage() {
    const [searchParams] = useSearchParams();
    const datasetId = searchParams.get('dataset');

    const [dataset, setDataset] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        if (datasetId) {
            loadDataset();
        }
    }, [datasetId]);

    const loadDataset = async () => {
        try {
            setLoading(true);
            // Fetch full data using the new endpoint
            const response = await api.get(`/datasets/${datasetId}/data`);
            setDataset({
                ...response.data.dataset_info,
                sample_data: response.data.data,
                columns: response.data.columns
            });
        } catch (error) {
            console.error('Error loading dataset:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="h-full flex items-center justify-center bg-background">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent mx-auto mb-4"></div>
                    <p className="text-muted-foreground">Loading data...</p>
                </div>
            </div>
        );
    }

    if (!dataset) {
        return (
            <div className="h-full flex items-center justify-center bg-background">
                <div className="text-center">
                    <p className="text-muted-foreground">Dataset not found</p>
                </div>
            </div>
        );
    }

    // Filter data based on search
    const filteredData = dataset.sample_data?.filter((row: any) => {
        if (!searchQuery) return true;
        return Object.values(row).some(val =>
            String(val).toLowerCase().includes(searchQuery.toLowerCase())
        );
    }) || [];

    return (
        <div className="h-full flex flex-col bg-background">
            {/* Header */}
            <div className="border-b border-border px-6 py-4">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h1 className="text-2xl font-semibold text-foreground">{dataset.name}</h1>
                        <p className="text-sm text-muted-foreground mt-1">
                            {dataset.row_count?.toLocaleString() || 0} rows · {dataset.column_count || 0} columns
                        </p>
                    </div>
                    <div className="flex items-center gap-2">
                        <Button variant="outline" size="sm" onClick={loadDataset}>
                            <RefreshCw className="w-4 h-4 mr-2" />
                            Refresh
                        </Button>
                        <Button variant="outline" size="sm">
                            <Download className="w-4 h-4 mr-2" />
                            Export
                        </Button>
                    </div>
                </div>

                {/* Search */}
                <div className="relative max-w-sm">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                        type="text"
                        placeholder="Search data..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10 h-9 bg-muted border-border"
                    />
                </div>
            </div>

            {/* Data Table */}
            <div className="flex-1 overflow-auto">
                {filteredData.length === 0 ? (
                    <div className="flex items-center justify-center h-full">
                        <p className="text-muted-foreground">
                            {searchQuery ? 'No matching data found' : 'No data available'}
                        </p>
                    </div>
                ) : (
                    <table className="w-full">
                        <thead className="sticky top-0 bg-muted/50 backdrop-blur-sm border-b border-border z-10">
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider w-12">
                                    #
                                </th>
                                {Object.keys(filteredData[0]).map((column) => (
                                    <th
                                        key={column}
                                        className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider"
                                    >
                                        {column}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {filteredData.map((row: any, index: number) => (
                                <tr key={index} className="hover:bg-muted/30 transition-colors">
                                    <td className="px-4 py-3 text-sm text-muted-foreground font-mono">
                                        {index + 1}
                                    </td>
                                    {Object.entries(row).map(([key, value]: [string, any]) => (
                                        <td key={key} className="px-4 py-3 text-sm text-foreground">
                                            {typeof value === 'number'
                                                ? value.toLocaleString()
                                                : value === null || value === undefined
                                                    ? <span className="text-muted-foreground italic">null</span>
                                                    : String(value)}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {/* Footer */}
            <div className="border-t border-border px-6 py-3 bg-muted/30">
                <p className="text-xs text-muted-foreground">
                    Showing {filteredData.length} of {dataset.row_count?.toLocaleString() || 0} rows
                    {searchQuery && ` (filtered from ${dataset.sample_data?.length || 0})`}
                </p>
            </div>
        </div>
    );
}
