/**
 * Simplified AIReviewPanel store for the ADE platform
 * This file has been streamlined to focus on the core multi-agent architecture
 * for local testing before cloud deployment on cloudev.ai
 */

import { makeAutoObservable } from 'mobx';
import { CodeIssue, FileAnalysis } from '../../services/codeAnalysis/CodeQualityService';

/**
 * Store for managing AI code review panel state
 */
export class AIReviewPanelStore {
  loading: boolean = false;
  currentFile: string | null = null;
  analysis: FileAnalysis | null = null;
  expandedIssue: string | null = null;
  feedback: Record<string, boolean> = {};

  constructor() {
    makeAutoObservable(this);
  }

  /**
   * Set the current file being analyzed
   */
  setCurrentFile(filePath: string | null) {
    this.currentFile = filePath;
  }

  /**
   * Set the analysis results
   */
  setAnalysis(analysis: FileAnalysis | null) {
    this.analysis = analysis;
    this.loading = false;
  }

  /**
   * Toggle the expanded state of an issue
   */
  toggleIssueExpanded(issueId: string) {
    this.expandedIssue = this.expandedIssue === issueId ? null : issueId;
  }

  /**
   * Record user feedback on an issue
   */
  recordFeedback(issueId: string, isHelpful: boolean) {
    this.feedback[issueId] = isHelpful;
  }

  /**
   * Reset the store state
   */
  reset() {
    this.loading = false;
    this.currentFile = null;
    this.analysis = null;
    this.expandedIssue = null;
    this.feedback = {};
  }
}

// Create a singleton instance
const store = new AIReviewPanelStore();
export default store;
