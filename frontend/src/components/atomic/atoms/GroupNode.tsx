'use client';

import React, { useMemo } from 'react';
import { Handle, NodeProps, Position, NodeResizer } from '@xyflow/react';

type Callbacks = {
  openSubflow: (groupNodeId: string) => void;
  ensureSubflow: (groupNodeId: string) => void;
  getSubflowCount: (groupNodeId: string) => { nodes: number; edges: number } | null;
};

function GroupNode({ id, data, selected, dragging, width, height }: NodeProps) {
  const cbs: Callbacks | undefined = data?.__callbacks as Callbacks | undefined;
  const sub = useMemo(() => cbs?.getSubflowCount?.(id) ?? null, [cbs, id]);
  
  // data에서 label을 안전하게 추출
  const groupLabel = (data as any)?.label || id;

  const onOpen = () => {
    if (!cbs) return;
    cbs.ensureSubflow(id);
    cbs.openSubflow(id);
  };

  // 경계 느낌을 위한 스타일(두꺼운 점선, 옅은 배경, 헤더 바)
  const boundaryStyle: React.CSSProperties = {
    position: 'relative',
    minWidth: 240,
    minHeight: 140,
    width,                // NodeResizer가 조절한 width/height를 React Flow가 넘겨줍니다.
    height,
    border: `3px dashed ${selected ? '#2563eb' : '#9ca3af'}`,
    borderRadius: 12,
    background:
      'repeating-linear-gradient(135deg, rgba(59,130,246,0.06) 0 12px, rgba(59,130,246,0.04) 12px 24px)', // 옅은 스트라이프
    boxShadow: selected ? '0 0 0 4px rgba(37,99,235,0.15)' : '0 2px 8px rgba(0,0,0,0.06)',
    overflow: 'hidden',
    // ✅ resize: 'both' 제거 - NodeResizer로 대체
  };

  const headerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 8,
    padding: '8px 10px',
    background: 'rgba(255,255,255,0.85)',
    borderBottom: '1px solid #e5e7eb',
    fontSize: 12,
    fontWeight: 700,
  };

  const badgeStyle: React.CSSProperties = {
    fontSize: 11,
    fontWeight: 600,
    color: '#374151',
  };

  const bodyStyle: React.CSSProperties = {
    padding: 10,
    fontSize: 12,
    color: '#6b7280',
  };

  // ✅ 모든 핸들을 초록색으로 통일
  const handleStyle = {
    background: '#10b981',
    width: 12,
    height: 12,
    border: '2px solid white',
    borderRadius: '50%',
  };

  return (
    <>
      {/* ✅ NodeResizer 추가 - 단일 프레임으로 리사이징 */}
      <NodeResizer
        minWidth={240}
        minHeight={140}
        isVisible={selected}
        lineClassName="border-2 border-blue-500"
        handleClassName="w-3 h-3 bg-blue-500 border-2 border-white rounded-full"
      />
      
      <div style={boundaryStyle}>
        {/* 헤더 */}
        <div className="nodrag" style={headerStyle}>
          <div>
            <span style={{ marginRight: 6 }}>🗂️</span>
            그룹 {groupLabel}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={badgeStyle}>
              {sub ? `Sub flow ${sub.nodes}·${sub.edges}` : 'Sub flow 0·0'}
            </span>
            <button
              onClick={onOpen}
              className="nodrag"
              style={{
                border: '1px solid #e5e7eb',
                background: '#fff',
                padding: '4px 8px',
                borderRadius: 8,
                fontSize: 12,
              }}
            >
              열기
            </button>
          </div>
        </div>

        {/* 바디(설명/요약용). 필요 없으면 제거 가능 */}
        <div className="nodrag" style={bodyStyle}>
          하위 공정(서브 플로우)을 정의하려면 &apos;열기&apos;를 눌러 편집하세요.
        </div>

        {/* ✅ 4방향 모든 핸들 추가 (모두 초록색) */}
        <Handle id="left" type="target" position={Position.Left} style={handleStyle} />
        <Handle id="right" type="source" position={Position.Right} style={handleStyle} />
        <Handle id="top" type="target" position={Position.Top} style={handleStyle} />
        <Handle id="bottom" type="source" position={Position.Bottom} style={handleStyle} />
      </div>
    </>
  );
}

export default GroupNode;
