'use client';

import { useCallback, useState, useRef } from 'react';
import type { Viewport, XYPosition } from '@xyflow/react';

// ============================================================================
// 🎯 Advanced Viewport 타입 정의
// ============================================================================

export type ViewportMode = 'default' | 'design-tool' | 'map' | 'presentation';

export interface ViewportOptions {
  mode: ViewportMode;
  panOnScroll?: boolean;
  panOnDrag?: boolean;
  selectionOnDrag?: boolean;
  zoomOnScroll?: boolean;
  zoomOnPinch?: boolean;
  zoomOnDoubleClick?: boolean;
  selectionMode?: 'partial' | 'full';
  multiSelectionKey?: 'shift' | 'ctrl' | 'meta';
  panOnMiddleMouse?: boolean;
  panOnRightMouse?: boolean;
  spacePan?: boolean;
}

export interface ViewportState {
  x: number;
  y: number;
  zoom: number;
  mode: ViewportMode;
  isPanning: boolean;
  isSelecting: boolean;
  isZooming: boolean;
}

// ============================================================================
// 🎯 Advanced Viewport 훅
// ============================================================================

export const useAdvancedViewport = () => {
  const [viewport, setViewport] = useState<ViewportState>({
    x: 0,
    y: 0,
    zoom: 1,
    mode: 'default',
    isPanning: false,
    isSelecting: false,
    isZooming: false
  });

  const [options, setOptions] = useState<ViewportOptions>({
    mode: 'default',
    panOnScroll: false,
    panOnDrag: true,
    selectionOnDrag: false,
    zoomOnScroll: true,
    zoomOnPinch: true,
    zoomOnDoubleClick: true,
    selectionMode: 'full',
    multiSelectionKey: 'shift',
    panOnMiddleMouse: false,
    panOnRightMouse: false,
    spacePan: false
  });

  const viewportRef = useRef<HTMLDivElement>(null);
  const isSpacePressed = useRef(false);

  // ============================================================================
  // 🎯 Design Tool Viewport Mode (Figma/Sketch 스타일)
  // ============================================================================
  
  const enableDesignToolMode = useCallback(() => {
    const designToolOptions: ViewportOptions = {
      mode: 'design-tool',
      panOnScroll: true,
      panOnDrag: false,
      selectionOnDrag: true,
      zoomOnScroll: false,
      zoomOnPinch: true,
      zoomOnDoubleClick: true,
      selectionMode: 'partial',
      multiSelectionKey: 'shift',
      panOnMiddleMouse: true,
      panOnRightMouse: true,
      spacePan: true
    };
    
    setOptions(designToolOptions);
    setViewport(prev => ({ ...prev, mode: 'design-tool' }));
  }, []);

  // ============================================================================
  // 🎯 Map Viewport Mode (지도 스타일)
  // ============================================================================
  
  const enableMapMode = useCallback(() => {
    const mapOptions: ViewportOptions = {
      mode: 'map',
      panOnScroll: false,
      panOnDrag: true,
      selectionOnDrag: false,
      zoomOnScroll: true,
      zoomOnPinch: true,
      zoomOnDoubleClick: true,
      selectionMode: 'full',
      multiSelectionKey: 'ctrl',
      panOnMiddleMouse: true,
      panOnRightMouse: false,
      spacePan: false
    };
    
    setOptions(mapOptions);
    setViewport(prev => ({ ...prev, mode: 'map' }));
  }, []);

  // ============================================================================
  // 🎯 Presentation Viewport Mode (프레젠테이션 스타일)
  // ============================================================================
  
  const enablePresentationMode = useCallback(() => {
    const presentationOptions: ViewportOptions = {
      mode: 'presentation',
      panOnScroll: false,
      panOnDrag: false,
      selectionOnDrag: false,
      zoomOnScroll: false,
      zoomOnPinch: false,
      zoomOnDoubleClick: false,
      selectionMode: 'full',
      multiSelectionKey: 'shift',
      panOnMiddleMouse: false,
      panOnRightMouse: false,
      spacePan: false
    };
    
    setOptions(presentationOptions);
    setViewport(prev => ({ ...prev, mode: 'presentation' }));
  }, []);

  // ============================================================================
  // 🎯 Default Viewport Mode (기본 React Flow 스타일)
  // ============================================================================
  
  const enableDefaultMode = useCallback(() => {
    const defaultOptions: ViewportOptions = {
      mode: 'default',
      panOnScroll: false,
      panOnDrag: true,
      selectionOnDrag: false,
      zoomOnScroll: true,
      zoomOnPinch: true,
      zoomOnDoubleClick: true,
      selectionMode: 'full',
      multiSelectionKey: 'shift',
      panOnMiddleMouse: false,
      panOnRightMouse: false,
      spacePan: false
    };
    
    setOptions(defaultOptions);
    setViewport(prev => ({ ...prev, mode: 'default' }));
  }, []);

  // ============================================================================
  // 🎯 Viewport 이동 제어
  // ============================================================================
  
  const panViewport = useCallback((delta: XYPosition) => {
    setViewport(prev => ({
      ...prev,
      x: prev.x + delta.x,
      y: prev.y + delta.y,
      isPanning: true
    }));
  }, []);

  const panToPosition = useCallback((position: XYPosition) => {
    setViewport(prev => ({
      ...prev,
      x: -position.x,
      y: -position.y,
      isPanning: false
    }));
  }, []);

  const panToCenter = useCallback(() => {
    setViewport(prev => ({
      ...prev,
      x: 0,
      y: 0,
      isPanning: false
    }));
  }, []);

  // ============================================================================
  // 🎯 Viewport 확대/축소 제어
  // ============================================================================
  
  const zoomViewport = useCallback((delta: number, center?: XYPosition) => {
    setViewport(prev => {
      const newZoom = Math.max(0.1, Math.min(2, prev.zoom + delta));
      
      if (center) {
        // 특정 지점을 중심으로 확대/축소
        const zoomRatio = newZoom / prev.zoom;
        const newX = center.x - (center.x - prev.x) * zoomRatio;
        const newY = center.y - (center.y - prev.y) * zoomRatio;
        
        return {
          ...prev,
          zoom: newZoom,
          x: newX,
          y: newY,
          isZooming: true
        };
      }
      
      return {
        ...prev,
        zoom: newZoom,
        isZooming: true
      };
    });
  }, []);

  const zoomToFit = useCallback((nodes: any[], padding: number = 50) => {
    if (nodes.length === 0) return;
    
    // 노드들의 경계 계산
    const bounds = nodes.reduce((acc, node) => {
      const x = node.position.x;
      const y = node.position.y;
      const width = node.style?.width || 100;
      const height = node.style?.height || 100;
      
      acc.minX = Math.min(acc.minX, x);
      acc.maxX = Math.max(acc.maxX, x + width);
      acc.minY = Math.min(acc.minY, y);
      acc.maxY = Math.max(acc.maxY, y + height);
      
      return acc;
    }, { minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity });
    
    // 뷰포트 크기 (임시값, 실제로는 DOM에서 가져와야 함)
    const viewportWidth = 800;
    const viewportHeight = 600;
    
    // 적절한 줌 레벨 계산
    const contentWidth = bounds.maxX - bounds.minX + padding * 2;
    const contentHeight = bounds.maxY - bounds.minY + padding * 2;
    
    const zoomX = viewportWidth / contentWidth;
    const zoomY = viewportHeight / contentHeight;
    const zoom = Math.min(zoomX, zoomY, 2); // 최대 2배 확대
    
    // 중앙 위치 계산
    const centerX = (bounds.minX + bounds.maxX) / 2;
    const centerY = (bounds.minY + bounds.maxY) / 2;
    
    setViewport(prev => ({
      ...prev,
      zoom,
      x: -centerX + viewportWidth / (2 * zoom),
      y: -centerY + viewportHeight / (2 * zoom),
      isZooming: false
    }));
  }, []);

  const resetViewport = useCallback(() => {
    setViewport(prev => ({
      ...prev,
      x: 0,
      y: 0,
      zoom: 1,
      isPanning: false,
      isSelecting: false,
      isZooming: false
    }));
  }, []);

  // ============================================================================
  // 🎯 키보드 단축키 처리
  // ============================================================================
  
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (event.code === 'Space') {
      isSpacePressed.current = true;
      if (options.spacePan) {
        event.preventDefault();
        setViewport(prev => ({ ...prev, isPanning: true }));
      }
    }
  }, [options.spacePan]);

  const handleKeyUp = useCallback((event: KeyboardEvent) => {
    if (event.code === 'Space') {
      isSpacePressed.current = false;
      setViewport(prev => ({ ...prev, isPanning: false }));
    }
  }, []);

  // ============================================================================
  // 🎯 마우스 이벤트 처리
  // ============================================================================
  
  const handleMouseDown = useCallback((event: React.MouseEvent, button: number) => {
    if (button === 1 && options.panOnMiddleMouse) { // 중간 버튼
      event.preventDefault();
      setViewport(prev => ({ ...prev, isPanning: true }));
    } else if (button === 2 && options.panOnRightMouse) { // 우클릭
      event.preventDefault();
      setViewport(prev => ({ ...prev, isPanning: true }));
    }
  }, [options.panOnMiddleMouse, options.panOnRightMouse]);

  const handleMouseUp = useCallback((event: React.MouseEvent, button: number) => {
    if (button === 1 || button === 2) {
      setViewport(prev => ({ ...prev, isPanning: false }));
    }
  }, []);

  // ============================================================================
  // 🎯 터치 이벤트 처리
  // ============================================================================
  
  const handleTouchStart = useCallback((event: React.TouchEvent) => {
    if (event.touches.length === 2) {
      setViewport(prev => ({ ...prev, isZooming: true }));
    }
  }, []);

  const handleTouchEnd = useCallback(() => {
    setViewport(prev => ({ ...prev, isZooming: false }));
  }, []);

  return {
    // 상태
    viewport,
    options,
    
    // 모드 설정
    enableDesignToolMode,
    enableMapMode,
    enablePresentationMode,
    enableDefaultMode,
    
    // 뷰포트 제어
    panViewport,
    panToPosition,
    panToCenter,
    zoomViewport,
    zoomToFit,
    resetViewport,
    
    // 이벤트 핸들러
    handleKeyDown,
    handleKeyUp,
    handleMouseDown,
    handleMouseUp,
    handleTouchStart,
    handleTouchEnd,
    
    // 유틸리티
    getViewportProps: () => ({
      panOnScroll: options.panOnScroll,
      panOnDrag: options.panOnDrag,
      selectionOnDrag: options.selectionOnDrag,
      zoomOnScroll: options.zoomOnScroll,
      zoomOnPinch: options.zoomOnPinch,
      zoomOnDoubleClick: options.zoomOnDoubleClick,
      selectionMode: options.selectionMode,
      multiSelectionKey: options.multiSelectionKey
    }),
    
    // 상태 체크
    isInDesignMode: viewport.mode === 'design-tool',
    isInMapMode: viewport.mode === 'map',
    isInPresentationMode: viewport.mode === 'presentation',
    isInDefaultMode: viewport.mode === 'default'
  };
};
