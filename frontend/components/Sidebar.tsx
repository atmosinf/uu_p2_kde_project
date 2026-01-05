import { FilterOptions } from '@/types';
import { Search, Filter, X } from 'lucide-react';
import { ThemeToggle } from '@/components/ThemeToggle';

interface SidebarProps {
    options: FilterOptions;
    filters: any;
    setFilters: (filters: any) => void;
    onSearch: () => void;
    loading: boolean;
}

export const Sidebar = ({ options, filters, setFilters, onSearch, loading }: SidebarProps) => {
    const handleChange = (key: string, value: any) => {
        setFilters((prev: any) => ({ ...prev, [key]: value }));
    };

    return (
        <aside className="w-80 h-screen overflow-y-auto bg-zinc-50 dark:bg-zinc-950 border-r border-zinc-200 dark:border-zinc-800 p-6 flex flex-col gap-8 fixed left-0 top-0 z-10 font-sans transition-colors duration-300">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 text-yellow-500">
                    <div className="p-2 bg-yellow-500/10 rounded-lg">
                        <Filter className="w-6 h-6" />
                    </div>
                    <h1 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-white">Movie Finder</h1>
                </div>
                <ThemeToggle />
            </div>

            <div className="space-y-6 flex-1">
                {/* Search Input */}
                <div className="space-y-2">
                    <label className="text-xs uppercase text-zinc-500 font-semibold tracking-wider">Title</label>
                    <div className="relative group">
                        <Search className="absolute left-3 top-3 w-4 h-4 text-zinc-500 group-focus-within:text-yellow-500 transition-colors" />
                        <input
                            type="text"
                            value={filters.title || ''}
                            onChange={(e) => handleChange('title', e.target.value)}
                            placeholder="The Lord of the Rings..."
                            className="w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg py-2.5 pl-10 pr-4 text-sm text-zinc-900 dark:text-white focus:outline-none focus:border-yellow-500 transition-colors placeholder:text-zinc-400 dark:placeholder:text-zinc-600"
                        />
                    </div>
                </div>

                {/* Dropdowns */}
                {['genre', 'director', 'actor'].map((field) => (
                    <div key={field} className="space-y-2">
                        <label className="text-xs uppercase text-zinc-500 font-semibold tracking-wider capitalize">{field}</label>
                        <select
                            className="w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg py-2.5 px-3 text-sm text-zinc-900 dark:text-white focus:outline-none focus:border-yellow-500 transition-colors appearance-none cursor-pointer"
                            value={filters[field] || ''}
                            onChange={(e) => handleChange(field, e.target.value)}
                        >
                            <option value="">Select {field}...</option>
                            {/* map options based on field name */}
                            {/* 
                   Note: options.genres matches 'genre', but 'director' -> options.directors, 'actor' -> options.actors.
                   Simple mapping logic:
                */}
                            {(options[field + 's' as keyof FilterOptions] || []).map((opt) => (
                                <option key={opt} value={opt}>{opt.replace(/_/g, ' ')}</option>
                            ))}
                        </select>
                    </div>
                ))}

                {/* Year Range (Simple Inputs for now) */}
                <div className="space-y-2">
                    <label className="text-xs uppercase text-zinc-500 font-semibold tracking-wider">Year Range</label>
                    <div className="flex gap-2">
                        <input
                            type="number"
                            placeholder="1900"
                            className="w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg py-2 px-3 text-sm text-zinc-900 dark:text-white focus:border-yellow-500 outline-none placeholder:text-zinc-400 dark:placeholder:text-zinc-600"
                            onChange={(e) => handleChange('year_start', e.target.value)}
                        />
                        <span className="text-zinc-400 dark:text-zinc-600 self-center">-</span>
                        <input
                            type="number"
                            placeholder="2025"
                            className="w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg py-2 px-3 text-sm text-zinc-900 dark:text-white focus:border-yellow-500 outline-none placeholder:text-zinc-400 dark:placeholder:text-zinc-600"
                            onChange={(e) => handleChange('year_end', e.target.value)}
                        />
                    </div>
                </div>

            </div>

            <button
                onClick={onSearch}
                disabled={loading}
                className="w-full bg-yellow-500 hover:bg-yellow-400 text-black font-bold py-3 rounded-lg shadow-lg shadow-yellow-500/20 active:scale-95 transition-all disabled:opacity-50 disabled:pointer-events-none"
            >
                {loading ? 'Searching...' : 'SEARCH'}
            </button>

            {/* Credit */}
            <div className="text-center">
                <p className="text-xs text-zinc-700">Semantic Web Project</p>
            </div>
        </aside>
    );
};
