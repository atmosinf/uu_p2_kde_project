"use client";

import { useEffect, useState } from 'react';
import { getOptions, searchMovies } from '@/lib/api';
import { FilterOptions, Movie } from '@/types';
import { Sidebar } from '@/components/Sidebar';
import { MovieCard } from '@/components/MovieCard';
import { Loader2 } from 'lucide-react';

export default function Home() {
  const [options, setOptions] = useState<FilterOptions>({ genres: [], actors: [], directors: [] });
  const [filters, setFilters] = useState<any>({});
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(false);
  const [initialLoad, setInitialLoad] = useState(true);

  // Fetch options on mount
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const opts = await getOptions();
        setOptions(opts);
      } catch (e) {
        console.error("Failed to fetch options", e);
      }
    };
    fetchOptions();
  }, []);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const results = await searchMovies(filters);
      setMovies(results);
    } catch (e) {
      console.error("Search failed", e);
    } finally {
      setLoading(false);
      setInitialLoad(false);
    }
  };

  return (
    <main className="min-h-screen pl-80 bg-zinc-50 dark:bg-black text-zinc-900 dark:text-white selection:bg-yellow-500 selection:text-black transition-colors duration-300">
      <Sidebar
        options={options}
        filters={filters}
        setFilters={setFilters}
        onSearch={handleSearch}
        loading={loading}
      />

      <div className="p-8 max-w-7xl mx-auto">
        {/* Top Bar (optional stats or sorting) */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Results</h2>
            <p className="text-zinc-500 text-sm">
              {initialLoad ? 'Ready to search' : `Found ${movies.length} movies`}
            </p>
          </div>
        </div>

        {/* Content Area */}
        {loading ? (
          <div className="h-96 flex flex-col items-center justify-center text-zinc-500">
            <Loader2 className="w-10 h-10 animate-spin mb-4 text-yellow-500" />
            <p>Querying Semantic Graph...</p>
          </div>
        ) : movies.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {movies.map((movie, idx) => (
              <MovieCard key={movie.id} movie={movie} index={idx} />
            ))}
          </div>
        ) : !initialLoad ? (
          <div className="h-64 flex flex-col items-center justify-center text-zinc-500 border border-zinc-200 dark:border-zinc-800 border-dashed rounded-lg">
            <p>No movies found matching criteria.</p>
          </div>
        ) : null}

        {/* Initial State */}
        {initialLoad && !loading && (
          <div className="text-center pt-20 opacity-50">
            <div className="inline-block p-4 border border-zinc-200 dark:border-zinc-800 rounded-full mb-4">
              <span className="text-4xl">🎬</span>
            </div>
            <h3 className="text-xl font-medium text-zinc-500 dark:text-zinc-400">Search for movies</h3>
            <p className="text-zinc-500 dark:text-zinc-600 mt-2">Use the sidebar filters to explore the semantic database.</p>
          </div>
        )}
      </div>
    </main>
  );
}
