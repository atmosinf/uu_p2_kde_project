import axios from 'axios';
import { FilterOptions, Movie } from '@/types';

const API_URL = 'http://127.0.0.1:8000';

export const api = axios.create({
    baseURL: API_URL,
});

export const getOptions = async (): Promise<FilterOptions> => {
    const response = await api.get('/options');
    return response.data;
};

export const searchMovies = async (params: any): Promise<Movie[]> => {
    const response = await api.get('/search', { params });
    return response.data;
};
