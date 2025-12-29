export interface Movie {
    id: string;
    title: string;
    year?: string;
    runtime?: string;
    genres: string[];
    directors: string[];
    actors: string[];
    similarity?: number;
}

export interface FilterOptions {
    genres: string[];
    actors: string[];
    directors: string[];
}
