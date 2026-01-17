import { motion } from 'framer-motion';
import { Movie } from '@/types';
import { User, Film, Clock, Star, Sparkles } from 'lucide-react';
import { useState } from 'react';
import { getSimilarMovies } from '@/lib/api';

interface MovieCardProps {
    movie: Movie;
    index: number;
    onQuickSearch: (key: string, value: string) => void;
}

export const MovieCard = ({ movie, index, onQuickSearch }: MovieCardProps) => {
    const [similarMovies, setSimilarMovies] = useState<Movie[]>([]);
    const [loadingSimilar, setLoadingSimilar] = useState(false);
    const [showSimilar, setShowSimilar] = useState(false);
    const [expandedSimilarId, setExpandedSimilarId] = useState<string | null>(null);

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
                <div className="text-sm">
                    <span className="text-zinc-500 text-xs uppercase tracking-wider block mb-0.5">Director</span>
                    <div className="text-zinc-700 dark:text-gray-300 max-h-16 overflow-y-auto block">
                        {movie.directors.map((d, i) => (
                            <span key={i}>
                                <span
                                    onClick={(e) => { e.stopPropagation(); onQuickSearch('director', d); }}
                                    className="hover:text-yellow-500 hover:underline cursor-pointer"
                                >
                                    {d.replace(/_/g, ' ')}
                                </span>
                                {i < movie.directors.length - 1 && ', '}
                            </span>
                        ))}
                    </div>
                </div>

                {movie.actors.length > 0 && (
                    <div className="text-sm">
                        <span className="text-zinc-500 text-xs uppercase tracking-wider block mb-0.5">Starring</span>
                        <p className="text-zinc-700 dark:text-gray-300 max-h-24 overflow-y-auto leading-relaxed">
                            {movie.actors.map((a, i) => (
                                <span key={i}>
                                    <span
                                        onClick={(e) => { e.stopPropagation(); onQuickSearch('actor', a); }}
                                        className="hover:text-yellow-500 hover:underline cursor-pointer"
                                    >
                                        {a.replace(/_/g, ' ')}
                                    </span>
                                    {i < movie.actors.length - 1 && ', '}
                                </span>
                            ))}
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
                    {loadingSimilar ? 'Finding...' : (showSimilar ? 'Hide Similar' : 'Find Similar')}
                </button>

                {/* Similar Movies List */}
                {showSimilar && (
                    <div className="mt-3 space-y-2 border-t border-zinc-200 dark:border-zinc-800 pt-3 animate-in fade-in slide-in-from-top-2">
                        <h4 className="text-xs font-bold uppercase text-zinc-400">Recommended for you</h4>
                        {similarMovies.length === 0 ? (
                            <p className="text-xs text-zinc-500 italic">No recommendations found.</p>
                        ) : (
                            similarMovies.map((sim, i) => (
                                <div
                                    key={i}
                                    onClick={() => setExpandedSimilarId(expandedSimilarId === sim.id ? null : sim.id)}
                                    className="flex flex-col text-sm p-2 rounded bg-zinc-50 dark:bg-zinc-800/50 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer border border-transparent hover:border-zinc-200 dark:hover:border-zinc-700"
                                >
                                    <div className="flex justify-between items-center w-full">
                                        <span className="font-medium text-zinc-800 dark:text-zinc-200 truncate pr-2">{sim.title}</span>
                                        <span className="text-xs text-zinc-500 whitespace-nowrap">{sim.year}</span>
                                    </div>

                                    {expandedSimilarId === sim.id && (
                                        <div className="mt-2 pt-2 border-t border-zinc-200 dark:border-zinc-700/50 space-y-2 text-xs animate-in fade-in zoom-in-95 duration-200 cursor-default max-h-60 overflow-y-auto pr-1" onClick={(e) => e.stopPropagation()}>
                                            <div className="flex flex-wrap gap-x-3 gap-y-1 text-zinc-500 dark:text-zinc-400">
                                                {sim.runtime && (
                                                    <span className="flex items-center gap-1">
                                                        <Clock className="w-3 h-3" /> {sim.runtime}m
                                                    </span>
                                                )}
                                                <span className="flex items-center gap-1">
                                                    <Film className="w-3 h-3" /> {sim.genres.slice(0, 3).join(', ')}
                                                </span>
                                            </div>

                                            {sim.directors.length > 0 && (
                                                <div>
                                                    <span className="text-zinc-400 uppercase text-[10px]">Director:</span>
                                                    <span className="text-zinc-700 dark:text-zinc-300 ml-1">
                                                        {sim.directors.map((d, i) => (
                                                            <span key={i}>
                                                                <span
                                                                    onClick={(e) => { e.stopPropagation(); onQuickSearch('director', d); }}
                                                                    className="hover:text-yellow-500 hover:underline cursor-pointer"
                                                                >
                                                                    {d.replace(/_/g, ' ')}
                                                                </span>
                                                                {i < sim.directors.length - 1 && ', '}
                                                            </span>
                                                        ))}
                                                    </span>
                                                </div>
                                            )}

                                            {sim.actors.length > 0 && (
                                                <div>
                                                    <span className="text-zinc-400 uppercase text-[10px]">Starring:</span>
                                                    <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
                                                        {sim.actors.map((a, i) => (
                                                            <span key={i}>
                                                                <span
                                                                    onClick={(e) => { e.stopPropagation(); onQuickSearch('actor', a); }}
                                                                    className="hover:text-yellow-500 hover:underline cursor-pointer"
                                                                >
                                                                    {a.replace(/_/g, ' ')}
                                                                </span>
                                                                {i < sim.actors.length - 1 && ', '}
                                                            </span>
                                                        ))}
                                                    </p>
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>
        </motion.div >
    );
};
