'use client';

import { memo } from 'react';

interface AnnotationNodeProps {
  data: {
    label: string;
    arrowStyle?: string;
    level?: number;
  };
}

function AnnotationNode({ data }: AnnotationNodeProps) {
  return (
    <>
      <div className="annotation-content">
        <div>{data.label}</div>
      </div>
      {data.arrowStyle && (
        <div className={`annotation-arrow ${data.arrowStyle}`}>
          <svg 
            width="16" 
            height="16" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round"
          >
            <path d="M8 18L12 22L16 18"/>
            <path d="M12 2V22"/>
          </svg>
        </div>
      )}
    </>
  );
}

export { AnnotationNode };
export default memo(AnnotationNode);
