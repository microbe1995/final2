'use client';

import { useState, useCallback } from 'react';

export const useProcessTypeModal = (
  onSelectNode: () => void,
  onSelectEdge: () => void
) => {
  const [isOpen, setIsOpen] = useState(false);

  const openModal = useCallback(() => {
    setIsOpen(true);
  }, []);

  const closeModal = useCallback(() => {
    setIsOpen(false);
  }, []);

  const handleSelectType = useCallback((type: 'node' | 'edge') => {
    if (type === 'node') {
      onSelectNode();
    } else if (type === 'edge') {
      onSelectEdge();
    }
    closeModal();
  }, [onSelectNode, onSelectEdge, closeModal]);

  return {
    isOpen,
    openModal,
    closeModal,
    handleSelectType,
  };
};
