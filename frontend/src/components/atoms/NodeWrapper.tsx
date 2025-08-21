'use client';

import React from 'react';

interface NodeWrapperProps {
  children: React.ReactNode;
  top?: number;
  bottom?: number;
  left?: number;
  right?: number;
  width?: number;
  height?: number;
}

const NodeWrapper: React.FC<NodeWrapperProps> = ({
  children,
  top,
  bottom,
  left,
  right,
  width,
  height,
}) => {
  const style: React.CSSProperties = {
    position: 'absolute',
    top: top !== undefined ? top : 'auto',
    bottom: bottom !== undefined ? bottom : 'auto',
    left: left !== undefined ? left : 'auto',
    right: right !== undefined ? right : 'auto',
    width: width !== undefined ? width : 'auto',
    height: height !== undefined ? height : 'auto',
    zIndex: 1000,
  };

  return <div style={style}>{children}</div>;
};

export default NodeWrapper;
