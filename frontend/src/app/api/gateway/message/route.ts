import { NextRequest, NextResponse } from 'next/server';

const GATEWAY_URL = process.env.GATEWAY_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // 터미널에 명확한 로그 출력
    console.log('\n' + '='.repeat(80));
    console.log('🌐 FRONTEND API ROUTE - 메시지 수신');
    console.log('='.repeat(80));
    console.log('📥 받은 메시지:', body.message);
    console.log('⏰ 수신 시간:', new Date().toISOString());
    console.log('🌐 게이트웨이 URL:', GATEWAY_URL);
    console.log('='.repeat(80) + '\n');

    // 게이트웨이로 요청 전송
    const response = await fetch(`${GATEWAY_URL}/message-service/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': request.headers.get('Authorization') || '',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('❌ 게이트웨이 에러:', errorData);
      
      return NextResponse.json(
        { error: errorData.detail || '게이트웨이 요청 실패' },
        { status: response.status }
      );
    }

    const data = await response.json();
    
    // 성공 로그 출력
    console.log('\n' + '='.repeat(80));
    console.log('✅ FRONTEND API ROUTE - 메시지 처리 완료');
    console.log('='.repeat(80));
    console.log('📤 게이트웨이 응답:', data);
    console.log('⏰ 완료 시간:', new Date().toISOString());
    console.log('='.repeat(80) + '\n');

    return NextResponse.json(data);
  } catch (error) {
    console.error('\n' + '='.repeat(80));
    console.error('🔴 FRONTEND API ROUTE - 에러 발생');
    console.error('='.repeat(80));
    console.error('❌ 에러 내용:', error);
    console.error('⏰ 에러 시간:', new Date().toISOString());
    console.error('='.repeat(80) + '\n');
    
    return NextResponse.json(
      { error: '서버 내부 오류가 발생했습니다.' },
      { status: 500 }
    );
  }
} 