import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { monitoringService } from '../../services/monitoring.service';
import { accessibilityService } from '../../services/accessibility.service';

interface ModelPerformanceChartProps {
  data: {
    accuracy: number;
    precision: number;
    recall: number;
    f1Score: number;
    timestamp: number;
  }[];
  width?: number;
  height?: number;
  className?: string;
}

export const ModelPerformanceChart: React.FC<ModelPerformanceChartProps> = ({
  data,
  width = 600,
  height = 400,
  className,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const metricsRef = useRef<THREE.Group | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Initialize scene
    const scene = new THREE.Scene();
    sceneRef.current = scene;

    // Initialize camera
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.z = 5;
    cameraRef.current = camera;

    // Initialize renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setClearColor(0x000000, 0);
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Add controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controlsRef.current = controls;

    // Add lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight.position.set(5, 5, 5);
    scene.add(directionalLight);

    // Create metrics group
    const metricsGroup = new THREE.Group();
    metricsRef.current = metricsGroup;
    scene.add(metricsGroup);

    // Add ARIA label
    if (containerRef.current) {
      accessibilityService.addAriaLabel(
        containerRef.current,
        '3D visualization of model performance metrics'
      );
    }

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };

    animate();

    // Cleanup
    return () => {
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [width, height]);

  useEffect(() => {
    if (!metricsRef.current || !data.length) return;

    // Clear existing metrics
    while (metricsRef.current.children.length > 0) {
      const child = metricsRef.current.children[0];
      if (child instanceof THREE.Mesh) {
        child.geometry.dispose();
        child.material.dispose();
      }
      metricsRef.current.remove(child);
    }

    // Create new metrics visualization
    const metrics = ['accuracy', 'precision', 'recall', 'f1Score'];
    const colors = [0x4caf50, 0x2196f3, 0xff9800, 0xf44336];

    metrics.forEach((metric, index) => {
      const value = data[data.length - 1][metric as keyof typeof data[0]];
      const geometry = new THREE.SphereGeometry(value, 32, 32);
      const material = new THREE.MeshPhongMaterial({
        color: colors[index],
        transparent: true,
        opacity: 0.8,
      });
      const sphere = new THREE.Mesh(geometry, material);
      sphere.position.x = (index - 1.5) * 2;
      metricsRef.current?.add(sphere);

      // Add label
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      if (context) {
        canvas.width = 256;
        canvas.height = 64;
        context.fillStyle = '#ffffff';
        context.font = 'bold 24px Arial';
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText(`${metric}: ${value.toFixed(2)}`, 128, 32);

        const texture = new THREE.CanvasTexture(canvas);
        const labelGeometry = new THREE.PlaneGeometry(2, 0.5);
        const labelMaterial = new THREE.MeshBasicMaterial({
          map: texture,
          transparent: true,
        });
        const label = new THREE.Mesh(labelGeometry, labelMaterial);
        label.position.set(sphere.position.x, -1.5, 0);
        metricsRef.current?.add(label);
      }
    });

    // Track performance
    monitoringService.trackPerformance({
      name: 'model_performance_chart_render',
      value: performance.now(),
      tags: {
        dataPoints: data.length.toString(),
      },
    });
  }, [data]);

  return (
    <div
      ref={containerRef}
      className={className}
      style={{ width, height }}
      role="img"
      aria-label="3D visualization of model performance metrics"
    />
  );
}; 