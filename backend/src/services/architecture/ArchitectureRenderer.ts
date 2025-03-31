import { ArchitectureSpec, ArchitectureComponent, ArchitectureConnection } from '../../../frontend/src/services/ArchitectureService';
import * as fs from 'fs';
import * as path from 'path';
import * as puppeteer from 'puppeteer';

interface RenderResult {
  svg: string;
  png: Buffer;
  pdf: Buffer;
}

export class ArchitectureRenderer {
  private readonly templatePath: string;
  private readonly outputDir: string;

  constructor() {
    this.templatePath = path.join(__dirname, '../../templates/architecture');
    this.outputDir = path.join(__dirname, '../../public/architecture');
    this.ensureDirectories();
  }

  private ensureDirectories() {
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }
  }

  async renderArchitecture(architecture: ArchitectureSpec): Promise<RenderResult> {
    // Generate SVG representation
    const svg = this.generateSVG(architecture);

    // Convert SVG to PNG and PDF using Puppeteer
    const { png, pdf } = await this.convertToFormats(svg);

    return {
      svg,
      png,
      pdf,
    };
  }

  private generateSVG(architecture: ArchitectureSpec): string {
    const { components, connections } = architecture;
    const width = 1200;
    const height = 800;
    const padding = 50;

    // Calculate component positions and sizes
    const layout = this.calculateLayout(components, width, height, padding);

    // Generate SVG content
    let svg = `<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">`;

    // Add background
    svg += `<rect width="100%" height="100%" fill="#f8f9fa"/>`;

    // Add connections
    connections.forEach(connection => {
      const source = layout.get(connection.sourceId);
      const target = layout.get(connection.targetId);
      if (source && target) {
        svg += this.generateConnectionSVG(source, target, connection);
      }
    });

    // Add components
    components.forEach(component => {
      const position = layout.get(component.id);
      if (position) {
        svg += this.generateComponentSVG(component, position);
      }
    });

    svg += '</svg>';
    return svg;
  }

  private calculateLayout(
    components: ArchitectureComponent[],
    width: number,
    height: number,
    padding: number
  ): Map<string, { x: number; y: number; width: number; height: number }> {
    const layout = new Map<string, { x: number; y: number; width: number; height: number }>();
    const gridSize = Math.ceil(Math.sqrt(components.length));
    const cellWidth = (width - 2 * padding) / gridSize;
    const cellHeight = (height - 2 * padding) / gridSize;

    components.forEach((component, index) => {
      const row = Math.floor(index / gridSize);
      const col = index % gridSize;
      const x = padding + col * cellWidth;
      const y = padding + row * cellHeight;

      layout.set(component.id, {
        x,
        y,
        width: cellWidth * 0.8,
        height: cellHeight * 0.8,
      });
    });

    return layout;
  }

  private generateComponentSVG(
    component: ArchitectureComponent,
    position: { x: number; y: number; width: number; height: number }
  ): string {
    const { x, y, width, height } = position;
    const style = component.style || {};
    const fill = style.color || '#ffffff';
    const stroke = style.borderColor || '#000000';
    const strokeWidth = style.borderWidth || 2;

    let svg = '';

    // Draw component background
    svg += `<rect
      x="${x}"
      y="${y}"
      width="${width}"
      height="${height}"
      fill="${fill}"
      stroke="${stroke}"
      stroke-width="${strokeWidth}"
      rx="5"
      ry="5"
    />`;

    // Add component title
    svg += `<text
      x="${x + width / 2}"
      y="${y + 25}"
      text-anchor="middle"
      font-size="14"
      font-weight="bold"
      fill="${style.textColor || '#000000'}"
    >${component.name}</text>`;

    // Add component type
    svg += `<text
      x="${x + width / 2}"
      y="${y + 45}"
      text-anchor="middle"
      font-size="12"
      fill="${style.textColor || '#666666'}"
    >${component.type}</text>`;

    return svg;
  }

  private generateConnectionSVG(
    source: { x: number; y: number; width: number; height: number },
    target: { x: number; y: number; width: number; height: number },
    connection: ArchitectureConnection
  ): string {
    const style = connection.style || {};
    const stroke = style.color || '#666666';
    const strokeWidth = style.borderWidth || 2;
    const strokeDasharray = this.getConnectionStyle(connection.type);

    // Calculate connection points
    const sourcePoint = this.calculateConnectionPoint(source, target);
    const targetPoint = this.calculateConnectionPoint(target, source);

    // Draw connection line
    let svg = `<path
      d="M ${sourcePoint.x} ${sourcePoint.y} L ${targetPoint.x} ${targetPoint.y}"
      stroke="${stroke}"
      stroke-width="${strokeWidth}"
      stroke-dasharray="${strokeDasharray}"
      fill="none"
    />`;

    // Add connection type label
    const midPoint = {
      x: (sourcePoint.x + targetPoint.x) / 2,
      y: (sourcePoint.y + targetPoint.y) / 2,
    };

    svg += `<text
      x="${midPoint.x}"
      y="${midPoint.y - 5}"
      text-anchor="middle"
      font-size="10"
      fill="${style.textColor || '#666666'}"
    >${connection.type}</text>`;

    return svg;
  }

  private calculateConnectionPoint(
    component: { x: number; y: number; width: number; height: number },
    target: { x: number; y: number; width: number; height: number }
  ): { x: number; y: number } {
    const centerX = component.x + component.width / 2;
    const centerY = component.y + component.height / 2;
    const targetCenterX = target.x + target.width / 2;
    const targetCenterY = target.y + target.height / 2;

    // Calculate angle between centers
    const angle = Math.atan2(targetCenterY - centerY, targetCenterX - centerX);

    // Calculate intersection point with component rectangle
    const halfWidth = component.width / 2;
    const halfHeight = component.height / 2;

    let x, y;
    if (Math.abs(Math.cos(angle)) * halfHeight > Math.abs(Math.sin(angle)) * halfWidth) {
      // Intersects with vertical edge
      x = Math.sign(Math.cos(angle)) * halfWidth + centerX;
      y = Math.tan(angle) * (x - centerX) + centerY;
    } else {
      // Intersects with horizontal edge
      y = Math.sign(Math.sin(angle)) * halfHeight + centerY;
      x = (y - centerY) / Math.tan(angle) + centerX;
    }

    return { x, y };
  }

  private getConnectionStyle(type: string): string {
    switch (type) {
      case 'dependency':
        return '5,5';
      case 'composition':
        return 'none';
      case 'aggregation':
        return '10,5';
      case 'inheritance':
        return 'none';
      default:
        return 'none';
    }
  }

  private async convertToFormats(svg: string): Promise<{ png: Buffer; pdf: Buffer }> {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    // Set viewport
    await page.setViewport({ width: 1200, height: 800 });

    // Load SVG
    await page.setContent(svg);

    // Generate PNG
    const png = await page.screenshot({
      type: 'png',
      fullPage: true,
    });

    // Generate PDF
    const pdf = await page.pdf({
      format: 'A4',
      printBackground: true,
    });

    await browser.close();

    return {
      png: png as Buffer,
      pdf,
    };
  }

  async saveRenderings(architecture: ArchitectureSpec): Promise<void> {
    const { svg, png, pdf } = await this.renderArchitecture(architecture);
    const basePath = path.join(this.outputDir, architecture.id);

    // Save SVG
    fs.writeFileSync(`${basePath}.svg`, svg);

    // Save PNG
    fs.writeFileSync(`${basePath}.png`, png);

    // Save PDF
    fs.writeFileSync(`${basePath}.pdf`, pdf);
  }
} 