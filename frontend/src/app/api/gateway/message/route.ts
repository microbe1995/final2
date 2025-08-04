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

    // Vercel 환경에서는 백엔드 연결을 시도하지 않고 시뮬레이션
    const isVercel = process.env.VERCEL === '1';
    
    if (isVercel) {
      console.log('🚀 Vercel 환경 감지 - 백엔드 시뮬레이션 모드');
      
      // 시뮬레이션된 응답 생성
      const simulatedResponse = {
        success: true,
        message: body.message,
        processed_at: new Date().toISOString(),
        message_id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        service_response: {
          status: 'success',
          message_id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          processed_message: body.message.toUpperCase(),
          processed_at: new Date().toISOString(),
          log_entry: `Vercel 환경에서 메시지 '${body.message}'가 시뮬레이션 처리되었습니다.`
        }
      };

      console.log('\n' + '='.repeat(80));
      console.log('✅ Vercel 환경 - 시뮬레이션 처리 완료');
      console.log('='.repeat(80));
      console.log('📤 시뮬레이션 응답:', simulatedResponse);
      console.log('⏰ 완료 시간:', new Date().toISOString());
      console.log('='.repeat(80) + '\n');

      return NextResponse.json(simulatedResponse);
    }

    // 로컬 환경에서는 실제 게이트웨이로 요청 전송
    console.log('🏠 로컬 환경 감지 - 실제 게이트웨이 연결 시도');
    
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
    
    // Vercel 환경에서는 에러가 발생해도 시뮬레이션 응답 반환
    if (process.env.VERCEL === '1') {
      console.log('🔄 Vercel 환경에서 에러 발생 - 시뮬레이션 응답으로 대체');
      
      const fallbackResponse = {
        success: true,
        message: 'Vercel 환경에서 처리됨',
        processed_at: new Date().toISOString(),
        message_id: `msg_fallback_${Date.now()}`,
        service_response: {
          status: 'simulated',
          message_id: `msg_fallback_${Date.now()}`,
          processed_message: 'Vercel 환경에서 시뮬레이션 처리됨',
          processed_at: new Date().toISOString(),
          log_entry: 'Vercel 환경에서 백엔드 연결 실패로 인한 시뮬레이션 처리'
        }
      };

      return NextResponse.json(fallbackResponse);
    }
    
    return NextResponse.json(
      { error: '서버 내부 오류가 발생했습니다.' },
      { status: 500 }
    );
  }
} 