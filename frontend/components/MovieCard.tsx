import { motion } from 'framer-motion';
import { Movie } from '@/types';
import { User, Film, Clock, Star, Sparkles } from 'lucide-react';
import { useState } from 'react';
import { getSimilarMovies } from '@/lib/api';

interface MovieCardProps {
    movie: Movie;
    index: number;
}

export const MovieCard = ({ movie, index }: MovieCardProps) => {
    const [similarMovies, setSimilarMovies] = useState<Movie[]>([]);
    const [loadingSimilar, setLoadingSimilar] = useState(false);
    const [showSimilar, setShowSimilar] = useState(false);

    const handleFindSimilar = async () => {
        if (showSimilar) {
            setShowSimilar(false);
            return;
        }

        if (similarMovies.length > 0) {
            setShowSimilar(true);
            return;
        }

        setLoadingSimilar(true);
        const results = await getSimilarMovies(movie.id);
        setSimilarMovies(results);
        setLoadingSimilar(false);
        setShowSimilar(true);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg overflow-hidden hover:border-yellow-500/50 dark:hover:border-yellow-500/50 transition-colors shadow-lg group"
        >
            <div className="p-4 space-y-3">
                {/* Header */}
                <div className="flex justify-between items-start">
                    <h3 className="text-lg font-bold text-zinc-900 dark:text-white group-hover:text-yellow-500 transition-colors line-clamp-2">
                        {movie.title}
                    </h3>
                    <span className="bg-yellow-500/10 text-yellow-600 dark:text-yellow-500 text-xs px-2 py-1 rounded font-mono">
                        {movie.year || 'N/A'}
                    </span>
                </div>

                {/* Info Grid */}
                <div className="grid grid-cols-2 gap-2 text-sm text-zinc-500 dark:text-gray-400">
                    {movie.runtime && (
                        <div className="flex items-center gap-1.5">
                            <Clock className="w-3 h-3" />
                            <span>{movie.runtime} min</span>
                        </div>
                    )}
                    <div className="flex items-start gap-1.5 col-span-2">
                        <Film className="w-3 h-3 flex-shrink-0 mt-1" />
                        <span className="max-h-16 overflow-y-auto block">{movie.genres.join(', ') || 'Unknown Genre'}</span>
                    </div>
                </div>

                {/* People */}
                {movie.directors.length > 0 && (
                    <div className="text-sm">
                        <span className="text-zinc-500 text-xs uppercase tracking-wider block mb-0.5">Director</span>
                        <span className="text-zinc-700 dark:text-gray-300 max-h-16 overflow-y-auto block">{movie.directors.join(', ')}</span>
                    </div>
                )}

                {movie.actors.length > 0 && (
                    <div className="text-sm">
                        <span className="text-zinc-500 text-xs uppercase tracking-wider block mb-0.5">Starring</span>
                        <p className="text-zinc-700 dark:text-gray-300 max-h-24 overflow-y-auto leading-relaxed">
                            {movie.actors.join(', ')}
                        </p>
                    </div>
                )}

                {/* Similarity Score Decoration */}
                {movie.similarity !== undefined && movie.similarity > 0 && (
                    <div className="pt-2 border-t border-zinc-200 dark:border-zinc-800 mt-2 flex items-center gap-2 text-yellow-500">
                        <Star className="w-4 h-4 fill-yellow-500" />
                        <span className="text-sm font-bold">Similarity: {movie.similarity}</span>
                    </div>
                )}

                {/* Similarity Button */}
                <button
                    onClick={handleFindSimilar}
                    disabled={loadingSimilar}
                    className="w-full mt-4 flex items-center justify-center gap-2 py-2 px-3 bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 rounded-md text-sm font-medium transition-colors text-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-700"
                >
                    <Sparkles className={`w-4 h-4 ${loadingSimilar ? 'animate-spin' : 'text-purple-500'}`} />
                    {loadingSimilar ? 'Finding...' : (showSimilar ? 'Hide Similar' : 'Find Similar (AI)')}
                </button>

                {/* Similar Movies List */}
                {showSimilar && (
                    <div className="mt-3 space-y-2 border-t border-zinc-200 dark:border-zinc-800 pt-3 animate-in fade-in slide-in-from-top-2">
                        <h4 className="text-xs font-bold uppercase text-zinc-400">Recommended for you</h4>
                        {similarMovies.length === 0 ? (
                            <p className="text-xs text-zinc-500 italic">No recommendations found.</p>
                        ) : (
                            similarMovies.map((sim, i) => (
                                <div key={i} className="flex justify-between items-center text-sm p-2 rounded bg-zinc-50 dark:bg-zinc-800/50 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors">
                                    <span className="font-medium text-zinc-800 dark:text-zinc-200">{sim.title}</span>
                                    <span className="text-xs text-zinc-500">{sim.year}</span>
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>
        </motion.div >
    );
};
