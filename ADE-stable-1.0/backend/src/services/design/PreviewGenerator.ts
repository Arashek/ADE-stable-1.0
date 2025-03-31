import { DesignSpec } from '../../../frontend/src/services/DesignAgentService';
import puppeteer from 'puppeteer';

export class PreviewGenerator {
  public async generatePreview(design: DesignSpec): Promise<string> {
    // Launch browser
    const browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    try {
      // Create new page
      const page = await browser.newPage();
      await page.setViewport({ width: 1920, height: 1080 });

      // Generate HTML content
      const html = this.generateHTML(design);

      // Set content and wait for rendering
      await page.setContent(html);
      await page.waitForSelector('#design-preview');

      // Take screenshot
      const screenshot = await page.screenshot({
        type: 'png',
        encoding: 'base64',
        fullPage: true
      });

      return `data:image/png;base64,${screenshot}`;
    } finally {
      await browser.close();
    }
  }

  private generateHTML(design: DesignSpec): string {
    const { components } = design;

    return `
      <!DOCTYPE html>
      <html>
        <head>
          <style>
            body {
              margin: 0;
              padding: 0;
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            }
            #design-preview {
              position: relative;
              width: 100%;
              min-height: 100vh;
              background: #f5f5f5;
            }
            .component {
              position: absolute;
              box-sizing: border-box;
              border: 1px solid #ccc;
              border-radius: 4px;
              background: white;
              box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .container {
              display: flex;
              flex-direction: column;
            }
            .button {
              display: inline-flex;
              align-items: center;
              justify-content: center;
              padding: 8px 16px;
              background: #1976d2;
              color: white;
              border: none;
              border-radius: 4px;
              cursor: pointer;
            }
            .input {
              padding: 8px;
              border: 1px solid #ccc;
              border-radius: 4px;
              width: 100%;
              box-sizing: border-box;
            }
            .text {
              padding: 8px;
            }
            .image {
              width: 100%;
              height: 100%;
              object-fit: cover;
            }
            .card {
              padding: 16px;
              background: white;
              border-radius: 8px;
              box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
          </style>
        </head>
        <body>
          <div id="design-preview">
            ${components.map(comp => this.generateComponentHTML(comp)).join('\n')}
          </div>
        </body>
      </html>
    `;
  }

  private generateComponentHTML(component: any): string {
    const { id, type, content, style, position, size } = component;

    const commonStyles = `
      left: ${position.x}px;
      top: ${position.y}px;
      width: ${size.width}px;
      height: ${size.height}px;
      ${Object.entries(style)
        .map(([key, value]) => `${key}: ${value};`)
        .join('\n')}
    `;

    switch (type) {
      case 'container':
        return `
          <div class="component container" id="${id}" style="${commonStyles}">
            ${component.children?.map((child: any) => this.generateComponentHTML(child)).join('\n') || ''}
          </div>
        `;

      case 'button':
        return `
          <button class="component button" id="${id}" style="${commonStyles}">
            ${content || 'Button'}
          </button>
        `;

      case 'input':
        return `
          <input class="component input" id="${id}" style="${commonStyles}" placeholder="${content || 'Input'}">
        `;

      case 'text':
        return `
          <div class="component text" id="${id}" style="${commonStyles}">
            ${content || 'Text'}
          </div>
        `;

      case 'image':
        return `
          <img class="component image" id="${id}" style="${commonStyles}" src="${content || 'https://via.placeholder.com/150'}" alt="Image">
        `;

      case 'card':
        return `
          <div class="component card" id="${id}" style="${commonStyles}">
            ${content || 'Card Content'}
          </div>
        `;

      default:
        return '';
    }
  }
} 