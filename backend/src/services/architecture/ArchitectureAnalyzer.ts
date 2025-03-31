import { ArchitectureSpec, ArchitectureComponent, ArchitectureConnection, ArchitectureAnalysis } from '../../../frontend/src/services/ArchitectureService';

export class ArchitectureAnalyzer {
  private readonly complexityThreshold = 10;
  private readonly couplingThreshold = 0.7;
  private readonly cohesionThreshold = 0.6;

  async analyzeArchitecture(architecture: ArchitectureSpec): Promise<ArchitectureAnalysis> {
    const components = architecture.components;
    const connections = architecture.connections;

    // Calculate metrics
    const complexity = this.calculateComplexity(components, connections);
    const coupling = this.calculateCoupling(components, connections);
    const cohesion = this.calculateCohesion(components, connections);
    const scalability = this.calculateScalability(components, connections);
    const maintainability = this.calculateMaintainability(components, connections);

    // Generate insights
    const insights = this.generateInsights(components, connections, {
      complexity,
      coupling,
      cohesion,
      scalability,
      maintainability,
    });

    // Generate recommendations
    const recommendations = this.generateRecommendations(components, connections, {
      complexity,
      coupling,
      cohesion,
      scalability,
      maintainability,
    });

    return {
      metrics: {
        complexity,
        coupling,
        cohesion,
        scalability,
        maintainability,
      },
      insights,
      recommendations,
      issues: this.identifyIssues(components, connections),
    };
  }

  private calculateComplexity(components: ArchitectureComponent[], connections: ArchitectureConnection[]): number {
    // Calculate cyclomatic complexity based on component relationships
    const componentConnections = new Map<string, number>();
    
    // Count incoming and outgoing connections for each component
    connections.forEach(connection => {
      componentConnections.set(
        connection.sourceId,
        (componentConnections.get(connection.sourceId) || 0) + 1
      );
      componentConnections.set(
        connection.targetId,
        (componentConnections.get(connection.targetId) || 0) + 1
      );
    });

    // Calculate average complexity
    const totalConnections = Array.from(componentConnections.values()).reduce((a, b) => a + b, 0);
    return components.length > 0 ? totalConnections / components.length : 0;
  }

  private calculateCoupling(components: ArchitectureComponent[], connections: ArchitectureConnection[]): number {
    // Calculate coupling based on component dependencies
    const maxPossibleConnections = components.length * (components.length - 1);
    return maxPossibleConnections > 0 ? connections.length / maxPossibleConnections : 0;
  }

  private calculateCohesion(components: ArchitectureComponent[], connections: ArchitectureConnection[]): number {
    // Calculate cohesion based on component relationships and responsibilities
    const componentGroups = this.groupComponentsByType(components);
    const totalGroups = componentGroups.size;
    
    if (totalGroups === 0) return 0;

    // Calculate average group size
    const averageGroupSize = components.length / totalGroups;
    const idealGroupSize = Math.sqrt(components.length);
    
    // Calculate cohesion based on group size distribution
    return Math.min(1, averageGroupSize / idealGroupSize);
  }

  private calculateScalability(components: ArchitectureComponent[], connections: ArchitectureConnection[]): number {
    // Calculate scalability based on component distribution and load balancing
    const componentGroups = this.groupComponentsByType(components);
    const totalGroups = componentGroups.size;
    
    if (totalGroups === 0) return 0;

    // Calculate load distribution
    const loadDistribution = Array.from(componentGroups.values()).map(group => group.length);
    const maxLoad = Math.max(...loadDistribution);
    const minLoad = Math.min(...loadDistribution);
    
    // Calculate scalability score based on load distribution
    return 1 - (maxLoad - minLoad) / components.length;
  }

  private calculateMaintainability(components: ArchitectureComponent[], connections: ArchitectureConnection[]): number {
    // Calculate maintainability based on component complexity and relationships
    const complexity = this.calculateComplexity(components, connections);
    const coupling = this.calculateCoupling(components, connections);
    const cohesion = this.calculateCohesion(components, connections);

    // Weighted average of metrics
    return (0.4 * (1 - complexity / this.complexityThreshold) +
            0.3 * (1 - coupling) +
            0.3 * cohesion);
  }

  private groupComponentsByType(components: ArchitectureComponent[]): Map<string, ArchitectureComponent[]> {
    const groups = new Map<string, ArchitectureComponent[]>();
    
    components.forEach(component => {
      const type = component.type;
      if (!groups.has(type)) {
        groups.set(type, []);
      }
      groups.get(type)?.push(component);
    });

    return groups;
  }

  private generateInsights(
    components: ArchitectureComponent[],
    connections: ArchitectureConnection[],
    metrics: {
      complexity: number;
      coupling: number;
      cohesion: number;
      scalability: number;
      maintainability: number;
    }
  ): string[] {
    const insights: string[] = [];

    // Complexity insights
    if (metrics.complexity > this.complexityThreshold) {
      insights.push('The architecture has high complexity, which may make it difficult to understand and maintain.');
    }

    // Coupling insights
    if (metrics.coupling > this.couplingThreshold) {
      insights.push('There is high coupling between components, which may lead to tight dependencies and reduced flexibility.');
    }

    // Cohesion insights
    if (metrics.cohesion < this.cohesionThreshold) {
      insights.push('The components show low cohesion, suggesting they may have too many responsibilities.');
    }

    // Scalability insights
    if (metrics.scalability < 0.6) {
      insights.push('The architecture may face scalability challenges due to uneven load distribution.');
    }

    // Maintainability insights
    if (metrics.maintainability < 0.6) {
      insights.push('The overall maintainability of the architecture could be improved.');
    }

    return insights;
  }

  private generateRecommendations(
    components: ArchitectureComponent[],
    connections: ArchitectureConnection[],
    metrics: {
      complexity: number;
      coupling: number;
      cohesion: number;
      scalability: number;
      maintainability: number;
    }
  ): string[] {
    const recommendations: string[] = [];

    // Complexity recommendations
    if (metrics.complexity > this.complexityThreshold) {
      recommendations.push('Consider breaking down complex components into smaller, more manageable pieces.');
    }

    // Coupling recommendations
    if (metrics.coupling > this.couplingThreshold) {
      recommendations.push('Introduce interfaces or abstractions to reduce direct dependencies between components.');
    }

    // Cohesion recommendations
    if (metrics.cohesion < this.cohesionThreshold) {
      recommendations.push('Refactor components to have more focused responsibilities and better separation of concerns.');
    }

    // Scalability recommendations
    if (metrics.scalability < 0.6) {
      recommendations.push('Implement load balancing and consider using microservices for better scalability.');
    }

    // Maintainability recommendations
    if (metrics.maintainability < 0.6) {
      recommendations.push('Add comprehensive documentation and consider implementing automated testing.');
    }

    return recommendations;
  }

  private identifyIssues(components: ArchitectureComponent[], connections: ArchitectureConnection[]): string[] {
    const issues: string[] = [];

    // Check for isolated components
    const connectedComponentIds = new Set<string>();
    connections.forEach(connection => {
      connectedComponentIds.add(connection.sourceId);
      connectedComponentIds.add(connection.targetId);
    });

    components.forEach(component => {
      if (!connectedComponentIds.has(component.id)) {
        issues.push(`Component "${component.name}" is isolated and not connected to any other components.`);
      }
    });

    // Check for circular dependencies
    const circularDependencies = this.findCircularDependencies(connections);
    if (circularDependencies.length > 0) {
      issues.push('Circular dependencies detected between components.');
    }

    // Check for single points of failure
    const criticalComponents = this.identifyCriticalComponents(components, connections);
    if (criticalComponents.length > 0) {
      issues.push(`Critical components identified: ${criticalComponents.map(c => c.name).join(', ')}`);
    }

    return issues;
  }

  private findCircularDependencies(connections: ArchitectureConnection[]): string[][] {
    const graph = new Map<string, Set<string>>();
    const visited = new Set<string>();
    const recursionStack = new Set<string>();
    const cycles: string[][] = [];

    // Build adjacency list
    connections.forEach(connection => {
      if (!graph.has(connection.sourceId)) {
        graph.set(connection.sourceId, new Set());
      }
      graph.get(connection.sourceId)?.add(connection.targetId);
    });

    // DFS to find cycles
    const dfs = (node: string, path: string[]) => {
      visited.add(node);
      recursionStack.add(node);
      path.push(node);

      const neighbors = graph.get(node) || new Set();
      for (const neighbor of neighbors) {
        if (!visited.has(neighbor)) {
          dfs(neighbor, [...path]);
        } else if (recursionStack.has(neighbor)) {
          const cycleStart = path.indexOf(neighbor);
          if (cycleStart !== -1) {
            cycles.push(path.slice(cycleStart));
          }
        }
      }

      recursionStack.delete(node);
    };

    // Check each component
    for (const node of graph.keys()) {
      if (!visited.has(node)) {
        dfs(node, []);
      }
    }

    return cycles;
  }

  private identifyCriticalComponents(
    components: ArchitectureComponent[],
    connections: ArchitectureConnection[]
  ): ArchitectureComponent[] {
    const criticalComponents: ArchitectureComponent[] = [];
    const componentConnections = new Map<string, Set<string>>();

    // Build connection map
    connections.forEach(connection => {
      if (!componentConnections.has(connection.sourceId)) {
        componentConnections.set(connection.sourceId, new Set());
      }
      if (!componentConnections.has(connection.targetId)) {
        componentConnections.set(connection.targetId, new Set());
      }
      componentConnections.get(connection.sourceId)?.add(connection.targetId);
      componentConnections.get(connection.targetId)?.add(connection.sourceId);
    });

    // Identify critical components
    components.forEach(component => {
      const connections = componentConnections.get(component.id) || new Set();
      if (connections.size >= 3) {
        criticalComponents.push(component);
      }
    });

    return criticalComponents;
  }
} 