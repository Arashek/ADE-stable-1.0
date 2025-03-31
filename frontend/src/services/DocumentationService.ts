import { Observable, Subject } from 'rxjs';
import { MonitoringService } from './monitoring.service';
import { Documentation, DocType, DocSection } from '../types/documentation';

export class DocumentationService {
    private static instance: DocumentationService;
    private readonly API_BASE = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
    private readonly monitoring: MonitoringService;
    private docsSubject = new Subject<Documentation[]>();

    private constructor() {
        this.monitoring = MonitoringService.getInstance();
    }

    static getInstance(): DocumentationService {
        if (!DocumentationService.instance) {
            DocumentationService.instance = new DocumentationService();
        }
        return DocumentationService.instance;
    }

    async generateDocumentation(
        projectId: string,
        docType: DocType,
        options: {
            sections?: string[];
            format?: string;
            includeExamples?: boolean;
            depth?: number;
        } = {}
    ): Promise<Documentation> {
        try {
            const response = await fetch(`${this.API_BASE}/api/docs/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    project_id: projectId,
                    doc_type: docType,
                    options,
                }),
            });

            const doc = await response.json();
            this.docsSubject.next([doc]);
            return doc;
        } catch (error) {
            this.monitoring.recordError('generate_docs_failed', error);
            throw error;
        }
    }

    async updateDocumentation(
        docId: string,
        updates: Partial<Documentation>
    ): Promise<Documentation> {
        try {
            const response = await fetch(`${this.API_BASE}/api/docs/${docId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updates),
            });

            return await response.json();
        } catch (error) {
            this.monitoring.recordError('update_docs_failed', error);
            throw error;
        }
    }

    async generateAPIDocumentation(
        projectId: string,
        options: {
            format?: string;
            includeExamples?: boolean;
            includeSchemas?: boolean;
        } = {}
    ): Promise<Documentation> {
        return this.generateDocumentation(projectId, DocType.API, options);
    }

    async generateUserGuide(
        projectId: string,
        options: {
            sections?: string[];
            includeExamples?: boolean;
        } = {}
    ): Promise<Documentation> {
        return this.generateDocumentation(projectId, DocType.USER_GUIDE, options);
    }

    async generateTechnicalDocs(
        projectId: string,
        options: {
            depth?: number;
            includeArchitecture?: boolean;
            includeDeployment?: boolean;
        } = {}
    ): Promise<Documentation> {
        return this.generateDocumentation(projectId, DocType.TECHNICAL, options);
    }

    async addDocSection(
        docId: string,
        section: DocSection
    ): Promise<Documentation> {
        try {
            const response = await fetch(
                `${this.API_BASE}/api/docs/${docId}/sections`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(section),
                }
            );

            return await response.json();
        } catch (error) {
            this.monitoring.recordError('add_section_failed', error);
            throw error;
        }
    }

    async updateDocSection(
        docId: string,
        sectionId: string,
        updates: Partial<DocSection>
    ): Promise<Documentation> {
        try {
            const response = await fetch(
                `${this.API_BASE}/api/docs/${docId}/sections/${sectionId}`,
                {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(updates),
                }
            );

            return await response.json();
        } catch (error) {
            this.monitoring.recordError('update_section_failed', error);
            throw error;
        }
    }

    async generateExample(
        docId: string,
        sectionId: string,
        context: any
    ): Promise<string> {
        try {
            const response = await fetch(
                `${this.API_BASE}/api/docs/${docId}/examples`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        section_id: sectionId,
                        context,
                    }),
                }
            );

            const data = await response.json();
            return data.example;
        } catch (error) {
            this.monitoring.recordError('generate_example_failed', error);
            throw error;
        }
    }

    watchDocumentation(): Observable<Documentation[]> {
        return this.docsSubject.asObservable();
    }
}
