import { motion } from 'framer-motion';
import { Movie } from '@/types';
import { User, Film, Clock, Star } from 'lucide-react';

interface MovieCardProps {
    movie: Movie;
    index: number;
}

export const MovieCard = ({ movie, index }: MovieCardProps) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden hover:border-yellow-500/50 transition-colors shadow-lg group"
        >
            <div className="p-4 space-y-3">
                {/* Header */}
                <div className="flex justify-between items-start">
                    <h3 className="text-lg font-bold text-white group-hover:text-yellow-500 transition-colors line-clamp-2">
                        {movie.title}
                    </h3>
                    <span className="bg-yellow-500/10 text-yellow-500 text-xs px-2 py-1 rounded font-mono">
                        {movie.year || 'N/A'}
                    </span>
                </div>

                {/* Info Grid */}
                <div className="grid grid-cols-2 gap-2 text-sm text-gray-400">
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
                        <span className="text-gray-300 max-h-16 overflow-y-auto block">{movie.directors.join(', ')}</span>
                    </div>
                )}

                {movie.actors.length > 0 && (
                    <div className="text-sm">
                        <span className="text-zinc-500 text-xs uppercase tracking-wider block mb-0.5">Starring</span>
                        <p className="text-gray-300 max-h-24 overflow-y-auto leading-relaxed">
                            {movie.actors.join(', ')}
                        </p>
                    </div>
                )}

                {/* Similarity Score Decoration */}
                {movie.similarity !== undefined && movie.similarity > 0 && (
                    <div className="pt-2 border-t border-zinc-800 mt-2 flex items-center gap-2 text-yellow-500">
                        <Star className="w-4 h-4 fill-yellow-500" />
                        <span className="text-sm font-bold">Similarity: {movie.similarity}</span>
                    </div>
                )}
            </div>
        </motion.div >
    );
};
