import { create } from 'zustand';
import useImageHandlerStore from './image-handler';
import Tesseract from 'tesseract.js';

const useImageUploadStore = create((set, get) => ({
  // Upload settings
  settings: {
    maxFileSize: 10 * 1024 * 1024, // 10MB
    maxDimensions: { width: 4096, height: 4096 },
    supportedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    compressionQuality: 0.8,
    autoResize: true,
    preserveMetadata: true,
    generateThumbnails: true,
    thumbnailSize: { width: 200, height: 200 }
  },

  // Processing state
  isProcessing: false,
  processingQueue: [],
  currentProcessing: null,
  processingHistory: [],
  error: null,

  // Initialize image processing
  initialize: async () => {
    // Initialize Tesseract.js for OCR
    await Tesseract.createWorker();
    return true;
  },

  // Update upload settings
  updateSettings: (newSettings) => {
    set(state => ({
      settings: { ...state.settings, ...newSettings }
    }));
  },

  // Process image upload with enhanced features
  processImageUpload: async (file) => {
    const { settings, processingQueue } = get();
    
    // Validate file
    if (!settings.supportedTypes.includes(file.type)) {
      set({ error: 'Unsupported file type' });
      return false;
    }

    if (file.size > settings.maxFileSize) {
      set({ error: 'File size exceeds limit' });
      return false;
    }

    if (get().isProcessing) {
      set({ processingQueue: [...processingQueue, file] });
      return;
    }

    set({ isProcessing: true, currentProcessing: file });

    try {
      // Create image object
      const image = await get().createImageObject(file);
      
      // Validate dimensions
      if (image.width > settings.maxDimensions.width || 
          image.height > settings.maxDimensions.height) {
        if (settings.autoResize) {
          await get().resizeImage(image);
        } else {
          set({ error: 'Image dimensions exceed limit' });
          return false;
        }
      }

      // Generate thumbnail if enabled
      if (settings.generateThumbnails) {
        image.thumbnail = await get().generateThumbnail(image);
      }

      // Process OCR if needed
      if (image.needsOCR) {
        await get().processOCR(image);
      }

      // Add to processing history
      set(state => ({
        processingHistory: [...state.processingHistory, {
          id: image.id,
          timestamp: Date.now(),
          size: image.size,
          dimensions: { width: image.width, height: image.height }
        }]
      }));

      // Process next in queue if any
      if (processingQueue.length > 0) {
        const nextFile = processingQueue[0];
        set({ processingQueue: processingQueue.slice(1) });
        get().processImageUpload(nextFile);
      } else {
        set({ isProcessing: false, currentProcessing: null });
      }

      return true;
    } catch (error) {
      set({ error: 'Image processing failed', isProcessing: false });
      return false;
    }
  },

  // Create image object from file
  createImageObject: (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          resolve({
            id: Date.now(),
            file,
            url: e.target.result,
            width: img.width,
            height: img.height,
            type: file.type,
            size: file.size,
            timestamp: Date.now(),
            annotations: [],
            needsOCR: true
          });
        };
        img.onerror = reject;
        img.src = e.target.result;
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  },

  // Resize image while maintaining aspect ratio
  resizeImage: async (image) => {
    const { settings } = get();
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    let width = image.width;
    let height = image.height;
    
    if (width > settings.maxDimensions.width) {
      height = Math.round((height * settings.maxDimensions.width) / width);
      width = settings.maxDimensions.width;
    }
    
    if (height > settings.maxDimensions.height) {
      width = Math.round((width * settings.maxDimensions.height) / height);
      height = settings.maxDimensions.height;
    }
    
    canvas.width = width;
    canvas.height = height;
    ctx.drawImage(image, 0, 0, width, height);
    
    return new Promise((resolve) => {
      canvas.toBlob(blob => {
        const resizedFile = new File([blob], image.file.name, { 
          type: image.file.type 
        });
        image.file = resizedFile;
        image.width = width;
        image.height = height;
        image.size = blob.size;
        resolve(image);
      }, image.file.type, settings.compressionQuality);
    });
  },

  // Generate thumbnail
  generateThumbnail: async (image) => {
    const { settings } = get();
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    let width = image.width;
    let height = image.height;
    
    if (width > settings.thumbnailSize.width) {
      height = Math.round((height * settings.thumbnailSize.width) / width);
      width = settings.thumbnailSize.width;
    }
    
    if (height > settings.thumbnailSize.height) {
      width = Math.round((width * settings.thumbnailSize.height) / height);
      height = settings.thumbnailSize.height;
    }
    
    canvas.width = width;
    canvas.height = height;
    ctx.drawImage(image, 0, 0, width, height);
    
    return new Promise((resolve) => {
      canvas.toBlob(blob => {
        resolve(URL.createObjectURL(blob));
      }, image.file.type, 0.6);
    });
  },

  // Process OCR on image
  processOCR: async (image) => {
    try {
      const worker = await Tesseract.createWorker();
      const result = await worker.recognize(image.url);
      await worker.terminate();
      
      image.ocrText = result.data.text;
      image.ocrConfidence = result.data.confidence;
      image.needsOCR = false;
      
      return image;
    } catch (error) {
      console.error('OCR processing failed:', error);
      return image;
    }
  },

  // Clear processing history
  clearHistory: () => {
    set({ processingHistory: [] });
  },

  // Get processing statistics
  getStatistics: () => {
    const { processingHistory } = get();
    return {
      totalProcessed: processingHistory.length,
      totalSize: processingHistory.reduce((acc, curr) => acc + curr.size, 0),
      averageDimensions: {
        width: processingHistory.reduce((acc, curr) => acc + curr.dimensions.width, 0) / processingHistory.length,
        height: processingHistory.reduce((acc, curr) => acc + curr.dimensions.height, 0) / processingHistory.length
      },
      lastProcessed: processingHistory[processingHistory.length - 1]?.timestamp
    };
  }
}));

export default useImageUploadStore; 