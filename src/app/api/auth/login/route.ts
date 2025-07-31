import { NextRequest, NextResponse } from 'next/server';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json();

    // 입력 검증
    if (!email || !password) {
      return NextResponse.json(
        { error: '이메일과 비밀번호를 입력해주세요.' },
        { status: 400 }
      );
    }

    // 이메일 형식 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: '유효한 이메일 주소를 입력해주세요.' },
        { status: 400 }
      );
    }

    // 실제 애플리케이션에서는 데이터베이스에서 사용자 조회
    // 여기서는 데모용으로 하드코딩된 사용자 정보 사용
    const demoUser = {
      id: '1',
      name: '데모 사용자',
      email: 'demo@example.com',
      password: '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8J8J8J8' // 'password123'
    };

    // 이메일 확인 (실제로는 데이터베이스 조회)
    if (email !== demoUser.email) {
      return NextResponse.json(
        { error: '이메일 또는 비밀번호가 올바르지 않습니다.' },
        { status: 401 }
      );
    }

    // 비밀번호 확인
    const isPasswordValid = await bcrypt.compare(password, demoUser.password);
    if (!isPasswordValid && password !== 'password123') { // 데모용 임시 비밀번호
      return NextResponse.json(
        { error: '이메일 또는 비밀번호가 올바르지 않습니다.' },
        { status: 401 }
      );
    }

    // JWT 토큰 생성
    const token = jwt.sign(
      { 
        userId: demoUser.id,
        email: demoUser.email,
        name: demoUser.name
      },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '7d' }
    );

    // 성공 응답
    return NextResponse.json({
      success: true,
      message: '로그인이 완료되었습니다.',
      user: {
        id: demoUser.id,
        name: demoUser.name,
        email: demoUser.email
      },
      token
    });

  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.json(
      { error: '서버 오류가 발생했습니다.' },
      { status: 500 }
    );
  }
} 