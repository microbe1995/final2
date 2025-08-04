import { NextRequest, NextResponse } from 'next/server';

const GATEWAY_URL = process.env.GATEWAY_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    console.log('프론트엔드에서 받은 데이터:', body);

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
      console.error('게이트웨이 에러:', errorData);
      
      return NextResponse.json(
        { error: errorData.detail || '게이트웨이 요청 실패' },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('게이트웨이 응답:', data);

    return NextResponse.json(data);
  } catch (error) {
    console.error('API 라우트 에러:', error);
    return NextResponse.json(
      { error: '서버 내부 오류가 발생했습니다.' },
      { status: 500 }
    );
  }
} 