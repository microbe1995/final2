import { redirect } from 'next/navigation';

export default function HomePage() {
  // 랜딩 제거에 따라 기본 홈을 CBAM으로 리다이렉트합니다.
  redirect('/cbam');
}
