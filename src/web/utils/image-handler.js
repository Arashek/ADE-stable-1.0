import { create } from 'zustand';
import Tesseract from 'tesseract.js';

const useImageHandlerStore = create((set, get) => ({
  images: [],
  currentImage: null,
  annotations: new Map(),
  isProcessing: false,
  error: null,
  dragOver: false,
  supportedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
  maxFileSize: 10 * 1024 * 1024, // 10MB
  maxDimensions: { width: 4096, height: 4096 },
  processingQueue: [],
  isQueueProcessing: false,

  addImage: (file) => {
    const { images, supportedTypes, maxFileSize, maxDimensions } = get();

    if (!supportedTypes.includes(file.type)) {
      set({ error: 'Unsupported file type' });
      return false;
    }

    if (file.size > maxFileSize) {
      set({ error: 'File size exceeds limit' });
      return false;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        if (img.width > maxDimensions.width || img.height > maxDimensions.height) {
          set({ error: 'Image dimensions exceed limit' });
          return;
        }

        const newImage = {
          id: Date.now(),
          file,
          url: e.target.result,
          width: img.width,
          height: img.height,
          type: file.type,
          size: file.size,
          timestamp: Date.now(),
          annotations: []
        };

        set({
          images: [...images, newImage],
          error: null
        });

        // Process image for OCR
        get().processImageOCR(newImage);
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
    return true;
  },

  removeImage: (imageId) => {
    const { images } = get();
    set({
      images: images.filter(img => img.id !== imageId),
      currentImage: get().currentImage?.id === imageId ? null : get().currentImage
    });
  },

  setCurrentImage: (imageId) => {
    const { images } = get();
    const image = images.find(img => img.id === imageId);
    set({ currentImage: image });
  },

  addAnnotation: (imageId, annotation) => {
    const { images } = get();
    const updatedImages = images.map(img => {
      if (img.id === imageId) {
        return {
          ...img,
          annotations: [...img.annotations, { ...annotation, id: Date.now() }]
        };
      }
      return img;
    });
    set({ images: updatedImages });
  },

  removeAnnotation: (imageId, annotationId) => {
    const { images } = get();
    const updatedImages = images.map(img => {
      if (img.id === imageId) {
        return {
          ...img,
          annotations: img.annotations.filter(ann => ann.id !== annotationId)
        };
      }
      return img;
    });
    set({ images: updatedImages });
  },

  processImageOCR: async (image) => {
    const { isProcessing, processingQueue } = get();
    if (isProcessing) {
      set({ processingQueue: [...processingQueue, image] });
      return;
    }

    set({ isProcessing: true });

    try {
      const result = await Tesseract.recognize(
        image.url,
        'eng',
        {
          logger: m => {
            if (m.status === 'recognizing text') {
              set({ progress: m.progress });
            }
          }
        }
      );

      const updatedImages = get().images.map(img => {
        if (img.id === image.id) {
          return {
            ...img,
            ocrText: result.data.text,
            ocrConfidence: result.data.confidence
          };
        }
        return img;
      });

      set({
        images: updatedImages,
        isProcessing: false,
        progress: 1
      });

      // Process next in queue if any
      if (processingQueue.length > 0) {
        const nextImage = processingQueue[0];
        set({ processingQueue: processingQueue.slice(1) });
        get().processImageOCR(nextImage);
      }
    } catch (error) {
      set({
        error: 'OCR processing failed',
        isProcessing: false
      });
    }
  },

  captureScreenshot: async (element) => {
    try {
      const canvas = await html2canvas(element, {
        useCORS: true,
        allowTaint: true,
        backgroundColor: null
      });

      const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
      const file = new File([blob], `screenshot-${Date.now()}.png`, { type: 'image/png' });
      
      return get().addImage(file);
    } catch (error) {
      set({ error: 'Screenshot capture failed' });
      return false;
    }
  },

  resizeImage: async (image, maxWidth, maxHeight) => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;

        if (width > maxWidth) {
          height = Math.round((height * maxWidth) / width);
          width = maxWidth;
        }

        if (height > maxHeight) {
          width = Math.round((width * maxHeight) / height);
          height = maxHeight;
        }

        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);

        canvas.toBlob(blob => {
          const file = new File([blob], image.file.name, { type: image.file.type });
          resolve(file);
        }, image.file.type);
      };
      img.onerror = reject;
      img.src = image.url;
    });
  },

  setDragOver: (isOver) => {
    set({ dragOver: isOver });
  },

  clearError: () => {
    set({ error: null });
  }
}));

export default useImageHandlerStore; 