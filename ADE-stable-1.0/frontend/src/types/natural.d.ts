declare module 'natural' {
    export class WordTokenizer {
        tokenize(text: string): string[] | null;
    }

    export class TfIdf {
        addDocument(document: string[]): void;
        listTerms(documentIndex: number): Array<{
            term: string;
            tfidf: number;
        }>;
    }

    export class EntityExtractor {
        extract(text: string): string[];
    }

    export const stopwords: string[];
} 