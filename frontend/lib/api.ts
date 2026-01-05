import axios from 'axios';
import { FilterOptions, Movie } from '@/types';

const API_URL = '/api';

export const api = axios.create({
    baseURL: API_URL,
});

export const getOptions = async (): Promise<FilterOptions> => {
    const response = await api.get('/options');
    return response.data;
};

export const searchMovies = async (params: any): Promise<Movie[]> => {
    console.log("DEBUG: Frontend API calling /api/search with params:", params);
    try {
        const response = await api.get('/search', { params });
        console.log("DEBUG: Search response:", response.data);
        return response.data;
    } catch (error) {
        console.error("DEBUG: Search error:", error);
        return [];
    }
};
