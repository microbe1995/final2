export interface MockProject {
  id: string;
  name: string;
  description: string;
  status: '진행 중' | '완료' | '초안';
  createdAt: string;
  updatedAt: string;
}

export const mockProjects: MockProject[] = [
  {
    id: 'proj-1',
    name: '철강 제품 LCA 분석',
    description: '고강도 철강 제품의 생명주기 환경영향 평가',
    status: '완료',
    createdAt: '2024-01-01',
    updatedAt: '2024-01-15',
  },
  {
    id: 'proj-2',
    name: '알루미늄 합금 LCA',
    description: '경량화를 위한 알루미늄 합금 소재 평가',
    status: '진행 중',
    createdAt: '2024-01-05',
    updatedAt: '2024-01-20',
  },
  {
    id: 'proj-3',
    name: '플라스틱 복합재 LCA',
    description: '자동차용 플라스틱 복합재 환경영향 분석',
    status: '초안',
    createdAt: '2024-01-10',
    updatedAt: '2024-01-18',
  },
];
